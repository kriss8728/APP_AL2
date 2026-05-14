// App.js - Xử lý logic cho giao diện EduSmart

// --- Chuyển đổi màn hình ---
function goToStudent() {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById('screen-student').classList.add('active');
    // Thêm tin nhắn chào mừng nếu chưa có
    const chatBox = document.getElementById('studentMessages');
    if (chatBox.children.length === 0) {
        addMessage('assistant', 'Chào em! Anh là EduBot AI. Anh có thể giúp gì cho em hôm nay? Em có thể hỏi bài tập hoặc liên lạc với thầy Hải nhé! 😊');
    }
}

function goToLogin() {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById('screen-login').classList.add('active');
}

function goBack(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
}

// --- Logic Chat Học Sinh ---
let contactStep = null;
let tempContact = {};

function sendStudentMsg() {
    const input = document.getElementById('studentInput');
    const msg = input.value.trim();
    if (!msg) return;

    // Hiển thị tin nhắn người dùng
    addMessage('user', msg);
    input.value = '';

    // Xử lý logic
    processStudentLogic(msg);
}

function sendQuick(text) {
    addMessage('user', text);
    processStudentLogic(text);
}

function processStudentLogic(msg) {
    const chatBox = document.getElementById('studentMessages');
    
    // --- Xử lý liên lạc theo từng bước ---
    if (contactStep === 'awaiting_name') {
        tempContact.name = msg;
        showTypingIndicator();
        setTimeout(() => {
            removeTypingIndicator();
            addMessage('assistant', `Chào ${msg}! Tiếp theo, em học lớp nào nhỉ?`);
            contactStep = 'awaiting_class';
        }, 800);
        return;
    }

    if (contactStep === 'awaiting_class') {
        tempContact.class = msg;
        showTypingIndicator();
        setTimeout(() => {
            removeTypingIndicator();
            addMessage('assistant', 'Cảm ơn em. Bây giờ em hãy nhập nội dung câu hỏi hoặc điều em muốn nhắn cho thầy nhé!');
            contactStep = 'awaiting_question';
        }, 800);
        return;
    }

    if (contactStep === 'awaiting_question') {
        tempContact.question = msg;
        showTypingIndicator();
        setTimeout(() => {
            removeTypingIndicator();
            addMessage('assistant', `✅ Đã lưu câu hỏi của em thành công! Thầy đã nhận được thông tin (Họ tên: ${tempContact.name}, Lớp: ${tempContact.class}). Thầy sẽ sớm phản hồi cho em nhé!`);
            contactStep = null;
            tempContact = {};
        }, 1500);
        return;
    }

    // Kiểm tra câu lệnh liên lạc ban đầu
    const lowerMsg = msg.toLowerCase();
    if (lowerMsg.includes('liên lạc') || lowerMsg.includes('gửi mail') || lowerMsg.includes('nhắn cho thầy') || lowerMsg.includes('gặp giáo viên')) {
        showTypingIndicator();
        setTimeout(() => {
            removeTypingIndicator();
            addMessage('assistant', 'Chào em! Để thầy có thể hỗ trợ tốt nhất, em vui lòng cho thầy biết **Họ và tên** của em là gì?');
            contactStep = 'awaiting_name';
        }, 800);
        return;
    }

    // Logic AI (Giả lập hoặc gọi API)
    showTypingIndicator();
    setTimeout(() => {
        removeTypingIndicator();
        addMessage('assistant', 'EduBot đang suy nghĩ câu trả lời cho em... (Tính năng AI đang được kết nối)');
    }, 1000);
}

function addMessage(role, text) {
    const chatBox = document.getElementById('studentMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}-message`;
    msgDiv.innerHTML = `<div class="message-content">${text}</div>`;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator() {
    const chatBox = document.getElementById('studentMessages');
    const typing = document.createElement('div');
    typing.id = 'typing-indicator';
    typing.className = 'message assistant-message';
    typing.innerHTML = '<div class="message-content"><i class="fas fa-ellipsis-h fa-beat"></i> EduBot đang soạn tin...</div>';
    chatBox.appendChild(typing);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTypingIndicator() {
    const typing = document.getElementById('typing-indicator');
    if (typing) typing.remove();
}

// --- Theme Toggle ---
function toggleTheme() {
    const html = document.documentElement;
    const theme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', theme);
    const icon = document.querySelector('.theme-toggle i');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// --- Cài đặt khác ---
function toggleEmojiPicker() {
    const picker = document.getElementById('emojiPicker');
    picker.style.display = picker.style.display === 'grid' ? 'none' : 'grid';
}

function addEmoji(emoji) {
    const input = document.getElementById('studentInput');
    input.value += emoji;
    toggleEmojiPicker();
}

// Khởi tạo các sự kiện khác nếu cần
