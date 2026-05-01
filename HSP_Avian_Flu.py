import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ---------------------------------------------------------
# ตั้งค่าหน้าเพจ
# ---------------------------------------------------------
st.set_page_config(page_title="PHEM & BCP - สคร.1 เชียงใหม่", layout="wide", initial_sidebar_state="collapsed")

# =========================================================
# เปลี่ยนฟอนต์ทั้งหน้าเว็บเป็น Prompt
# =========================================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;700&display=swap');
        
        html, body, [class*="css"], [class*="st-"], p, h1, h2, h3, h4, h5, h6, span, div, label, button, input, select, textarea {
            font-family: 'Prompt', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1newH4TiteAxJxKnikgI4L8TA1HRfLaXGB6iFFTBvApc/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

# =========================================================
# ฟังก์ชันดึงข้อมูล EOC จาก Sheet แยก 2 ตาราง (A-B และ D)
# =========================================================
@st.cache_data(ttl=60) # จำข้อมูล 1 นาที กันโควตาเต็ม
def get_eoc_data():
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet="EOC_Status", ttl=60)
        df.columns = df.columns.str.strip()
        
        # ตาราง 1: ดึงคอลัมน์ EOC List กับ Status
        df_eoc = df[['EOC List', 'Status']].dropna(subset=['EOC List'])
        eoc_dict = dict(zip(df_eoc['EOC List'], df_eoc['Status']))
        
        # ตาราง 2: ดึงลิสต์สถานะจากคอลัมน์ D
        status_list = df['Status_list'].dropna().tolist()
        
        return eoc_dict, status_list, df_eoc, df
    except Exception as e:
        st.error(f"⚠️ ไม่สามารถเชื่อมต่อชีต EOC_Status ได้: {e}")
        return {}, [], pd.DataFrame(), pd.DataFrame()

# โหลดข้อมูล EOC มาเก็บไว้
eoc_statuses, eoc_status_list, df_eoc_table, df_full_eoc = get_eoc_data()

# =========================================================
# 1. ระบบจัดการ State
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

# ---------------------------------------------------------
# ฟังก์ชันดึงสี ไอคอน และ สไตล์
# ---------------------------------------------------------
def get_status_style(status):
    if status == "Watch Mode":
        return "#F5F5F5", "#616161", "⚪", ":gray[Watch Mode]" 
    elif status == "Alert Mode":
        return "#FFF9C4", "#F57F17", "🟡", ":orange[Alert Mode]"  
    elif status == "Response 1":
        return "#FFCDD2", "#D32F2F", "🟠", ":red[**Response 1**]" 
    elif status == "Response 2":
        return "#E53935", "#FFFFFF", "🔴", ":red[**Response 2**]" 
    elif status == "Response 3":
        return "#B71C1C", "#FFFFFF", "🚨", ":red[**Response 3**]" 
    elif status == "Recovery Mode":
        return "#C8E6C9", "#1B5E20", "🟢", ":green[Recovery Mode]"  
    return "#FFFFFF", "#000000", "❓", status

# =========================================================
# หน้าที่ 1: PUBLIC HOMEPAGE
# =========================================================
def render_homepage():
    st.markdown("""<style>[data-testid="collapsedControl"] {display: none;}</style>""", unsafe_allow_html=True)
    
    st.title("🚨 PHEM & BCP Command Center")
    st.markdown("**ศูนย์ปฏิบัติการตอบโต้ภาวะฉุกเฉินทางสาธารณสุข - สคร.1 เชียงใหม่**")
    st.divider()
    
    # ป้องกันบั๊กกรณี Sheet ยังไม่มีข้อมูล
    if not eoc_statuses:
        st.warning("กำลังรอการเชื่อมต่อข้อมูล EOC จากฐานข้อมูล...")
        return

    st.header("🌐 ภาพรวมสถานการณ์ (คลิกเพื่อดูรายละเอียดแต่ละศูนย์)")
    
    all_hazard_key = list(eoc_statuses.keys())[0] # ดึงตัวแรกสุด (All Hazard)
    all_hazard_stat = eoc_statuses[all_hazard_key]
    _, _, icon_all, btn_text_all = get_status_style(all_hazard_stat)
    
    col_all1, col_all2, col_all3 = st.columns([1, 2, 1])
    with col_all2:
        st.subheader(f"ร่มใหญ่: {all_hazard_key}")
        if st.button(f"{icon_all} **{all_hazard_key}** \n\n {btn_text_all}", use_container_width=True):
            st.session_state.selected_eoc = all_hazard_key
            st.session_state.current_page = 'Public_EOC'
            st.rerun()

    st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)
    st.subheader("🎯 ศูนย์ปฏิบัติการรายเหตุการณ์ (Hazard Specific)")
    
    hazards = list(eoc_statuses.keys())[1:] # ตัดตัวแรกออก
    cols = st.columns(4)
    
    for i, hazard in enumerate(hazards):
        with cols[i % 4]:
            stat = eoc_statuses[hazard]
            _, _, icon, btn_text = get_status_style(stat)
            
            if st.button(f"{icon} **{hazard}** \n\n {btn_text}", key=f"btn_{hazard}", use_container_width=True):
                st.session_state.selected_eoc = hazard
                st.session_state.current_page = 'Public_EOC'
                st.rerun()

