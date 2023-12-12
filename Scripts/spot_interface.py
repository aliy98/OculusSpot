import logging
import time

import bosdyn.api.spot.robot_command_pb2 as spot_command_pb2
import bosdyn.client.util
from bosdyn import geometry
from bosdyn.api import geometry_pb2, trajectory_pb2
from bosdyn.api.geometry_pb2 import SE2Velocity, SE2VelocityLimit, Vec2
from bosdyn.client import create_standard_sdk
from bosdyn.client.estop import EstopClient, EstopEndpoint, EstopKeepAlive
from bosdyn.client.lease import LeaseClient
from bosdyn.client.power import PowerClient
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient, blocking_stand
from bosdyn.client.robot_state import RobotStateClient

LOGGER = logging.getLogger()
VELOCITY_BASE_SPEED = 0.5  # m/s
VELOCITY_BASE_ANGULAR = 0.8  # rad/sec
VELOCITY_CMD_DURATION = 0.6  # seconds
MAX_PITCH = 0.35 # rad
MAX_ROLL = 0.17 # rad


class SpotInterface:
    def __init__(self):
        self._roll = 0.0
        self._pitch = 0.0
        self._yaw = 0.0
        self._z = 0.0
        self._v_x = 0.0
        self._v_y = 0.0
        self._v_rot = 0.0
        self._powered_on = False
        sdk = create_standard_sdk("spot_interface")
        self._robot = sdk.create_robot('192.168.80.3')
        self._robot.authenticate('user', 'wruzvkg4rce4')
        self._robot.time_sync.wait_for_sync()
        self._lease_client = self._robot.ensure_client(LeaseClient.default_service_name)
        self._power_client = self._robot.ensure_client(PowerClient.default_service_name)
        self._robot_state_client = self._robot.ensure_client(RobotStateClient.default_service_name)
        self._robot_command_client = self._robot.ensure_client(RobotCommandClient.default_service_name)
        self._lease = self._lease_client.take()
        self._lease_keepalive = bosdyn.client.lease.LeaseKeepAlive(self._lease_client)
        self._power_on()
        time.sleep(5)
        blocking_stand(self._robot_command_client)
        time.sleep(5)
        LOGGER.info("ready to take commands")
        
    def _orientation_cmd_helper(self, yaw=0.0, roll=0.0, pitch=0.0, height=0.0):
        orientation = geometry.EulerZXY(yaw, roll, pitch)
        cmd = RobotCommandBuilder.synchro_stand_command(body_height=height, footprint_R_body=orientation)
        self._robot_command_client.robot_command(lease=None, command=cmd, end_time_secs=time.time() + VELOCITY_CMD_DURATION)

    def _velocity_cmd_helper(self, v_x=0.0, v_y=0.0, v_rot=0.0):
        mobility_params = self._set_mobility_params()
        cmd = RobotCommandBuilder.synchro_velocity_command(v_x=v_x, v_y=v_y, v_rot=v_rot, params=mobility_params)
        self._robot_command_client.robot_command(lease=None, command=cmd, end_time_secs=time.time() + VELOCITY_CMD_DURATION)
        
    def _set_mobility_params(self):
        obstacles = spot_command_pb2.ObstacleParams(disable_vision_body_obstacle_avoidance=False,
                                                    disable_vision_foot_obstacle_avoidance=False,
                                                    disable_vision_foot_constraint_avoidance=False,
                                                    disable_vision_foot_obstacle_body_assist= False,
                                                    disable_vision_negative_obstacles=False,
                                                    obstacle_avoidance_padding=0.1)
        footprint_R_body = geometry.EulerZXY(roll=self._roll, pitch=self._pitch, yaw=self._yaw)
        position = geometry_pb2.Vec3(x=0.0, y=0.0, z=0.0)
        rotation = footprint_R_body.to_quaternion()
        pose = geometry_pb2.SE3Pose(position=position, rotation=rotation)
        point = trajectory_pb2.SE3TrajectoryPoint(pose=pose)
        traj = trajectory_pb2.SE3Trajectory(points=[point])
        body_control=spot_command_pb2.BodyControlParams(base_offset_rt_footprint=traj)
        speed_limit = SE2VelocityLimit(max_vel=SE2Velocity(linear=Vec2(x=1.0, y=1.0), angular=0.7))
        mobility_params = spot_command_pb2.MobilityParams(obstacle_params=obstacles, vel_limit=speed_limit, body_control=body_control, locomotion_hint=spot_command_pb2.HINT_AUTO)
        return mobility_params
    
    def get_body_vel(self):
        robot_state = self._robot_state_client.get_robot_state()
        vis_vel_ang = robot_state.kinematic_state.velocity_of_body_in_vision.angular
        vis_vel_lin = robot_state.kinematic_state.velocity_of_body_in_vision.linear
        measures = [vis_vel_ang.z, vis_vel_ang.y, vis_vel_ang.x, vis_vel_lin.x, vis_vel_lin.y]
        return measures

    def set_controls(self, controls, dt):
        v_rot = controls[0]
        dpitch = controls[1] * dt
        droll = controls[2] * dt
        v_x = controls[3] 
        v_y = controls[4] 
        if abs(self._pitch + dpitch) < MAX_PITCH:
            self._pitch = self._pitch + dpitch
        if abs(self._roll + droll) < MAX_ROLL:
            self._roll = self._roll + droll
        if abs(v_x) < VELOCITY_BASE_SPEED:
            self._v_x = v_x
        if abs(v_y) < VELOCITY_BASE_SPEED:
            self._v_y = v_y
        if abs(v_rot) < VELOCITY_BASE_ANGULAR:
            self._v_rot = v_rot
        self._orientation_cmd_helper(roll=self._roll, pitch=self._pitch)
        #self._velocity_cmd_helper(v_x=self._v_x, v_y=self._v_y, v_rot=self._v_rot)
        
    def _power_on(self):
        self._robot.power_on()
        self._powered_on=True

    def power_off(self):
        safe_power_off_cmd=RobotCommandBuilder.safe_power_off_command()
        self._robot_command_client.robot_command(command= safe_power_off_cmd)
        time.sleep(2.5)
        self._powered_on=False
    
    def reset_orientation(self):
        self._orientation_cmd_helper(yaw=0.0, roll=0.0, pitch=0.0)



