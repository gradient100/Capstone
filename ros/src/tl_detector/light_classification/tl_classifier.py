from styx_msgs.msg import TrafficLight
import cv2
import numpy as np

THRESH_RED = 40
FRACTION_KEPT = 1/3.0

class TLClassifier(object):
    def __init__(self):
        #TODO load classifier
        pass

    def get_classification(self, image):
        """Determines the color of the traffic light in the image

        Args:
            image (cv::Mat): image containing the traffic light

        Returns:
            int: ID of traffic light color (specified in styx_msgs/TrafficLight)

        """
	image = image[0:int(image.shape[0] * FRACTION_KEPT) , : ]
	hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	
	RED_MIN1 = np.array([0,100,100], np.uint8)
	RED_MAX1 = np.array([10,255,255], np.uint8)

	# hsv range goes from 0-180 in Open CV
	RED_MIN2 = np.array([170, 100, 100], np.uint8) 
	RED_MAX2 = np.array([180, 255, 255], np.uint8)

	frame_threshed1 = cv2.inRange(hsv_img, RED_MIN1, RED_MAX1)
	frame_threshed2 = cv2.inRange(hsv_img, RED_MIN2, RED_MAX2)
	if cv2.countNonZero(frame_threshed1) + cv2.countNonZero(frame_threshed2) > THRESH_RED:
		return TrafficLight.RED

#	YELLOW_MIN = np.array([40.0/360*255, 100, 100], np.uint8)
#	YELLOW_MAX = np.array([66.0/360*255, 255, 255], np.uint8)
#        frame_threshed3 = cv2.inRange(hsv_img, YELLOW_MIN, YELLOW_MAX)
#        if cv2.countNonZero(frame_threshed3) > THRESH:
#                return TrafficLight.YELLOW

#	GREEN_MIN = np.array([90.0/360*255, 100, 100], np.uint8)
#        GREEN_MAX = np.array([140.0/360*255, 255, 255], np.uint8)
#        frame_threshed4 = cv2.inRange(hsv_img, GREEN_MIN, GREEN_MAX)
#        if cv2.countNonZero(frame_threshed3) > THRESH:
#                return TrafficLight.GREEN

	return TrafficLight.UNKNOWN
