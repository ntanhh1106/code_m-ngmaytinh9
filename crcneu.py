import streamlit as st
import random
import pandas as pd

# --- PHẦN LOGIC (GIỮ NGUYÊN TỪ CODE CỦA BẠN) ---
def xor(a, b):
    result = []
    for i in range(1, len(b)):
        result.append('0' if a[i] == b[i] else '1')
    return "".join(result)

def crc_division(dividend, divisor):
    pick = len(divisor)
    temp = dividend[0:pick]
    while pick < len(dividend):
        if temp[0] == '1':
            temp = xor(divisor, temp) + dividend[pick]
        else:
            temp = xor('0' * len(divisor), temp) + dividend[pick]
        pick += 1
    if temp[0] == '1':
        temp = xor(divisor, temp)
    else:
        temp = xor('0' * len(divisor), temp)
    return temp

def flip_bit(bit):
    return '1' if bit == '0' else '0'

# --- GIAO DIỆN NGƯỜI DÙNG (STREAMLIT) ---
st.set_page_config(page_title="Mô phỏng CRC-4 NEU", layout="wide")

st.title("🛡️ Mô phỏng Truyền tin An toàn - Thuật toán CRC-4")
st.markdown("---")

# Cột bên trái: Nhập liệu | Cột bên phải: Kết quả
col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Cấu hình bên Gửi")
    data = st.text_input("Nhập dữ liệu nhị phân (4-16 bit):", value="1011001")
    generator = "10011"
    st.info(f"Đa thức tạo (Generator): **{generator}**")
    
    error_choice = st.selectbox(
        "Chọn loại lỗi giả lập:",
        ["Không lỗi", "Lỗi đơn bit", "Lỗi đôi bit", "Lỗi chùm Burst (4 bit)", "Lỗi lẻ (3 bit)"]
    )

if st.button("BẮT ĐẦU TRUYỀN TIN"):
    with col2:
        # --- BÊN GỬI ---
        appended_data = data + '0' * (len(generator) - 1)
        remainder = crc_division(appended_data, generator)
        codeword = data + remainder
        
        st.subheader("📡 Kết quả tại bên Gửi")
        st.code(f"Dữ liệu gốc: {data}\nMã CRC tạo ra: {remainder}\nKhung tin gửi đi: {codeword}")

        # --- GIẢ LẬP LỖI ---
        received = list(codeword)
        msg = "Dữ liệu an toàn"
        
        if error_choice == "Lỗi đơn bit":
            idx = random.randint(0, len(codeword)-1)
            received[idx] = flip_bit(received[idx])
            msg = f"Lỗi tại vị trí {idx+1}"
        elif error_choice == "Lỗi đôi bit":
            idxs = random.sample(range(len(codeword)), 2)
            for i in idxs: received[i] = flip_bit(received[i])
            msg = f"Lỗi tại vị trí {idxs}"
        elif error_choice == "Lỗi chùm Burst (4 bit)":
            start = random.randint(0, len(codeword)-4)
            for i in range(start, start+4): received[i] = flip_bit(received[i])
            msg = f"Lỗi chùm từ {start+1} đến {start+4}"
        elif error_choice == "Lỗi lẻ (3 bit)":
            idxs = random.sample(range(len(codeword)), 3)
            for i in idxs: received[i] = flip_bit(received[i])
            msg = f"Lỗi 3 bit ngẫu nhiên"

        received_str = "".join(received)
        
        st.subheader("⚠️ Trạng thái đường truyền")
        if error_choice == "Không lỗi":
            st.success(f"✅ {msg}")
        else:
            st.warning(f"⚡ Đã xảy ra: {msg}")
        st.code(f"Gói tin nhận được: {received_str}")

        # --- BÊN NHẬN ---
        st.subheader("📥 Kiểm tra tại bên Nhận")
        check_remainder = crc_division(received_str, generator)
        is_valid = int(check_remainder, 2) == 0
        
        if is_valid:
            st.balloons()
            st.success(f"KẾT QUẢ: HỢP LỆ (Dư = {check_remainder})")
            st.info(f"Dữ liệu trích xuất: **{received_str[:-4]}**")
        else:
            st.error(f"KẾT QUẢ: PHÁT HIỆN LỖI (Dư = {check_remainder})")
            st.error("Hành động: Hủy khung tin & Yêu cầu gửi lại (ARQ)")