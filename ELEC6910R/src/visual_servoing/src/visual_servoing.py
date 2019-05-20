#!/usr/bin/env python

import cv2
import rospy
import numpy as np

from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import String, Bool, Float32
from geometry_msgs.msg import Twist, TwistStamped

myBridge = CvBridge()
cmd_pub = []
img_pub = []
tk_x_pub = []
tk_r_pub = []
pub = []
switch = False
tracker = 'Naive'
angular_pid = linear_pid = []
angular_kf = linear_kf = []



def pub_vel(publisher, linear, angular):
    twist = Twist()
    twist.linear.x = linear
    twist.angular.z = angular
    publisher.publish(twist)

def pub_err(publisher, tracker, err_x, err_r):
    twist = TwistStamped()
    twist.header.frame_id = tracker
    twist.twist.linear.x = err_x
    twist.twist.linear.y = err_r
    publisher.publish(twist)

def FindObjectCenter(img):
    x = 0.0
    y = 0.0
    r = 0.0
    counter = 0
    imgHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(imgHSV,np.array([16,39,50]),np.array([45,255,255]))
    kernelOpen=np.ones((8,8))
    kernelClose=np.ones((25,25))
    maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
    maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
    conts,hi =cv2.findContours(maskClose.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    img_show=img
    h = 0
    w = 0
    if conts:
        x,y,w,h=cv2.boundingRect(conts[0])
        cv2.rectangle(img_show,(x,y),(x+w,y+h),(0,0,255), 2)
        cx = (x+w+x)/2
        cy = (y+y+h)/2
        cv2.circle(img_show,(cx,cy), 10, (0,0,255), -1)
        r = (float(h*w))/(512*512)
    else:
        cx = 0
        cy = 0
    # print("center x ", cx,"\n", "center y ",cy)
    # cv2.imshow("img_show",img_show)
    # cv2.waitKey(1)
    img_msgs = myBridge.cv2_to_imgmsg(img_show)
    img_pub.publish(img_msgs)
    return cx, cy, r

def NaiveTracker(x, y, r):    
    linear = 0.0
    angular = 0.0
    traget_x = 256
    traget_r = 1./8.
    if r:
        angular = float(traget_x - x)*3/256
    else: 
        angular = 0
    if r < traget_r:
        linear = 0.8
    elif r > traget_r:
        linear = -0.8
    else:
        linear = 0
    if r < 0.01:
        angular = 0
        linear = 0
    angular = max(min(angular, 1), -1)
    linear = max(min(linear, 0.8), -0.8)
    print("[Naive controller] x = ", x, "angular = ", angular)
    pub_err(tk_pub, 'Naive', float(traget_x-x)/256, traget_r - r)
    return linear, angular 

def PIDTracker(x, y, r):
    linear = angular = 0.0
    traget_x = 256
    traget_r = 1./8.
    angular = angular_pid.update(float(traget_x-x)/256)
    linear = linear_pid.update(traget_r - r)
    
    angular = max(min(angular, 1), -1)
    linear = max(min(linear, 0.8), -0.8)
    print('[PID controller]: err_x = ', float(traget_x-x), 'angular = ', angular, 'error_z = ', traget_r - r, 'linear = ', linear)
    pub_err(tk_pub, 'PID', float(traget_x-x)/256, traget_r - r)
    return linear, angular

def KalmanTraker(x, y, r):
    linear = angular = 0.0
    traget_x = 256
    traget_r = 1./8.
    angular_kf.update(float(x-traget_x)/256)
    linear_kf.update(r-traget_r)
    angular = angular_kf.lqr_control()
    linear = linear_kf.lqr_control()

    angular = max(min(angular, 1), -1)
    linear = max(min(linear, 0.8), -0.8)

    print('[Kalman controller]: err_x = ', float(traget_x-x), 'angular = ', angular, 'error_z = ', traget_r - r, 'linear = ', linear)
    pub_err(tk_pub, 'Kalman', float(traget_x-x)/256, traget_r - r)
    return linear, angular

def TrackingCallback(data):
    # rospy.loginfo(rospy.get_caller_id())
    global tracker
    if not switch:
        return

    img = myBridge.imgmsg_to_cv2(data, "bgr8")
    img = cv2.flip(img, 1)

    x, y ,r = FindObjectCenter(img)
    print(tracker)
    if tracker == 'Naive':
        linear, angular = NaiveTracker(x, y, r)
    elif tracker == 'PID':
        linear, angular = PIDTracker(x, y, r)
    elif tracker == 'Kalman':
        linear, angular = KalmanTraker(x, y, r)
    else:
        linear = angular = 0.0

    pub_vel(cmd_pub, linear, angular)

def TrackerSelectionCallback(data):
    global tracker
    tracker = data.data
    print('Tracker selected: ', tracker)

def FlagCallback(data):
    switch = data.data
    if switch:
        print('Visual servoing switched on')
    else:
        print('Visual servoing switched off')
    false_msgs = Bool()
    false_msgs.data = False
    pub.publish(false_msgs)
    # print(switch)

class PID:
    def __init__(self, P=0.2, I=0.0, D=0.0, windup_guard=20):

        self.Kp = P
        self.Ki = I
        self.Kd = D

        self.current_time = 0
        self.last_time = self.current_time
        self.windup_guard = windup_guard

        self.clear()

    def clear(self):
        """Clears PID computations and coefficients"""
        self.SetPoint = 0.0

        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0

        # Windup Guard
        self.int_error = 0.0
        # self.windup_guard = 20.0

        self.output = 0.0

    def update(self, feedback_value):
        error = self.SetPoint - feedback_value

        delta_error = error - self.last_error

        self.PTerm = self.Kp * error
        self.ITerm += error

        if (self.ITerm < -self.windup_guard):
            self.ITerm = -self.windup_guard
        elif (self.ITerm > self.windup_guard):
            self.ITerm = self.windup_guard

        self.DTerm = delta_error

        self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)

        return self.output

