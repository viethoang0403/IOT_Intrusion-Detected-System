import os

# Đường dẫn đến thư mục chứa các file ảnh
image_folder = "datasets"

# Định danh cho 'hien' và 'hoang'
user_ids = {'hien': 0, 'hoang': 1}

# Duyệt qua các file trong thư mục
count_dict = {'hien': 0, 'hoang': 0}  # Đếm số file cho mỗi user
for filename in sorted(os.listdir(image_folder)):
    # Tách phần tên và đuôi file
    name, ext = os.path.splitext(filename)

    # Kiểm tra file có chứa tên của 'hien' hay 'hoang'
    for user in user_ids:
        if user in name:
            # Đổi tên file theo định dạng User.<id>.<count>.jpg
            new_name = f"User.{user_ids[user]}.{count_dict[user]}{ext}"
            old_file = os.path.join(image_folder, filename)
            new_file = os.path.join(image_folder, new_name)

            # Đổi tên file
            os.rename(old_file, new_file)

            # Tăng giá trị count cho user đó
            count_dict[user] += 1

# Thông báo hoàn thành
print("Đổi tên file thành công!")
