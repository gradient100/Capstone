import rospy
from pid import PID
from yaw_controller import YawController
from lowpass import LowPassFilter

GAS_DENSITY = 2.858
ONE_MPH = 0.44704


class Controller(object):
    def __init__(self, vehicle_mass, fuel_capacity, brake_deadband, decel_limit, accel_limit, wheel_radius, wheel_base, steer_ratio, max_lat_accel, max_steer_angle):
	
	self.yaw_controller = YawController(wheel_base, steer_ratio, 0.1, max_lat_accel, max_steer_angle)

	kp = 0.3
	ki = 0.1
	kd = 0.
	tMin = 0. # Min throttle
	tMax = 0.2 # Max throttle
	self.throttle_controller = PID(kp, ki, kd, tMin, tMax)

	tau = 0.5 # 1/(2pi*tau) = cutoff frequency
	ts = 0.02 # Sample time
	self.vel_lpf = LowPassFilter(tau, ts)

	self.vehicle_mass = vehicle_mass
	self.fuel_capacity = fuel_capacity
	self.brake_deadband = brake_deadband
	self.decel_limit = decel_limit
	self.accel_limit = accel_limit
	self.wheel_radius = wheel_radius

	self.last_time = rospy.get_time()

    def control(self, current_vel, dbw_enabled, targ_linear_vel, targ_angular_vel):
	if not dbw_enabled:
		self.throttle_controller.reset()
		return 0., 0., 0.
	current_vel = self.vel_lpf.filt(current_vel)
	steering = self.yaw_controller.get_steering(targ_linear_vel, targ_angular_vel, current_vel)

	vel_diff = current_vel - targ_linear_vel
	self.last_vel = current_vel

	current_time = rospy.get_time()
	sample_time = current_time-self.last_time
	self.last_time = current_time

	throttle = self.throttle_controller.step(-vel_diff, sample_time) # -vel_diff because vel_diff is neg if currently going slower than desired speed.  So, we want to throttle, but pid controller is expecting a positive diff
	brake = 0.
	
	if targ_linear_vel == 0. and current_vel < 0.1:
		throttle = 0.
		brake = 700. #N*m
	elif throttle < .1 and vel_diff > 0:
		throttle = 0.
		#decel = min(abs(vel_diff), abs(self.decel_limit))
		decel = min(abs(1.0*vel_diff/sample_time), abs(self.decel_limit))
		brake = abs(decel)*self.vehicle_mass*self.wheel_radius
		#brake = min(abs(decel)*self.vehicle_mass*self.wheel_radius,700)

	return throttle, brake, steering
