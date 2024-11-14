import cv2


class FaceDatasetCollector:
    def __init__(self, cascade_path="haarcascade_frontalface_default.xml"):
        # Khởi tạo video capture và cascade classifier cho phát hiện khuôn mặt
        # self.video = cv2.VideoCapture(0)
        # self.video = None

        self.facedetect = cv2.CascadeClassifier(cascade_path)
        self.count = 0

    def collect_faces(self, user_name, user_id, image_path, num_images=100):
        user_id = int(user_id)
        self.count = 0

        # Đọc ảnh từ tệp
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.facedetect.detectMultiScale(gray, 1.3, 7)

        # Lặp qua các khuôn mặt phát hiện được
        for i in range(num_images):
            for (x, y, w, h) in faces:
                # self.count += 1
                # Lưu ảnh xám của khuôn mặt vào folder datasets
                cv2.imwrite(f'datasets/{user_name}.{user_id}.{i}.jpg', gray[y:y + h, x:x + w])
                # Vẽ khung hình chữ nhật xung quanh khuôn mặt
                cv2.rectangle(image, (x, y), (x + w, y + h), (50, 50, 255), 2)

                # # Dừng lại nếu đã đủ số lượng ảnh yêu cầu
                # if self.count >= num_images:
                #     break

        # Hiển thị ảnh với khuôn mặt được đánh dấu
        # cv2.imshow("Detected Faces", image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        cv2.imwrite(image_path, image)

        print(f"Dataset Collection Done. Collected {self.count} images.")

    def face_detection(self, img_path):
        # Đọc ảnh và chuyển sang ảnh xám
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Phát hiện khuôn mặt
        faces = self.facedetect.detectMultiScale(gray, 1.3, 7)

        print(faces)
        # Nếu phát hiện ít nhất 1 khuôn mặt, trả về "Yes", nếu không thì trả về "No"
        if len(faces) == 1:
            return 1
        else:
            return 0



# collector = FaceDatasetCollector()
#
# collector.collect_faces(user_id=input("Enter Your ID: "), num_images=100)
