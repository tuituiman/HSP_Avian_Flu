import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# ---------------------------------------------------------
# ตั้งค่าหน้าเพจ & URL ฐานข้อมูล
# ---------------------------------------------------------
st.set_page_config(page_title="EOC สคร.1 เชียงใหม่ - ไข้หวัดนก", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1newH4TiteAxJxKnikgI4L8TA1HRfLaXGB6iFFTBvApc/edit?gid=0#gid=0"

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
    
    with my_tabs[0]:
        st.markdown("**หน้าประกาศทั่วไป:** ใช้แสดงสรุปสถานการณ์ให้ทุกคนรับทราบ")
        
    # --- ฟีเจอร์หน้า ADMIN ---
    if st.session_state.role == "Admin":
        with my_tabs[1]:
            st.header("⚙️ ระบบจัดการบัญชีผู้ใช้งาน (User Management)")
            
            try:
                # โหลดข้อมูลทั้ง 2 ชีต
                df_users = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=0)
                df_roles = conn.read(spreadsheet=SHEET_URL, worksheet="Role_Mapping", ttl=0)
                
                if df_users.empty:
                    df_users = pd.DataFrame(columns=["username", "password", "role"])
                
                # เตรียมลิสต์ Role สำหรับให้เลือก
                main_roles_list = df_roles["Main Role"].dropna().unique().tolist()
                all_roles_list = df_roles["Role"].dropna().unique().tolist()

                # --- โซน 1: ฟอร์มเพิ่มผู้ใช้ใหม่ (อัจฉริยะ) ---
                with st.expander("➕ เพิ่มผู้ใช้งานใหม่ (Add New User)", expanded=True):
                    st.markdown("ระบบจะกรอง **กลุ่มภารกิจ (Role)** ตาม **สายงาน (Main Role)** ที่คุณเลือกโดยอัตโนมัติ")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        # ผู้ใช้เลือก Main Role ก่อน (อยู่นอก Form เพื่อให้ dropdown ชั้นที่ 2 เปลี่ยนค่าตามได้ทันที)
                        selected_main_role = st.selectbox("1. เลือกสายงาน (Main Role)", ["กรุณาเลือกสายงาน..."] + main_roles_list)
                    
                    # กรอง Role ย่อยตาม Main Role ที่ถูกเลือก
                    filtered_roles = []
                    if selected_main_role != "กรุณาเลือกสายงาน...":
                        filtered_roles = df_roles[df_roles["Main Role"] == selected_main_role]["Role"].tolist()
                    
                    with c2:
                        selected_role = st.selectbox("2. เลือกกลุ่มภารกิจ (Role)", ["กรุณาเลือกกลุ่มภารกิจ..."] + filtered_roles)

                    # รับค่า Username / Password
                    new_user = st.text_input("Username (ห้ามเว้นว่างและห้ามซ้ำ)")
                    new_pwd = st.text_input("Password", type="password")
                    
                    if st.button("บันทึกผู้ใช้ใหม่ลงฐานข้อมูล"):
                        if selected_role == "กรุณาเลือกกลุ่มภารกิจ..." or not new_user:
                            st.warning("⚠️ กรุณากรอก Username และเลือกกลุ่มภารกิจให้ครบถ้วน")
                        elif new_user in df_users['username'].values:
                            st.error("❌ Username นี้มีในระบบแล้ว กรุณาใช้ชื่ออื่น")
                        else:
                            new_data = pd.DataFrame([{"username": new_user, "password": new_pwd, "role": selected_role}])
                            updated_df = pd.concat([df_users, new_data], ignore_index=True)
                            conn.update(spreadsheet=SHEET_URL, worksheet="Users", data=updated_df)
                            st.success(f"✅ สร้างบัญชี {new_user} ({selected_role}) สำเร็จ!")
                            st.rerun()

                st.divider()

                # --- โซน 2: ตารางจัดการผู้ใช้เดิม ---
                st.subheader("🛠️ แก้ไข/ลบ บัญชีผู้ใช้งานปัจจุบัน")
                st.info("💡 **วิธีใช้งาน:** แก้ไข Password หรือเปลี่ยน Role ได้ในตารางโดยตรง หากต้องการลบให้คลิกซ้ายที่หน้าแถว (ช่องตัวเลข) แล้วกด Delete บนคีย์บอร์ด เสร็จแล้วกดปุ่มบันทึกด้านล่าง")
                
                edited_users = st.data_editor(
                    df_users,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "username": st.column_config.TextColumn("Username", disabled=True), # ล็อกไว้ไม่ให้เปลี่ยนชื่อ User เดิม
                        "password": st.column_config.TextColumn("Password"),
                        "role": st.column_config.SelectboxColumn("Role (กลุ่มภารกิจ)", options=all_roles_list)
                    }
                )
                
                if st.button("💾 บันทึกการแก้ไขตาราง"):
                    edited_users = edited_users.dropna(subset=['username'])
                    conn.update(spreadsheet=SHEET_URL, worksheet="Users", data=edited_users)
                    st.success("✅ อัปเดตข้อมูลผู้ใช้งานลง Google Sheet เรียบร้อยแล้ว!")
                    st.rerun()

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")

    # (โค้ดสำหรับ Role อื่นๆ ยังคงเว้นโครงไว้เหมือนเดิม)
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
