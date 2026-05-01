import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ---------------------------------------------------------
# ตั้งค่าหน้าเพจ
# ---------------------------------------------------------
st.set_page_config(page_title="PHEM & BCP Command Center - สคร.1 เชียงใหม่", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1newH4TiteAxJxKnikgI4L8TA1HRfLaXGB6iFFTBvApc/edit?gid=0#gid=0"

# ตัวแปร Session State พื้นฐาน
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = ""
if 'main_role' not in st.session_state:
    st.session_state.main_role = ""

# =========================================================
# โครงสร้างสถานะ EOC จำลอง (อนาคตสามารถดึงจาก Google Sheet ได้)
# =========================================================
if 'eoc_statuses' not in st.session_state:
    st.session_state.eoc_statuses = {
        "All Hazard Response": "Watch Mode",
        "Disease X": "Watch Mode",
        "Avian Influenza": "Alert Mode",
        "Influenza": "Watch Mode",
        "อุทกภัย (Floods)": "Response 1",
        "PM 2.5": "Response 2",
        "MERS": "Watch Mode",
        "VPD (MMR)": "Watch Mode"
    }

conn = st.connection("gsheets", type=GSheetsConnection)

# ---------------------------------------------------------
# ฟังก์ชันสร้าง UI การ์ดแสดงสถานะ (Graphic Box)
# ---------------------------------------------------------
def render_status_card(hazard_name, status):
    # กำหนดสีและไอคอนตามระดับสถานะ
    if status == "Watch Mode":
        bg_color, text_color, icon = "#E8F5E9", "#1B5E20", "🟢" # เขียว (Inactive)
        level_text = "INACTIVE: Watch Mode"
    elif status == "Alert Mode":
        bg_color, text_color, icon = "#FFFDE7", "#F57F17", "🟡" # เหลือง (Inactive)
        level_text = "INACTIVE: Alert Mode"
    elif status == "Response 1":
        bg_color, text_color, icon = "#FFE0B2", "#E65100", "🟠" # ส้ม (Activated)
        level_text = "ACTIVATED: Response Level 1"
    elif status == "Response 2":
        bg_color, text_color, icon = "#FFCDD2", "#B71C1C", "🔴" # แดง (Activated)
        level_text = "ACTIVATED: Response Level 2"
    elif status == "Response 3":
        bg_color, text_color, icon = "#D1C4E9", "#4A148C", "🟣" # ม่วงเข้ม (Activated สูงสุด)
        level_text = "ACTIVATED: Response Level 3"
    else:
        bg_color, text_color, icon = "#F5F5F5", "#424242", "⚪"
        level_text = "Unknown Status"

    # สร้างกล่อง HTML/CSS
    html_card = f"""
    <div style="background-color: {bg_color}; padding: 15px; border-radius: 10px; border-left: 6px solid {text_color}; margin-bottom: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
        <h4 style="margin: 0; color: {text_color};">{icon} {hazard_name}</h4>
        <p style="margin: 5px 0 0 0; font-weight: bold; color: {text_color}; font-size: 14px;">{level_text}</p>
    </div>
    """
    st.markdown(html_card, unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. หน้า Login (ตัดโค้ดเดิมมาใส่ได้เลย ผมย่อไว้เพื่อความกะทัดรัด)
# ---------------------------------------------------------
def login_page():
    st.title("🔐 เข้าสู่ระบบ PHEM & BCP Command Center")
    st.markdown("สำนักงานป้องกันควบคุมโรคที่ 1 เชียงใหม่")
    # ... (โค้ด Login ดึงจากของเดิมได้เลยครับ) ...
    # สมมติว่าเข้าระบบผ่านแล้วเพื่อทดสอบหน้าจอ:
    if st.button("ข้าม Login เพื่อทดสอบหน้าจอ Dashboard"):
        st.session_state.logged_in = True
        st.session_state.role = "Admin"
        st.rerun()

# ---------------------------------------------------------
# 2. หน้า Dashboard หลัก
# ---------------------------------------------------------
def main_dashboard():
    # --- Sidebar ---
    st.sidebar.header("👤 ข้อมูลผู้ใช้งาน")
    st.sidebar.write(f"**Username:** {st.session_state.username}")
    st.sidebar.write(f"**กลุ่มภารกิจ:** {st.session_state.role}")
    
    if st.sidebar.button("🚪 ออกจากระบบ (Logout)"):
        st.session_state.logged_in = False
        st.rerun()

    # หัวเว็บใหม่ ครอบคลุมทั้ง PHEM และ BCP
    st.title("🚨 PHEM & BCP Command Center")
    st.markdown("**ระบบบัญชาการเหตุการณ์ฉุกเฉินทางสาธารณสุข และ แผนความต่อเนื่องทางธุรกิจ (สคร.1 เชียงใหม่)**")
    st.divider()

    # --- กระดาน Tab หลัก ---
    tabs_to_show = ["🏠 หน้าหลัก (Home)", "📍 ประกาศและข้อสั่งการ"]
    if st.session_state.role == "Admin":
        tabs_to_show.extend(["⚙️ จัดการผู้ใช้", "📝 อัปเดตสถานะ EOC (Admin)"])
    else:
        tabs_to_show.extend(["📥 ส่งงาน"])

    my_tabs = st.tabs(tabs_to_show)
    
    # =========================================================
    # TAB 1: หน้าหลัก (Home) - แสดง Graphic สถานะ EOC ทั้งหมด
    # =========================================================
    with my_tabs[0]:
        st.header("ภาพรวมสถานการณ์ (EOC Status Dashboard)")
        
        # ส่วนที่ 1: All Hazard Response (ร่มใหญ่)
        st.subheader("🌐 All Hazard Response")
        render_status_card("All Hazard Response (ภาพรวมทุกภัย)", st.session_state.eoc_statuses["All Hazard Response"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ส่วนที่ 2: Hazard Specific Response
        st.subheader("🎯 Hazard Specific Response (ภัยรายโรค/เหตุการณ์)")
        
        # แบ่งเป็น 3 คอลัมน์ให้ดูสวยงามเหมือน Dashboard
        col1, col2, col3 = st.columns(3)
        
        with col1:
            render_status_card("Disease X", st.session_state.eoc_statuses["Disease X"])
            render_status_card("Avian Influenza", st.session_state.eoc_statuses["Avian Influenza"])
            render_status_card("Influenza", st.session_state.eoc_statuses["Influenza"])
            
        with col2:
            render_status_card("อุทกภัย (Floods)", st.session_state.eoc_statuses["อุทกภัย (Floods)"])
            render_status_card("PM 2.5", st.session_state.eoc_statuses["PM 2.5"])
            
        with col3:
            render_status_card("MERS", st.session_state.eoc_statuses["MERS"])
            render_status_card("VPD (MMR)", st.session_state.eoc_statuses["VPD (MMR)"])

    # =========================================================
    # TAB 2: พื้นที่เว้นไว้พัฒนาต่อ
    # =========================================================
    with my_tabs[1]:
        st.markdown("**พื้นที่สำหรับประกาศจาก IC และผู้บริหาร**")
        
    # TAB แอดมินสำหรับปรับสถานะโชว์ที่หน้า Home
    if st.session_state.role == "Admin":
        with my_tabs[-1]: # แท็บสุดท้ายของ Admin
            st.header("ปรับปรุงสถานะศูนย์ EOC")
            for hazard in st.session_state.eoc_statuses.keys():
                new_status = st.selectbox(
                    f"สถานะของ {hazard}:",
                    ["Watch Mode", "Alert Mode", "Response 1", "Response 2", "Response 3"],
                    index=["Watch Mode", "Alert Mode", "Response 1", "Response 2", "Response 3"].index(st.session_state.eoc_statuses[hazard]),
                    key=f"select_{hazard}"
                )
                if new_status != st.session_state.eoc_statuses[hazard]:
                    st.session_state.eoc_statuses[hazard] = new_status
                    st.rerun()

# ---------------------------------------------------------
# ควบคุม Flow หน้าจอ
# ---------------------------------------------------------
if not st.session_state.logged_in:
    login_page()
else:
    main_dashboard()
