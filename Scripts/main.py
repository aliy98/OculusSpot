import os
import time
import struct
from spot_interface import SpotInterface
from controller import Controller
import matplotlib.pyplot as plt

def main():
    pipe_path = r'\\.\pipe\MyPipe'
    pipe = open(pipe_path, 'rb')
    spot = SpotInterface()
    controller = Controller()
    start_time = time.time()
    previous_time = start_time

    t = []
    e_roll = []
    c_roll = []
    e_pitch = []
    c_pitch = []
    e_yaw = []
    c_yaw = []

    try:
        while True:
            current_time = time.time()
            dt = current_time - previous_time
            data = pipe.read(20) 
            received_tuple = struct.unpack('5f', data)
            setpoints = list(received_tuple)
            measures = spot.get_body_vel()
            errors = [a - b for a, b in zip(measures, setpoints)]
            print(errors)
            controls = controller.get_controlls(errors)
            spot.set_controls(controls, dt)
            time.sleep(0.1)
            previous_time = current_time

            t.append(current_time)
            e_yaw.append(errors[0])
            c_yaw.append(controls[0])
            e_pitch.append(errors[1])
            c_pitch.append(controls[1])
            e_roll.append(errors[2])
            c_roll.append(controls[2])

    except KeyboardInterrupt:
        pass
    
    finally:
        pipe.close()
        # plt.subplot(3, 1, 1)
        # plt.plot(t, e_roll, label='e_roll', color='blue')
        # plt.plot(t, c_roll, label='c_roll', color='red')
        # plt.xlabel('Time (sec)')
        # plt.ylabel('Values (rad)')
        # plt.legend()
        # plt.title('Roll Control')

        # plt.subplot(3, 1, 2)
        plt.plot(t, e_pitch, label='e_pitch', color='blue')
        plt.plot(t, c_pitch, label='c_pitch', color='red')
        plt.xlabel('Time (sec)')
        plt.ylabel('Values (rad)')
        plt.legend()
        plt.title('Pitch Control')

        # plt.subplot(3, 1, 3)
        # plt.plot(t, e_yaw, label='e_yaw', color='blue')
        # plt.plot(t, c_yaw, label='c_yaw', color='red')
        # plt.xlabel('Time (sec)')
        # plt.ylabel('Values (rad)')
        # plt.legend()
        # plt.title('Yaw Control')

        # plt.tight_layout()
        plt.show()

        spot.shutdown()
        

if __name__ == '__main__':
    main()
