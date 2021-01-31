import os
import json
import sys
import src.cameraClass as camCls
import src.camMngClass as camMng
import atexit
import aiohttp
import asyncio
import cv2

GAME_SERVER_URL = 'http://localhost:8000/'
GAME_ID = 'dascr'
GAME_URL = GAME_SERVER_URL + 'api/game/' + GAME_ID + '/'

cam_manager = camMng.camManager()

def exit_handler():
    cam_manager.stop_cams()

async def main():

    global GAME_SERVER_URL, GAME_ID, GAME_URL

    async with aiohttp.ClientSession() as session:
        async with session.get(GAME_SERVER_URL) as response:

            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])


        while True:
            try:
                number, multiplier, nextPlayer = cam_manager.detection()
            except Exception as ex:
                print(ex)
                continue

            if nextPlayer:
                async with session.post(GAME_URL + 'nextPlayer') as response:
                    print(response)
            else:
                async with session.post(GAME_URL + 'throw/{}/{}'.format(number, multiplier)) as response:
                    print(response)

if __name__ == '__main__':
    atexit.register(exit_handler)
    
    cam_manager.start_cams()

    #cam_manager.take_pic()

    #cam_manager.manual_calibration()
    #cam_manager.cam_list[0].calibrate_board(18)
    #cam_manager.cam_list[1].calibrate_board(11)
    #cam_manager.cam_list[2].calibrate_board(2) 

    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(main())

    while True:
        try:
            cam_manager.detection()
        except Exception as ex:
            print(ex)
            
    #app.run(host='0.0.0.0', port='8090') #, debug=True



    cam_manager.stop_cams()
