import streamlit as st
import pandas as pd
import time
import os
from openai import OpenAI
from streamlit_option_menu import option_menu

# --- PATHS ---
CHATBOX_PATH = r"d:\TIN HOC\A2. Năm học 2025 -2026\10002.Github\CHATBOX12052026"

def get_chatbox_file(filename):
    return os.path.join(CHATBOX_PATH, filename)

def rfile(name_file):
    try:
        with open(get_chatbox_file(name_file), "r", encoding="utf-8") as file:
            return file.read()
    except:
        return ""

# --- CONFIGURATION ---
st.set_page_config(page_title="EduSmart - Hệ thống Giáo dục Thông minh", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM CSS FOR PREMIUM LOOK ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background-color: #f8f9fa;
    }

    /* Role Selection Cards */
    .role-container {
        display: flex;
        justify-content: center;
        gap: 1rem;
        padding-top: 1rem;
    }

    .role-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        width: 280px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid transparent;
    }

    .role-card:hover {
        transform: translateY(-5px);
        border-color: #007bff;
        box-shadow: 0 15px 30px rgba(0,123,255,0.1);
    }

    .role-icon {
        font-size: 2.5rem;
        color: #007bff;
        margin-bottom: 0.8rem;
    }

    .role-title {
        font-weight: 700;
        font-size: 1.2rem;
        color: #333;
        margin-bottom: 0.5rem;
    }

    .role-desc {
        color: #666;
        font-size: 0.9rem;
    }

    /* Gradient Text */
    .gradient-text {
        background: linear-gradient(90deg, #007bff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Login Form */
    .login-box {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        max-width: 450px;
        margin: auto;
        margin-top: 5rem;
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #ffffff;
    }

    /* Chatbox */
    .chat-container {
        max-width: 800px;
        margin: auto;
        background: white;
        border-radius: 15px;
        padding: 20px;
        height: 60vh;
        overflow-y: auto;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'contact_step' not in st.session_state:
    st.session_state.contact_step = None
if 'temp_contact' not in st.session_state:
    st.session_state.temp_contact = {}

# --- FUNCTIONS ---
def login_teacher(username, password):
    try:
        df = pd.read_excel('taikhoangv.xlsx')
        user = df[(df['username'] == username) & (df['password'].astype(str) == password)]
        if not user.empty:
            return True, user.iloc[0]['fullname']
        else:
            return False, ""
    except Exception as e:
        st.error(f"Lỗi đọc file Excel: {e}")
        return False, ""

def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_name = ""
    st.rerun()

# --- APP LOGIC ---

# 1. TRANG CHỦ (CHỌN VAI TRÒ)
if st.session_state.role is None:
    # Hiển thị Logo trường (nhỏ gọn hơn)
    col_l1, col_l2, col_l3 = st.columns([4.5, 1, 4.5])
    with col_l2:
        try:
            st.image("logotruong.jpg", use_container_width=True)
        except:
            pass
            
    st.markdown("<h4 style='text-align: center; color: #007bff; margin-top: 0rem; font-weight: 600;'>Trường Tiểu học An Lạc 2</h4>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-top: -0.5rem;'>Chào mừng đến với <span class='gradient-text'>EduSmart</span></h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 0.9rem; margin-top: -1rem;'>Vui lòng chọn vai trò để tiếp tục</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='role-container'>
            <div class='role-card' id='student-card'>
                <div class='role-icon'>🎓</div>
                <div class='role-title'>Học Sinh</div>
                <div class='role-desc'>Trò chuyện với AI, ôn bài, hỏi đáp thông minh</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Truy cập Học sinh", use_container_width=True, type="primary"):
            st.session_state.role = "Học sinh"
            st.rerun()

    with col2:
        st.markdown("""
        <div class='role-container'>
            <div class='role-card' id='teacher-card'>
                <div class='role-icon'>👨‍🏫</div>
                <div class='role-title'>Giáo Viên</div>
                <div class='role-desc'>Quản lý lớp học, theo dõi điểm số, bài giảng</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Truy cập Giáo viên", use_container_width=True):
            st.session_state.role = "Giáo viên"
            st.rerun()

    # Footer (gần hơn)
    st.markdown("<p style='text-align: center; color: #888; font-size: 0.75rem; font-style: italic; margin-top: 1rem;'>Design by Thầy Hải Tin học</p>", unsafe_allow_html=True)

# 2. GIAO DIỆN GIÁO VIÊN
elif st.session_state.role == "Giáo viên":
    if not st.session_state.logged_in:
        # Nút quay lại trang chủ
        if st.button("🏠 Quay lại Trang chủ", key="back_home_teacher"):
            st.session_state.role = None
            st.rerun()
            
        # Trang đăng nhập
        with st.container():
            st.markdown("<div class='login-box'>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center;'>Đăng Nhập Giáo Viên</h2>", unsafe_allow_html=True)
            
            user_input = st.text_input("Tên đăng nhập")
            pass_input = st.text_input("Mật khẩu", type="password")
            
            if st.button("Đăng nhập", use_container_width=True, type="primary"):
                success, name = login_teacher(user_input, pass_input)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_name = name
                    st.session_state.user_id = user_input # Lưu lại username để check admin
                    st.success(f"Chào mừng thầy/cô {name}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Sai tên đăng nhập hoặc mật khẩu!")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Dashboard Giáo viên
        with st.sidebar:
            st.markdown(f"### 👨‍🏫 {st.session_state.user_name}")
            st.markdown("---")
            options = ["Nộp kế hoạch bài dạy", "Tập huấn"]
            icons = ["file-earmark-arrow-up", "mortarboard"]
            
            # Chỉ admin mới thấy mục "Câu hỏi học sinh"
            if st.session_state.get('user_id') == 'admin':
                options.append("Câu hỏi học sinh")
                icons.append("chat-dots")
                
            options.append("Đăng xuất")
            icons.append("box-arrow-right")
            
            selected = option_menu(
                menu_title="Menu Giáo Viên",
                options=options,
                icons=icons,
                menu_icon="cast",
                default_index=0,
            )

        if selected == "Nộp kế hoạch bài dạy":
            st.title("📂 Nộp kế hoạch bài dạy")
            st.markdown(f"""
                <div style="text-align: center; margin-top: 50px; background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05);">
                    <div style="font-size: 80px; color: #007bff; margin-bottom: 20px;">📤</div>
                    <h2 style="color: #333;">Hệ thống nộp kế hoạch bài dạy</h2>
                    <p style="color: #666; font-size: 1.1rem; margin-bottom: 30px;">
                        Thầy/Cô vui lòng nhấn vào nút dưới đây để chuyển sang trang quản lý và nộp bài dạy của nhà trường.
                    </p>
                    <a href="https://hsdttruong.qlgd.edu.vn/Login.aspx?returnUrl=~/default.aspx" target="_blank" 
                       style="text-decoration: none; background: linear-gradient(90deg, #007bff, #00d4ff); color: white; padding: 15px 35px; border-radius: 12px; font-weight: bold; font-size: 1.2rem; box-shadow: 0 8px 20px rgba(0,123,255,0.2); display: inline-block;">
                        🚀 Truy cập Hệ thống
                    </a>
                </div>
            """, unsafe_allow_html=True)

        elif selected == "Tập huấn":
            st.title("🎓 Chương trình Tập huấn")
            st.markdown(f"""
                <div style="text-align: center; margin-top: 50px; background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05);">
                    <div style="font-size: 80px; color: #6f42c1; margin-bottom: 20px;">📖</div>
                    <h2 style="color: #333;">Hệ thống tập huấn CSDL</h2>
                    <p style="color: #666; font-size: 1.1rem; margin-bottom: 30px;">
                        Tham gia các khóa bồi dưỡng, tập huấn chuyên môn nghiệp vụ trên hệ thống của Bộ Giáo dục.
                    </p>
                    <a href="https://taphuan.csdl.edu.vn/dashboard" target="_blank" 
                       style="text-decoration: none; background: linear-gradient(90deg, #6f42c1, #a927f9); color: white; padding: 15px 35px; border-radius: 12px; font-weight: bold; font-size: 1.2rem; box-shadow: 0 8px 20px rgba(111,66,193,0.2); display: inline-block;">
                        🌟 Vào Tập huấn
                    </a>
                </div>
            """, unsafe_allow_html=True)
            
        elif selected == "Câu hỏi học sinh":
            st.title("💬 Câu hỏi từ học sinh")
            try:
                if os.path.exists("cau_hoi_hoc_sinh.xlsx"):
                    df_q = pd.read_excel("cau_hoi_hoc_sinh.xlsx")
                    st.dataframe(df_q, use_container_width=True)
                    
                    if st.button("Xóa tất cả câu hỏi", type="secondary"):
                        os.remove("cau_hoi_hoc_sinh.xlsx")
                        st.success("Đã xóa dữ liệu câu hỏi.")
                        st.rerun()
                else:
                    st.info("Hiện chưa có câu hỏi nào từ học sinh.")
            except Exception as e:
                st.error(f"Lỗi đọc dữ liệu: {e}")
                
        elif selected == "Đăng xuất":
            logout()

# 3. GIAO DIỆN HỌC SINH (KẾ THỪA TỪ CHATBOX12052026)
elif st.session_state.role == "Học sinh":
    # Nút quay lại
    if st.button("← Quay lại Trang chủ", key="back_from_student"):
        st.session_state.role = None
        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- LOGIC TỪ CHATBOX12052026 ---
    
    # Hiển thị tiêu đề từ file 00.xinchao.txt
    title_content = rfile("00.xinchao.txt")
    st.markdown(
        f"""<h1 style="text-align: center; font-size: 28px;" class="gradient-text">{title_content}</h1>""",
        unsafe_allow_html=True
    )

    # Lấy OpenAI API key
    openai_api_key = st.secrets.get("OPENAI_API_KEY")
    if not openai_api_key:
        st.error("⚠️ Thiếu OpenAI API Key! Vui lòng kiểm tra file secrets.toml.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)

    # Khởi tạo tin nhắn
    INITIAL_SYSTEM_MESSAGE = {"role": "system", "content": rfile("01.system_trainning.txt")}
    INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": rfile("02.assistant.txt")}

    if "messages_student" not in st.session_state:
        st.session_state.messages_student = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

    # Custom CSS cho Chatbox (giống phong cách cũ nhưng tích hợp)
    st.markdown("""
        <style>
            .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
            .assistant-box { background-color: #f0f7ff; padding: 15px; border-radius: 15px; border-left: 5px solid #007bff; margin: 10px 0; }
            .user-box { background-color: #ffffff; padding: 15px; border-radius: 15px; border-right: 5px solid #00d4ff; margin: 10px 0; text-align: right; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        </style>
    """, unsafe_allow_html=True)

    # Hiển thị lịch sử
    for message in st.session_state.messages_student:
        if message["role"] == "system": continue
        
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Ô nhập liệu
    if prompt := st.chat_input("Bạn nhập nội dung cần trao đổi ở đây nhé?"):
        st.session_state.messages_student.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Kiểm tra chế độ liên lạc giáo viên (theo từng bước)
        if st.session_state.contact_step == "awaiting_name":
            st.session_state.temp_contact['name'] = prompt
            msg = f"Chào {prompt}! Tiếp theo, em học lớp nào nhỉ?"
            with st.chat_message("assistant"):
                st.markdown(msg)
            st.session_state.messages_student.append({"role": "assistant", "content": msg})
            st.session_state.contact_step = "awaiting_class"
            
        elif st.session_state.contact_step == "awaiting_class":
            st.session_state.temp_contact['class'] = prompt
            msg = "Cảm ơn em. Bây giờ em hãy nhập nội dung câu hỏi hoặc điều em muốn nhắn cho thầy nhé!"
            with st.chat_message("assistant"):
                st.markdown(msg)
            st.session_state.messages_student.append({"role": "assistant", "content": msg})
            st.session_state.contact_step = "awaiting_question"
            
        elif st.session_state.contact_step == "awaiting_question":
            st.session_state.temp_contact['question'] = prompt
            with st.chat_message("assistant"):
                with st.spinner("Đang lưu thông tin..."):
                    # Lưu vào Excel
                    new_data = {
                        'Thời gian': [time.strftime("%Y-%m-%d %H:%M:%S")],
                        'Họ tên': [st.session_state.temp_contact['name']],
                        'Lớp': [st.session_state.temp_contact['class']],
                        'Nội dung': [prompt]
                    }
                    df_new = pd.DataFrame(new_data)
                    
                    if os.path.exists("cau_hoi_hoc_sinh.xlsx"):
                        df_old = pd.read_excel("cau_hoi_hoc_sinh.xlsx")
                        df_final = pd.concat([df_old, df_new], ignore_index=True)
                    else:
                        df_final = df_new
                    
                    df_final.to_excel("cau_hoi_hoc_sinh.xlsx", index=False)
                    
                    time.sleep(1)
                    st.success(f"✅ Đã lưu câu hỏi của em thành công!")
                    msg = "Thầy đã nhận được thông tin của em. Thầy sẽ xem và trả lời em sớm nhất có thể nhé!"
                    st.markdown(msg)
                    st.session_state.messages_student.append({"role": "assistant", "content": msg})
            
            # Reset state
            st.session_state.contact_step = None
            st.session_state.temp_contact = {}
            
        elif any(keyword in prompt.lower() for keyword in ["liên lạc", "gửi mail", "nhắn cho thầy", "gặp giáo viên"]):
            with st.chat_message("assistant"):
                msg = "Chào em! Để thầy có thể hỗ trợ tốt nhất, em vui lòng cho thầy biết **Họ và tên** của em là gì?"
                st.markdown(msg)
                st.session_state.messages_student.append({"role": "assistant", "content": msg})
            st.session_state.contact_step = "awaiting_name"
            
        else:
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                
                try:
                    model_name = rfile("module_chatgpt.txt").strip() or "gpt-3.5-turbo"
                    stream = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages_student],
                        stream=True,
                    )
                    
                    for chunk in stream:
                        if chunk.choices:
                            full_response += chunk.choices[0].delta.content or ""
                            response_placeholder.markdown(full_response + "▌")
                    
                    response_placeholder.markdown(full_response)
                    st.session_state.messages_student.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"❌ Lỗi: {e}")

