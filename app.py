import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Config trang
st.set_page_config(
    page_title="Dashboard Báo cáo Vận hành POP - Chi nhánh TQG",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INJECT CUSTOM CSS (ĐÃ TỐI ƯU CHIỀU CAO HEADER) ---
st.markdown("""
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    .stApp {
        background-color: #f8fafc;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }
    
    [data-testid="stSidebar"] {
        display: none;
    }

    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    /* --- GIẢM CHIỀU CAO BANNER HEADER --- */
    div[data-testid="stVerticalBlock"] > div:has(div.custom-header-marker) {
        background-color: #0f172a !important;
        border-radius: 12px;
        padding: 8px 18px !important; /* Giảm padding trên dưới xuống 8px */
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        margin-bottom: 16px;
    }
    
    .header-text-title {
        color: #ffffff !important;
        font-size: 18px; /* Tối ưu lại font size */
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    .header-text-sub {
        color: #94a3b8 !important;
        font-size: 11px;
        margin-top: 2px;
        margin-bottom: 0;
    }

    /* Thu gọn File Uploader */
    div[data-testid="stFileUploader"] {
        margin-bottom: 0px !important;
    }
    div[data-testid="stFileUploader"] section {
        padding: 2px 8px !important; /* Thu nhỏ chiều cao khung upload */
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        min-height: 38px !important;
    }
    div[data-testid="stFileUploader"] section:hover {
        border-color: #3b82f6 !important;
        background-color: #334155 !important;
    }
    div[data-testid="stFileUploader"] section * {
        color: #f8fafc !important;
        font-size: 11px !important;
        font-weight: 500 !important;
    }
    div[data-testid="stFileUploader"] section small {
        display: none !important;
    }

    /* Thu gọn nút Reset */
    div[data-testid="stButton"] > button {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        height: 38px !important; /* Khớp chiều cao với ô upload */
        width: 100% !important;
        padding: 0 !important;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: #3b82f6 !important;
        color: #60a5fa !important;
    }

    /* Stat Cards */
    .stat-card {
        background-color: #ffffff;
        padding: 14px 16px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    .stat-label {
        font-size: 11px;
        font-weight: 700;
        color: #94a3b8;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .stat-value {
        font-size: 22px;
        font-weight: 800;
        color: #0f172a;
        margin-top: 2px;
    }
    .stat-subtext {
        font-size: 11px;
        font-weight: 500;
        margin-top: 2px;
    }
    .icon-box {
        padding: 10px;
        border-radius: 10px;
        font-size: 16px;
    }
    
    .top-item-card {
        background-color: rgba(248, 250, 252, 0.5);
        border: 1px solid rgba(226, 232, 240, 0.7);
        border-radius: 10px;
        padding: 8px 12px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .badge-rank {
        width: 22px;
        height: 22px;
        border-radius: 9999px;
        color: white;
        font-weight: 700;
        font-size: 11px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    div[data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# --- DỮ LIỆU ---
DEFAULT_KPI_ROWS = [
    {"STT": 1, "CHỈ SỐ KPIS": "Số lượng sự cố (Slg)", "26-W35": "13", "26-W36": "16", "26-W37": "28", "26-W38": "23", "26-T9": "54", "PLAN M1": "50", "+ / - PLAN": "+4"},
    {"STT": 2, "CHỈ SỐ KPIS": "KHG ảnh hưởng/ sự cố (Slg)", "26-W35": "21.00", "26-W36": "16.00", "26-W37": "17.70", "26-W38": "14.20", "26-T9": "16.80", "PLAN M1": "16", "+ / - PLAN": "+1"},
    {"STT": 3, "CHỈ SỐ KPIS": "Số lượng KHG ảnh hưởng (Slg)", "26-W35": "276", "26-W36": "255", "26-W37": "495", "26-W38": "326", "26-T9": "326", "PLAN M1": "800", "+ / - PLAN": "-474"},
    {"STT": 4, "CHỈ SỐ KPIS": "Thời gian XLSC trung bình (phút)", "26-W35": "89", "26-W36": "180", "26-W37": "128", "26-W38": "169", "26-T9": "169", "PLAN M1": "120", "+ / - PLAN": "+49"},
    {"STT": 5, "CHỈ SỐ KPIS": "Thời gian gián đoạn TB (phút)", "26-W35": "99", "26-W36": "178", "26-W37": "164", "26-W38": "212", "26-T9": "212", "PLAN M1": "170", "+ / - PLAN": "+42"},
    {"STT": 6, "CHỈ SỐ KPIS": "SAIDI (phút)", "26-W35": "0.79", "26-W36": "1.32", "26-W37": "2.36", "26-W38": "2.01", "26-T9": "2.01", "PLAN M1": "5.0", "+ / - PLAN": "-3.0"},
    {"STT": 7, "CHỈ SỐ KPIS": "Tỷ lệ KHG ảnh hưởng (%)", "26-W35": "0.80%", "26-W36": "0.74%", "26-W37": "1.44%", "26-W38": "0.95%", "26-T9": "0.95%", "PLAN M1": "3.00%", "+ / - PLAN": "-2.1%"}
]

RAW_POP_DATA = [
    {"stt": 1, "name": "TQGP001", "total": 1576, "used": 915},
    {"stt": 2, "name": "TQGP002", "total": 1432, "used": 823},
    {"stt": 3, "name": "TQGP003", "total": 1760, "used": 1051},
    {"stt": 4, "name": "TQGP004", "total": 2672, "used": 1657},
    {"stt": 5, "name": "TQGP005", "total": 2080, "used": 1208},
    {"stt": 6, "name": "TQGP006", "total": 2824, "used": 1855},
    {"stt": 7, "name": "TQGP007", "total": 1712, "used": 1161},
    {"stt": 8, "name": "TQGP008", "total": 2920, "used": 2188},
    {"stt": 9, "name": "TQGP009", "total": 1952, "used": 899},
    {"stt": 10, "name": "TQGP010", "total": 1496, "used": 1078}
]

if 'pop_df' not in st.session_state:
    df_init = pd.DataFrame(RAW_POP_DATA)
    df_init['free'] = df_init['total'] - df_init['used']
    df_init['rate'] = (df_init['used'] / df_init['total']) * 100
    st.session_state['pop_df'] = df_init

if 'kpi_df' not in st.session_state:
    st.session_state['kpi_df'] = pd.DataFrame(DEFAULT_KPI_ROWS)

# --- HEADER BANNER THU GỌN CHIỀU CAO ---
with st.container():
    st.markdown('<div class="custom-header-marker"></div>', unsafe_allow_html=True)
    
    col_title, col_actions = st.columns([2.5, 1.5], vertical_alignment="center")
    
    with col_title:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="
                background: linear-gradient(135deg, #1e3a8a, #2563eb); 
                width: 36px; 
                height: 36px; 
                border-radius: 8px; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                flex-shrink: 0;
            ">
                <i class="fa-solid fa-chart-line" style="font-size: 16px; color: #ffffff;"></i>
            </div>
            <div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <h1 class="header-text-title">DASHBOARD PHÒNG KĨ THUẬT</h1>
                    <span style="
                        background: #1e293b; 
                        color: #94a3b8; 
                        font-size: 10px; 
                        font-weight: 600;
                        padding: 2px 8px; 
                        border-radius: 12px; 
                        border: 1px solid #334155;
                    ">Chi Nhánh TQG</span>
                </div>
                <p class="header-text-sub">
                    
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_actions:
        up_col, reset_col = st.columns([3.5, 1], vertical_alignment="center")
        with up_col:
            uploaded_file = st.file_uploader(
                "Upload Excel", 
                type=["xlsx", "xls"], 
                label_visibility="collapsed"
            )
        with reset_col:
            if st.button("🔄", help="Khôi phục dữ liệu gốc"):
                st.rerun()

# Dữ liệu hiển thị bên dưới
df_pop = st.session_state['pop_df']
total_pops = len(df_pop)
sum_total_ports = df_pop['total'].sum()
sum_used_ports = df_pop['used'].sum()
avg_rate = (sum_used_ports / sum_total_ports * 100) if sum_total_ports > 0 else 0

# Stat cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-card"><div><div class="stat-label">TỔNG SỐ TRẠM POP</div><div class="stat-value">{total_pops}</div><div class="stat-subtext" style="color: #10b981;">TQGP001 - TQGP038</div></div><div class="icon-box" style="background-color: #eff6ff; color: #2563eb;"><i class="fa-solid fa-network-wired"></i></div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card"><div><div class="stat-label">TỈ LỆ KHAI THÁC TB</div><div class="stat-value">{avg_rate:.1f}%</div><div class="stat-subtext" style="color: #64748b;">Đã dùng {sum_used_ports:,} Port</div></div><div class="icon-box" style="background-color: #ecfdf5; color: #059669;"><i class="fa-solid fa-gauge-high"></i></div></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="stat-card"><div><div class="stat-label">SỰ CỐ T9</div><div class="stat-value" style="color: #e11d48;">54</div><div class="stat-subtext" style="color: #e11d48;">↑ +4 so với Plan</div></div><div class="icon-box" style="background-color: #fff1f2; color: #e11d48;"><i class="fa-solid fa-triangle-exclamation"></i></div></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="stat-card"><div><div class="stat-label">CHỈ SỐ SAIDI</div><div class="stat-value" style="color: #059669;">2.01</div><div class="stat-subtext" style="color: #059669;">↓ -3.0 phút so với Plan</div></div><div class="icon-box" style="background-color: #f1f5f9; color: #94a3b8;"><i class="fa-solid fa-clock"></i></div></div>', unsafe_allow_html=True)
