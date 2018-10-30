<<<<<<< HEAD
## Programming a Real Self-Driving Car

# System Integration Project

## Introduction

![alt text] (https://github.com/gradient100/Capstone/blob/master/imgs/readme_img0.jpg "Hello, I am Carla!")

This is the capstone project of the Udacity Self-Driving Car Nanodegree: Programming a Real Self-Driving Car.  I implemented software to automously drive Udacity's self-drivind car, Carla, equipped with the appropriate sensors and actuators, around a test track with traffic lights.  The Robot Operating System, ROS, was used to implement nodes for trajectory planning, drive-by-wire control, and traffic light detection and classification.

## System Architecture

![alt text] (https://github.com/gradient100/Capstone/blob/master/imgs/readme_img1.jpg "Hello, I look important!")

* This project consists of three modules: `Perception`,  `Planning`,  and `Control`.  Each module consists of at least one ROS node, which utilizes publish/subscribe (pub-sub) and request/response service requests to communicate between nodes.  
* The `Perception` module perceives the environment (localization of the car's position, lane lines, traffic lights, etc.) state of the traffic lights,with onboard sensors (cameras, lidar, radar, etc.).
* The `Planning` module dynamically receives the information from perception to publish a trajectory of waypoints and their target velocities.
* The `Control` module dynamically receives the waypoints from planning and smoothly executes the target velocities by directing the appropriate steering, throttle, brake level.

## Implementation

As the above system schematic shows, there are six ROS nodes in three different modules.  Of these, two are already implemented by Udacity: `Obstacle Detector`, `Waypoint Loader`, and  `Waypoint Follower` is unimplemented, as that use case is unanticipated in testing.  Lastly, I have implemented the remaining three ROS nodes : `Traffic Light Detector`, `Waypoint Updater`, and `Drive by Wire` .

### Traffic Light Detector

This node uses the subscribed topics: `/base_waypoints`, `/current_pose`, and `/image_color` to detect  (1) the nearest traffic light in the configuration list of traffic lights to the car's current published position and (2) whether this nearest traffic light is red.  If the light is red, the node decelerates by calculating and publishing the appropriate speeds at each waypoint from the current waypoint to the stop line at the nearest red traffic light.

Whether the light color is red is implemented by taking the subscibed color image and converting to HSV space.  The red color of traffic lights has a hue in a specific range.  The image is then cropped to the upper third (since anticipated traffic lights are high in the field of view), and If this hue occurs above a certain threshold in the image, it is concluded that there are red lights in the image. This method would be adequate for this use case of a highway track with traffic lights and no other (red) cars, because, fortunately, traffic lights have a predetermined position and the same red hue at that position does not regularly exist outside of traffic lights (even red tree leaves are usually cleared around traffic lights, and the red hue of the afternoon horizon can usually be filtered out with the appropriate hue and saturation ranges).

### Waypoint Updater

This node uses the subscribed topics: `/base_waypoints`, `/obstacle_waypoints` (not used), `/traffic_waypoint`, and `/current_pose` to publish `/final_waypoints`, representing a fixed number of waypoints ahead of the car (in order from closest to farthest from the car's current position), as well as computed velocities for each of those waypoints.

The specific waypoints ahead of the car are found simply by using the subscribed base waypoints, finding the closest base waypoint in front of the car's current position, and then appending the next fixed number of waypoints.

The velocities for each of the future waypoints are calculated by using the subscribed `/traffic_waypoint` message published from the traffic light detector node to get the waypoint of the nearest traffic light ahead of the car and the color of that light (red or not red).  If the color of that light is red, the node uses a kinematics equation to find the current velocity needed at each waypoint to reach a final velocity of 0 a fixed number of waypoints before the waypoint of the nearest stop light, with fixed deceleration.

### Drive by Wire

This node uses the subscribed  topics: `/final_waypoints`, `/twist_cmd`, `/vehicle/dbw_enabled`, `/current_pose`, and `/current_velocity` to publish `/vehicle/throttle_cmd`, `/vehicle/steer_cmd`, and `/vehicle/brake_cmd`.

This node sends the `/twist_cmd` message (with target linear and angular velocities), and current velocity, to the twist controller node to determine required steering and throttle (already implemented), and brake.  Brake is calculated as the wheel torque needed, under a fixed maximum deceleration.  Throttle is determined using a pre-implemented pid controller, unless braking is required, and then throttle is set to 0.   Steering is pre-implemented with a yaw controller.

## Installation
=======
Test : This is the project repo for the final project of the Udacity Self-Driving Car Nanodegree: Programming a Real Self-Driving Car. For more information about the project, see the project introduction [here](https://classroom.udacity.com/nanodegrees/nd013/parts/6047fe34-d93c-4f50-8336-b70ef10cb4b2/modules/e1a23b06-329a-4684-a717-ad476f0d8dff/lessons/462c933d-9f24-42d3-8bdc-a08a5fc866e4/concepts/5ab4b122-83e6-436d-850f-9f4d26627fd9).
>>>>>>> b3f74e9900ae6edbb469663a5789bb2a61b1a84e

Please use **one** of the two installation options, either native **or** docker installation.


* Be sure that your workstation is running Ubuntu 16.04 Xenial Xerus or Ubuntu 14.04 Trusty Tahir. [Ubuntu downloads can be found here](https://www.ubuntu.com/download/desktop).
* If using a Virtual Machine to install Ubuntu, use the following configuration as minimum:
  * 2 CPU
  * 2 GB system memory
  * 25 GB of free hard drive space

  The Udacity provided virtual machine has ROS and Dataspeed DBW already installed, so you can skip the next two steps if you are using this.

* Follow these instructions to install ROS
  * [ROS Kinetic](http://wiki.ros.org/kinetic/Installation/Ubuntu) if you have Ubuntu 16.04.
  * [ROS Indigo](http://wiki.ros.org/indigo/Installation/Ubuntu) if you have Ubuntu 14.04.
* [Dataspeed DBW](https://bitbucket.org/DataspeedInc/dbw_mkz_ros)
  * Use this option to install the SDK on a workstation that already has ROS installed: [One Line SDK Install (binary)](https://bitbucket.org/DataspeedInc/dbw_mkz_ros/src/81e63fcc335d7b64139d7482017d6a97b405e250/ROS_SETUP.md?fileviewer=file-view-default)
* Download the [Udacity Simulator](https://github.com/udacity/CarND-Capstone/releases).

### Docker Installation
[Install Docker](https://docs.docker.com/engine/installation/)

Build the docker container
```bash
docker build . -t capstone
```

Run the docker file
```bash
docker run -p 4567:4567 -v $PWD:/capstone -v /tmp/log:/root/.ros/ --rm -it capstone
```

### Port Forwarding
To set up port forwarding, please refer to the [instructions from term 2](https://classroom.udacity.com/nanodegrees/nd013/parts/40f38239-66b6-46ec-ae68-03afd8a601c8/modules/0949fca6-b379-42af-a919-ee50aa304e6a/lessons/f758c44c-5e40-4e01-93b5-1a82aa4e044f/concepts/16cf4a78-4fc7-49e1-8621-3450ca938b77)

### Usage

1. Clone the project repository
```bash
git clone https://github.com/udacity/CarND-Capstone.git
```

2. Install python dependencies
```bash
cd CarND-Capstone
pip install -r requirements.txt
```
3. Make and run styx
```bash
cd ros
catkin_make
source devel/setup.sh
roslaunch launch/styx.launch
```
4. Run the simulator

### Real world testing
1. Download [training bag](https://s3-us-west-1.amazonaws.com/udacity-selfdrivingcar/traffic_light_bag_file.zip) that was recorded on the Udacity self-driving car.
2. Unzip the file
```bash
unzip traffic_light_bag_file.zip
```
3. Play the bag file
```bash
rosbag play -l traffic_light_bag_file/traffic_light_training.bag
```
4. Launch your project in site mode
```bash
cd CarND-Capstone/ros
roslaunch launch/site.launch
```
5. Confirm that traffic light detection works on real life images
