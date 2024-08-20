import matplotlib.pyplot as plt
import numpy as np
import os
import tensorflow as tf
import cv2
import sys

def open_one_image(path, h, w):
  img = tf.keras.utils.load_img(path, target_size=(h, w))
  img_array = tf.keras.utils.img_to_array(img)
  img_array = tf.expand_dims(img_array, 0) # Create a batch
  return img_array


def do_predict(img_array):
  predictions = model.predict(img_array)
  #print(predictions)
  score = tf.nn.softmax(predictions[0])
  if(np.max(score)>0.8):
    print(
      "{} with a {:.2f} percent confidence."
      .format(class_names[np.argmax(score)], 100 * np.max(score))
    )
    #predictions = tf.argmax(predictions, axis=1)
    #print('Predictions:\n', predictions.numpy())
  else:
    pass


PATH = 'dataset'


train_dir = os.path.join(PATH, 'train')
validation_dir = os.path.join(PATH, 'validation')

BATCH_SIZE = 32
IMG_SIZE = (224, 224)
img_height = IMG_SIZE[0]
img_width = IMG_SIZE[1]
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




#0 or 1
print("摄像头开启中")
cap = cv2.VideoCapture(0)

print("摄像头开启成功")










# 加载预训练的物体识别模型
model = tf.keras.models.load_model("./model/flower.h5")





if not cap.isOpened():
    print("can not open camera")
    exit()
while True:
    ret, frame = cap.read()
    if not ret:
        print("需要重新安装摄像头")
        break
    cv2.imshow('logi cam', frame)
    cv2.imwrite('test.jpg',frame)
    img_array = open_one_image("test.jpg", img_height, img_width)
    do_predict(img_array)
    
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()










  













