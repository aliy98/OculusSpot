import os
import time
import struct
from spot_interface import SpotInterface
from controller import Controller


def main():
    pipe_path = r'\\.\pipe\MyPipe'
    pipe = open(pipe_path, 'rb')
    spot = SpotInterface()
    controller = Controller()
    start_time = time.time()
    previous_time = start_time
    image_timeout_count = 0
    try:
        while True:
            current_time = time.time()
            dt = current_time - previous_time
            data = pipe.read(24) 
            received_tuple = struct.unpack('6f', data)
            setpoints = list(received_tuple)
            hmd_setpoints = setpoints[0:3]
            touch_setpoints = setpoints[3:6]
            spot_measures = spot.get_body_vel()
            hmd_errors = [a - b for a, b in zip(spot_measures, hmd_setpoints)]
            hmd_controls = controller.get_hmd_controlls(hmd_errors)
            touch_controls = controller.get_touch_controls(touch_setpoints)
            controls = hmd_controls + touch_controls
            print(controls)
            spot.set_controls(controls, dt)
            image_timeout_count = spot.get_image(image_timeout_count)
            time.sleep(0.1)
            previous_time = current_time

    except KeyboardInterrupt:
        pass
    
    finally:
        pipe.close()
        spot.shutdown()
        

if __name__ == '__main__':
    main()