# =========================================================
# หน้าที่ 2: PUBLIC EOC PAGE
# =========================================================
def render_public_eoc():
    st.markdown("""<style>[data-testid="collapsedControl"] {display: none;}</style>""", unsafe_allow_html=True)
    
    if st.button("⬅️ กลับหน้าหลัก (Home)"):
        st.session_state.current_page = 'Home'
        st.rerun()
        
    current_status = eoc_statuses.get(st.session_state.selected_eoc, "Watch Mode")
    bg_color, text_color, icon, _ = get_status_style(current_status) 
    
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
# หน้าที่ 3: OPERATION DASHBOARD
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

    current_status = eoc_statuses.get(st.session_state.selected_eoc, "Watch Mode")
    bg_color, text_color, icon, _ = get_status_style(current_status)
    
    st.markdown(f"""
    <div style="background-color: {bg_color}; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <h3 style="margin: 0; color: {text_color};">{icon} กระดานปฏิบัติงานหลังบ้าน: {st.session_state.selected_eoc}</h3>
    </div>
    """, unsafe_allow_html=True)

    tabs_to_show = ["🗣️ ข้อสั่งการ IC และวาระการประชุม"]
    
    if st.session_state.role == "Admin" or st.session_state.role == "IC (ผู้บัญชาการ)":
        tabs_to_show.extend(["📝 อัปเดตสถานะ EOC", "⚙️ จัดการผู้ใช้"])
    else:
        tabs_to_show.extend([f"📥 ส่งรายงาน ({st.session_state.role})"])

    my_tabs = st.tabs(tabs_to_show)
    
    with my_tabs[0]:
        st.write("พื้นที่สำหรับรับทราบข้อสั่งการจากผู้บัญชาการเหตุการณ์ (IC)")
        
    if st.session_state.role == "Admin" or st.session_state.role == "IC (ผู้บัญชาการ)":
        
        # --- แท็บอัปเดตสถานะ EOC ทะลุเข้า Sheet ---
        with my_tabs[1]:
            st.header("📝 อัปเดตระดับความรุนแรง EOC")
            st.info("แก้ไขสถานะในคอลัมน์ 'Status' แล้วกดบันทึกเพื่ออัปเดตหน้า Homepage ทันที")
            
            edited_eoc = st.data_editor(
                df_eoc_table,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "EOC List": st.column_config.TextColumn("รายชื่อศูนย์ EOC", disabled=True),
                    "Status": st.column_config.SelectboxColumn("สถานะ (Status)", options=eoc_status_list)
                }
            )
            
            if st.button("💾 บันทึกการเปลี่ยนสถานะ EOC", type="primary"):
                df_full_eoc.update(edited_eoc) # เอาที่แก้ไปสวมทับตารางหลัก (จะได้ไม่ทำคอลัมน์ D พัง)
                conn.update(spreadsheet=SHEET_URL, worksheet="EOC_Status", data=df_full_eoc)
                st.cache_data.clear() # ล้างความจำเพื่อดึงข้อมูลอัปเดต
                st.success("✅ อัปเดตสถานะ EOC ขึ้นหน้า Home เรียบร้อย!")
                st.rerun()

        with my_tabs[2]:
            st.info("ระบบจัดการบัญชีผู้ใช้งาน (ยกยอดโครงสร้างมาจากของเดิม เตรียมพัฒนาต่อ)")
    else:
        with my_tabs[1]:
            st.info(f"ฟอร์มรายงานผลการปฏิบัติงานของกลุ่ม: {st.session_state.role} สำหรับเหตุการณ์นี้")

# =========================================================
# ROUTER
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
