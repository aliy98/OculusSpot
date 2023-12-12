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
    setpoints = []
    start_time = time.time()
    previous_time = start_time

    try:
        while True:
            current_time = time.time()
            dt = current_time - previous_time
            data = pipe.read(20) 
            floats = struct.unpack('5f', data)
            for index, value in enumerate(floats):
                setpoints[index] = value
            measures = spot.get_body_vel()
            controls = controller.get_controlls(float(setpoints), measures)
            spot.set_controls(controls, dt)
            time.sleep(0.1)
            previous_time = current_time

    except KeyboardInterrupt:
        pass
    
    finally:
        pipe.close()
        spot.reset_orientation()
        spot.power_off()
