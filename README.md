# AirPointer

[![Built with Python](https://img.shields.io/badge/built%20with-python-3776AB.svg?logo=python&logoColor=white)](https://python.org)  
[![Gesture Controlled](https://img.shields.io/badge/Control-Hand%20Gesture-yellowgreen)](#)

**AirPointer** is a gesture-based pointer system that allows users to control mouse movements and perform actions using hand gestures detected via a webcam. It is built using **Python**, **OpenCV**, and **MediaPipe**, offering an intuitive and touch-free interaction experience.

---

## Project Objective

Create a virtual pointer system that reacts to real-time hand gestures to perform actions such as:
- Moving the cursor
- Clicking
- Dragging

---

## Core Features

- **Real-time Hand Tracking**  
  Powered by MediaPipe for efficient multi-landmark detection

- **Gesture-to-Action Mapping**  
  Supports gestures for mouse movement, left/right click, and drag

- **Smooth Pointer Movement**  
  Enhanced with filtering to reduce jitter

- **Modular and Extendable**  
  Easy to integrate with other gesture-based control systems

---

##  Installation

### Prerequisites

Ensure the following are installed on your system:

- Python 3.8 or higher
- pip (Python package manager)
- Webcam

---

### Clone and Run the Project Locally

Step 1: Clone the Repository--> 
git clone https://github.com/ujjwal-singh26/AirPointer.git

Step 2: Navigate to the Project Directory-->
cd AirPointer

Step 3: Create Virtual Environment-->
python -m venv gesture_env

Step 4: Activate the Virtual Environment-->
gesture_env\Scripts\activate (for Windows)

Step 5: Install Dependencies-->
pip install -r requirements.txt

Step 6: Run the Gesture Controller-->
python src/Gesture_Controller.py

---

### Project Structure

```text
AirPointer/
├── gesture_env/               # Python virtual environment (ignored in Git)
├── src/                       
│   └── Gesture_Controller.py  # Main script to detect and respond to hand gestures
├── requirements.txt           # Python dependencies
├── .gitignore                 # Files/folders to ignore in Git
└── README.md                  # Project documentation (this file)

```

### How It Works

 The program opens the webcam and continuously reads video frames.
 MediaPipe detects hand landmarks (like fingertips and joints).
 Finger gestures (like index up, both index and middle up, etc.) are interpreted.
 Cursor movements and actions (clicks, drags) are triggered using pyautogui.

### Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new branch
3. Submit a pull request

## Contact

Created by Ujjwal Singh <br>
Email: singhujjwal1703@gmail.com

 ### Thank you for checking out AirPointer! 
