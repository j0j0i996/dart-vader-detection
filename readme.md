### Automated dart scoring project using a raspberry pi and opencv

- Dart recognition is built with python3. For image processing openCV is used.
- Backend of website is built with Flask
- Frontend is built with HTML, CSS and Javascript

# Readme.md

**Table of Contents**

# Getting Started
##Set up camera for raspberry pi: 
The camera(s) should be placed somewhere around the dart board with a clear view on the board. A good distance is 20-50 cm from the outer board edge. 

### Clone git project:
https://github.com/j0j0i996/steel_dart_dect.git

### Create venv (Virtual environment):
https://flask.palletsprojects.com/en/1.1.x/installation/
###Install environment requirements:
> pip install -r requirements.txt

### Enable venv:
> venv/bin/activate

### Disable venv:
> deactivate

# Concept of dart recognition:

> The used flow-charts can be viewed and edited in *dart_project.drawio*

We are going to use different coordinate systems to simplify the recognition of the dart and the transformation of the recognized position into an actual score. For the recognition of the dart, a camera specific coordinate system is used. Afterward the relative dart position will be transformed into a standardized coordinate system with a standardized position of the dart board. Lastly, we will transform the cathesian coordinates of the dart position into polar coordinates to simplify the process of mapping the dart position to a score.


## General Flow

Let's look into the general flow first. Initially the camera needs to be calibrated. This means we need to detect the dart board either automatically or manually to enable a later transformation to the standard coordinate system of the standard board. 

Afterwards a motion detection will detect changes in the camera capture and will store an image before and after the motion. A dartThrow class will be initialzed. To be continued


### 1. Calibration (WIP)

### 2.  Motion detection

To check for motions, the difference between two consecutive images is being taken. If there is a difference, there was some kind of motion. To filter out noises and objects which are not darts, thresholds number of different pixels and the duration of the motion are used.

<img src="docs/Motion_detection.png?raw=true" alt="drawing" width="200"/>

### 3.  Detect dart position


To be filled

### 4 Transform dart tip position to score

Now we have a position of the dart tip, which is relative to the position of the camera. We need to transform this into the standardized coordinates of the standard board ((0,0) is the center of the board). Afterwards we can transform the position into polar coordinates and use that coordinates to determine the score.

<img src="docs/Get_score_flow.png?raw=true" alt="drawing" width="300"/>

# Classes

<img src="docs/Classes.png?raw=true" alt="drawing" width="400"/>

# Other
