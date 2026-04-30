import streamlit as st
import pandas as pd

# ตั้งค่าหน้าเพจ
st.set_page_config(page_title="EOC สคร.1 เชียงใหม่ - แผนไข้หวัดนก", layout="wide")

st.title("🚨 ระบบแจ้งเตือนและแผนปฏิบัติการ EOC กรณีไข้หวัดนก (HSP 2568)")
st.markdown("**สำนักงานป้องกันควบคุมโรคที่ 1 เชียงใหม่**")

# 1. ฐานข้อมูลจำลองจากแผน HSP (สามารถนำไปแยกเป็นไฟล์ Excel/CSV ได้ในอนาคต)
data = {
    "Role": ["SAT", "SAT", "SAT", "SAT", "JIT", "JIT", "JIT", "Logistics", "Logistics"],
    "Mode": ["Alert", "Alert", "Response", "Response", "Alert", "Alert", "Response", "Alert", "Response"],
    "Task": [
        "ติดตามสถานการณ์การระบาด ตรวจสอบเหตุการณ์สัปดาห์ละ 1 ครั้ง",
        "จัดทำข้อเสนอเพื่อยกระดับศูนย์ EOC และขอสนับสนุนกำลังคน",
        "วิเคราะห์สถานการณ์ และจัดทำรายงานเป็น Infographic/Slide นำเสนอวันละ 1 ครั้ง",
        "ประเมินสถานการณ์เพื่อเสนอเปิดศูนย์ EOC",
        "จัดเตรียมความพร้อมทีม (JIT) และฝึกซ้อมการสวม-ถอด PPE",
        "กรณีพบผู้ป่วยสงสัย: ตรวจสอบเหตุการณ์, ส่งแล็บ, ลง M-EBS",
        "สอบสวนโรค ค้นหาผู้ป่วยเพิ่มเติม ค้นหาผู้สัมผัส และควบคุมการระบาด",
        "สำรวจ เตรียมสำรองวัสดุ เวชภัณฑ์ เช่น Oseltamivir และ N95",
        "สนับสนุนพาหนะ/วัสดุอุปกรณ์/เวชภัณฑ์/PPE แก่หน่วยงานปฏิบัติการ"
    ]
}
df = pd.DataFrame(data)

# ข้อมูลเวชภัณฑ์ขั้นต่ำ (Minimum Stock)
stock_data = {
    "รายการ": ["Oseltamivir 75 mg (เม็ด)", "Surgical Mask (ชิ้น)", "Mask N95 (ชิ้น)", "ชุด Cover all (ชุด)"],
    "Alert Mode": ["1,000", "40,000", "1,000", "100"],
    "Response 1": ["2,000", "50,000", "2,000", "200"],
    "Response 2": ["5,000", "100,000", "5,000", "400"]
}
df_stock = pd.DataFrame(stock_data)

# 2. Sidebar สำหรับเลือกสถานการณ์และกลุ่มภารกิจ
st.sidebar.header("เมนูควบคุม (Control Panel)")
selected_mode = st.sidebar.radio("📌 ระดับสถานการณ์ (Mode):", ["Alert", "Response"])
selected_role = st.sidebar.selectbox("👥 กลุ่มภารกิจของคุณ:", ["SAT", "JIT", "Logistics"])

# 3. การแสดงผลเนื้อหาหลัก (Main Content)
st.header(f"📋 ภารกิจของ: กลุ่ม {selected_role}")
st.subheader(f"สถานการณ์ปัจจุบัน: 🔴 {selected_mode} Mode")

# กรองข้อมูลตามที่ผู้ใช้เลือก
filtered_df = df[(df['Role'] == selected_role) & (df['Mode'] == selected_mode)]

# แสดง Checklist
st.markdown("### ภารกิจที่ต้องดำเนินการทันที:")
for index, row in filtered_df.iterrows():
    st.checkbox(row['Task'], key=f"task_{index}")

st.divider()

# 4. แสดงข้อมูลพิเศษตามกลุ่มภารกิจ (เช่น Logistics ให้ดูสต็อกเวชภัณฑ์)
if selected_role == "Logistics":
    st.markdown("### 📦 รายการทรัพยากรและเวชภัณฑ์ที่จำเป็น (Minimum Stock)")
    st.dataframe(df_stock, use_container_width=True)

elif selected_role == "SAT":
    st.info("💡 หมายเหตุ SAT: หากพบผู้ป่วยยืนยันติดเชื้อในประเทศ ให้รีบแจ้ง IC เพื่อยกระดับเป็น Response Mode 1")