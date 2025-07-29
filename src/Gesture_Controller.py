import cv2
import mediapipe as mp
import pyautogui
import math
from enum import IntEnum
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbcontrol
from google.protobuf.json_format import MessageToDict

pyautogui.FAILSAFE = False
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Gesture Enumeration
class Gest(IntEnum):
    FIST = 0
    PINKY = 1
    RING = 2
    MID = 4
    LAST3 = 7
    INDEX = 8
    FIRST2 = 12
    LAST4 = 15
    THUMB = 16
    PALM = 31
    V_GEST = 33
    TWO_FINGER_CLOSED = 34
    PINCH_MAJOR = 35
    PINCH_MINOR = 36

class HLabel(IntEnum):
    MINOR = 0
    MAJOR = 1

# Hand Recognition Class
class HandRecog:
    def __init__(self, hand_label):
        self.finger = 0
        self.ori_gesture = Gest.PALM
        self.prev_gesture = Gest.PALM
        self.frame_count = 0
        self.hand_result = None
        self.hand_label = hand_label

    def update_hand_result(self, hand_result):
        self.hand_result = hand_result

    def get_signed_dist(self, point):
        sign = -1
        if self.hand_result.landmark[point[0]].y < self.hand_result.landmark[point[1]].y:
            sign = 1
        dist = (self.hand_result.landmark[point[0]].x - self.hand_result.landmark[point[1]].x)**2
        dist += (self.hand_result.landmark[point[0]].y - self.hand_result.landmark[point[1]].y)**2
        return math.sqrt(dist) * sign

    def get_dist(self, point):
        dist = (self.hand_result.landmark[point[0]].x - self.hand_result.landmark[point[1]].x)**2
        dist += (self.hand_result.landmark[point[0]].y - self.hand_result.landmark[point[1]].y)**2
        return math.sqrt(dist)

    def get_dz(self, point):
        return abs(self.hand_result.landmark[point[0]].z - self.hand_result.landmark[point[1]].z)

    def set_finger_state(self):
        if self.hand_result is None:
            return
        points = [[8,5,0],[12,9,0],[16,13,0],[20,17,0]]
        self.finger = 0
        for point in points:
            dist = self.get_signed_dist(point[:2])
            dist2 = self.get_signed_dist(point[1:])
            try:
                ratio = round(dist/dist2, 1)
            except:
                ratio = 0
            self.finger <<= 1
            if ratio > 0.5:
                self.finger |= 1

    def get_gesture(self):
        if self.hand_result is None:
            return Gest.PALM

        current_gesture = Gest.PALM
        if self.finger in [Gest.LAST3,Gest.LAST4] and self.get_dist([8,4]) < 0.05:
            current_gesture = Gest.PINCH_MINOR if self.hand_label == HLabel.MINOR else Gest.PINCH_MAJOR
        elif Gest.FIRST2 == self.finger:
            dist1 = self.get_dist([8,12])
            dist2 = self.get_dist([5,9])
            ratio = dist1/dist2
            if ratio > 1.7:
                current_gesture = Gest.V_GEST
            else:
                if self.get_dz([8,12]) < 0.1:
                    current_gesture = Gest.TWO_FINGER_CLOSED
                else:
                    current_gesture = Gest.MID
        else:
            current_gesture = self.finger

        if current_gesture == self.prev_gesture:
            self.frame_count += 1
        else:
            self.frame_count = 0

        self.prev_gesture = current_gesture
        if self.frame_count > 4:
            self.ori_gesture = current_gesture
        return self.ori_gesture

