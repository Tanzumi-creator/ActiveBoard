import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import io

# 1. ตั้งค่าหน้าเพจและธีมสี (Navy - Orange)
st.set_page_config(page_title="ระบบติดตามมติการประชุม", layout="wide")

st.markdown("""
    <style>
    .header-text { color: #1B365D; text-align: center; font-weight: bold; }
    .sub-header { color: #F26522; text-align: center; }
    .stDataFrame { border-top: 3px solid #1B365D; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 class='header-text'>สำนักงานคณะกรรมการส่งเสริมวิทยาศาสตร์ วิจัยและนวัตกรรม</h2>", unsafe_allow_html=True)
st.markdown("<h4 class='sub-header'>แดชบอร์ดติดตามความก้าวหน้าผลการดำเนินงานตามมติที่ประชุม</h4>", unsafe_allow_html=True)
st.divider()

# 2. เชื่อมต่อ Google Sheets ผ่าน API
# อย่าลืมเปลี่ยน URL ตรงนี้ให้เป็นไฟล์ของคุณ
SHEET_URL = "https://docs.google.com/spreadsheets/d/1a7BDdWXv-MiPZYLkXPob48VA3ajPImQLxz1cJZNB7vY/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(spreadsheet=SHEET_URL, ttl=300)
    df = df.dropna(how="all")
    
    # 3. ส่วนแสดงผลสรุป (KPI Metrics)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("จำนวนวาระทั้งหมด", len(df))
    with col2:
        finished = len(df[df['สถานะ'] == 'เสร็จสิ้น']) if 'สถานะ' in df.columns else 0
        st.metric("เสร็จสิ้นแล้ว", finished)
    with col3:
        in_progress = len(df[df['สถานะ'] == 'กำลังดำเนินการ']) if 'สถานะ' in df.columns else 0
        st.metric("กำลังดำเนินการ", in_progress)

    st.write("") 

    # 4. ฟิลเตอร์สำหรับค้นหาและกรองข้อมูล
    st.subheader("🔍 ค้นหาและกรองข้อมูล")
    filter_col1, filter_col2 = st.columns(2)
    
    filtered_df = df.copy()
    
    if 'ผู้รับผิดชอบ' in df.columns:
        with filter_col1:
            selected_dept = st.multiselect("กรองตามผู้รับผิดชอบ", options=df['ผู้รับผิดชอบ'].dropna().unique())
            if selected_dept:
                filtered_df = filtered_df[filtered_df['ผู้รับผิดชอบ'].isin(selected_dept)]
                
    if 'สถานะ' in df.columns:
        with filter_col2:
            selected_status = st.multiselect("กรองตามสถานะ", options=df['สถานะ'].dropna().unique())
            if selected_status:
                filtered_df = filtered_df[filtered_df['สถานะ'].isin(selected_status)]

    # 5. แสดงตารางผลลัพธ์
    st.subheader("📋 รายละเอียดผลการดำเนินงานรายวาระ")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    # ---------------------------------------------------------
    # 6. ส่วนเพิ่มเติม: ปุ่มดาวน์โหลดรายงาน
    # ---------------------------------------------------------
    st.write("---")
    st.subheader("📥 ดาวน์โหลดรายงานผลการดำเนินงาน")

    def to_excel(df_to_export):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_to_export.to_excel(writer, index=False, sheet_name='ความก้าวหน้ามติที่ประชุม')
        return output.getvalue()

    @st.cache_data
    def convert_df(df_to_export):
        return df_to_export.to_csv(index=False, encoding='utf-8-sig')

    if not filtered_df.empty:
        excel_file = to_excel(filtered_df)
        csv_file = convert_df(filtered_df)
        
        btn_col1, btn_col2, _ = st.columns([1, 1, 2])
        
        with btn_col1:
            st.download_button(
                label="📊 ดาวน์โหลดไฟล์ Excel",
                data=excel_file,
                file_name="progress_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        with btn_col2:
            st.download_button(
                label="📄 ดาวน์โหลดไฟล์ CSV",
                data=csv_file,
                file_name="progress_report.csv",
                mime="text/csv"
            )
    else:
        st.info("ไม่มีข้อมูลสำหรับดาวน์โหลด กรุณาปรับเงื่อนไขการค้นหาใหม่")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อข้อมูล: {e}")
