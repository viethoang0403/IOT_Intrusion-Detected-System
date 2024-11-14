import cv2
import numpy as np
from PIL import Image
import os


class FaceTrainer:
    def __init__(self, dataset_path="datasets", trainer_file="Trainer.yml"):
        # Đường dẫn đến thư mục chứa dữ liệu khuôn mặt và file huấn luyện
        self.dataset_path = dataset_path
        self.trainer_file = trainer_file
        # Khởi tạo mô hình nhận diện khuôn mặt
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

    def get_image_and_id(self):
        # Lấy tất cả các đường dẫn của các file ảnh trong dataset
        image_paths = [os.path.join(self.dataset_path, f) for f in os.listdir(self.dataset_path)]
        faces = []
        ids = []
        names = []

        for image_path in image_paths:
            # Mở ảnh và chuyển sang ảnh xám
            face_image = Image.open(image_path).convert('L')
            face_np = np.array(face_image)

            # Lấy ID của ảnh từ tên file (dạng User.ID.x.jpg)
            id_ = int(os.path.split(image_path)[-1].split(".")[1])
            name_ = os.path.split(image_path)[-1].split(".")[0]

            faces.append(face_np)
            ids.append(id_)
            if name_ not in names:
                names.append(name_)

            # Hiển thị quá trình huấn luyện (từng khuôn mặt)
            cv2.imshow("Training", face_np)
            cv2.waitKey(1)

        return names, ids, faces

    def train_model(self):
        # Lấy dữ liệu khuôn mặt và ID từ các file ảnh
        names, ids, faces = self.get_image_and_id()

        # Huấn luyện mô hình với dữ liệu khuôn mặt và ID
        print("Training model with collected face data...")
        self.recognizer.train(faces, np.array(ids))

        # Lưu mô hình đã huấn luyện vào file trainer_file
        self.recognizer.write(self.trainer_file)
        print(f"Training completed. Model saved to {self.trainer_file}")
        print(f"User: " + " ".join(names))

        # Đóng tất cả các cửa sổ hiển thị
        cv2.destroyAllWindows()

        return names


# Example usage:
# Khởi tạo đối tượng FaceTrainer và huấn luyện mô hình nhận diện khuôn mặt
# trainer = FaceTrainer(dataset_path="datasets", trainer_file="Trainer.yml")
# trainer.train_model()
