import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# ---------------------------------------------------------
# ตั้งค่าหน้าเพจ & URL ฐานข้อมูล
# ---------------------------------------------------------
st.set_page_config(page_title="EOC สคร.1 เชียงใหม่ - ไข้หวัดนก", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1newH4TiteAxJxKnikgI4L8TA1HRfLaXGB6iFFTBvApc/edit?gid=0#gid=0"

# Session State สำหรับเก็บข้อมูลการล็อกอินและสถานะ EOC
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = ""
if 'eoc_status' not in st.session_state:
    st.session_state.eoc_status = "Watch Mode (เฝ้าระวังปกติ)"

conn = st.connection("gsheets", type=GSheetsConnection)

# ---------------------------------------------------------
# 1. หน้า Login
# ---------------------------------------------------------
def login_page():
    st.title("🔐 เข้าสู่ระบบ EOC Command Center")
    st.markdown("สำนักงานป้องกันควบคุมโรคที่ 1 เชียงใหม่ (กรณีโรคไข้หวัดนก)")
    
    try:
        df_users = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=0)
    except Exception as e:
        st.error(f"⚠️ ตรวจพบ Error จากระบบหลังบ้าน: {e}")
        st.stop()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("Sign In")
            input_user = st.text_input("Username")
            input_pwd = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("เข้าสู่ระบบ")

            if submit_btn:
                df_users['password'] = df_users['password'].astype(str)
                match = df_users[(df_users['username'] == input_user) & (df_users['password'] == str(input_pwd))]
                
                if not match.empty:
                    st.success("เข้าสู่ระบบสำเร็จ!")
                    st.session_state.logged_in = True
                    st.session_state.username = input_user
                    st.session_state.role = match.iloc[0]['role']
                    st.rerun()
                else:
                    st.error("❌ Username หรือ Password ไม่ถูกต้อง!")

