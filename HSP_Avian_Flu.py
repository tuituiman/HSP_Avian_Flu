import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ---------------------------------------------------------
# ตั้งค่าหน้าเพจ
# ---------------------------------------------------------
st.set_page_config(page_title="EOC สคร.1 เชียงใหม่ - ไข้หวัดนก", layout="wide")

# ลิงก์ Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1newH4TiteAxJxKnikgI4L8TA1HRfLaXGB6iFFTBvApc/edit?gid=0#gid=0"

# สร้าง Session State สำหรับเก็บข้อมูลการล็อกอินและสถานะ EOC
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = ""
if 'eoc_status' not in st.session_state:
    st.session_state.eoc_status = "Watch Mode (เฝ้าระวังปกติ)"

# ---------------------------------------------------------
# 1. หน้า Login (อ่านจากชีต Users)
# ---------------------------------------------------------
def login_page():
    st.title("🔐 เข้าสู่ระบบ EOC Command Center")
    st.markdown("สำนักงานป้องกันควบคุมโรคที่ 1 เชียงใหม่ (กรณีโรคไข้หวัดนก)")
    
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        # อ่านข้อมูลจากชีต Users
        df_users = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=0)
    except Exception as e:
        st.error("ไม่สามารถเชื่อมต่อฐานข้อมูลได้ โปรดตรวจสอบการตั้งค่า secrets.toml และสิทธิ์การแชร์ Sheet")
        st.stop()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("Sign In")
            input_user = st.text_input("Username")
            input_pwd = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("เข้าสู่ระบบ")

            if submit_btn:
                # ป้องกัน Error กรณีรหัสผ่านใน Sheet เป็นตัวเลข
                df_users['password'] = df_users['password'].astype(str)
                # กรองหา User/Password ที่ตรงกัน
                match = df_users[(df_users['username'] == input_user) & (df_users['password'] == str(input_pwd))]
                
                if not match.empty:
                    st.success("เข้าสู่ระบบสำเร็จ!")
                    st.session_state.logged_in = True
                    st.session_state.username = input_user
                    # เก็บ Role เพื่อนำไปใช้โชว์/ซ่อน Tab
                    st.session_state.role = match.iloc[0]['role'] 
                    st.rerun()
                else:
                    st.error("❌ Username หรือ Password ไม่ถูกต้อง!")

