#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np
import tensorflow as tf
import os
import re


import PIL
 




h=224
w=224
'''
node_id_to_name = {}
node_id_to_name[0]=   '       藿香蓟            Ageratum conyzoides'
node_id_to_name[1]=   '       反枝苋            Amaranthus retroflexus'
node_id_to_name[2]=   '       钻形紫菀           Aster subulatus Michx'
node_id_to_name[3]=   '       水盾草            Cabomba caroliniana Gray'
node_id_to_name[4]=   '       青葙             Celosia argentea'
node_id_to_name[5]=   '       凤眼蓝            Eichhornia crassipes'
node_id_to_name[6]=   '       食蚊鱼(未识别)      Gambusia affinis(find nothing)'
node_id_to_name[7]=   '       五爪金龙           Ipomoea cairica'
node_id_to_name[8]=   '       垂序商陆           Phytolacca Americana'
node_id_to_name[9]=   '       大薸             Pistia stratiotes'
node_id_to_name[10]=  '       红腹锯鲑脂鲤         Pygocentrus nattereri'
node_id_to_name[11]=  '       红棕象甲           Rhynchophorus ferrugineus'
node_id_to_name[12]=  '       喀西茄            Solanum aculeatissimum Jacquin'
node_id_to_name[13]=  '       黄花刺茄           Solanum rostratum Dunal'
node_id_to_name[14]=  '       红火蚁            Solenopsis invicta Buren'
node_id_to_name[15]=  '       加拿大一枝黄花        Solidago Canadensis'
node_id_to_name[16]=  '       巴西龟            Trachemyss cripta elegans'
node_id_to_name[17]=  '       刺苍耳            Xanthium spinosum'
'''
node_id_to_name = {}
node_id_to_name[0]=   'Ageratum conyzoides'
node_id_to_name[1]=   'Amaranthus retroflexus'
node_id_to_name[2]=   'Aster subulatus Michx'
node_id_to_name[3]=   'Cabomba caroliniana Gray'
node_id_to_name[4]=   'Celosia argentea'
node_id_to_name[5]=   'Eichhornia crassipes'
node_id_to_name[6]=   'Gambusia affinis'
node_id_to_name[7]=   'Ipomoea cairica'
node_id_to_name[8]=   'Phytolacca Americana'
node_id_to_name[9]=   'Pistia stratiotes'
node_id_to_name[10]=  'Pygocentrus nattereri'
node_id_to_name[11]=  'Rhynchophorus ferrugineus'
node_id_to_name[12]=  'Solanum aculeatissimum Jacquin'
node_id_to_name[13]=  'Solanum rostratum Dunal'
node_id_to_name[14]=  'Solenopsis invicta Buren'
node_id_to_name[15]=  'Solidago Canadensis'
node_id_to_name[16]=  'Trachemyss cripta elegans'
node_id_to_name[17]=  'Xanthium spinosum'





class RosTensorFlow():
    def __init__(self):
       
        # In tensorflow V1, session can operate a compute graph
        self._session = tf.compat.v1.Session()
        # usa a convert between ROS and openCV
        self._cv_bridge = CvBridge()
        # Subscriber: get a image from usb_cameral
        self._sub = rospy.Subscriber('/usb_cam/image_raw', Image, self.callback, queue_size=1)
        # Publisher: send a result str to screen
        self._pub = rospy.Publisher('/riasdrs_image', Image, queue_size=1)
        
    
    def callback(self, image_msg):
        #convert image str to opencv cv_image
        cv_image = self._cv_bridge.imgmsg_to_cv2(image_msg, "bgr8")
        frame = cv_image

        #covert bgr to rgb
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

        

        #resize to the size of model
        image_data = cv2.resize(cv_image,(w,h))
        
        

        #Creates graph from saved GraphDef.
        #Identity:0 is the output
        #Input:0 is the input
        softmax_tensor = self._session.graph.get_tensor_by_name('Identity:0')
        predictions = self._session.run(softmax_tensor, {'Input:0': np.reshape(image_data,(1,w,h,3))})
        
        #
        score = tf.nn.softmax(predictions[0])
        score_max_persent = np.max(score)*100
        result = np.argmax(predictions, axis=1)
        if((score_max_persent>80) and (result[0]!=6)):   
            
            display_str=node_id_to_name[result[0]]
            score_str=str(score_max_persent)[0:2]+'%'
            frame = cv2.putText(frame, display_str, (10,50),cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 6, cv2.LINE_AA)
            frame = cv2.putText(frame,   score_str, (10,100),cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 6, cv2.LINE_AA)
        else:
            display_str='confidence is low'
            score_str=''
            frame = cv2.putText(frame, display_str, (10,50),cv2.FONT_HERSHEY_SIMPLEX, 2,(0,255,0), 6, cv2.LINE_AA)
            frame = cv2.putText(frame,   score_str, (10,100),cv2.FONT_HERSHEY_SIMPLEX, 2,(0,255,0), 6, cv2.LINE_AA)


        imgmsg = self._cv_bridge.cv2_to_imgmsg(frame,encoding="bgr8")
        self._pub.publish(imgmsg)
        #rospy.loginfo(display_str)   




    def main(self):
        rospy.spin()

if __name__ == '__main__':
    #load h5 model use for result_1
    model = tf.keras.models.load_model("/home/wheeltec/wheeltec_robot/src/lhz/RIASDR/model/flower.h5")
    
    #set model path and load pb model for result_2
    PATH_TO_MODEL = '/home/wheeltec/wheeltec_robot/src/lhz/RIASDR/model/flower_h5.pb'
    with tf.io.gfile.GFile(PATH_TO_MODEL, 'rb') as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')    
    #initialize ros node
    rospy.init_node('ros_riasdr')
    #initialize a instance
    tensor = RosTensorFlow()
    #main() run rospy.spin() to give the control to the ROS
    tensor.main()