# ---------------------------------------------------------
# 2. หน้า Dashboard หลัก
# ---------------------------------------------------------
def main_dashboard():
    # --- แถบ Sidebar ---
    st.sidebar.header("👤 ข้อมูลผู้ใช้งาน")
    st.sidebar.write(f"**Username:** {st.session_state.username}")
    st.sidebar.write(f"**กลุ่มภารกิจ:** {st.session_state.role}")
    
    if st.sidebar.button("🚪 ออกจากระบบ (Logout)"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    st.title("🚨 EOC Action Plan: กรณีไข้หวัดนก (HSP 2568)")
    
    # --- แสดง Status ของ EOC ---
    st.header("📊 สถานะศูนย์ปฏิบัติการตอบโต้ภาวะฉุกเฉิน")
    
    if st.session_state.role == "IC (ผู้บัญชาการ)":
        new_status = st.selectbox(
            "ปรับระดับสถานการณ์ EOC:", 
            ["Watch Mode (เฝ้าระวังปกติ)", "Alert Mode (เตรียมความพร้อม)", "Response Mode (ตอบโต้ฉุกเฉิน)", "Recovery Mode (ฟื้นฟู/หลังเกิดเหตุ)"],
            index=["Watch Mode (เฝ้าระวังปกติ)", "Alert Mode (เตรียมความพร้อม)", "Response Mode (ตอบโต้ฉุกเฉิน)", "Recovery Mode (ฟื้นฟู/หลังเกิดเหตุ)"].index(st.session_state.eoc_status)
        )
        if new_status != st.session_state.eoc_status:
            st.session_state.eoc_status = new_status
            st.rerun()
            
    if "Watch" in st.session_state.eoc_status:
        st.info(f"🟢 สถานะปัจจุบัน: **{st.session_state.eoc_status}**")
    elif "Alert" in st.session_state.eoc_status:
        st.warning(f"🟡 สถานะปัจจุบัน: **{st.session_state.eoc_status}**")
    elif "Response" in st.session_state.eoc_status:
        st.error(f"🔴 สถานะปัจจุบัน: **{st.session_state.eoc_status}**")
    elif "Recovery" in st.session_state.eoc_status:
        st.success(f"🔵 สถานะปัจจุบัน: **{st.session_state.eoc_status}**")

    st.divider()

    # --- จัดการ Tab ตาม Role ---
    st.subheader("กระดานปฏิบัติงาน")
    
    tabs_to_show = ["📍 ภาพรวมและประกาศ"]
    
    # เพิ่ม Tab ตามเงื่อนไข Role
    if st.session_state.role == "Admin":
        tabs_to_show.extend(["⚙️ จัดการผู้ใช้ (Admin)"])
    elif st.session_state.role == "IC (ผู้บัญชาการ)":
        tabs_to_show.extend(["🗣️ ข้อสั่งการ (IC เท่านั้น)", "📈 ติดตามงานทุกกลุ่ม"])
    elif st.session_state.role == "SAT":
        tabs_to_show.extend(["📝 ประเมิน Trigger Point", "📥 ส่งงาน SAT"])
    elif st.session_state.role == "JIT":
        tabs_to_show.extend(["📥 ส่งงาน JIT"])
    else:
        tabs_to_show.extend([f"📥 ส่งงาน {st.session_state.role}"])

    my_tabs = st.tabs(tabs_to_show)
    
    # Tab 0: เนื้อหาที่ทุกคนเห็น
    with my_tabs[0]:
        st.markdown("**หน้าประกาศทั่วไป:** ใช้แสดงสรุปสถานการณ์ให้ทุกคนรับทราบ")
        
    # Tab ถัดไป ขึ้นอยู่กับ Role
    if st.session_state.role == "Admin":
        with my_tabs[1]:
            st.header("⚙️ ระบบจัดการบัญชีผู้ใช้งาน (User Management)")
            st.info("💡 **วิธีใช้งาน:** แก้ไขรหัสผ่านได้โดยตรงในตาราง เพิ่มพนักงานใหม่ให้เลื่อนไปบรรทัดล่างสุดแล้วพิมพ์ได้เลย หากต้องการลบให้คลิกซ้ายที่หน้าแถวแล้วกดปุ่ม Delete (หรือ Backspace) บนคีย์บอร์ด เมื่อเสร็จแล้วต้องกดปุ่ม 'บันทึก' ด้านล่าง")
            
            # ดึงข้อมูล Users ใหม่สุดมาแสดงให้ Admin แก้ไข
            try:
                df_admin_users = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=0)
                # ป้องกัน Error กรณีตารางว่าง
                if df_admin_users.empty:
                    df_admin_users = pd.DataFrame(columns=["username", "password", "role"])
                
                # ฟีเจอร์ data_editor อนุญาตให้เพิ่ม/ลบแถว (num_rows="dynamic")
                edited_users = st.data_editor(
                    df_admin_users,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "username": st.column_config.TextColumn("Username (ห้ามซ้ำ)"),
                        "password": st.column_config.TextColumn("Password"),
                        "role": st.column_config.SelectboxColumn("Role (กลุ่มภารกิจ)", options=["Admin", "IC (ผู้บัญชาการ)", "SAT", "JIT", "Logistics", "RC", "Liaison", "อื่นๆ"])
                    }
                )
                
                # ปุ่มบันทึกอัปเดตลง Google Sheet
                if st.button("💾 บันทึกการเปลี่ยนแปลง (Save to Database)"):
                    # ลบแถวที่ username ว่างเปล่าออกก่อนเซฟ (ป้องกันข้อมูลขยะ)
                    edited_users = edited_users.dropna(subset=['username'])
                    conn.update(spreadsheet=SHEET_URL, worksheet="Users", data=edited_users)
                    st.success("✅ อัปเดตข้อมูลผู้ใช้งานลง Google Sheet เรียบร้อยแล้ว!")
                    
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")

    elif st.session_state.role == "IC (ผู้บัญชาการ)":
        with my_tabs[1]:
            st.markdown("**หน้าออกข้อสั่งการ:** (พื้นที่เตรียมพัฒนาต่อ...)")
        with my_tabs[2]:
            st.markdown("**หน้าติดตามงาน:** (พื้นที่เตรียมพัฒนาต่อ...)")
            
    elif st.session_state.role == "SAT":
        with my_tabs[1]:
            st.markdown("**หน้าประเมินเกณฑ์ระบาด:** (พื้นที่เตรียมพัฒนาต่อ...)")
        with my_tabs[2]:
            st.markdown("**หน้าอัปเดตงาน SAT:** (พื้นที่เตรียมพัฒนาต่อ...)")
            
    else:
        with my_tabs[1]:
            st.markdown(f"**หน้าอัปเดตงาน {st.session_state.role}:** (พื้นที่เตรียมพัฒนาต่อ...)")

# ---------------------------------------------------------
# ควบคุม Flow หน้าจอ
# ---------------------------------------------------------
if not st.session_state.logged_in:
    login_page()
else:
    main_dashboard()
