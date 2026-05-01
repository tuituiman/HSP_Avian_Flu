import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ---------------------------------------------------------
# ตั้งค่าหน้าเพจ
# ---------------------------------------------------------
st.set_page_config(page_title="PHEM & BCP - สคร.1 เชียงใหม่", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1newH4TiteAxJxKnikgI4L8TA1HRfLaXGB6iFFTBvApc/edit?gid=0#gid=0"

# =========================================================
# 1. ระบบจัดการ State (ว่าตอนนี้อยู่หน้าไหน)
# =========================================================
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home' # หน้าที่เปิดได้มี: Home, Login, EOC_Dashboard
if 'selected_eoc' not in st.session_state:
    st.session_state.selected_eoc = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = ""
if 'main_role' not in st.session_state:
    st.session_state.main_role = ""

# ข้อมูลจำลองสถานะ EOC (รอเชื่อม Sheet)
if 'eoc_statuses' not in st.session_state:
    st.session_state.eoc_statuses = {
        "All Hazard Response": "Watch Mode",
        "Disease X": "Watch Mode",
        "Avian Influenza": "Alert Mode",
        "Influenza": "Recovery Mode",
        "อุทกภัย (Floods)": "Response 1",
        "PM 2.5": "Response 2",
        "MERS": "Response 3",
        "VPD (MMR)": "Watch Mode"
    }

conn = st.connection("gsheets", type=GSheetsConnection)

# ---------------------------------------------------------
# ฟังก์ชันกำหนดสีตามระดับความรุนแรง
# ---------------------------------------------------------
def get_status_style(status):
    # (สีพื้นหลัง, สีตัวหนังสือ, ไอคอน)
    if status == "Watch Mode":
        return "#EEEEEE", "#424242", "⚪" # เทา (Inactive)
    elif status == "Alert Mode":
        return "#FFF59D", "#F57F17", "🟡" # เหลือง (Inactive)
    elif status == "Response 1":
        return "#FFCDD2", "#C62828", "🟠" # แดงอ่อน
    elif status == "Response 2":
        return "#EF5350", "#FFFFFF", "🔴" # แดงกลาง (ตัวหนังสือขาว)
    elif status == "Response 3":
        return "#B71C1C", "#FFFFFF", "🚨" # แดงเข้ม (ตัวหนังสือขาว)
    elif status == "Recovery Mode":
        return "#C8E6C9", "#1B5E20", "🟢" # เขียว (ฟื้นฟู)
    return "#FFFFFF", "#000000", "❓"

# =========================================================
# หน้าที่ 1: PUBLIC HOMEPAGE (เข้าได้ทุกคน)
# =========================================================
def render_homepage():
    st.title("🚨 PHEM & BCP Command Center")
    st.markdown("**ศูนย์ปฏิบัติการตอบโต้ภาวะฉุกเฉินทางสาธารณสุข - สคร.1 เชียงใหม่**")
    st.divider()
    
    st.header("🌐 ภาพรวมสถานการณ์ (Public Dashboard)")
    
    # ฟังก์ชันช่วยวาดกล่อง EOC และปุ่ม Login
    def draw_eoc_card(hazard_name):
        status = st.session_state.eoc_statuses.get(hazard_name, "Watch Mode")
        bg_color, text_color, icon = get_status_style(status)
        
        # วาดกล่องสถานะ
        html = f"""
        <div style="background-color: {bg_color}; padding: 15px; border-radius: 8px; margin-bottom: 10px; text-align: center; border: 1px solid rgba(0,0,0,0.1);">
            <h4 style="margin: 0; color: {text_color}; font-size: 16px;">{icon} {hazard_name}</h4>
            <p style="margin: 5px 0 0 0; font-weight: bold; color: {text_color}; font-size: 14px;">{status}</p>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        
        # วาดปุ่มกดเพื่อแยกล็อกอิน
        if st.button(f"เข้าสู่ระบบ", key=f"btn_{hazard_name}", use_container_width=True):
            st.session_state.selected_eoc = hazard_name
            st.session_state.current_page = 'Login'
            st.rerun()

    # จัด Layout ตรงกลางสำหรับ All Hazard
    col_all1, col_all2, col_all3 = st.columns([1, 2, 1])
    with col_all2:
        st.subheader("All Hazard Response")
        draw_eoc_card("All Hazard Response")

    st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)
    st.subheader("🎯 Hazard Specific Response (ภัยรายโรค/เหตุการณ์)")
    
    # จัด Layout 4 คอลัมน์สำหรับโรคต่างๆ
    hazards = list(st.session_state.eoc_statuses.keys())[1:] # ตัด All Hazard ออก
    cols = st.columns(4)
    
    for i, hazard in enumerate(hazards):
        with cols[i % 4]: # กระจายลงทีละคอลัมน์
            draw_eoc_card(hazard)

# =========================================================
# หน้าที่ 2: LOGIN PAGE (เจาะจงราย EOC)
# =========================================================
def render_login():
    st.button("⬅️ กลับหน้าหลัก (Home)", on_click=lambda: st.session_state.update(current_page='Home'))
    st.title(f"🔐 เข้าสู่ระบบ EOC: {st.session_state.selected_eoc}")
    
    try:
        df_users = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=600)
        df_users.columns = df_users.columns.str.strip()
    except Exception as e:
        st.error(f"⚠️ ตรวจพบ Error จากระบบหลังบ้าน: {e}")
        st.stop()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.info(f"คุณกำลังเข้าสู่ห้องปฏิบัติการ: **{st.session_state.selected_eoc}**")
            input_user = st.text_input("Username")
            input_pwd = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("เข้าสู่ระบบ")

            if submit_btn:
                df_users['Password'] = df_users['Password'].astype(str)
                match = df_users[(df_users['Username'] == input_user) & (df_users['Password'] == str(input_pwd))]
                
                if not match.empty:
                    st.success("เข้าสู่ระบบสำเร็จ!")
                    st.session_state.logged_in = True
                    st.session_state.username = input_user
                    st.session_state.role = match.iloc[0]['Role']
                    st.session_state.main_role = match.iloc[0]['Main_Role']
                    st.session_state.current_page = 'EOC_Dashboard' # เปลี่ยนหน้าไปที่ Dashboard
                    st.rerun()
                else:
                    st.error("❌ Username หรือ Password ไม่ถูกต้อง!")

# =========================================================
# หน้าที่ 3: OPERATION DASHBOARD (หลังบ้านของ EOC นั้นๆ)
# =========================================================
def render_dashboard():
    # --- Sidebar ---
    st.sidebar.header(f"📍 EOC: {st.session_state.selected_eoc}")
    st.sidebar.divider()
    st.sidebar.header("👤 ข้อมูลปฏิบัติงาน")
    st.sidebar.write(f"**Username:** {st.session_state.username}")
    st.sidebar.write(f"**สายงาน:** {st.session_state.main_role}")
    st.sidebar.write(f"**ภารกิจ:** {st.session_state.role}")
    
    if st.sidebar.button("🚪 ออกจากระบบ (กลับหน้าโฮม)"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.current_page = 'Home'
        st.rerun()

    # --- ส่วนหัว Dashboard ---
    current_status = st.session_state.eoc_statuses[st.session_state.selected_eoc]
    bg_color, text_color, icon = get_status_style(current_status)
    
    st.markdown(f"""
    <div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="margin: 0; color: {text_color};">{icon} ศูนย์ปฏิบัติการ: {st.session_state.selected_eoc}</h2>
        <h4 style="margin: 5px 0 0 0; color: {text_color};">ระดับสถานการณ์ปัจจุบัน: {current_status}</h4>
    </div>
    """, unsafe_allow_html=True)

    # --- เมนูการทำงาน ---
    st.subheader("กระดานปฏิบัติงาน")
    tabs_to_show = ["📍 ประกาศและข้อสั่งการ"]
    
    if st.session_state.role == "Admin" or st.session_state.role == "IC (ผู้บัญชาการ)":
        tabs_to_show.extend(["📈 ติดตามงานทุกกลุ่ม", "⚙️ จัดการผู้ใช้"])
    else:
        tabs_to_show.extend([f"📥 ส่งงาน ({st.session_state.role})"])

    my_tabs = st.tabs(tabs_to_show)
    
    with my_tabs[0]:
        st.write("พื้นที่แสดงผล Situation Report (SitRep) และข้อสั่งการจาก IC สำหรับภัยนี้โดยเฉพาะ")
        
    if st.session_state.role == "Admin" or st.session_state.role == "IC (ผู้บัญชาการ)":
        with my_tabs[2]:
            st.info("พื้นที่จัดการบัญชีผู้ใช้งาน (ยกยอดมาจากโค้ดเดิม)")
            # สามารถนำโค้ด Data Editor ของเดิมมาใส่ในบล็อกนี้ได้เลย
            
    else:
        with my_tabs[1]:
            st.info(f"ฟอร์มรายงานผลการปฏิบัติงานของกลุ่ม: {st.session_state.role}")

# =========================================================
# ROUTER: ตัวควบคุมทิศทาง (ว่าหน้าจอควรแสดงอะไร)
# =========================================================
if st.session_state.current_page == 'Home':
    render_homepage()
elif st.session_state.current_page == 'Login':
    render_login()
elif st.session_state.current_page == 'EOC_Dashboard' and st.session_state.logged_in:
    render_dashboard()
else:
    # กันเหนียวเผื่อ State รวน
    st.session_state.current_page = 'Home'
    st.rerun()
