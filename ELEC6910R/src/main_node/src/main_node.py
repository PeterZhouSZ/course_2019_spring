#!/usr/bin/env python

import cv2
import rospy
import numpy as np

from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import String, Bool, Float32
from geometry_msgs.msg import Twist, TwistStamped

import matplotlib.pyplot as plt
import matplotlib.text as txt
# from matplotlib import text
from matplotlib.widgets import Button
from matplotlib.widgets import CheckButtons

fig, (ax1, ax2) = plt.subplots(1,2)
plt.subplots_adjust(top=0.8)
myBridge = CvBridge()

tk_x_err = []
tk_r_err = []

class MainPanel(object):
    def __init__(self):
        self.vs_pub = rospy.Publisher('/visual_servoing_flag', Bool, queue_size=1)
        self.fd_pub = rospy.Publisher('/face_detector_flag', Bool, queue_size=1)
        self.tk_pub = rospy.Publisher('/traker_selector', String, queue_size=1)
        self.im_sub = rospy.Subscriber('/img_show', Image, self.im_show_callback, queue_size=1)
        self.tk_x_sub = rospy.Subscriber('/tk_err', TwistStamped, self.tk_callback, queue_size=1)

        ax_vs = plt.axes([0.1, 0.85, 0.2, 0.1])
        ax_fd = plt.axes([0.35, 0.85, 0.2, 0.1])

        ax_tk = plt.axes([0.6, 0.85, 0.2, 0.1])
        ax_cl = plt.axes([0.85, 0.85, 0.1, 0.1])

        self.vs_check = Button(ax_vs, 'Visual Servoing')
        self.fd_check = Button(ax_fd, 'Face Detector')
        self.cl_check = Button(ax_cl, 'Clear')

        self.vs_check.on_clicked(self.vs_checked)
        self.fd_check.on_clicked(self.fd_checked)
        self.cl_check.on_clicked(self.cl_checked)
    
        self.tk_check = CheckButtons(ax_tk, ['Naive', 'PID', 'Kalman'], [False, True, False])
        self.tk_check.on_clicked(self.tk_checked)

        self.false_msgs = Bool()
        self.false_msgs.data = False
        self.true_msgs = Bool()
        self.true_msgs.data = True
        self.str_msgs = String()

    def vs_checked(self, event):
        self.vs_pub.publish(self.true_msgs)
        self.fd_pub.publish(self.false_msgs)
        print("visual servoing checked")

    def fd_checked(self, event):
        self.vs_pub.publish(self.false_msgs)
        self.fd_pub.publish(self.true_msgs)
        print("face detector checked")       

    def tk_checked(self, label):
        self.str_msgs.data = label
        self.tk_pub.publish(self.str_msgs)
        print(label, "checked")
    
    def cl_checked(self, event):
        print("clear checked")
        global tk_r_err
        global tk_x_err
        tk_x_err = []
        tk_r_err = []
        ax2.cla()
    
    def im_show_callback(self, img):
        img = myBridge.imgmsg_to_cv2(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # plt.subplot(1,2,1)
        ax1.set_title("robot view")
        ax1.imshow(img)
        plt.show(block=False)
        
    def tk_callback(self, err):
        global tk_r_err
        global tk_x_err
        err_x = err.twist.linear.x
        err_r = err.twist.linear.y
        tk_x_err.append(abs(err_x))
        tk_r_err.append(abs(err_r))
        # plt.subplot(1,2,2)
        ax2.set_title("tracking error " + err.header.frame_id)
        ax2.plot(tk_x_err, 'r')
        ax2.plot(tk_r_err, 'b')
        plt.show(block=False)


if __name__ == '__main__':
    rospy.init_node('main_node')

    myPanel = MainPanel()

    plt.show()
    
    rospy.spin()

