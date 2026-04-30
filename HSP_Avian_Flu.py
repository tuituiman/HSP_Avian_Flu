import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ---------------------------------------------------------
# ตั้งค่าหน้าเพจ & URL ฐานข้อมูล
# ---------------------------------------------------------
st.set_page_config(page_title="EOC สคร.1 เชียงใหม่ - ไข้หวัดนก", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1newH4TiteAxJxKnikgI4L8TA1HRfLaXGB6iFFTBvApc/edit?gid=0#gid=0"

# ตัวแปร Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = ""
if 'main_role' not in st.session_state:
    st.session_state.main_role = ""
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
        # แก้ไขตรงนี้: เปลี่ยน ttl=0 เป็น ttl=10 (ให้จำข้อมูล 10 วินาที ช่วยลดโควตา)
        df_users = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=10)
        df_users.columns = df_users.columns.str.strip()
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
                df_users['Password'] = df_users['Password'].astype(str)
                match = df_users[(df_users['Username'] == input_user) & (df_users['Password'] == str(input_pwd))]
                
                if not match.empty:
                    st.success("เข้าสู่ระบบสำเร็จ!")
                    st.session_state.logged_in = True
                    st.session_state.username = input_user
                    st.session_state.role = match.iloc[0]['Role']
                    st.session_state.main_role = match.iloc[0]['Main_Role']
                    st.rerun()
                else:
                    st.error("❌ Username หรือ Password ไม่ถูกต้อง!")

