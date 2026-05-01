import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ---------------------------------------------------------
# ตั้งค่าหน้าเพจ
# ---------------------------------------------------------
st.set_page_config(page_title="PHEM & BCP - สคร.1 เชียงใหม่", layout="wide", initial_sidebar_state="collapsed")

# =========================================================
# เปลี่ยนฟอนต์ทั้งหน้าเว็บเป็น Prompt (Google Fonts)
# =========================================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;700&display=swap');
        
        /* บังคับใช้ฟอนต์ Prompt กับทุกองค์ประกอบในเว็บ */
        html, body, [class*="css"], [class*="st-"], p, h1, h2, h3, h4, h5, h6, span, div, label, button, input, select, textarea {
            font-family: 'Prompt', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1newH4TiteAxJxKnikgI4L8TA1HRfLaXGB6iFFTBvApc/edit?gid=0#gid=0"

# =========================================================
# 1. ระบบจัดการ State (ตัวควบคุมทิศทางหน้าเว็บ)
# =========================================================
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home' 
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

# ข้อมูลจำลองสถานะ EOC
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
# ฟังก์ชันดึงสีและไอคอนตามระดับสถานะ
# ---------------------------------------------------------
def get_status_style(status):
    if status == "Watch Mode":
        return "#EEEEEE", "#424242", "⚪" 
    elif status == "Alert Mode":
        return "#FFF59D", "#F57F17", "🟡" 
    elif status == "Response 1":
        return "#FFCC80", "#E65100", "🟠" 
    elif status == "Response 2":
        return "#EF9A9A", "#B71C1C", "🔴" 
    elif status == "Response 3":
        return "#B71C1C", "#FFFFFF", "🚨" 
    elif status == "Recovery Mode":
        return "#C8E6C9", "#1B5E20", "🟢" 
    return "#FFFFFF", "#000000", "❓"

# =========================================================
# หน้าที่ 1: PUBLIC HOMEPAGE (หน้าแรกสุด สำหรับทุกคน)
# =========================================================
def render_homepage():
    st.markdown("""<style>[data-testid="collapsedControl"] {display: none;}</style>""", unsafe_allow_html=True)
    
    st.title("🚨 PHEM & BCP Command Center")
    st.markdown("**ศูนย์ปฏิบัติการตอบโต้ภาวะฉุกเฉินทางสาธารณสุข - สคร.1 เชียงใหม่**")
    st.divider()
    
    st.header("🌐 ภาพรวมสถานการณ์ (คลิกเพื่อดูรายละเอียดแต่ละศูนย์)")
    
    all_hazard_stat = st.session_state.eoc_statuses["All Hazard Response"]
    icon_all = get_status_style(all_hazard_stat)[2]
    
    col_all1, col_all2, col_all3 = st.columns([1, 2, 1])
    with col_all2:
        st.subheader("ร่มใหญ่: All Hazard Response")
        if st.button(f"{icon_all} All Hazard Response \n\n สถานะ: {all_hazard_stat}", use_container_width=True):
            st.session_state.selected_eoc = "All Hazard Response"
            st.session_state.current_page = 'Public_EOC'
            st.rerun()

    st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)
    st.subheader("🎯 ศูนย์ปฏิบัติการรายเหตุการณ์ (Hazard Specific)")
    
    hazards = list(st.session_state.eoc_statuses.keys())[1:] 
    cols = st.columns(4)
    
    for i, hazard in enumerate(hazards):
        with cols[i % 4]:
            stat = st.session_state.eoc_statuses[hazard]
            icon = get_status_style(stat)[2]
            
            if st.button(f"{icon} {hazard} \n\n {stat}", key=f"btn_{hazard}", use_container_width=True):
                st.session_state.selected_eoc = hazard
                st.session_state.current_page = 'Public_EOC'
                st.rerun()

