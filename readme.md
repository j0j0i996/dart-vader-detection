# OpenCV dart scoring tool for Raspberry Pi using 3 Webcams

- Automized camera calibration
- 95% accuracy
- Automatic change of player
- All events are send to a Websocket (SocketIO)
- Mobile app used as frontend:
  - Repository: https://github.com/j0j0i996/dart_vader_scorer_app.
  - The APP can be used directly on iOS and Android by downloading the Expo Go APP and using this link: https://expo.dev/accounts/j0j0i996/projects/scorer_app/
  - Any other frontend can be connected as well

# Getting Started

## Hardware

### Electronics:

- I use a Raspberry Pi 4 Model B (4Gb). Similar hardware should work as well.
- 3 Webcams. It is crucial, that webcams support H.264 compression, as otherwise the Raspberry Pi will have problems with processing. I use these Larmtek webcams: https://www.amazon.de/gp/product/B085ZF1FQC/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1. They are cheap and work well, but have quite a bit of distortion which is filtered out by software. Higher end cameras will probably come with less

### Mounting:

I bought 3 camera clamps and attached them to the light ring of my dart board. Feel free to copy my solution or be creative with other ideas on mouniting the cameras :)

- 3 Camera clamps https://www.amazon.de/gp/product/B00SIRAYX0/ref=ppx_yo_dt_b_asin_title_o01_s00?ie=UTF8&psc=1
- Light ring https://www.amazon.de/Winmau-Dartboard-Plasma-Dartscheibe-Beleuchtung/dp/B07K1G7C4G/ref=sr_1_1?keywords=winmau+light&qid=1640966044&sr=8-1

It is important, that the camera(s) should be placed somwhere with a distance of 20 cm - 50 cm around the board. The center of each camera should approximiatly be the Bullseye. Make sure the whole dart board is visible on the camera image. Rule of thumb: In an image taken with the camera, you should be able to read all numbers on the board. The cameras should be positioned in a distance of approximitally 120 degree around the dart board. I positioned my cameras at the field 18, 2 and 11.

## Software

### Clone git project:

https://github.com/j0j0i996/steel_dart_dect.git

### Create venv (Virtual environment):

https://flask.palletsprojects.com/en/1.1.x/installation/

### Install environment requirements:

> pip install -r requirements.txt

### Enable venv:

> venv/bin/activate

### Run tool

> python3 app.py
>
> --> From here on you should be able to interact with the recognition using the frontend https://github.com/j0j0i996/dart_vader_scorer_app

### Autostart at boot:

I modified the .bashrc file to make sure the recognition automatically starts when booting the Raspberry: https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/

# General concept of dart recognition:

The cameras check for motions by taking the difference of two consecutive images. When a dart hits the board, the difference of the last two images is transformed into a black and white image. In this, only the dart should be white, while the rest of the image is black. Afterward a line is fitted through the middle of the arrow. This is the most important and most complicated step and determines the accuracy of the recognition. Above happens for all 3 cameras in parallel.
Once a line is fitted through the dart for all 3 cameras, the lines are transformed from a camera specific coordinate system to a standardized dart booard coordinate system. In here, the point where all three lines intersect represents the point in which the dart hit the board. This point now only needs to be transformed into a field and a multiplier.
In case one camera doesn't find the dart, e.g. when the dart is hidden by another dart, the recognition also works with 2 cameras. If only one camera finds the dart, a back-up detection of the dart tip jumps in. However the detection with only one camera is much less accurate.

The tool also recognizes if a player removes the darts from the board, by checking the following criteria:

- Large object (hand) in image
- Continuous movements for longer than 1 sec
- Board looks equal as the last time a player removed darts from the board)

--> Check out the images under static/jpg to see how the calibration and dart recognition look like in action
