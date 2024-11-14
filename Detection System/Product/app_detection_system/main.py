import cv2
from detection import FaceRecognition
from datacollect import FaceDatasetCollector
from training import FaceTrainer
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# Thư mục để lưu ảnh đã chụp
REGISTERED_FOLDER = 'static/registered_faces/'
DETECTED_FOLDER = 'static/warning/'
TRAINER_FILE = "Trainer.yml"
DATASET_FOLDER = "datasets"
STATIC_FOLDER = "static"

# Tạo thư mục nếu chưa tồn tại
os.makedirs(REGISTERED_FOLDER, exist_ok=True)
os.makedirs(DETECTED_FOLDER, exist_ok=True)
os.makedirs(DATASET_FOLDER, exist_ok=True)

collector = FaceDatasetCollector()
detector = None
isIntruded = False

# Biến để kiểm tra trạng thái chụp ảnh từ ESP32
current_user = ""
current_image = ""
current_user_id = 0
current_user_name = ""
user_list = []

ESP32_IP = 'http://192.168.246.237'


# Trang chủ
@app.route('/')
def index():
    return render_template('index.html')


# Đăng ký khuôn mặt
@app.route('/register', methods=['GET', 'POST'])
def register():
    global current_user, current_image, current_user_id, current_user_name
    if request.method == 'POST':
        name = request.form['name']

        # Gửi yêu cầu chụp ảnh đến ESP32
        response = requests.get(f'{ESP32_IP}/capture_photo')

        if not name:
            return render_template('register.html', error="Vui lòng nhập họ tên", image=current_image)

        current_user = "_".join(name.lower().split())

        current_img_path = REGISTERED_FOLDER + current_image
        face_detected = collector.face_detection(current_img_path)

        if face_detected:
            current_user_id += 1
            collector.collect_faces(current_user, current_user_id, current_img_path)

            message = "Khuôn mặt đã được đăng ký thành công!"
        else:
            message = "Vui lòng chụp lại, không phát hiện khuôn mặt."

        print(current_image + " " + message)

        if response.status_code == 200:
            return render_template('register.html', image=current_image, message=message)
        else:
            return render_template('register.html', error="ESP32 không phản hồi, vui lòng thử lại.",
                                   image=current_image)

    return render_template('register.html', image=current_image)


# Nhận ảnh từ ESP32
@app.route('/upload', methods=['POST'])
def upload_image():
    global current_user, current_image, current_user_name, isIntruded
    img_data = request.data
    detection_mode = request.args.get('mode', 'register')  # mặc định là 'register'

    # Tạo tên file với timestamp
    username = current_user if detection_mode == 'register' else "motion"
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{username}_{timestamp}.jpg"

    # Chọn thư mục lưu
    folder = REGISTERED_FOLDER if detection_mode == 'register' else DETECTED_FOLDER
    file_path = os.path.join(folder, filename)

    # Lưu ảnh
    with open(file_path, 'wb') as f:
        f.write(img_data)

    current_image = filename

    if detection_mode == 'register':
        current_user_name = username
        return render_template('register.html', image=current_image)
    else:
        isIntruded = checking(file_path)
        print(isIntruded)
        return jsonify({"status": "success", "path": file_path})


motion_detect_enabled = False


# Kích hoạt/tắt chế độ phát khiện chuyển động
@app.route('/toggle_motion', methods=['POST'])
def toggle_motion():
    global motion_detect_enabled
    data = request.json
    motion_detect_enabled = data.get('enabled', False)

    # Gửi yêu cầu tới ESP32 để bật/tắt phát hiện chuyển động
    if motion_detect_enabled:
        url = f"{ESP32_IP}/enable_motion"
    else:
        url = f"{ESP32_IP}/disable_motion"
    response = requests.get(url)

    if response.status_code == 200:
        return jsonify({'status': 'success', 'enabled': motion_detect_enabled})
    else:
        return jsonify({'status': 'failed', 'enabled': motion_detect_enabled, 'error': 'ESP32 không phản hồi'})


buzzer_enabled = False

@app.route('/toggle_buzzer', methods=['POST'])
def toggle_buzzer():
    global buzzer_enabled, isIntruded
    data = request.json
    buzzer_enabled = data.get('enabled', False)

    # Gửi yêu cầu tới ESP32 để bật/tắt phát hiện chuyển động
    if buzzer_enabled:
        if isIntruded:
            url = f"{ESP32_IP}/enable_buzzer"
        else:
            url = f"{ESP32_IP}/disable_buzzer"
    else:
        url = f"{ESP32_IP}/disable_buzzer"
    response = requests.get(url)

    if response.status_code == 200:
        return jsonify({'status': 'success', 'enabled': buzzer_enabled})
    else:
        return jsonify({'status': 'failed', 'enabled': buzzer_enabled, 'error': 'ESP32 không phản hồi'})


# Quay về trang chủ
@app.route('/back')
def back():
    return redirect(url_for('index'))

@app.route('/save')
def save():
    global user_list, detector
    trainer = FaceTrainer(dataset_path="datasets", trainer_file="Trainer.yml")
    user_list = trainer.train_model()
    detector = FaceRecognition(user_list)

    return redirect(url_for('index'))

@app.route('/clear_model', methods=['POST'])
def clear_model():
    # Xóa tệp Trainer.yml
    if os.path.exists(TRAINER_FILE):
        os.remove(TRAINER_FILE)

    # Xóa tất cả các tệp trong thư mục datasets
    if os.path.exists(DATASET_FOLDER):
        for filename in os.listdir(DATASET_FOLDER):
            file_path = os.path.join(DATASET_FOLDER, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Không thể xóa {file_path}. Lỗi: {e}")

    # Xóa tất cả các tệp trong thư mục static
    if os.path.exists(REGISTERED_FOLDER):
        for filename in os.listdir(REGISTERED_FOLDER):
            file_path = os.path.join(REGISTERED_FOLDER, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Không thể xóa {file_path}. Lỗi: {e}")

    if os.path.exists(DETECTED_FOLDER):
        for filename in os.listdir(DETECTED_FOLDER):
            file_path = os.path.join(DETECTED_FOLDER, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Không thể xóa {file_path}. Lỗi: {e}")

    # Trả về phản hồi sau khi xóa
    os.makedirs(REGISTERED_FOLDER, exist_ok=True)
    os.makedirs(DETECTED_FOLDER, exist_ok=True)
    os.makedirs(DATASET_FOLDER, exist_ok=True)

    return redirect(url_for('index'))

def checking(img_path):
    global detector
    if detector is not None:
        result = detector.recognize_faces(img_path)
        return result
    return False



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
