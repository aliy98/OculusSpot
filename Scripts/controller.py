from simple_pid import PID

MAX_LIN_VEL = 0.5 # m/s
MAX_ANG_VEL = 0.8 # rad/s

class Controller:
    def __init__(self):
        self._kp_ang = 1
        self._ki_ang = 0
        self._kd_ang = 0
        self._kp_lin = 1
        self._ki_lin = 0
        self._kd_lin = 0

        self._pid_ang_x = PID(self._kp_ang, self._ki_ang, self._kd_ang)
        self._pid_ang_y = PID(self._kp_ang, self._ki_ang, self._kd_ang)
        self._pid_ang_z = PID(self._kp_ang, self._ki_ang, self._kd_ang)
        self._pid_lin_x = PID(self._kp_lin, self._ki_lin, self._kd_lin)
        self._pid_lin_y = PID(self._kp_lin, self._ki_lin, self._kd_lin)

        self._pid_ang_x.output_limits = (-MAX_ANG_VEL, MAX_ANG_VEL)
        self._pid_ang_y.output_limits = (-MAX_ANG_VEL, MAX_ANG_VEL)
        self._pid_ang_z.output_limits = (-MAX_ANG_VEL, MAX_ANG_VEL)
        self._pid_lin_x.output_limits = (-MAX_LIN_VEL, MAX_LIN_VEL)
        self._pid_lin_y.output_limits = (-MAX_LIN_VEL, MAX_LIN_VEL)

        self._pid_ang_x.set_auto_mode(enabled=True)
        self._pid_ang_y.set_auto_mode(enabled=True)
        self._pid_ang_z.set_auto_mode(enabled=True)
        self._pid_lin_x.set_auto_mode(enabled=True)
        self._pid_lin_y.set_auto_mode(enabled=True)
    
    def get_controlls(self, errors):
        controls = []
        controls.append(self._pid_ang_z(errors[0]))
        controls.append(self._pid_ang_y(errors[1]))
        controls.append(self._pid_ang_x(errors[2]))
        controls.append(self._pid_lin_x(errors[3]))
        controls.append(self._pid_lin_y(errors[4]))
        return controls
        



