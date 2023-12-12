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

        self._pid_ang_x.output_limits(-MAX_ANG_VEL, MAX_ANG_VEL)
        self._pid_ang_y.output_limits(-MAX_ANG_VEL, MAX_ANG_VEL)
        self._pid_ang_z.output_limits(-MAX_ANG_VEL, MAX_ANG_VEL)
        self._pid_lin_x.output_limits(-MAX_LIN_VEL, MAX_LIN_VEL)
        self._pid_lin_y.output_limits(-MAX_LIN_VEL, MAX_LIN_VEL)

        self._pid_ang_x.set_auto_mode(enabled=True)
        self._pid_ang_y.set_auto_mode(enabled=True)
        self._pid_ang_z.set_auto_mode(enabled=True)
        self._pid_lin_x.set_auto_mode(enabled=True)
        self._pid_lin_y.set_auto_mode(enabled=True)
        
        self._controls = []
    
    def get_controlls(self, setpoints, measures):
        self.controls[0] = self._pid_ang_z(setpoints[0] - measures[0])
        self.controls[1] = self._pid_ang_y(setpoints[1] - measures[1])
        self.controls[2] = self._pid_ang_x(setpoints[2] - measures[2])
        self.controls[3] = self._pid_lin_x(setpoints[3] - measures[3])
        self.controls[4] = self._pid_lin_y(setpoints[4] - measures[4])
        return self.controls
        



