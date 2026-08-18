import streamlit as st
import pandas as pd
import io

# 1. ตั้งค่าหน้าเพจและธีมสี
st.set_page_config(page_title="ระบบติดตามมติการประชุม", layout="wide")

st.markdown("""
    <style>
    .header-text { color: #1B365D; text-align: center; font-weight: bold; }
    .sub-header { color: #F26522; text-align: center; }
    .stDataFrame { border-top: 3px solid #1B365D; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 class='header-text'>สำนักงานคณะกรรมการส่งเสริมวิทยาศาสตร์ วิจัยและนวัตกรรม</h2>", unsafe_allow_html=True)
st.markdown("<h4 class='sub-header'>ระบบรายงานและติดตามความก้าวหน้าผลการดำเนินงานตามมติที่ประชุมคณะกรรมการอำนวยการ</h4>", unsafe_allow_html=True)
st.divider()

# 2. สร้างโครงสร้างตารางเริ่มต้น (ถ้ายังไม่มีข้อมูล)
if 'board_data' not in st.session_state:
    st.session_state.board_data = pd.DataFrame(
        columns=['ชื่อวาระ', 'มติการประชุม', 'ผู้รับผิดชอบ', 'ผลการดำเนินงาน', 'วันที่ส่งมอบ', 'สถานะ'],
        data=[
            ['วาระที่ 1', 'ข้อสั่งการ...', 'ฝ่าย...', 'รอการรายงาน...', '-', 'รอดำเนินการ']
        ]
    )

st.write("📌 **คำแนะนำ:** คุณสามารถคลิกที่ตารางด้านล่างเพื่อพิมพ์ข้อความแก้ไข เพิ่มแถวใหม่ หรือลบข้อมูลได้ทันที")

# 3. ส่วนกรอกและแก้ไขข้อมูลตรงบนเว็บ (Data Editor)
edited_df = st.data_editor(
    st.session_state.board_data,
    num_rows="dynamic", # อนุญาตให้กดปุ่ม + เพิ่มแถวใหม่ได้
    use_container_width=True,
    column_config={
        "สถานะ": st.column_config.SelectboxColumn(
            "สถานะการดำเนินงาน",
            help="เลือกสถานะ",
            options=["รอดำเนินการ", "กำลังดำเนินการ", "เสร็จสิ้น"],
            required=True
        )
    }
)

# บันทึกข้อมูลที่แก้ไขกลับเข้าไปในระบบ
st.session_state.board_data = edited_df

st.divider()

# 4. ส่วนแสดงผลสรุป (KPI Metrics) ที่อัปเดตตามที่กรอกแบบ Real-time
st.subheader("📊 สรุปภาพรวมการดำเนินงาน")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("จำนวนวาระทั้งหมด", len(edited_df))
with col2:
    finished = len(edited_df[edited_df['สถานะ'] == 'เสร็จสิ้น'])
    st.metric("เสร็จสิ้นแล้ว", finished)
with col3:
    in_progress = len(edited_df[edited_df['สถานะ'] == 'กำลังดำเนินการ'])
    st.metric("กำลังดำเนินการ", in_progress)

# ---------------------------------------------------------
# 5. ส่วนดาวน์โหลดรายงาน
# ---------------------------------------------------------
st.write("---")
st.subheader("📥 ดาวน์โหลดข้อมูลที่กรอกเรียบร้อยแล้ว")

def to_excel(df_to_export):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_to_export.to_excel(writer, index=False, sheet_name='รายงานความก้าวหน้า')
    return output.getvalue()

if not edited_df.empty:
    excel_file = to_excel(edited_df)
    
    st.download_button(
        label="📊 บันทึกและดาวน์โหลดไฟล์ Excel",
        data=excel_file,
        file_name="progress_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
