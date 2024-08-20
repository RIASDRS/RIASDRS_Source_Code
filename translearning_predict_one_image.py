import matplotlib.pyplot as plt
import numpy as np
import os
import tensorflow as tf

def open_one_image(path, h, w):
  
  img = tf.keras.utils.load_img(path, target_size=(h, w))
  img_array = tf.keras.utils.img_to_array(img)
  #print(img_array)
  img_array = tf.expand_dims(img_array, 0) # Create a batch

  
  return img_array


def do_predict(img_array):
  predictions = model.predict(img_array)
  print(predictions)
  score = tf.nn.softmax(predictions[0])
  print(
    "This image most likely belongs to {} with a {:.2f} percent confidence."
    .format(class_names[np.argmax(score)], 100 * np.max(score))
  )
  predictions = tf.argmax(predictions, axis=1)
  print('Predictions:\n', predictions.numpy())

#获取类名
PATH = 'dataset'


train_dir = os.path.join(PATH, 'train')
validation_dir = os.path.join(PATH, 'validation')

BATCH_SIZE = 32
IMG_SIZE = (224, 224)
#模型h w
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








model = tf.keras.models.load_model("./model/flower.h5")

img_array = open_one_image("test0.jpg", img_height, img_width)
do_predict(img_array)
img_array = open_one_image("test1.jpg", img_height, img_width)
do_predict(img_array)
img_array = open_one_image("test2.jpg", img_height, img_width)
do_predict(img_array)
img_array = open_one_image("test3.jpg", img_height, img_width)
do_predict(img_array)
img_array = open_one_image("test4.jpg", img_height, img_width)
do_predict(img_array)
img_array = open_one_image("test5.jpg", img_height, img_width)
do_predict(img_array)