# ---------------------------------------------------------
# 2. หน้า Dashboard หลัก
# ---------------------------------------------------------
def main_dashboard():
    st.sidebar.header("👤 ข้อมูลผู้ใช้งาน")
    st.sidebar.write(f"**Username:** {st.session_state.username}")
    st.sidebar.write(f"**สายงาน (Main Role):** {st.session_state.main_role}")
    st.sidebar.write(f"**กลุ่มภารกิจ (Role):** {st.session_state.role}")
    
    if st.sidebar.button("🚪 ออกจากระบบ (Logout)"):
        st.cache_data.clear() # ล้างความจำก่อนออก
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.main_role = ""
        st.rerun()

    st.title("🚨 EOC Action Plan: กรณีไข้หวัดนก (HSP 2568)")
    
    st.header("📊 สถานะศูนย์ปฏิบัติการตอบโต้ภาวะฉุกเฉิน")
    
    if st.session_state.role in ["IC (ผู้บัญชาการ)", "Admin"]:
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

    st.subheader("กระดานปฏิบัติงาน")
    tabs_to_show = ["📍 ภาพรวมและประกาศ"]
    
    if st.session_state.role == "Admin":
        tabs_to_show.extend(["⚙️ จัดการผู้ใช้ (Admin)"])
    elif st.session_state.role == "IC (ผู้บัญชาการ)":
        tabs_to_show.extend(["🗣️ ข้อสั่งการ (IC เท่านั้น)", "📈 ติดตามงานทุกกลุ่ม"])
    else:
        tabs_to_show.extend([f"📥 ส่งงาน {st.session_state.role}"])

    my_tabs = st.tabs(tabs_to_show)
    
    with my_tabs[0]:
        st.markdown("**หน้าประกาศทั่วไป:** ใช้แสดงสรุปสถานการณ์ให้ทุกคนรับทราบ")
        
    # =========================================================
    # ฟีเจอร์หน้า ADMIN 
    # =========================================================
    if st.session_state.role == "Admin":
        with my_tabs[1]:
            st.header("⚙️ ระบบจัดการบัญชีผู้ใช้งาน (User Management)")
            
            try:
                # แก้ไขตรงนี้: เพิ่ม ttl=10 เพื่อลดภาระการดึงข้อมูล
                df_users = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=10)
                df_users.columns = df_users.columns.str.strip()
                
                # Role_Mapping นานๆ เปลี่ยนที ให้จำไว้ 60 วินาทีเลย
                df_roles_raw = conn.read(spreadsheet=SHEET_URL, worksheet="Role_Mapping", ttl=60)
                df_roles_raw.columns = df_roles_raw.columns.str.strip()
                
                if 'Main Role' in df_roles_raw.columns and 'Role' in df_roles_raw.columns:
                    df_roles = df_roles_raw[['Main Role', 'Role']].dropna(how='all')
                    df_roles.rename(columns={'Main Role': 'Main_Role'}, inplace=True)
                else:
                    df_roles = df_roles_raw.iloc[:, :2].dropna(how='all')
                    df_roles.columns = ['Main_Role', 'Role']
                
                if df_users.empty:
                    df_users = pd.DataFrame(columns=["Username", "Password", "Main_Role", "Role"])
                
                main_roles_list = df_roles["Main_Role"].dropna().unique().tolist()
                all_roles_list = df_roles["Role"].dropna().unique().tolist()

                # --- ส่วนที่ 1: เพิ่มผู้ใช้ใหม่ ---
                with st.expander("➕ เพิ่มผู้ใช้งานใหม่ (Add New User)", expanded=True):
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        selected_main_role = st.selectbox("1. เลือกสายงาน (Main_Role)", ["-- เลือกสายงาน --"] + main_roles_list)
                    
                    filtered_roles = []
                    selected_role = "-- เลือกกลุ่มภารกิจ --"
                    
                    if selected_main_role != "-- เลือกสายงาน --":
                        filtered_roles = df_roles[df_roles["Main_Role"] == selected_main_role]["Role"].dropna().tolist()
                    
                    with c2:
                        if selected_main_role == "-- เลือกสายงาน --":
                            st.selectbox("2. เลือกกลุ่มภารกิจ (Role)", ["-- กรุณาเลือกสายงานก่อน --"], disabled=True)
                        elif len(filtered_roles) == 1:
                            selected_role = filtered_roles[0]
                            st.info(f"📌 กลุ่มภารกิจ (Role): **{selected_role}** (เลือกล็อกอัตโนมัติ)")
                        else:
                            selected_role = st.selectbox("2. เลือกกลุ่มภารกิจ (Role)", ["-- เลือกกลุ่มภารกิจ --"] + filtered_roles)

                    col_u, col_p = st.columns(2)
                    with col_u:
                        new_user = st.text_input("Username (ห้ามซ้ำ)")
                    with col_p:
                        new_pwd = st.text_input("Password", type="password")
                    
                    if st.button("เพิ่มบัญชีผู้ใช้งาน", type="primary"):
                        if selected_main_role == "-- เลือกสายงาน --" or selected_role == "-- เลือกกลุ่มภารกิจ --" or not new_user or not new_pwd:
                            st.warning("⚠️ กรุณากรอกข้อมูลและเลือกระดับชั้นให้ครบถ้วน")
                        elif new_user in df_users['Username'].values:
                            st.error("❌ Username นี้มีในระบบแล้ว กรุณาใช้ชื่ออื่น")
                        else:
                            new_data = pd.DataFrame([{
                                "Username": new_user, 
                                "Password": new_pwd, 
                                "Main_Role": selected_main_role, 
                                "Role": selected_role
                            }])
                            updated_df = pd.concat([df_users, new_data], ignore_index=True)
                            conn.update(spreadsheet=SHEET_URL, worksheet="Users", data=updated_df)
                            st.cache_data.clear() # <- พระเอกของเรา! สั่งล้างความจำทันทีหลังเซฟ เพื่อให้ระบบดึงข้อมูลใหม่
                            st.success(f"✅ บันทึกบัญชี **{new_user}** ({selected_role}) ลง Database สำเร็จ!")
                            st.rerun()

                st.divider()

                # --- ส่วนที่ 2: ตารางจัดการผู้ใช้ปัจจุบัน ---
                st.subheader("🛠️ จัดการบัญชีปัจจุบัน")
                st.info("แก้ไขข้อมูลในตารางได้โดยตรง | ลบบัญชี: กดคลิกที่ช่องหน้าสุดของแถว แล้วกดปุ่ม Delete บนคีย์บอร์ด")
                
                edited_users = st.data_editor(
                    df_users,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "Username": st.column_config.TextColumn("Username", disabled=True), 
                        "Password": st.column_config.TextColumn("Password"),
                        "Main_Role": st.column_config.SelectboxColumn("สายงานหลัก", options=main_roles_list),
                        "Role": st.column_config.SelectboxColumn("กลุ่มภารกิจย่อย", options=all_roles_list)
                    }
                )
                
                if st.button("💾 บันทึกการเปลี่ยนแปลงตาราง (Save Changes)"):
                    edited_users = edited_users.dropna(subset=['Username'])
                    conn.update(spreadsheet=SHEET_URL, worksheet="Users", data=edited_users)
                    st.cache_data.clear() # <- สั่งล้างความจำหลังแก้ไขตารางเสร็จ
                    st.success("✅ อัปเดตข้อมูลผู้ใช้งานลง Google Sheets เรียบร้อยแล้ว!")
                    st.rerun()

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล Database: {e}")
                
    # =========================================================
    # เว้นโครงสำหรับ Role อื่นๆ
    # =========================================================
    elif st.session_state.role == "IC (ผู้บัญชาการ)":
        with my_tabs[1]:
            st.markdown("**หน้าออกข้อสั่งการ:** (พื้นที่เตรียมพัฒนาต่อ...)")
        with my_tabs[2]:
            st.markdown("**หน้าติดตามงาน:** (พื้นที่เตรียมพัฒนาต่อ...)")
            
    else:
        with my_tabs[1]:
            st.markdown(f"**หน้าอัปเดตงาน {st.session_state.role}:** (พื้นที่เตรียมพัฒนาต่อ...)")

if not st.session_state.logged_in:
    login_page()
else:
    main_dashboard()