# =========================================================
# หน้าที่ 2: PUBLIC EOC PAGE (หน้าแสดงข้อมูลสาธารณะ + ช่อง Login)
# =========================================================
def render_public_eoc():
    st.markdown("""<style>[data-testid="collapsedControl"] {display: none;}</style>""", unsafe_allow_html=True)
    
    if st.button("⬅️ กลับหน้าหลัก (Home)"):
        st.session_state.current_page = 'Home'
        st.rerun()
        
    current_status = st.session_state.eoc_statuses[st.session_state.selected_eoc]
    bg_color, text_color, icon = get_status_style(current_status)
    
    st.markdown(f"""
    <div style="background-color: {bg_color}; padding: 25px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1);">
        <h1 style="margin: 0; color: {text_color}; font-size: 2.2em;">{icon} ศูนย์ EOC: {st.session_state.selected_eoc}</h1>
        <h3 style="margin: 10px 0 0 0; color: {text_color};">ระดับการตอบโต้: {current_status}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col_public, col_login = st.columns([2, 1.2])
    
    with col_public:
        st.header("📢 ข่าวสารและประกาศสาธารณะ")
        st.info("พื้นที่สำหรับแสดง Situation Report (SitRep), สรุปสถานการณ์ประจำวัน, และคำแนะนำเบื้องต้นสำหรับประชาชนและเครือข่าย")
        st.markdown("""
        * **อัปเดตล่าสุด:** สถานการณ์อยู่ในเกณฑ์ที่ควบคุมได้
        * **ข้อแนะนำ:** สวมหน้ากากอนามัยและล้างมือบ่อยๆ
        * *(เตรียมเชื่อมฐานข้อมูลประกาศในอนาคต)*
        """)
        
    with col_login:
        st.subheader("🔐 สำหรับเจ้าหน้าที่ (Staff Login)")
        
        try:
            df_users = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=600)
            df_users.columns = df_users.columns.str.strip()
        except Exception as e:
            st.error(f"⚠️ โหลดข้อมูลผู้ใช้ไม่ได้: {e}")
            st.stop()

        with st.form("login_form"):
            st.write(f"เข้าสู่พื้นที่ปฏิบัติงาน: **{st.session_state.selected_eoc}**")
            input_user = st.text_input("Username")
            input_pwd = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("Log In เข้าสู่ระบบ", type="primary")

            if submit_btn:
                df_users['Password'] = df_users['Password'].astype(str)
                match = df_users[(df_users['Username'] == input_user) & (df_users['Password'] == str(input_pwd))]
                
                if not match.empty:
                    st.success("เข้าสู่ระบบสำเร็จ!")
                    st.session_state.logged_in = True
                    st.session_state.username = input_user
                    st.session_state.role = match.iloc[0]['Role']
                    st.session_state.main_role = match.iloc[0]['Main_Role']
                    st.session_state.current_page = 'EOC_Dashboard' 
                    st.rerun()
                else:
                    st.error("❌ Username หรือ Password ไม่ถูกต้อง!")

# =========================================================
# หน้าที่ 3: OPERATION DASHBOARD (หลังบ้านของเจ้าหน้าที่)
# =========================================================
def render_dashboard():
    st.sidebar.header(f"📍 ภารกิจ: {st.session_state.selected_eoc}")
    st.sidebar.divider()
    st.sidebar.header("👤 ข้อมูลปฏิบัติงาน")
    st.sidebar.write(f"**Username:** {st.session_state.username}")
    st.sidebar.write(f"**สายงาน:** {st.session_state.main_role}")
    st.sidebar.write(f"**กลุ่มภารกิจ:** {st.session_state.role}")
    
    if st.sidebar.button("🚪 กลับสู่หน้า Public"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.main_role = ""
        st.session_state.current_page = 'Public_EOC'
        st.rerun()

    current_status = st.session_state.eoc_statuses[st.session_state.selected_eoc]
    bg_color, text_color, icon = get_status_style(current_status)
    
    st.markdown(f"""
    <div style="background-color: {bg_color}; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: {text_color};">{icon} กระดานปฏิบัติงานหลังบ้าน: {st.session_state.selected_eoc}</h3>
    </div>
    """, unsafe_allow_html=True)

    tabs_to_show = ["🗣️ ข้อสั่งการ IC และวาระการประชุม"]
    
    if st.session_state.role == "Admin" or st.session_state.role == "IC (ผู้บัญชาการ)":
        tabs_to_show.extend(["📈 ติดตามงานทุกกลุ่ม", "⚙️ จัดการผู้ใช้"])
    else:
        tabs_to_show.extend([f"📥 ส่งรายงาน ({st.session_state.role})"])

    my_tabs = st.tabs(tabs_to_show)
    
    with my_tabs[0]:
        st.write("พื้นที่สำหรับรับทราบข้อสั่งการจากผู้บัญชาการเหตุการณ์ (IC)")
        
    if st.session_state.role == "Admin" or st.session_state.role == "IC (ผู้บัญชาการ)":
        with my_tabs[2]:
            st.info("ระบบจัดการบัญชีผู้ใช้งาน (ยกยอดโครงสร้างมาจากของเดิม เตรียมพัฒนาต่อ)")
    else:
        with my_tabs[1]:
            st.info(f"ฟอร์มรายงานผลการปฏิบัติงานของกลุ่ม: {st.session_state.role} สำหรับเหตุการณ์นี้")

# =========================================================
# ROUTER: ตัวควบคุมทิศทาง (ว่าหน้าจอควรแสดงอะไร)
# =========================================================
if st.session_state.current_page == 'Home':
    render_homepage()
elif st.session_state.current_page == 'Public_EOC':
    render_public_eoc()
elif st.session_state.current_page == 'EOC_Dashboard' and st.session_state.logged_in:
    render_dashboard()
else:
    st.session_state.current_page = 'Home'
    st.rerun()
