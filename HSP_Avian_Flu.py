import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------
# 1. ตั้งค่าหน้าเพจ
# ---------------------------------------------------------
st.set_page_config(page_title="EOC สคร.1 เชียงใหม่ - ไข้หวัดนก", layout="wide")
st.title("🚨 EOC Command Center: โรคไข้หวัดนก (HSP 2568)")

# URL Google Sheet ของคุณ
SHEET_URL = "https://docs.google.com/spreadsheets/d/1newH4TiteAxJxKnikgI4L8TA1HRfLaXGB6iFFTBvApc/edit?gid=0#gid=0"

# ---------------------------------------------------------
# 2. จำลอง Database ด้วย Session State (เพื่อให้เว็บทำงานได้ทันที)
# ---------------------------------------------------------
if 'commands' not in st.session_state:
    st.session_state.commands = []
if 'tasks' not in st.session_state:
    st.session_state.tasks = {
        "SAT_1": "รอรับคำสั่ง", "JIT_1": "รอรับคำสั่ง", "Log_1": "รอรับคำสั่ง"
    }
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "Watch Mode (ปกติ)"

# ---------------------------------------------------------
# 3. Sidebar - ระบุตัวตน
# ---------------------------------------------------------
st.sidebar.header("👤 เข้าสู่ระบบ")
user_role = st.sidebar.selectbox("กลุ่มภารกิจของคุณ:", 
    ["IC (ผู้บัญชาการ)", "SAT", "JIT", "Logistics", "RC", "อื่นๆ"]
)

# แถบแจ้งเตือนระดับสถานการณ์ปัจจุบัน
st.info(f"สถานการณ์ปัจจุบัน: **{st.session_state.current_mode}**")

# ถ้ามีข้อสั่งการล่าสุด ให้แสดงแถบแจ้งเตือน
if len(st.session_state.commands) > 0:
    st.warning(f"📢 **ข้อสั่งการล่าสุด (จาก IC):** {st.session_state.commands[-1]['msg']} ({st.session_state.commands[-1]['time']})")

# ---------------------------------------------------------
# 4. สร้างโครงสร้าง Tab (แยกหน้าการทำงาน)
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📝 ประเมินสถานการณ์ (Trigger Points)", "📋 กระดานติดตามงาน (Task Board)", "🗣️ ระบบข้อสั่งการ (IC Command)"])

# ==========================================
# TAB 1: ประเมินเกณฑ์การยกระดับ (Trigger Points)
# ==========================================
with tab1:
    st.header("เกณฑ์การเปิดใช้แผนและยกระดับ EOC")
    st.markdown("อ้างอิงจากแผนปฏิบัติการเฉพาะโรค ไข้หวัดนก (HSP)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🟡 เกณฑ์เข้าสู่ Alert Mode")
        a1 = st.checkbox("พบผู้ป่วยโรคไข้หวัดนกในพื้นที่ติดกับเขตสุขภาพที่ 1 หรือ ปท.ที่มีบินตรง")
        a2 = st.checkbox("พบการติดเชื้อยืนยันในปศุสัตว์ในพื้นที่เขต 1 หรือจังหวัดชายแดนติดต่อ")
        a3 = st.checkbox("พบสัตว์ปีกป่วยตายผิดปกติ + มีผู้ป่วยสงสัยในเขต 1")
        
    with col2:
        st.subheader("🔴 เกณฑ์ยกระดับ Response Mode 1-3")
        r1 = st.checkbox("พบผู้ป่วยยืนยันติดเชื้อในประเทศ + แพร่จากสัตว์สู่คน ในเขต 1 (Response 1)")
        r2 = st.checkbox("พบผู้ป่วยกลุ่มก้อน >=2 cluster + แพร่ 4 จังหวัดขึ้นไป (Response 2)")
        r3 = st.checkbox("ระบาดคนสู่คนวงกว้าง + อัตราป่วยตาย > 50% (Response 3)")

    if st.button("ประเมินสถานการณ์ (Update Mode)"):
        if r3:
            st.session_state.current_mode = "Response Mode 3 (วิกฤต)"
        elif r2:
            st.session_state.current_mode = "Response Mode 2"
        elif r1:
            st.session_state.current_mode = "Response Mode 1"
        elif a1 or a2 or a3:
            st.session_state.current_mode = "Alert Mode"
        else:
            st.session_state.current_mode = "Watch Mode (ปกติ)"
        st.rerun()

