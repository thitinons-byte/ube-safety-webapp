import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from src.storage import CSV_COLUMNS, save_report
from src.validation import validate_report

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(
    page_title="UBE Safety Talk",
    page_icon="🦺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Styling (CSS)
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Prompt', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .stApp {
            background: linear-gradient(135deg, #f4f8f5 0%, #e8f2ec 100%);
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d3325 0%, #164e37 100%);
            border-right: none;
            box-shadow: 6px 0 24px rgba(0, 0, 0, 0.12);
        }
        
        [data-testid="stSidebar"] > div:first-child {
            padding: 1.8rem 1.2rem;
        }

        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 0.9rem;
            padding: 0.4rem 0 1rem;
        }

        .sidebar-icon {
            display: grid;
            width: 3.5rem;
            height: 3.5rem;
            place-items: center;
            font-size: 1.8rem;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.25);
            border-radius: 1rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .sidebar-brand h2 {
            margin: 0;
            color: #ffffff;
            font-size: 1.35rem;
            font-weight: 700;
            line-height: 1.2;
        }

        .sidebar-brand span {
            color: #b3dfc6;
            font-size: 0.78rem;
            font-weight: 500;
            letter-spacing: 0.05em;
        }

        .menu-label {
            margin: 0.5rem 0 0.6rem;
            color: #92caa8;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }

        /* Custom Sidebar Buttons */
        [data-testid="stSidebar"] [data-testid="stButton"] {
            margin-bottom: 0.4rem;
        }

        [data-testid="stSidebar"] [data-testid^="stBaseButton-"] {
            min-height: 3.5rem;
            justify-content: flex-start;
            padding: 0.75rem 1.1rem;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 0.85rem;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }

        [data-testid="stSidebar"] [data-testid^="stBaseButton-"] p {
            color: #e3f2e9;
            font-size: 0.98rem;
            font-weight: 500;
        }

        [data-testid="stSidebar"] [data-testid^="stBaseButton-"]:hover {
            background: rgba(255, 255, 255, 0.14);
            border-color: rgba(255, 255, 255, 0.25);
            transform: translateX(4px);
        }

        [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
            background: #ffffff !important;
            border-color: #ffffff !important;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        }

        [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] p {
            color: #0d3325 !important;
            font-weight: 700 !important;
        }

        .sidebar-note {
            padding: 0.85rem 1rem;
            color: #c2e2d0;
            font-size: 0.8rem;
            line-height: 1.5;
            background: rgba(0, 0, 0, 0.18);
            border-radius: 0.75rem;
            border-left: 3px solid #289e68;
        }

        /* Main Header Banner */
        .ube-header {
            padding: 2rem 2.2rem;
            margin-bottom: 1.8rem;
            color: white;
            background: linear-gradient(125deg, #124e36 0%, #1e6d4c 60%, #298d63 100%);
            border-radius: 1.25rem;
            box-shadow: 0 10px 30px rgba(18, 78, 54, 0.18);
        }

        .ube-header h1 {
            margin: 0;
            color: #ffffff;
            font-size: 2.1rem;
            font-weight: 700;
        }

        .ube-header p {
            margin: 0.4rem 0 0;
            color: #d1ebd9;
            font-size: 1rem;
            font-weight: 400;
        }

        /* Content Area Styling */
        .page-kicker {
            color: #1e6d4c;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }

        .page-intro {
            color: #435e52;
            font-size: 1.05rem;
            line-height: 1.7;
            margin: 0.4rem 0 1.2rem;
        }

        /* Custom Placeholder Box */
        .custom-placeholder {
            padding: 1.1rem 1.3rem;
            background-color: #eaf5ee;
            border: 1px solid #c5e4d2;
            border-left: 4px solid #1e6d4c;
            border-radius: 0.75rem;
            color: #1a4d36;
            font-size: 0.95rem;
            line-height: 1.6;
        }

        /* Visual Card Styling */
        .visual-card {
            position: relative;
            overflow: hidden;
            min-height: 185px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 1.2rem 0.9rem;
            background: linear-gradient(145deg, #ffffff 0%, #f0f7f2 100%);
            border: 1px solid #d8e9dd;
            border-radius: 1rem;
            box-shadow: 0 8px 22px rgba(22, 78, 55, 0.07);
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .visual-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 18px 40px rgba(22, 78, 55, 0.12);
        }

        .visual-card::before, .visual-card::after {
            content: "";
            position: absolute;
            border-radius: 50%;
            background: rgba(30, 109, 76, 0.06);
        }

        .visual-card::before { width: 95px; height: 95px; top: -40px; right: -30px; }
        .visual-card::after { width: 70px; height: 70px; bottom: -35px; left: -20px; }

        .visual-icon {
            display: grid;
            place-items: center;
            width: 64px;
            height: 64px;
            margin-bottom: 0.7rem;
            color: #ffffff;
            background: linear-gradient(135deg, #227b55, #124e36);
            border: 4px solid #ffffff;
            border-radius: 1.2rem;
            box-shadow: 0 8px 18px rgba(18, 78, 54, 0.18);
            transform: rotate(-4deg);
            transition: transform 0.3s ease;
        }

        .visual-card:hover .visual-icon {
            transform: rotate(0deg) scale(1.05);
        }

        .visual-icon svg { width: 30px; height: 30px; }

        .visual-title {
            color: #124e36;
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.4;
        }

        .visual-subtitle {
            color: #5c7a6c;
            font-size: 0.78rem;
            line-height: 1.45;
            margin-top: 0.2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. Session State Initialization
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "บันทึก Safety Talk"

def select_page(page_name: str) -> None:
    st.session_state.selected_page = page_name


def reset_dashboard_department() -> None:
    st.session_state.dashboard_department = "ทั้งหมด"

# 4. Sidebar Navigation
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-icon">🦺</div>
            <div>
                <h2>UBE Safety Talk</h2>
                <span>WORKSHOP • DAY 1</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown('<div class="menu-label">เมนูใช้งาน</div>', unsafe_allow_html=True)
    
    menu_items = (
        ("📝  บันทึก Safety Talk", "บันทึก Safety Talk"),
        ("📊  Dashboard", "Dashboard"),
        ("📋  ประวัติรายงาน", "ประวัติรายงาน"),
    )
    
    for button_label, page_name in menu_items:
        st.button(
            button_label,
            key=f"menu_{page_name}",
            type=(
                "primary"
                if st.session_state.selected_page == page_name
                else "secondary"
            ),
            use_container_width=True,
            on_click=select_page,
            args=(page_name,),
        )
        
    st.divider()
    st.markdown(
        """
        <div class="sidebar-note">
            📌 <strong>ระบบสาธิตภายในเครื่อง</strong><br>
            สำหรับการอบรมเท่านั้น
        </div>
        """,
        unsafe_allow_html=True,
    )

# 5. Page Content Configuration
selected_page = st.session_state.selected_page

st.markdown(
    """
    <div class="ube-header">
        <h1>UBE Safety Talk</h1>
        <p>ระบบบันทึกและติดตามกิจกรรม Safety Talk สำหรับ UBE และ UBS</p>
    </div>
    """,
    unsafe_allow_html=True,
)

page_content = {
    "บันทึก Safety Talk": {
        "kicker": "SAFETY TALK RECORD",
        "title": "บันทึก Safety Talk",
        "intro": "เริ่มต้นบันทึกการสื่อสารด้านความปลอดภัยของทีมในที่เดียว",
        "placeholder": "💡 พื้นที่สำหรับกรอกวันที่ บริษัท หน่วยงาน ผู้รายงาน หัวข้อ จำนวนผู้เข้าร่วม และแนบหลักฐาน (จะพัฒนาในขั้นตอนถัดไป)",
        "visual_title": "บันทึกเรื่องราวความปลอดภัย",
        "visual_subtitle": "ทุกการพูดคุย ช่วยสร้างความปลอดภัยร่วมกัน",
        "icon": '<path d="M9 5h10a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h1"/><rect x="7" y="3" width="10" height="4" rx="2"/><path d="M8 12h8M8 16h6"/>',
    },
    "Dashboard": {
        "kicker": "ACTIVITY OVERVIEW",
        "title": "Dashboard",
        "intro": "ดูภาพรวมกิจกรรม Safety Talk ของ UBE และ UBS ได้อย่างเข้าใจง่าย",
        "placeholder": "💡 พื้นที่สำหรับแสดงจำนวนรายงาน จำนวนผู้เข้าร่วม รายงานของ UBE/UBS และกิจกรรมรายเดือน (จะพัฒนาในขั้นตอนถัดไป)",
        "visual_title": "ภาพรวมกิจกรรม",
        "visual_subtitle": "ติดตามการสื่อสารด้านความปลอดภัย",
        "icon": '<path d="M4 20h16M6 17v-5M12 17V5M18 17V9"/><circle cx="6" cy="9" r="1"/><circle cx="18" cy="6" r="1"/>',
    },
    "ประวัติรายงาน": {
        "kicker": "REPORT HISTORY",
        "title": "ประวัติรายงาน",
        "intro": "รวบรวมรายการ Safety Talk เพื่อให้กลับมาตรวจสอบได้สะดวก",
        "placeholder": "💡 พื้นที่สำหรับค้นหาและตรวจสอบรายการ Safety Talk ที่บันทึกไว้ (จะพัฒนาในขั้นตอนถัดไป)",
        "visual_title": "ค้นหาประวัติได้สะดวก",
        "visual_subtitle": "ทบทวนข้อมูลกิจกรรมที่ผ่านมา",
        "icon": '<rect x="4" y="3" width="13" height="17" rx="2"/><path d="M8 8h5M8 12h4"/><circle cx="17" cy="17" r="3"/><path d="m19.2 19.2 2.3 2.3"/>',
    },
}

content = page_content[selected_page]

# 6. Render Main Layout
text_column, visual_column = st.columns([4, 1], gap="large")

with text_column:
    st.markdown(f'<div class="page-kicker">{content["kicker"]}</div>', unsafe_allow_html=True)
    st.header(content["title"])
    st.markdown(f'<p class="page-intro">{content["intro"]}</p>', unsafe_allow_html=True)
    if selected_page == "บันทึก Safety Talk":
        departments_path = Path(__file__).resolve().parent / "config" / "departments.json"
        try:
            with departments_path.open(encoding="utf-8") as file:
                departments = json.load(file)
            if not isinstance(departments, dict) or any(
                not isinstance(departments.get(name), list)
                or not departments[name]
                or not all(isinstance(item, str) and item.strip() for item in departments[name])
                for name in ("UBE", "UBS")
            ):
                raise ValueError("ข้อมูลหน่วยงานไม่ถูกต้อง")
        except (OSError, ValueError):
            st.error("ไม่สามารถโหลดรายชื่อหน่วยงานได้ กรุณาตรวจสอบ config/departments.json")
        else:
            company = st.selectbox("บริษัท *", ("UBE", "UBS"), index=None, placeholder="เลือกบริษัท")
            with st.form("safety_talk_form"):
                department = st.selectbox(
                    "หน่วยงาน *",
                    departments[company] if company else [],
                    index=None,
                    placeholder="เลือกหน่วยงาน" if company else "กรุณาเลือกบริษัทก่อน",
                    key=f"department_{company}",
                    disabled=company is None,
                )
                date_column, participants_column = st.columns(2)
                with date_column:
                    talk_date = st.date_input("วันที่สื่อสาร *", value=None)
                with participants_column:
                    participants = st.number_input(
                        "จำนวนผู้เข้าร่วม (คน) *", min_value=1, value=1, step=1
                    )
                reporter = st.text_input("ชื่อผู้รายงาน *")
                topic = st.text_input("หัวข้อ Safety Talk *")
                notes = st.text_area(
                    "หมายเหตุรายละเอียด (ไม่บังคับ • ส่วนขยายจากโจทย์)",
                    help="เป็นช่องเพิ่มเติมสำหรับ workshop และยังไม่ได้บันทึกลงไฟล์ CSV",
                )
                st.caption("หมายเหตุเป็นส่วนขยายจากโจทย์ และยังไม่ได้บันทึกลงไฟล์ CSV")
                st.caption("ไฟล์แนบสำหรับข้อมูลทดสอบเท่านั้น ห้ามใช้ข้อมูลจริงหรือเอกสารลับ")
                uploads = st.file_uploader(
                    "แนบหลักฐาน (ไม่บังคับ • น้อยกว่า 5 MB ต่อไฟล์)",
                    type=["jpg", "jpeg", "png", "pdf"],
                    accept_multiple_files=True,
                )
                submitted = st.form_submit_button("บันทึกรายงาน")
            if submitted:
                report = {
                    "talk_date": talk_date,
                    "company": company,
                    "department": department,
                    "reporter": reporter,
                    "topic": topic,
                    "participants": participants,
                }
                errors = validate_report(report, departments)
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    try:
                        report_id = save_report(report, uploads)
                    except PermissionError:
                        st.error(
                            "ไม่สามารถเขียนไฟล์รายงานหรือไฟล์แนบได้ "
                            "กรุณาปิด data/reports.csv หากเปิดอยู่ใน Excel หรือโปรแกรมอื่น "
                            "แล้วลองบันทึกอีกครั้ง หากยังไม่ได้ให้ตรวจสิทธิ์เขียนโฟลเดอร์ data"
                        )
                    except (OSError, ValueError) as error:
                        st.error(f"ไม่สามารถบันทึกรายงานได้: {error}")
                    else:
                        st.success(f"บันทึกรายงานสำเร็จ: {report_id}")
    elif selected_page == "Dashboard":
        reports_path = Path(__file__).resolve().parent / "data" / "reports.csv"
        sample_path = Path(__file__).resolve().parent / "data" / "sample_safety_talk.csv"
        try:
            reports = pd.read_csv(reports_path, encoding="utf-8-sig")
            is_demo = reports.empty
            if is_demo:
                reports = pd.read_csv(sample_path, encoding="utf-8-sig")
        except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as error:
            st.error(f"ไม่สามารถอ่านข้อมูล Dashboard ได้: {error}")
        else:
            required_columns = set(CSV_COLUMNS)
            if not required_columns.issubset(reports.columns):
                st.error("ไฟล์ CSV ไม่มีคอลัมน์ที่จำเป็นสำหรับ Dashboard")
            else:
                if is_demo:
                    st.warning("DEMO — กำลังแสดงข้อมูลตัวอย่างจาก sample_safety_talk.csv เนื่องจากยังไม่มีรายงานจริง")
                else:
                    st.caption("ข้อมูลรายงานที่บันทึกใน data/reports.csv")
                date_text = reports["talk_date"].astype("string").str.strip()
                slash_dates = date_text.str.contains("/", regex=False).fillna(False)
                parsed_dates = pd.Series(pd.NaT, index=reports.index, dtype="datetime64[ns]")
                parsed_dates.loc[slash_dates] = pd.to_datetime(
                    date_text.loc[slash_dates], format="%d/%m/%Y", errors="coerce"
                )
                parsed_dates.loc[~slash_dates] = pd.to_datetime(
                    date_text.loc[~slash_dates], errors="coerce"
                )

                filter_row_one = st.columns(2)
                filter_row_two = st.columns(2)
                with filter_row_one[0]:
                    company_filter = st.selectbox(
                        "บริษัท", ("ทั้งหมด", "UBE", "UBS"),
                        key="dashboard_company", on_change=reset_dashboard_department,
                    )
                company_reports = reports
                if company_filter != "ทั้งหมด":
                    company_reports = reports.loc[reports["company"] == company_filter]
                departments = company_reports["department"].dropna().astype(str).str.strip()
                department_options = ("ทั้งหมด", *dict.fromkeys(departments[departments != ""]))
                if st.session_state.get("dashboard_department") not in department_options:
                    st.session_state.dashboard_department = "ทั้งหมด"
                with filter_row_one[1]:
                    department_filter = st.selectbox(
                        "หน่วยงาน", department_options, key="dashboard_department"
                    )
                years = sorted(parsed_dates.dropna().dt.year.unique().tolist())
                with filter_row_two[0]:
                    year_filter = st.selectbox("ปี", ("ทั้งหมด", *years), key="dashboard_year")
                with filter_row_two[1]:
                    month_filter = st.selectbox(
                        "เดือน", ("ทั้งหมด", *range(1, 13)), key="dashboard_month",
                        format_func=lambda value: value if value == "ทั้งหมด" else f"{value:02d}",
                    )

                filtered = company_reports
                if department_filter != "ทั้งหมด":
                    filtered = filtered.loc[filtered["department"] == department_filter]
                if year_filter != "ทั้งหมด":
                    filtered = filtered.loc[parsed_dates.loc[filtered.index].dt.year == year_filter]
                if month_filter != "ทั้งหมด":
                    filtered = filtered.loc[parsed_dates.loc[filtered.index].dt.month == month_filter]

                participant_total = int(
                    pd.to_numeric(filtered["participants"], errors="coerce").fillna(0).sum()
                )
                company_counts = filtered["company"].value_counts()
                first_row = st.columns(2)
                second_row = st.columns(2)
                first_row[0].metric("จำนวนรายงาน Safety Talk", len(filtered))
                first_row[1].metric("จำนวนผู้เข้าร่วมทั้งหมด", participant_total)
                second_row[0].metric("จำนวนรายงาน UBE", int(company_counts.get("UBE", 0)))
                second_row[1].metric("จำนวนรายงาน UBS", int(company_counts.get("UBS", 0)))
                st.subheader("จำนวนกิจกรรม Safety Talk รายเดือน")
                valid_dates = parsed_dates.loc[filtered.index].dropna()
                if valid_dates.empty:
                    st.info("ยังไม่มีวันที่สื่อสารที่ถูกต้องสำหรับแสดงกราฟรายเดือน")
                else:
                    monthly_counts = (
                        valid_dates.dt.to_period("M")
                        .astype(str)
                        .value_counts()
                        .sort_index()
                        .rename_axis("เดือน")
                        .reset_index(name="จำนวนกิจกรรม")
                    )
                    st.bar_chart(monthly_counts, x="เดือน", y="จำนวนกิจกรรม")
                export_data = filtered.loc[:, CSV_COLUMNS].to_csv(index=False).encode("utf-8-sig")
                export_date = datetime.now(ZoneInfo("Asia/Bangkok")).strftime("%Y%m%d")
                st.download_button(
                    "ดาวน์โหลด CSV (DEMO)" if is_demo else "ดาวน์โหลด CSV ที่กรองแล้ว",
                    data=export_data,
                    file_name=f"SafetyTalk_{export_date}.csv",
                    mime="text/csv",
                    disabled=filtered.empty,
                )
    elif selected_page == "ประวัติรายงาน":
        reports_path = Path(__file__).resolve().parent / "data" / "reports.csv"
        try:
            history = pd.read_csv(reports_path, encoding="utf-8-sig")
        except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as error:
            st.error(f"ไม่สามารถอ่านประวัติรายงานได้: {error}")
        else:
            search_columns = {"report_id", "topic", "reporter", "company"}
            if not search_columns.issubset(history.columns):
                st.error("ไฟล์ CSV ไม่มีคอลัมน์ที่จำเป็นสำหรับประวัติรายงาน")
            elif history.empty:
                st.info("ยังไม่มีรายงาน Safety Talk ที่บันทึกไว้ เมื่อบันทึกรายงานแล้วจะเห็นรายการที่นี่")
            else:
                search_column, company_column = st.columns([2, 1])
                with search_column:
                    query = st.text_input("ค้นหารหัสรายงาน หัวข้อ หรือผู้รายงาน").strip()
                with company_column:
                    company_filter = st.selectbox("บริษัท", ("ทั้งหมด", "UBE", "UBS"))

                filtered = history
                if query:
                    matches = pd.Series(False, index=history.index)
                    for column in ("report_id", "topic", "reporter"):
                        matches |= history[column].astype("string").str.contains(
                            query, case=False, regex=False, na=False
                        )
                    filtered = filtered.loc[matches]
                if company_filter != "ทั้งหมด":
                    filtered = filtered.loc[filtered["company"] == company_filter]

                if filtered.empty:
                    st.info("ไม่พบรายงานที่ตรงกับคำค้นหาและบริษัทที่เลือก")
                else:
                    st.caption(f"พบ {len(filtered)} รายงาน")
                    st.dataframe(filtered, hide_index=True, width="stretch")
    else:
        st.markdown(f'<div class="custom-placeholder">{content["placeholder"]}</div>', unsafe_allow_html=True)

with visual_column:
    st.markdown(
        f"""
        <div class="visual-card">
            <div class="visual-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
                     stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"
                     aria-hidden="true">{content["icon"]}</svg>
            </div>
            <div class="visual-title">{content["visual_title"]}</div>
            <div class="visual-subtitle">{content["visual_subtitle"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()
st.caption(
    "สำหรับการอบรมและสาธิตด้วยข้อมูลตัวอย่างเท่านั้น "
    "กรุณาอย่าใช้ข้อมูลส่วนบุคคลจริงหรือเอกสารลับ"
)
