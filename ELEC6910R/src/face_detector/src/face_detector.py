#!/usr/bin/python

import cv2
import rospy
import numpy as np
import matplotlib.pyplot as plt

from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import String, Bool, Float32
from geometry_msgs.msg import Twist
from sklearn.linear_model import LogisticRegression
from geometry_msgs.msg import PoseStamped, Point, Quaternion
from tf.transformations import * 
import math
from visualization_msgs.msg import Marker
import tf2_ros


# # DATA_PATH = "picture"
clf = None
img_pub = None
matcher = None
myBridge = CvBridge()
switch = False
tfBuffer = None
listener = None


def face_detection(gray):
    """
    Face detection function
    \return: result is the bounding box position in (x1, y1, x2, y2)
    """
    # convert to the original
    gray=cv2.cvtColor(gray,cv2.COLOR_BGR2GRAY)
    
    faces_cascade=cv2.CascadeClassifier('/home/chengwei/Projects/6910/catkin_ws/src/face_detector/haarcascade_frontalface_default.xml')
    # sliding window detection, 1.3 is the scaling factor of the window 
    # return the region contains the faces
    faces = faces_cascade.detectMultiScale(gray,1.3,5)
    result=[]
    for (x,y,width,height) in faces:
        result.append((x,y,x+width,y+height))

    return result


def detectCallback(data):
    if switch is not True:
        return
    # rospy.loginfo(rospy.get_caller_id() + 'I got image')
    cv_img = myBridge.imgmsg_to_cv2(data, "bgr8")
    cv_img = cv2.flip(cv_img, 1)
    faces = face_detection(cv_img)
    img_show = cv_img.copy()
    if faces:
        for (x1,y1,x2,y2) in faces:
            # append face region to the original image
            face_region = cv_img[y1:y2,x1:x2]
            cv2.rectangle(img_show, (x1,y1),(x2,y2),(255,255,0), thickness=8)
        print("face detected", (x1,y1,x2,y2))
    else:
        print("face not detected")

    startX, startY, endX, endY, label = matcher.match(cv_img)
    cv2.rectangle(img_show, (startX, startY), (endX, endY), (0, 0, 255), thickness=8)

    if faces is not []:
        cv2.putText(img_show, label, (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 255), 5)
    img_msgs = myBridge.cv2_to_imgmsg(img_show)
    img_pub.publish(img_msgs)

class TemplateMatching:
    def __init__(self, prefix):
        self.templates = []
        for i in range(5):
            # read in the image and reshape to 100,100
            image_name = prefix + str(i+1) + '.jpg'
            image = cv2.imread(image_name, 0)
            if i is 4 or i is 2:
                image = cv2.flip(image, 1)
            image = cv2.resize(image, (100, 100))
            template = cv2.Canny(image, 50, 200)
            (self.tH, self.tW) = template.shape[:2]
            self.templates.append(template)
        self.labels = ['barack obama', 'avril lavigne', 'asian', 'elf', 'cartoon']

    def match(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        found = None
        found_img = None
        i = 0
        for template in self.templates:
            for scale in np.exp(np.linspace(0.2, 2.5, 10))/6:
                resized = self.resize(gray, width = int(gray.shape[1] * scale))
                r = gray.shape[1] / float(resized.shape[1])

                if resized.shape[0] < self.tH or resized.shape[1] < self.tW:
                    break

                edged = cv2.Canny(resized, 50, 200)
                result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
                (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

                if found is None or maxVal > found[0]:
                    found = (maxVal, maxLoc, r, i)
                    found_img = template
            i = i + 1

        (_, maxLoc, r, idx) = found
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + self.tW) * r), int((maxLoc[1] + self.tH) * r))
        print(maxVal, idx)
        cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), thickness=8)

        return startX, startY, endX, endY, self.labels[idx]

    def resize(self, image, width = None, height = None, inter = cv2.INTER_AREA):
        dim = None
        (h, w) = image.shape[:2]

        if width is None and height is None:
            return image

        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))

        resized = cv2.resize(image, dim, interpolation = inter)

        return resized

def FlagCallback(data):
    global switch
    switch = data.data
    if switch:
        print('Face detector switched on')
    else:
        print('Face detector switched off')
    # false_msgs = Bool()
    # false_msgs.data = False
    # pub.publish(false_msgs)


class Transformer:
    def __init__(self):
        self.robot_sub = rospy.Subscriber('/slam_out_pose', PoseStamped, self.poseCallback, queue_size=1)
        self.robot_pub = rospy.Publisher('/slam_out_pose_rec', PoseStamped, queue_size=1)
        self.img_mk_pub = rospy.Publisher('/image_maker', Marker, queue_size=1)
        
    def poseCallback(self, pose):
        pose_out = pose
        q0 = [pose.pose.orientation.x, pose.pose.orientation.y, pose.pose.orientation.z, pose.pose.orientation.w]
        q1 = quaternion_about_axis(math.pi, (1,0,0))
        q2 = quaternion_multiply(q1, q0)
        pose_out.pose.orientation.x = q2[0]
        pose_out.pose.orientation.y = q2[1]
        pose_out.pose.orientation.z = q2[2]
        pose_out.pose.orientation.w = q2[3]
        self.robot_pub.publish(pose_out)
        
    def rectPose(self, startX, startY, endX, endY):
        marker = Marker()
        marker.type = Marker.CUBE
        pixel = (endX - startX + endY - startY) / 2
        z = 256. / pixel / math.tan(math.pi / 8)

        marker.scale.x = 1
        marker.scale.y = 1
        marker.color.b = 1.0
        marker.color.a = 1.0
        marker.pose.position = geom_msg.Point(0,0,0)
        marker.pose.orientation = geom_msg.Quaternion(0,0,0,1)
        # trans = tfBuffer.lookup_transform('camera_link', 'world', rospy.Time())
        self.img_mk_pub.publish(marker)

    
        




if __name__=='__main__':
    rospy.init_node('face_classification')
    rospy.Subscriber('vrep/image', Image, detectCallback, queue_size=1)
    rospy.Subscriber('/face_detector_flag', Bool, FlagCallback, queue_size=1)
    img_pub = rospy.Publisher('/img_show', Image, queue_size=1)

    matcher = TemplateMatching('/home/chengwei/Projects/6910/catkin_ws/src/face_detector/picture/pic00')
    
    transformer = Transformer()

    tfBuffer = tf2_ros.Buffer()
    listener = tf2_ros.TransformListener(tfBuffer)

    rospy.spin()
