import cv2
import datetime
import os
import threading
import asyncio
from telegram_utils import send_telegram


class FaceRecognition:
    def __init__(self, name_list, model_path="Trainer.yml",
                 cascade_path="haarcascade_frontalface_default.xml"):
        # Load the face recognizer and haarcascade model
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read(model_path)
        self.facedetect = cv2.CascadeClassifier(cascade_path)
        self.name_list = name_list
        self.last_alert = datetime.datetime.now(datetime.timezone.utc)
        self.alert_telegram_each = 10

    def recognize_faces(self, image_path):
        save_directory = "test face"
        os.makedirs(save_directory, exist_ok=True)

        # Convert the image to grayscale for face detection
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Detect faces in the image
        faces = self.facedetect.detectMultiScale(gray, 1.3, 7)

        if len(faces) == 0:
            print("No faces detected.")
            return False

        # print("-----------------" + " ".join(self.name_list))
        detected_names = []
        # Loop over all detected faces
        for (x, y, w, h) in faces:
            # Predict the identity of the face
            serial, conf = self.recognizer.predict(gray[y:y + h, x:x + w])
            if conf > 50 and serial <= len(self.name_list):
                print("______________" + str(serial))
                name = self.name_list[serial - 1]
            else:
                name = "Unknown"
            print("Detected " + name)
            # Add the name to the list of detected names
            detected_names.append(name)

            # Draw a rectangle around the face and label it
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 1)
            cv2.rectangle(image, (x, y), (x + w, y + h), (50, 50, 255), 2)
            cv2.rectangle(image, (x, y - 40), (x + w, y), (50, 50, 255), -1)
            cv2.putText(image, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = os.path.join(save_directory, f"{name}_{timestamp}.jpg")

            # Lưu ảnh
            cv2.imwrite(image_filename, image)

            if name == "Unknown":
                img = self.alert(image)
                return True

        # Return the image with the drawn rectangles and the list of detected names
        return False

    def alert(self, img):
        # Vẽ thông báo "ALARM!!!!" trên ảnh
        cv2.putText(img, "ALARM!!!!", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Kiểm tra xem có nên gửi cảnh báo Telegram hay không
        if (self.last_alert is None) or (
                (datetime.datetime.now(
                    datetime.timezone.utc) - self.last_alert).total_seconds() > self.alert_telegram_each):

            self.last_alert = datetime.datetime.now(datetime.timezone.utc)

            timestamp = self.last_alert.strftime("%Y%m%d_%H%M%S")

            folder_path = "static/alert_img"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            image_filename = os.path.join(folder_path, f"alert_{timestamp}.png")

            cv2.imwrite(image_filename, cv2.resize(img, dsize=None, fx=0.5, fy=0.5))

            # Tạo một luồng mới để gửi cảnh báo qua Telegram không chặn luồng chính

            thread = threading.Thread(target=self.send_alert(image_filename))
            thread.start()

        return img

    def send_alert(self, image_filename):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_telegram(image_filename))
        loop.close()







# recognizer = FaceRecognition()
#
# # Load an image (replace 'input_image.jpg' with the path to your image)
# image = cv2.imread("datasets/User.0.0.jpg")
#
# # Call the recognize_faces method to process the image
# result = recognizer.recognize_faces(image)
#
# if result is not None:
#     processed_image, detected_names = result
#     print("Detected Names:", detected_names)
#     cv2.imshow("Processed Image", processed_image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
# else:
#     print("No faces warning.")

