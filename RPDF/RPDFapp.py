import streamlit as st
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import io
import base64
import os
from openai import OpenAI

# ========================================================================================
# CẤU HÌNH TRANG
# ========================================================================================
st.set_page_config(
    page_title="Trợ lý OCR Thông minh (AI Enhanced)",
    page_icon="📄",
    layout="wide"
)

# Thêm CSS để giao diện chuyên nghiệp hơn
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        border-radius: 8px;
    }
    .stTextArea>div>div>textarea {
        font-family: 'Inter', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# ========================================================================================
# KIỂM TRA HỆ THỐNG (Tesseract & Poppler)
# ========================================================================================
# Hỗ trợ chạy local trên Windows nếu người dùng đã cài đặt Tesseract
if os.name == 'nt':
    # Thử các đường dẫn phổ biến của Tesseract trên Windows
    common_tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Users\\' + os.getlogin() + r'\AppData\Local\Tesseract-OCR\tesseract.exe'
    ]
    for path in common_tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

# ========================================================================================
# CẤU HÌNH SIDEBAR
# ========================================================================================
# Khởi tạo API Key mặc định từ secrets hoặc để trống
DEFAULT_API_KEY = st.secrets.get("OPENAI_API_KEY", "")

with st.sidebar:
    st.header("⚙️ Cấu hình AI")
    api_key = st.text_input("Nhập OpenAI API Key:", value=DEFAULT_API_KEY, type="password", help="Dùng để trích xuất văn bản bằng mô hình GPT-4o")
    
    ocr_method = st.radio(
        "Chọn phương pháp OCR:",
        ("Tiêu chuẩn (Tesseract)", "AI Nâng cao (GPT-4o)"),
        index=1,
        help="AI Nâng cao sử dụng GPT-4o cho độ chính xác vượt trội."
    )
    
    st.markdown("---")
    st.info("💡 **Mẹo:** Sử dụng AI Nâng cao cho văn bản viết tay, bảng biểu hoặc tài liệu có bố cục phức tạp.")
    
    if st.button("Xóa Cache"):
        st.cache_data.clear()
        st.success("Đã xóa bộ nhớ đệm!")

# ========================================================================================
# HÀM HỖ TRỢ (LOGIC XỬ LÝ)
# ========================================================================================

def encode_image_to_base64(image_bytes):
    """Mã hóa bytes ảnh sang chuỗi base64."""
    return base64.b64encode(image_bytes).decode('utf-8')

def get_mime_type(file_extension):
    """Trả về MIME type phù hợp cho OpenAI API."""
    mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'webp': 'image/webp'
    }
    return mime_types.get(file_extension.lower(), 'image/jpeg')

def ocr_with_ai(image_bytes, api_key, file_extension='jpg'):
    """Gửi ảnh đến OpenAI GPT-4o để trích xuất văn bản."""
    try:
        client = OpenAI(api_key=api_key)
        base64_image = encode_image_to_base64(image_bytes)
        mime_type = get_mime_type(file_extension)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Sử dụng gpt-4o-mini cho tốc độ và hiệu quả chi phí
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Hãy trích xuất toàn bộ văn bản trong ảnh này một cách chính xác nhất. Giữ nguyên định dạng và xuống dòng. Nếu có bảng biểu, hãy cố gắng giữ cấu trúc văn bản của bảng. Chỉ trả về văn bản đã trích xuất, không thêm lời dẫn hay nhận xét nào khác."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=4000,
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, f"Lỗi OpenAI: {str(e)}"

