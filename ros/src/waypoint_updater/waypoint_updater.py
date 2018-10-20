#!/usr/bin/env python


import rospy
import numpy as np
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane, Waypoint
from scipy.spatial import KDTree
from std_msgs.msg import Int32

import math

'''
This node will publish waypoints from the car's current position to some `x` distance ahead.

As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.

Once you have created dbw_node, you will update this node to use the status of traffic lights too.

Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.

TODO (for Yousuf and Aaron): Stopline location for each traffic light.
'''

LOOKAHEAD_WPS = 200 # Number of waypoints we will publish. You can change this number
MAX_DECEL = 5


class WaypointUpdater(object):
    def __init__(self):
        rospy.init_node('waypoint_updater')

        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)
	rospy.Subscriber('/traffic_waypoint', Int32, self.traffic_cb)

	#self.pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)
	self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)

	self.base_lane = None
	self.pose = None
	#self.base_waypoints = None
	self.waypoints_2d = None
	self.waypoint_tree = None

	self.stopline_wp_index = -1

        self.loop()

    def loop(self):
	rate = rospy.Rate(10)
	while not rospy.is_shutdown():
		#if self.pose and self.base_waypoints and self.waypoints_2d:

		if self.pose and self.base_lane and self.waypoints_2d:
			closest_waypoint_index = self.get_closest_waypoint_index()
			#self.publish_waypoints(closest_waypoint_index)
			self.publish_waypoints()
		rate.sleep()

    def get_closest_waypoint_index(self):
	x = self.pose.pose.position.x
	y = self.pose.pose.position.y
	if not self.waypoint_tree:
		#self.waypoints_2d  = [[w.pose.pose.position.x, w.pose.pose.position.y] for w in self.base_waypoints.waypoints]
		self.waypoints_2d  = [[w.pose.pose.position.x, w.pose.pose.position.y] for w in self.base_lane.waypoints]
                self.waypoint_tree = KDTree(self.waypoints_2d)
	closest_index = self.waypoint_tree.query([x,y], 1)[1]
	# is closest waypoint ahead or behind vehicle?
	closest_coord = self.waypoints_2d[closest_index]
	prev_coord = self.waypoints_2d[closest_index-1]

	# hyperplane through closest coords
	cl_vec = np.array(closest_coord)
	prev_vec = np.array(prev_coord)
	pos_vec = np.array([x,y])

	dot = np.dot(pos_vec-prev_vec, cl_vec-pos_vec)
	
	# closest coordinate is behind position position
	if dot < 0: 
		closest_index = (closest_index + 1) % len(self.waypoints_2d)
	return closest_index 

    #def publish_waypoints(self, closest_index):
#       lane = Lane()
#       lane.waypoints = self.base_waypoints.waypoints[closest_index:closest_index + LOOKAHEAD_WPS]
#       self.pub.publish(lane)


    def publish_waypoints(self):
	final_lane = self.generate_lane()
	self.final_waypoints_pub.publish(final_lane)

    def generate_lane(self):
	lane = Lane()

	closest_index = self.get_closest_waypoint_index()
	farthest_index = closest_index + LOOKAHEAD_WPS
	base_waypoints = self.base_lane.waypoints[closest_index:farthest_index]

	if self.stopline_wp_index==-1 or (self.stopline_wp_index >= farthest_index):
		lane.waypoints = base_waypoints
	else:
		lane.waypoints = self.decelerate_waypoints(base_waypoints, closest_index)

	return lane

    def decelerate_waypoints(self, waypoints, closest_index):
	temp = []
	for i, wp in enumerate(waypoints):

		p = Waypoint()
		p.pose = wp.pose

		stop_index = max(self.stopline_wp_index - closest_index - 2, 0)
		dist = self.distance(waypoints, i, stop_index)
		vel = math.sqrt(2*MAX_DECEL * dist)
		if vel < 1.:
			vel = 0.

		p.twist.twist.linear.x = min(vel, wp.twist.twist.linear.x)
		temp.append(p)

	return temp

    def pose_cb(self, msg):
	self.pose = msg
        

    def waypoints_cb(self, waypoints):
	#self.base_waypoints = waypoints
	self.base_lane = waypoints
	if not self.waypoints_2d:
		self.waypoints_2d  = [[w.pose.pose.position.x, w.pose.pose.position.y] for w in waypoints.waypoints]
		self.waypoint_tree = KDTree(self.waypoints_2d)


    def traffic_cb(self, msg):
        # TODO: Callback for /traffic_waypoint message. Implement
        self.stopline_wp_index = msg.data

    def obstacle_cb(self, msg):
        # TODO: Callback for /obstacle_waypoint message. We will implement it later
        pass

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, waypoints, wp1, wp2):
        dist = 0
        dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)
        for i in range(wp1, wp2+1):
            dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
            wp1 = i
        return dist


if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')