class KalmanFilter:
    def __init__(self, A = 1, B = 1, C = 1, R = 0.1, Q = 0.1):
        self.A = A
        self.B = B
        self.C = C
        self.R = R
        self.Q = Q
        self.x_ = self.x = 0
        self.P_ = self.P = 0.1

        self.clear()
    
    def clear(self):
        self.x_ = self.x = 0
        self.P_ = self.P = 0.1

    def update(self, y):
        self.x_ = self.x
        self.P_ = self.P
        # Predicition update
        x_ = self.A * self.x_
        P_ = self.A * self.P_ * self.A + self.Q
        # Measurement update
        K = P_ * self.C / (self.C * P_ * self.C + self.R)
        self.x = x_ + K * (y - self.C * x_)
        self.P = P_ - K * self.C * P_

    def lqr_control(self):
        L = - self.B * self.P * self.A / (self.B * self.P * self.B + self.R)
        u = L * self.x
        print("[debug: ] x", self.x, "P", self.P, "L", L, "u", u)
        return u


if __name__ == '__main__':
    rospy.init_node('visual_servoing')

    rospy.Subscriber('vrep/image', Image, TrackingCallback, queue_size=1)
    rospy.Subscriber('visual_servoing_flag', Bool, FlagCallback, queue_size=1)
    rospy.Subscriber('traker_selector', String, TrackerSelectionCallback, queue_size=1)
    pub = rospy.Publisher('/vrep/laser_switch', Bool, queue_size=1)
    false_msgs = Bool()
    false_msgs.data = False
    pub.publish(false_msgs)
    cmd_pub = rospy.Publisher('/vrep/cmd_vel', Twist, queue_size=1)
    img_pub = rospy.Publisher('/img_show', Image, queue_size=1)
    tk_pub = rospy.Publisher('/tk_err', TwistStamped, queue_size=1)
    
    angular_pid = PID(-9, 0.01, 0, windup_guard= 1)
    linear_pid = PID(-20, 0.01, 0, windup_guard=0.5)

    angular_kf = KalmanFilter(A=1, B=1, C=0.1, R=0.1, Q=0.1)
    linear_kf = KalmanFilter(A=1, B=1, C=0.1, R=0.1, Q=0.1)
    rospy.spin()