@st.cache_data(show_spinner=False)
def process_file(file_bytes, file_extension, method, api_key=None):
    """
    Hàm trung tâm xử lý file đầu vào (ảnh hoặc PDF) và trả về văn bản được trích xuất.
    """
    lang_code = "vie+eng"
    extracted_text = ""
    
    try:
        if method == "AI Nâng cao (GPT-4o)":
            if not api_key:
                return None, "Vui lòng nhập OpenAI API Key ở thanh bên để sử dụng tính năng AI."
            
            if file_extension == 'pdf':
                try:
                    images = convert_from_bytes(file_bytes)
                except Exception as e:
                    return None, f"Lỗi chuyển đổi PDF (Có thể thiếu Poppler): {e}"
                
                all_text = []
                progress_bar = st.progress(0, text="AI đang đọc file PDF...")
                for i, img in enumerate(images):
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    img_bytes = img_byte_arr.getvalue()
                    
                    text, err = ocr_with_ai(img_bytes, api_key, 'jpg')
                    if err: return None, err
                    all_text.append(text)
                    progress_bar.progress((i + 1) / len(images))
                extracted_text = "\n\n--- Hết trang ---\n\n".join(all_text)
            else:
                text, err = ocr_with_ai(file_bytes, api_key, file_extension)
                if err: return None, err
                extracted_text = text
        else:
            # Phương pháp Tesseract
            if file_extension == 'pdf':
                try:
                    images = convert_from_bytes(file_bytes)
                except Exception as e:
                    return None, f"Lỗi chuyển đổi PDF (Có thể thiếu Poppler): {e}"
                
                all_text = []
                progress_bar = st.progress(0, text="Đang xử lý file PDF bằng Tesseract...")
                for i, img in enumerate(images):
                    try:
                        text = pytesseract.image_to_string(img, lang=lang_code)
                        all_text.append(text)
                    except Exception as e:
                        return None, f"Lỗi Tesseract: {e}. Vui lòng kiểm tra cài đặt Tesseract OCR."
                    progress_bar.progress((i + 1) / len(images))
                extracted_text = "\n\n--- Hết trang ---\n\n".join(all_text)
            elif file_extension in ['png', 'jpg', 'jpeg', 'webp']:
                image = Image.open(io.BytesIO(file_bytes))
                try:
                    extracted_text = pytesseract.image_to_string(image, lang=lang_code)
                except Exception as e:
                    return None, f"Lỗi Tesseract: {e}. Vui lòng kiểm tra cài đặt Tesseract OCR."
            else:
                return None, f"Định dạng file .{file_extension} chưa được hỗ trợ cho Tesseract."
        
        return extracted_text, None
    except Exception as e:
        return None, f"Đã xảy ra lỗi không xác định: {e}"

# ========================================================================================
# GIAO DIỆN CHÍNH CỦA ỨNG DỤNG
# ========================================================================================

st.title("📄 Trợ lý OCR Thông minh (AI & Tesseract)")
st.write(f"Đang sử dụng phương pháp: **{ocr_method}**")

# Cột cho phần tải lên và hướng dẫn
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_files = st.file_uploader(
        "Tải lên file (PDF, PNG, JPG, JPEG, WEBP):",
        type=['pdf', 'png', 'jpg', 'jpeg', 'webp'],
        accept_multiple_files=True
    )

with col2:
    with st.expander("💡 Hướng dẫn & Mẹo", expanded=True):
        st.markdown(f"""
        - **{ocr_method}**: {'Phù hợp cho văn bản in rõ nét, tốc độ nhanh.' if ocr_method == 'Tiêu chuẩn (Tesseract)' else 'Phù hợp cho mọi loại văn bản, kể cả viết tay.'}
        - **Ngôn ngữ**: Hỗ trợ tốt nhất cho Tiếng Việt và Tiếng Anh.
        - **Bảng biểu**: AI có khả năng giữ cấu trúc bảng tốt hơn Tesseract.
        """)

# Xử lý nếu người dùng đã tải file lên
if uploaded_files:
    st.markdown("---")
    st.subheader(f"🔍 Kết quả xử lý ({len(uploaded_files)} file)")

    for uploaded_file in uploaded_files:
        # Tạo key duy nhất cho mỗi file để tránh xung đột UI
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        
        with st.expander(f"📄 {uploaded_file.name}", expanded=True):
            with st.spinner(f"Đang phân tích '{uploaded_file.name}'..."):
                file_bytes = uploaded_file.getvalue()
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                # Gọi hàm xử lý
                text, error = process_file(file_bytes, file_extension, ocr_method, api_key)

            if error:
                st.error(error)
                if "Tesseract" in error and os.name == 'nt':
                    st.warning("Gợi ý: Nếu chạy trên Windows, hãy đảm bảo bạn đã cài đặt Tesseract OCR và thêm nó vào PATH hoặc cấu hình đường dẫn trong code.")
            else:
                if text.strip():
                    st.text_area("Văn bản trích xuất được:", text, height=350, key=f"text_{file_key}")
                    st.download_button(
                        label="📥 Tải file .txt",
                        data=text.encode('utf-8'),
                        file_name=f"ocr_{uploaded_file.name.split('.')[0]}.txt",
                        mime="text/plain",
                        key=f"download_{file_key}"
                    )
                else:
                    st.warning("Không tìm thấy văn bản nào trong file này.")

