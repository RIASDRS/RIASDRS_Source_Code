import tensorflow as tf
import numpy as np
import cv2


def recognize(jpg_path, pb_file_path):
    with tf.Graph().as_default():
        output_graph_def = tf.compat.v1.GraphDef()
 
        with open(pb_file_path, "rb") as f:
            output_graph_def.ParseFromString(f.read())
            tensors = tf.import_graph_def(output_graph_def, name="")

 

        with tf.compat.v1.Session() as sess:
            init = tf.compat.v1.global_variables_initializer()
            sess.run(init)
 
            op = sess.graph.get_operations()
 
            ## 打印图中有的操作
            #for i,m in enumerate(op):
            #    print('op{}:'.format(i),m.values())
 
            input_x = sess.graph.get_tensor_by_name("Input:0")  
            out_softmax = sess.graph.get_tensor_by_name("Identity:0")  
 

            img = cv2.imread(jpg_path, 1)    
            img=cv2.resize(img,(h,w))

 
            img_out_softmax = sess.run(out_softmax,
                                       feed_dict={input_x: np.reshape(img,(1,h,w,3))})  


            #print("img_out_softmax:", img_out_softmax)
            #for i,prob in enumerate(img_out_softmax[0]):
            #    print('class {} prob:{}'.format(i,prob))
            prediction_labels = np.argmax(img_out_softmax, axis=1)
            print("find :",prediction_labels)
            #print("prob of label:",img_out_softmax[0,prediction_labels])
 

h=224
w=224 
class_names=["0","1""2""3","4","5","6","7""8","9""10""11""12""13""14","15","16","17"]
pb_path = './model/flower_h5.pb'
img = 'test0.jpg'
recognize(img, pb_path)
img = 'test1.jpg'
recognize(img, pb_path)
img = 'test2.jpg'
recognize(img, pb_path)
img = 'test3.jpg'
recognize(img, pb_path)
img = 'test4.jpg'
recognize(img, pb_path)
img = 'test5.jpg'
recognize(img, pb_path)


