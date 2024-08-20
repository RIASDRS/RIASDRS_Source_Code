import cv2
import tensorflow as tf
import numpy as np
import os

# 加载预训练的物体识别模型
#model = tf.keras.applications.MobileNetV2(weights='imagenet')
model = tf.keras.models.load_model("./model/flower.h5")

#模型h w
IMG_SIZE = (224, 224)
img_height = IMG_SIZE[0]
img_width = IMG_SIZE[1]
BATCH_SIZE = 32

#获取类名
PATH = 'dataset'
train_dir = os.path.join(PATH, 'train')
validation_dir = os.path.join(PATH, 'validation')
train_dataset = tf.keras.utils.image_dataset_from_directory(train_dir,
                                            batch_size=BATCH_SIZE,
                                            image_size=IMG_SIZE)
validation_dataset = tf.keras.utils.image_dataset_from_directory(validation_dir,
                                                                 shuffle=True,
                                                                 batch_size=BATCH_SIZE,
                                                                 image_size=IMG_SIZE)
val_batches = tf.data.experimental.cardinality(validation_dataset)
test_dataset = validation_dataset.take(val_batches // 5)
AUTOTUNE = tf.data.AUTOTUNE
test_dataset = test_dataset.prefetch(buffer_size=AUTOTUNE)
class_names = train_dataset.class_names




# 打开摄像头
cap = cv2.VideoCapture(0)

while True:
      # 读取摄像头图像
      ret, bgr = cap.read()
      rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
      cv2.imshow('cap', bgr)


      # 1将图像不转换
      img = tf.image.resize(bgr, (img_height, img_width))
      img = tf.expand_dims(img, axis=0)
      predictions = model.predict(img)
      score = tf.nn.softmax(predictions[0])
      print("1:bgr1 most likely belongs to {} with a {:.2f} percent confidence.".format(class_names[np.argmax(score)], 100 * np.max(score)))
 

      # 2将图像转换
      img = tf.image.resize(rgb, (img_height, img_width))
      img = tf.expand_dims(img, axis=0)
      predictions = model.predict(img)
      score = tf.nn.softmax(predictions[0])
      print("2:rgb1 most likely belongs to {} with a {:.2f} percent confidence.".format(class_names[np.argmax(score)], 100 * np.max(score)))


      # 3将图像不转换保存为图片
      cv2.imwrite('brg.jpg',bgr)
      img = tf.keras.utils.load_img("brg.jpg", target_size=(img_height, img_width))
      img = tf.keras.utils.img_to_array(img)
      img = tf.expand_dims(img, 0) # Create a batch
      predictions = model.predict(img)
      score = tf.nn.softmax(predictions[0])
      print("3:bgr2 most likely belongs to {} with a {:.2f} percent confidence.".format(class_names[np.argmax(score)], 100 * np.max(score)))




      # 4将图像转换保存为图片
      cv2.imwrite('rgb.jpg',rgb)
      img = tf.keras.utils.load_img("rgb.jpg", target_size=(img_height, img_width))
      img = tf.keras.utils.img_to_array(img)
      img = tf.expand_dims(img, 0) # Create a batch
      predictions = model.predict(img)
      score = tf.nn.softmax(predictions[0])
      print("4:rgb2 most likely belongs to {} with a {:.2f} percent confidence.".format(class_names[np.argmax(score)], 100 * np.max(score)))
 
      


      # 按下'q'键退出程序
      if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# 释放摄像头资源
cap.release()
cv2.destroyAllWindows()