# Controller Class
class Controller:
    tx_old = ty_old = 0
    flag = grabflag = pinchmajorflag = pinchminorflag = False
    pinchstartxcoord = pinchstartycoord = None
    pinchdirectionflag = None
    prevpinchlv = pinchlv = framecount = 0
    prev_hand = None
    pinch_threshold = 0.3

    def getpinchxlv(hand_result): return round((hand_result.landmark[8].x - Controller.pinchstartxcoord) * 10, 1)
    def getpinchylv(hand_result): return round((Controller.pinchstartycoord - hand_result.landmark[8].y) * 10, 1)

    def changesystembrightness():
        curr = sbcontrol.get_brightness(display=0)/100.0 + Controller.pinchlv/50.0
        sbcontrol.set_brightness(int(max(0, min(1, curr)) * 100))

    def changesystemvolume():
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar() + Controller.pinchlv/50.0
        volume.SetMasterVolumeLevelScalar(max(0, min(1, current)), None)

    def scrollVertical(): pyautogui.scroll(120 if Controller.pinchlv > 0 else -120)
    def scrollHorizontal():
        pyautogui.keyDown('shift'); pyautogui.keyDown('ctrl')
        pyautogui.scroll(-120 if Controller.pinchlv > 0 else 120)
        pyautogui.keyUp('ctrl'); pyautogui.keyUp('shift')

    def get_position(hand_result):
        point = 9
        x, y = int(hand_result.landmark[point].x * pyautogui.size()[0]), int(hand_result.landmark[point].y * pyautogui.size()[1])
        if Controller.prev_hand is None:
            Controller.prev_hand = [x, y]
        delta_x = x - Controller.prev_hand[0]
        delta_y = y - Controller.prev_hand[1]
        Controller.prev_hand = [x, y]
        distsq = delta_x**2 + delta_y**2
        ratio = 0 if distsq <= 25 else (0.07 * distsq**0.5 if distsq <= 900 else 2.1)
        return pyautogui.position()[0] + delta_x * ratio, pyautogui.position()[1] + delta_y * ratio

    def pinch_control_init(hand_result):
        Controller.pinchstartxcoord = hand_result.landmark[8].x
        Controller.pinchstartycoord = hand_result.landmark[8].y
        Controller.pinchlv = Controller.prevpinchlv = Controller.framecount = 0

    def pinch_control(hand_result, controlHorizontal, controlVertical):
        if Controller.framecount == 5:
            Controller.framecount = 0
            Controller.pinchlv = Controller.prevpinchlv
            (controlHorizontal if Controller.pinchdirectionflag else controlVertical)()
        lvx, lvy = Controller.getpinchxlv(hand_result), Controller.getpinchylv(hand_result)
        if abs(lvy) > abs(lvx) and abs(lvy) > Controller.pinch_threshold:
            Controller.pinchdirectionflag = False
            Controller.framecount = Controller.framecount + 1 if abs(Controller.prevpinchlv - lvy) < Controller.pinch_threshold else 0
            Controller.prevpinchlv = lvy
        elif abs(lvx) > Controller.pinch_threshold:
            Controller.pinchdirectionflag = True
            Controller.framecount = Controller.framecount + 1 if abs(Controller.prevpinchlv - lvx) < Controller.pinch_threshold else 0
            Controller.prevpinchlv = lvx

    def handle_controls(gesture, hand_result):
        if gesture != Gest.PALM:
            x, y = Controller.get_position(hand_result)
        if gesture != Gest.FIST and Controller.grabflag:
            Controller.grabflag = False
            pyautogui.mouseUp()
        if gesture != Gest.PINCH_MAJOR and Controller.pinchmajorflag:
            Controller.pinchmajorflag = False
        if gesture != Gest.PINCH_MINOR and Controller.pinchminorflag:
            Controller.pinchminorflag = False
        if gesture == Gest.V_GEST:
            Controller.flag = True; pyautogui.moveTo(x, y, duration=0.1)
        elif gesture == Gest.FIST:
            if not Controller.grabflag: Controller.grabflag = True; pyautogui.mouseDown()
            pyautogui.moveTo(x, y, duration=0.1)
        elif gesture == Gest.MID and Controller.flag:
            pyautogui.click(); Controller.flag = False
        elif gesture == Gest.INDEX and Controller.flag:
            pyautogui.click(button='right'); Controller.flag = False
        elif gesture == Gest.TWO_FINGER_CLOSED and Controller.flag:
            pyautogui.doubleClick(); Controller.flag = False
        elif gesture == Gest.PINCH_MINOR:
            if not Controller.pinchminorflag:
                Controller.pinch_control_init(hand_result); Controller.pinchminorflag = True
            Controller.pinch_control(hand_result, Controller.scrollHorizontal, Controller.scrollVertical)
        elif gesture == Gest.PINCH_MAJOR:
            if not Controller.pinchmajorflag:
                Controller.pinch_control_init(hand_result); Controller.pinchmajorflag = True
            Controller.pinch_control(hand_result, Controller.changesystembrightness, Controller.changesystemvolume)

# Main Controller
class GestureController:
    gc_mode = 1
    cap = cv2.VideoCapture(0)
    CAM_HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    CAM_WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    hr_major = hr_minor = None
    dom_hand = True

    def classify_hands(results):
        left = right = None
        try:
            handedness_dict = MessageToDict(results.multi_handedness[0])
            if handedness_dict['classification'][0]['label'] == 'Right':
                right = results.multi_hand_landmarks[0]
            else:
                left = results.multi_hand_landmarks[0]
            handedness_dict = MessageToDict(results.multi_handedness[1])
            if handedness_dict['classification'][0]['label'] == 'Right':
                right = results.multi_hand_landmarks[1]
            else:
                left = results.multi_hand_landmarks[1]
        except:
            pass
        GestureController.hr_major = right if GestureController.dom_hand else left
        GestureController.hr_minor = left if GestureController.dom_hand else right

    def start(self):
        print("[INFO] Starting Gesture Controller...")
        handmajor = HandRecog(HLabel.MAJOR)
        handminor = HandRecog(HLabel.MINOR)
        with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
            while GestureController.cap.isOpened() and GestureController.gc_mode:
                success, image = GestureController.cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    continue
                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = hands.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                if results.multi_hand_landmarks:
                    GestureController.classify_hands(results)
                    handmajor.update_hand_result(GestureController.hr_major)
                    handminor.update_hand_result(GestureController.hr_minor)
                    handmajor.set_finger_state()
                    handminor.set_finger_state()
                    gest_name = handminor.get_gesture()
                    if gest_name == Gest.PINCH_MINOR:
                        Controller.handle_controls(gest_name, handminor.hand_result)
                    else:
                        gest_name = handmajor.get_gesture()
                        Controller.handle_controls(gest_name, handmajor.hand_result)
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                else:
                    Controller.prev_hand = None
                cv2.imshow('Gesture Controller', image)
                if cv2.waitKey(5) & 0xFF == 13:  # Press Enter to quit
                    break
        GestureController.cap.release()
        cv2.destroyAllWindows()

# Start program
if __name__ == "__main__":
    print("Starting Gesture Controller")
    gc1 = GestureController()
    gc1.start()
