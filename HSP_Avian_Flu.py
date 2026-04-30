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
        df_users = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=0)
        df_users.columns = df_users.columns.str.strip() # ป้องกันช่องว่างที่หัวตาราง
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
# 2. หน้า Dashboard หลัก (EOC Action Plan)
# ---------------------------------------------------------
def main_dashboard():
    # --- Sidebar ---
    st.sidebar.header("👤 ข้อมูลผู้ใช้งาน")
    st.sidebar.write(f"**Username:** {st.session_state.username}")
    st.sidebar.write(f"**สายงาน (Main Role):** {st.session_state.main_role}")
    st.sidebar.write(f"**กลุ่มภารกิจ (Role):** {st.session_state.role}")
    
    if st.sidebar.button("🚪 ออกจากระบบ (Logout)"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.main_role = ""
        st.rerun()

    st.title("🚨 EOC Action Plan: กรณีไข้หวัดนก (HSP 2568)")
    
    # --- สถานะ EOC ---
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

    # --- กระดาน Tab ---
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
    # ฟีเจอร์หน้า ADMIN (จัดการ User)
    # =========================================================
    if st.session_state.role == "Admin":
        with my_tabs[1]:
            st.header("⚙️ ระบบจัดการบัญชีผู้ใช้งาน (User Management)")
            
            try:
                # โหลดข้อมูล
                df_users = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=0)
                df_roles = conn.read(spreadsheet=SHEET_URL, worksheet="Role_Mapping", ttl=0)
                
                # บังคับชื่อหัวคอลัมน์ให้ปลอดภัยจากการเคาะ Spacebar
                df_users.columns = df_users.columns.str.strip()
                df_roles.columns = ["Main_Role", "Role"] # บังคับเปลี่ยนชื่อคอลัมน์ให้อ่านง่าย
                
                if df_users.empty:
                    df_users = pd.DataFrame(columns=["Username", "Password", "Main_Role", "Role"])
                
                # ลิสต์สำหรับทำ Dropdown
                main_roles_list = df_roles["Main_Role"].dropna().unique().tolist()
                all_roles_list = df_roles["Role"].dropna().unique().tolist()

                # --- ส่วนที่ 1: เพิ่มผู้ใช้ใหม่ ---
                with st.expander("➕ เพิ่มผู้ใช้งานใหม่ (Add New User)", expanded=True):
                    st.markdown("ระบบจะดึงกลุ่มภารกิจจากชีต `Role_Mapping` มาให้เลือกโดยอัตโนมัติ")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        selected_main_role = st.selectbox("1. เลือกสายงาน (Main_Role)", ["-- เลือกสายงาน --"] + main_roles_list)
                    
                    # กรอง Role ตาม Main_Role
                    filtered_roles = []
                    if selected_main_role != "-- เลือกสายงาน --":
                        filtered_roles = df_roles[df_roles["Main_Role"] == selected_main_role]["Role"].tolist()
                    
                    with c2:
                        selected_role = st.selectbox("2. เลือกกลุ่มภารกิจ (Role)", ["-- เลือกกลุ่มภารกิจ --"] + filtered_roles)

                    new_user = st.text_input("Username (ห้ามซ้ำ)")
                    new_pwd = st.text_input("Password", type="password")
                    
                    if st.button("เพิ่มบัญชีผู้ใช้งาน", type="primary"):
                        if selected_role == "-- เลือกกลุ่มภารกิจ --" or not new_user:
                            st.warning("⚠️ กรุณากรอก Username และเลือกข้อมูลให้ครบถ้วน")
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
                            st.success(f"✅ บันทึกข้อมูลบัญชี **{new_user}** สำเร็จ!")
                            st.rerun()

                st.divider()

                # --- ส่วนที่ 2: ตารางแก้ไข/ลบ ผู้ใช้ปัจจุบัน ---
                st.subheader("🛠️ จัดการบัญชีปัจจุบัน")
                st.info("แก้ไขรหัสผ่านและกลุ่มภารกิจได้โดยตรงในตาราง หากต้องการลบบัญชี ให้คลิกเลือกที่หน้าแถวแล้วกดปุ่ม **Delete** หรือ **Backspace** บนคีย์บอร์ด")
                
                edited_users = st.data_editor(
                    df_users,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "Username": st.column_config.TextColumn("Username", disabled=True), # ไม่อนุญาตให้แก้ Username ป้องกัน Database พัง
                        "Password": st.column_config.TextColumn("Password"),
                        "Main_Role": st.column_config.SelectboxColumn("สายงานหลัก", options=main_roles_list),
                        "Role": st.column_config.SelectboxColumn("กลุ่มภารกิจย่อย", options=all_roles_list)
                    }
                )
                
                if st.button("💾 บันทึกการเปลี่ยนแปลง (Save Changes)"):
                    edited_users = edited_users.dropna(subset=['Username']) # ลบแถวว่างทิ้ง
                    conn.update(spreadsheet=SHEET_URL, worksheet="Users", data=edited_users)
                    st.success("✅ อัปเดตข้อมูลผู้ใช้งานลง Google Sheets เรียบร้อยแล้ว!")
                    st.rerun()

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
                
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

# ---------------------------------------------------------
# ควบคุม Flow หน้าจอ
# ---------------------------------------------------------
if not st.session_state.logged_in:
    login_page()
else:
    main_dashboard()
