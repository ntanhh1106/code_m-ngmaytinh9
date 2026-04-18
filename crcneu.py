import streamlit as st
import random
import pandas as pd
import time

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Mô phỏng CRC-4 NEU",
    page_icon="🛡️",
    layout="wide"
)

# --- LOGIC THUẬT TOÁN ---
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

# --- GIAO DIỆN THANH BÊN (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Cấu hình hệ thống")
    data = st.text_input("Nhập dữ liệu nhị phân (4-16 bit):", value="1011001")
    
    # Kiểm tra nhập liệu ngay lập tức
    is_valid_input = True
    if not all(bit in '01' for bit in data):
        st.error("⚠️ Chỉ được nhập bit '0' hoặc '1'")
        is_valid_input = False
    elif not (4 <= len(data) <= 16):
        st.warning("⚠️ Độ dài phải từ 4-16 bit")
        is_valid_input = False
        
    generator = "10011"
    st.info(f"Đa thức tạo CRC-4: **{generator}**")
    
    error_choice = st.selectbox(
        "Giả lập loại lỗi đường truyền:",
        ["Không lỗi", "Lỗi đơn bit", "Lỗi đôi bit", "Lỗi chùm Burst (4 bit)", "Lỗi lẻ (3 bit)"]
    )
    
    st.markdown("---")
    btn_run = st.button("🚀 BẮT ĐẦU TRUYỀN TIN", use_container_width=True)

# --- MÀN HÌNH CHÍNH ---
st.title("🛡️ Hệ Thống Kiểm Tra Lỗi CRC-4 Chuyên Nghiệp")
st.write("Mô phỏng quá trình đóng gói, truyền tin và kiểm tra lỗi tại NEU Server.")

if btn_run:
    if is_valid_input:
        # 1. Quá trình tại Bên Gửi
        with st.status("📡 Đang xử lý dữ liệu...", expanded=True) as status:
            st.write("Đang tính toán mã CRC...")
            appended_data = data + '0' * (len(generator) - 1)
            remainder = crc_division(appended_data, generator)
            codeword = data + remainder
            time.sleep(0.8)
            
            st.write("Đang giả lập truyền tin qua kênh nhiễu...")
            # Giả lập lỗi
            received = list(codeword)
            error_msg = "Không có lỗi"
            if error_choice == "Lỗi đơn bit":
                idx = random.randint(0, len(codeword)-1)
                received[idx] = flip_bit(received[idx])
                error_msg = f"Bị nhiễu tại vị trí {idx+1}"
            elif error_choice == "Lỗi đôi bit":
                idxs = random.sample(range(len(codeword)), 2)
                for i in idxs: received[i] = flip_bit(received[i])
                error_msg = f"Nhiễu 2 vị trí: {', '.join(map(str, [x+1 for x in idxs]))}"
            elif error_choice == "Lỗi chùm Burst (4 bit)":
                start = random.randint(0, len(codeword)-4)
                for i in range(start, start+4): received[i] = flip_bit(received[i])
                error_msg = f"Lỗi chùm từ {start+1} đến {start+4}"
            elif error_choice == "Lỗi lẻ (3 bit)":
                idxs = random.sample(range(len(codeword)), 3)
                for i in idxs: received[i] = flip_bit(received[i])
                error_msg = "Lỗi lẻ 3 bit bất kỳ"
            
            received_str = "".join(received)
            time.sleep(0.7)
            status.update(label="✅ Truyền tin hoàn tất!", state="complete", expanded=False)

        # 2. Hiển thị Metrics (Chỉ số)
        check_remainder = crc_division(received_str, generator)
        is_success = int(check_remainder, 2) == 0
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Dữ liệu gốc", f"{len(data)} bits")
        col_m2.metric("Mã CRC-4", remainder)
        col_m3.metric("Kết quả", "THÀNH CÔNG" if is_success else "LỖI", 
                      delta="Sạch" if is_success else "Bị nhiễu",
                      delta_color="normal" if is_success else "inverse")

        st.markdown("---")

        # 3. So sánh trực quan các chuỗi bit
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("📤 Bên Gửi (Sender)")
            st.code(f"Dữ liệu: {data}\nKhung tin: {codeword}", language="text")
            st.caption("Khung tin đã bao gồm Data + CRC")

        with c2:
            st.subheader("📥 Bên Nhận (Receiver)")
            # Highlight bit lỗi bằng màu đỏ
            highlighted = ""
            for i in range(len(codeword)):
                if codeword[i] != received_str[i]:
                    highlighted += f":red[{received_str[i]}]"
                else:
                    highlighted += received_str[i]
            
            st.markdown(f"**Khung tin nhận được:** {highlighted}")
            st.markdown(f"**Trạng thái nhiễu:** {error_msg}")

        # 4. Phân tích kết quả
        st.subheader("🔍 Phân tích Modulo-2")
        if is_success:
            st.balloons()
            st.success(f"Dư cuối cùng = {check_remainder} (Bằng 0). Chấp nhận khung tin!")
            st.info(f"💾 Dữ liệu trích xuất cuối cùng: **{received_str[:-4]}**")
        else:
            st.error(f"Dư cuối cùng = {check_remainder} (Khác 0). Phát hiện lỗi đường truyền!")
            st.warning("⚠️ Hành động: Đã hủy khung tin (Discard) và gửi tín hiệu NAK yêu cầu truyền lại.")
            
        # 5. Bảng dữ liệu chi tiết
        with st.expander("Xem bảng so sánh chi tiết"):
            df = pd.DataFrame({
                "Thông số": ["Chuỗi bit", "Giá trị CRC", "Trạng thái"],
                "Bên Gửi": [codeword, remainder, "Gốc"],
                "Bên Nhận": [received_str, check_remainder, "Đã qua kênh nhiễu"]
            })
            st.table(df)

    else:
        st.error("Vui lòng kiểm tra lại dữ liệu nhập ở thanh bên!")
