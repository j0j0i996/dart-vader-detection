### Automated dart scoring project using a raspberry pi and opencv

- Dart recognition is built with python3. For image processing openCV is used.
- Backend of website is built with Flask
- Frontend is built with HTML, CSS and Javascript

# Readme.md

**Table of Contents**


# Getting Started
##Set up camera for raspberry pi: 
The camera(s) should be placed somewhere around the dart board with a clear view on the board. A good distance is 20-50 cm from the outer board edge. The angle between the board plane and the camera should be kept low.
https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/3

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


## 1.  General Flow

Let's look into the general flow first. Initially the camera needs to be calibrated. This means we need to detect the dart board either automatically or manually to enable a later transformation to the standard coordinate system of the standard board. 

Afterwards a motion detection will detect changes in the camera capture and will store an image before and after the motion. A dartThrow class will be initialzed. The class checks if the motion was actually a dart. In case it is, we proceed with the recoginition of the score of the dart.

![alt text](docs/General_flow.png?raw=true)

## 2.  Detect dart tip

We now have two images - one from before the throw and one from after the throw. We use opencv to take the difference of both images. Other openCV functions help us to convert the image to black and white, whereas the white pixels are the one which haved changed.

![alt text](docs/BW_diff.png?raw=true)

To detect the dart tip positon now, we can simply use the most top white pixel in the image difference. This works as long as the angle of the camera relative to the dart board plane is lower than angle between the dart board and the dart.

![alt text](docs/Detection_flow.png?raw=true)

## 3. Transform dart tip postion to score

Now we have a position of the dart tip, which is relative to the position of the camera. We need to transform this into the standardized coordinates of the standard board ((0,0) is the center of the board). Afterwards we can transform the position into polar coordinates and use that coordinates to estimate the score.

![alt text](docs/Get_score_flow.png?raw=true)

# Classes

![alt text](docs/Classes.png?raw=true)

# Other