# ---------------------------------------------------------
# หน้า Dashboard หลัก (หลัง Login ผ่าน)
# ---------------------------------------------------------
def main_dashboard():
    # --- แถบ Sidebar แสดงข้อมูลตัวเอง ---
    st.sidebar.header("👤 ข้อมูลผู้ใช้งาน")
    st.sidebar.write(f"**Username:** {st.session_state.username}")
    st.sidebar.write(f"**กลุ่มภารกิจ (Role):** {st.session_state.role}")
    
    if st.sidebar.button("🚪 ออกจากระบบ (Logout)"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    st.title("🚨 EOC Action Plan: กรณีไข้หวัดนก (HSP 2568)")
    
    # ---------------------------------------------------------
    # 2. หน้าหลัก: แสดง Status ของ EOC
    # ---------------------------------------------------------
    st.header("📊 สถานะศูนย์ปฏิบัติการตอบโต้ภาวะฉุกเฉิน")
    
    # ระบบให้ IC เป็นคนเปลี่ยนสถานะได้ (ถ้า Role อื่นจะเห็นแค่สถานะอย่างเดียว เปลี่ยนไม่ได้)
    if st.session_state.role == "IC (ผู้บัญชาการ)":
        new_status = st.selectbox(
            "ปรับระดับสถานการณ์ EOC:", 
            ["Watch Mode (เฝ้าระวังปกติ)", "Alert Mode (เตรียมความพร้อม)", "Response Mode (ตอบโต้ฉุกเฉิน)", "Recovery Mode (ฟื้นฟู/หลังเกิดเหตุ)"],
            index=["Watch Mode (เฝ้าระวังปกติ)", "Alert Mode (เตรียมความพร้อม)", "Response Mode (ตอบโต้ฉุกเฉิน)", "Recovery Mode (ฟื้นฟู/หลังเกิดเหตุ)"].index(st.session_state.eoc_status)
        )
        if new_status != st.session_state.eoc_status:
            st.session_state.eoc_status = new_status
            st.rerun()
            
    # แสดงแถบสีตามสถานะ EOC
    if "Watch" in st.session_state.eoc_status:
        st.info(f"🟢 สถานะปัจจุบัน: **{st.session_state.eoc_status}**")
    elif "Alert" in st.session_state.eoc_status:
        st.warning(f"🟡 สถานะปัจจุบัน: **{st.session_state.eoc_status}**")
    elif "Response" in st.session_state.eoc_status:
        st.error(f"🔴 สถานะปัจจุบัน: **{st.session_state.eoc_status}**")
    elif "Recovery" in st.session_state.eoc_status:
        st.success(f"🔵 สถานะปัจจุบัน: **{st.session_state.eoc_status}**")

    st.divider()

    # ---------------------------------------------------------
    # 3. จัดการ Tab แบบ Dynamic (แสดงเฉพาะ Role ที่เกี่ยวข้อง)
    # ---------------------------------------------------------
    st.subheader("กระดานปฏิบัติงาน")
    
    # สร้าง List ของ Tab ที่ต้องการให้แสดง โดยเริ่มจาก Tab กลางที่ทุกคนต้องเห็น
    tabs_to_show = ["📍 ภาพรวมและประกาศ"]
    
    # เพิ่ม Tab ตาม Role ที่ล็อกอินเข้ามา
    if st.session_state.role == "IC (ผู้บัญชาการ)":
        tabs_to_show.extend(["🗣️ ข้อสั่งการ (IC เท่านั้น)", "📈 ติดตามงานทุกกลุ่ม"])
        
    elif st.session_state.role == "SAT":
        tabs_to_show.extend(["📝 ประเมิน Trigger Point", "📥 ส่งงาน SAT"])
        
    elif st.session_state.role == "JIT":
        tabs_to_show.extend(["📥 ส่งงาน JIT"])
        
    else:
        # กลุ่มอื่นๆ ที่ยังไม่ได้กำหนดเงื่อนไข ให้เห็นแค่ส่งงานของตัวเอง
        tabs_to_show.extend([f"📥 ส่งงาน {st.session_state.role}"])

    # สร้างชุดของ Tabs ขึ้นมาจริงๆ ตามเงื่อนไขด้านบน
    my_tabs = st.tabs(tabs_to_show)
    
    # --- ใส่เนื้อหาในแต่ละ Tab (เว้นโครงไว้ก่อน) ---
    with my_tabs[0]:
        st.markdown("**หน้าประกาศทั่วไป:** ใช้แสดงข้อสั่งการหรือสรุปสถานการณ์ให้ทุกคนรับทราบ (รอพัฒนาต่อ...)")
        
    # เช็คว่าล็อกอินเป็นอะไร แล้วค่อยดึง Index ของ Tab มาใช้
    if st.session_state.role == "IC (ผู้บัญชาการ)":
        with my_tabs[1]:
            st.markdown("**หน้าออกข้อสั่งการ:** (รอพัฒนาฟอร์มเขียนข้อความลง Database...)")
        with my_tabs[2]:
            st.markdown("**หน้าติดตามงาน:** (รอพัฒนาดึงข้อมูลทุกกลุ่มมาแสดงเป็นตาราง...)")
            
    elif st.session_state.role == "SAT":
        with my_tabs[1]:
            st.markdown("**หน้าประเมินเกณฑ์ระบาด:** (รอพัฒนา Checkbox เงื่อนไขต่างๆ...)")
        with my_tabs[2]:
            st.markdown("**หน้าอัปเดตงาน SAT:** (รอพัฒนาฟอร์มส่งงาน...)")
            
    elif st.session_state.role == "JIT":
        with my_tabs[1]:
            st.markdown("**หน้าอัปเดตงาน JIT:** (รอพัฒนาฟอร์มส่งงาน...)")
            
    else:
        with my_tabs[1]:
            st.markdown(f"**หน้าอัปเดตงาน {st.session_state.role}:** (รอพัฒนาฟอร์มส่งงาน...)")

# ---------------------------------------------------------
# ตัวควบคุมการสลับหน้า Login / Dashboard
# ---------------------------------------------------------
if not st.session_state.logged_in:
    login_page()
else:
    main_dashboard()