# ==========================================
# TAB 2: กระดานส่งงาน (Task Board)
# ==========================================
with tab2:
    st.header(f"หน้าต่างส่งงาน: กลุ่ม {user_role}")
    
    if user_role == "SAT":
        st.markdown("**ภารกิจ: วิเคราะห์สถานการณ์และจัดทำ Spot Report**")
        sat_status = st.selectbox("สถานะงาน:", ["รอรับคำสั่ง", "กำลังดำเนินการ ⏳", "เสร็จสิ้น ✅"], index=["รอรับคำสั่ง", "กำลังดำเนินการ ⏳", "เสร็จสิ้น ✅"].index(st.session_state.tasks["SAT_1"]))
        sat_link = st.text_input("แนบลิงก์ผลงาน (เช่น Google Drive / PDF):")
        if st.button("อัปเดตงาน (SAT)"):
            st.session_state.tasks["SAT_1"] = sat_status
            st.success("บันทึกข้อมูลลงฐานข้อมูลเรียบร้อย!")

    elif user_role == "JIT":
        st.markdown("**ภารกิจ: ลงสอบสวนโรคและลงข้อมูล M-EBS**")
        jit_status = st.selectbox("สถานะงาน:", ["รอรับคำสั่ง", "กำลังดำเนินการ ⏳", "เสร็จสิ้น ✅"], index=["รอรับคำสั่ง", "กำลังดำเนินการ ⏳", "เสร็จสิ้น ✅"].index(st.session_state.tasks["JIT_1"]))
        if st.button("อัปเดตงาน (JIT)"):
            st.session_state.tasks["JIT_1"] = jit_status
            st.success("บันทึกข้อมูลลงฐานข้อมูลเรียบร้อย!")
            
    elif user_role == "IC (ผู้บัญชาการ)":
        st.markdown("### ภาพรวมสถานะภารกิจทั้งหมด (Dashboard)")
        st.write(f"- **กลุ่ม SAT:** {st.session_state.tasks['SAT_1']}")
        st.write(f"- **กลุ่ม JIT:** {st.session_state.tasks['JIT_1']}")
        st.write(f"- **กลุ่ม Logistics:** {st.session_state.tasks['Log_1']}")
    else:
        st.info("กรุณาเลือกกลุ่มภารกิจที่เมนูด้านซ้ายเพื่ออัปเดตงาน")

# ==========================================
# TAB 3: ระบบข้อสั่งการ (IC Command)
# ==========================================
with tab3:
    st.header("ประกาศข้อสั่งการ (เฉพาะ IC / Liaison)")
    
    if user_role in ["IC (ผู้บัญชาการ)", "อื่นๆ"]:
        new_cmd = st.text_area("พิมพ์ข้อสั่งการใหม่ที่นี่:")
        if st.button("ส่งข้อสั่งการ"):
            if new_cmd:
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                st.session_state.commands.append({"msg": new_cmd, "time": now})
                st.success("ประกาศข้อสั่งการเรียบร้อย ทุกกลุ่มจะเห็นข้อความนี้ทันที")
                st.rerun()
    else:
        st.warning("หน้านี้สงวนสิทธิ์การแก้ไขสำหรับผู้บัญชาการเหตุการณ์ (IC) และกลุ่ม Liaison")
    
    st.divider()
    st.subheader("ประวัติข้อสั่งการย้อนหลัง")
    for c in reversed(st.session_state.commands):
        st.write(f"▪️ **[{c['time']}]** {c['msg']}")

st.caption("กำลังเชื่อมต่อฐานข้อมูล: " + SHEET_URL)
