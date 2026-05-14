import pandas as pd

# Tạo dữ liệu mẫu cho giáo viên
data = {
    'username': ['admin', 'gv01', 'gv02'],
    'password': ['123456', 'pass01', 'pass02'],
    'fullname': ['Quản trị viên', 'Nguyễn Văn A', 'Trần Thị B']
}

df = pd.DataFrame(data)
df.to_excel('taikhoangv.xlsx', index=False)
print("Đã tạo file taikhoangv.xlsx thành công!")
