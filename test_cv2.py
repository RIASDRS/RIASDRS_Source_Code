import cv2
import tensorflow as tf

# 加载预训练的物体识别模型
model = tf.keras.applications.MobileNetV2(weights='imagenet')

# 打开摄像头
cap = cv2.VideoCapture(0)

while True:
 # 读取摄像头图像
 ret, frame = cap.read()

 # 将图像转换为模型所需的输入格式
 #img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
 img = frame
 img = tf.image.resize(img, (224, 224))
 img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
 img = tf.expand_dims(img, axis=0)

 # 使用模型进行物体识别
 predictions = model.predict(img)
 predicted_label = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=1)[0][0][1]

 # 在图像上打印识别出的物品名称
 cv2.putText(frame, predicted_label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
 cv2.imshow('Object Detection', frame)

 # 按下'q'键退出程序
 if cv2.waitKey(1) & 0xFF == ord('q'):
     break

# 释放摄像头资源
cap.release()
cv2.destroyAllWindows()
