import os
import json
import sys
import src.cameraClass as camCls
import src.camMngClass as camMng
import atexit
import asyncio
import websockets
import cv2
import time
import logging

logger = logging.getLogger('Logging')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('logger.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

cam_manager = camMng.camManager(local_video=False)

def exit_handler():
    cam_manager.stop_cams()

async def app(websocket, path):
    logger.info('Server connected')
    while True:
        try:
            field, multiplier, nextPlayer = cam_manager.detection()
            await websocket.send(json.dumps({"field": field, "multiplier": multiplier, "nextPlayer": nextPlayer}))
            print('message sent')
            logger.info('Event detected')
        except Exception as ex:
                print(ex)      
                logger.error(ex)

if __name__ == '__main__':

    logger.info('Program start')
    atexit.register(exit_handler)

    cam_manager.start_cams()

    start_server = websockets.serve(app, "192.168.0.10", 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

    #cam_manager.take_pic()
    #cam_manager.manual_calibration()

    """
    while True:
        try:
            cam_manager.detection()
        except Exception as ex:
            print(ex)
    """

    cam_manager.stop_cams()
