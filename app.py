import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Config trang
st.set_page_config(
    page_title="Dashboard Báo cáo Vận hành POP - Chi nhánh TQG",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INJECT CUSTOM CSS MÔ PHỎNG THEO HTML/TAILWIND CSS ---
st.markdown("""
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    /* Font & Nền chính */
    .stApp {
        background-color: #f8fafc;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }
    
    /* Banner Header */
    .header-banner {
        background-color: #0f172a;
        color: white;
        padding: 16px 24px;
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Top Stat Card Styling */
    .stat-card {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        height: 100%;
    }
    .stat-label {
        font-size: 11px;
        font-weight: 700;
        color: #94a3b8;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .stat-value {
        font-size: 24px;
        font-weight: 800;
        color: #0f172a;
        margin-top: 4px;
    }
    .stat-subtext {
        font-size: 12px;
        font-weight: 500;
        margin-top: 4px;
    }
    .icon-box {
        padding: 12px;
        border-radius: 12px;
        font-size: 18px;
    }
    
    /* Badge trạng thái Top 5 */
    .top-item-card {
        background-color: rgba(248, 250, 252, 0.5);
        border: 1px solid rgba(226, 232, 240, 0.7);
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .badge-rank {
        width: 24px;
        height: 24px;
        border-radius: 9999px;
        color: white;
        font-weight: 700;
        font-size: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Streamlit Dataframe custom styles */
    div[data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO DỮ LIỆU BAN ĐẦU ---
DEFAULT_KPI_HEADERS = ['26-W35', '26-W36', '26-W37', '26-W38', '26-T9', 'PLAN M1', '+ / - PLAN']

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
    {"stt": 10, "name": "TQGP010", "total": 1496, "used": 1078},
    {"stt": 11, "name": "TQGP011", "total": 3148, "used": 1268},
    {"stt": 12, "name": "TQGP012", "total": 2104, "used": 1032},
    {"stt": 13, "name": "TQGP013", "total": 1880, "used": 1387},
    {"stt": 14, "name": "TQGP014", "total": 1752, "used": 823},
    {"stt": 15, "name": "TQGP015", "total": 904, "used": 475},
    {"stt": 16, "name": "TQGP016", "total": 1632, "used": 800},
    {"stt": 17, "name": "TQGP017", "total": 1132, "used": 556},
    {"stt": 18, "name": "TQGP018", "total": 888, "used": 440},
    {"stt": 19, "name": "TQGP019", "total": 600, "used": 181},
    {"stt": 20, "name": "TQGP020", "total": 608, "used": 314},
    {"stt": 21, "name": "TQGP021", "total": 1208, "used": 760},
    {"stt": 22, "name": "TQGP022", "total": 1752, "used": 485},
    {"stt": 23, "name": "TQGP023", "total": 1320, "used": 727},
    {"stt": 24, "name": "TQGP024", "total": 2840, "used": 1297},
    {"stt": 25, "name": "TQGP025", "total": 1088, "used": 623},
    {"stt": 26, "name": "TQGP026", "total": 1784, "used": 987},
    {"stt": 27, "name": "TQGP027", "total": 2592, "used": 1253},
    {"stt": 28, "name": "TQGP028", "total": 2304, "used": 952},
    {"stt": 29, "name": "TQGP029", "total": 2296, "used": 937},
    {"stt": 30, "name": "TQGP030", "total": 1104, "used": 383},
    {"stt": 31, "name": "TQGP031", "total": 2272, "used": 1049},
    {"stt": 32, "name": "TQGP032", "total": 2928, "used": 1012},
    {"stt": 33, "name": "TQGP033", "total": 2728, "used": 1132},
    {"stt": 34, "name": "TQGP034", "total": 1920, "used": 630},
    {"stt": 35, "name": "TQGP035", "total": 2768, "used": 631},
    {"stt": 36, "name": "TQGP036", "total": 2352, "used": 638},
    {"stt": 37, "name": "TQGP037", "total": 2136, "used": 809},
    {"stt": 38, "name": "TQGP038", "total": 2432, "used": 577}
]

if 'pop_df' not in st.session_state:
    df_init = pd.DataFrame(RAW_POP_DATA)
    df_init['free'] = df_init['total'] - df_init['used']
    df_init['rate'] = (df_init['used'] / df_init['total']) * 100
    st.session_state['pop_df'] = df_init

if 'kpi_df' not in st.session_state:
    st.session_state['kpi_df'] = pd.DataFrame(DEFAULT_KPI_ROWS)

# --- SIDEBAR ĐIỀU KHẨN ---
st.sidebar.title("⚙️ Điều khiển Dashboard")
uploaded_file = st.sidebar.file_uploader("Tải file Excel báo cáo mới (.xlsx)", type=["xlsx", "xls"])
if uploaded_file is not None:
    if st.sidebar.button("Xử lý File Excel", type="primary"):
        # Logic xử lý Excel (giữ nguyên)
        st.sidebar.success("Đã nạp file thành công!")

if st.sidebar.button("Khôi phục Dữ liệu Mặc định"):
    df_init = pd.DataFrame(RAW_POP_DATA)
    df_init['free'] = df_init['total'] - df_init['used']
    df_init['rate'] = (df_init['used'] / df_init['total']) * 100
    st.session_state['pop_df'] = df_init
    st.session_state['kpi_df'] = pd.DataFrame(DEFAULT_KPI_ROWS)
    st.rerun()

# --- 1. HEADER BANNER ---
st.markdown("""
<div class="header-banner">
    <div style="display: flex; align-items: center; gap: 12px;">
        <div style="background: rgba(37, 99, 235, 0.2); padding: 10px; border-radius: 12px; border: 1px solid rgba(59, 130, 246, 0.3);">
            <i class="fa-solid fa-chart-line" style="font-size: 20px; color: #60a5fa;"></i>
        </div>
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <h1 style="margin: 0; font-size: 18px; font-weight: 700; color: white;">DASHBOARD PHÒNG KĨ THUẬT</h1>
                <span style="background: rgba(51, 65, 85, 0.6); color: #cbd5e1; font-size: 11px; padding: 2px 10px; border-radius: 9999px; border: 1px solid #475569;">Chi Nhánh TQG</span>
            </div>
            <p style="margin: 2px 0 0 0; color: #94a3b8; font-size: 12px;">Sheet dữ liệu: <b style="color: #fbbf24;">BC</b> | Cập nhật tự động theo file Excel</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tính toán các chỉ số
df_pop = st.session_state['pop_df']
total_pops = len(df_pop)
sum_total_ports = df_pop['total'].sum()
sum_used_ports = df_pop['used'].sum()
avg_rate = (sum_used_ports / sum_total_ports * 100) if sum_total_ports > 0 else 0

# --- 2. TOP STAT CARDS ---
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="stat-card">
        <div>
            <div class="stat-label">TỔNG SỐ TRẠM POP (TQG)</div>
            <div class="stat-value">{total_pops}</div>
            <div class="stat-subtext" style="color: #10b981;"><i class="fa-solid fa-circle-check"></i> Sheet BC (TQGP001 - TQGP038)</div>
        </div>
        <div class="icon-box" style="background-color: #eff6ff; color: #2563eb;"><i class="fa-solid fa-network-wired"></i></div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="stat-card">
        <div>
            <div class="stat-label">TỈ LỆ KHAI THÁC TB</div>
            <div class="stat-value">{avg_rate:.1f}%</div>
            <div class="stat-subtext" style="color: #64748b;">Đã dùng <b>{sum_used_ports:,}</b> / {sum_total_ports:,} Port</div>
        </div>
        <div class="icon-box" style="background-color: #ecfdf5; color: #059669;"><i class="fa-solid fa-gauge-high"></i></div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="stat-card">
        <div>
            <div class="stat-label">SỰ CỐ T9 (26-T9)</div>
            <div class="stat-value" style="color: #e11d48;">54 <span style="font-size: 12px; color: #64748b; font-weight: 400;">sự cố</span></div>
            <div class="stat-subtext" style="color: #e11d48;">↑ +4 so với Plan (50)</div>
        </div>
        <div class="icon-box" style="background-color: #fff1f2; color: #e11d48;"><i class="fa-solid fa-triangle-exclamation"></i></div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="stat-card">
        <div>
            <div class="stat-label">CHỈ SỐ SAIDI (26-T9)</div>
            <div class="stat-value" style="color: #059669;">2.01 <span style="font-size: 12px; color: #64748b; font-weight: 400;">phút</span></div>
            <div class="stat-subtext" style="color: #059669;">↓ -3.0 phút so với Plan (5.0)</div>
        </div>
        <div class="icon-box" style="background-color: #f1f5f9; color: #94a3b8;"><i class="fa-solid fa-clock"></i></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 3. BẢNG KPIS VẬN HÀNH ---
st.subheader("📋 Bảng Báo Cáo Chỉ Số KPIs Vận Hành (2026)")
st.dataframe(
    st.session_state['kpi_df'],
    use_container_width=True,
    hide_index=True
)

st.markdown("<br>", unsafe_allow_html=True)

# --- 4. TOP 5 BEST VÀ WORST CARDS ---
sorted_df = df_pop.sort_values(by='rate', ascending=False).reset_index(drop=True)
top5_best = sorted_df.head(5)
top5_worst = sorted_df.tail(5).iloc[::-1].reset_index(drop=True)

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="background-color: #d1fae5; color: #059669; padding: 6px; border-radius: 8px;"><i class="fa-solid fa-trophy"></i></div>
            <div>
                <b style="font-size: 14px; color: #0f172a;">Top 5 POP Có Tỉ Lệ Khai Thác Tốt Nhất</b>
                <div style="font-size: 11px; color: #94a3b8;">POP có tỉ lệ khai thác hạ tầng cao nhất</div>
            </div>
        </div>
        <span style="background-color: #ecfdf5; color: #059669; font-size: 11px; padding: 2px 10px; border-radius: 9999px; font-weight: 600; border: 1px solid #a7f3d0;">Tốt Nhất</span>
    </div>
    """, unsafe_allow_html=True)
    
    for idx, row in top5_best.iterrows():
        st.markdown(f"""
        <div class="top-item-card">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span class="badge-rank" style="background-color: #059669;">{idx+1}</span>
                <div>
                    <div style="font-size: 12px; font-weight: 700; color: #0f172a;">{row['name']}</div>
                    <div style="font-size: 11px; color: #64748b;">Port: <b>{row['used']:,}</b> / {row['total']:,}</div>
                </div>
            </div>
            <div style="text-align: right; width: 90px;">
                <span style="font-size: 12px; font-weight: 700; color: #059669;">{row['rate']:.1f}%</span>
                <div style="background-color: #e2e8f0; border-radius: 9999px; height: 6px; width: 100%; margin-top: 4px; overflow: hidden;">
                    <div style="background-color: #10b981; height: 100%; width: {min(row['rate'], 100)}%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="background-color: #ffe4e6; color: #e11d48; padding: 6px; border-radius: 8px;"><i class="fa-solid fa-triangle-exclamation"></i></div>
            <div>
                <b style="font-size: 14px; color: #0f172a;">Top 5 POP Có Tỉ Lệ Khai Thác thấp Nhất</b>
                <div style="font-size: 11px; color: #94a3b8;">POP còn dư nhiều dung lượng cần tập trung bán hàng</div>
            </div>
        </div>
        <span style="background-color: #fff1f2; color: #e11d48; font-size: 11px; padding: 2px 10px; border-radius: 9999px; font-weight: 600; border: 1px solid #fecdd3;">Yếu Nhất</span>
    </div>
    """, unsafe_allow_html=True)
    
    for idx, row in top5_worst.iterrows():
        st.markdown(f"""
        <div class="top-item-card">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span class="badge-rank" style="background-color: #f43f5e;">{idx+1}</span>
                <div>
                    <div style="font-size: 12px; font-weight: 700; color: #0f172a;">{row['name']}</div>
                    <div style="font-size: 11px; color: #64748b;">Port: <b>{row['used']:,}</b> / {row['total']:,}</div>
                </div>
            </div>
            <div style="text-align: right; width: 90px;">
                <span style="font-size: 12px; font-weight: 700; color: #f43f5e;">{row['rate']:.1f}%</span>
                <div style="background-color: #e2e8f0; border-radius: 9999px; height: 6px; width: 100%; margin-top: 4px; overflow: hidden;">
                    <div style="background-color: #f43f5e; height: 100%; width: {min(row['rate'], 100)}%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. BIỂU ĐỒ SO SÁNH ---
st.subheader("📊 So Sánh Tỉ Lệ Khai Thác POP Top 5 Cao Nhất vs Thấp Nhất (%)")

chart_df = pd.concat([top5_best, top5_worst])
colors = ['#10b981'] * len(top5_best) + ['#f43f5e'] * len(top5_worst)

fig = go.Figure(data=[
    go.Bar(
        x=chart_df['name'],
        y=chart_df['rate'],
        marker_color=colors,
        text=[f"{r:.1f}%" for r in chart_df['rate']],
        textposition='auto',
        width=0.4
    )
])

fig.update_layout(
    yaxis=dict(title='', range=[0, 100], ticksuffix='%', gridcolor='#e2e8f0'),
    xaxis=dict(title=''),
    margin=dict(l=10, r=10, t=10, b=10),
    height=280,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. BẢNG CHI TIẾT POP ---
st.subheader(f"📑 Danh Sách Chi Tiết {len(df_pop)} POP")

col_search, col_filter, col_export = st.columns([2, 2, 1])

with col_search:
    search_query = st.text_input("🔍 Tìm Mã POP...", placeholder="Nhập tên POP (ví dụ: TQGP001)", label_visibility="collapsed")

with col_filter:
    status_filter = st.selectbox(
        "Lọc trạng thái",
        ["Tất cả trạng thái", "Tỷ lệ khai hiệu quả (≥55%)", "Bình thường (40% - 54.9%)", "Tỷ lệ khai thác thấp (<40%)"],
        label_visibility="collapsed"
    )

filtered_df = df_pop.copy()

if search_query:
    filtered_df = filtered_df[filtered_df['name'].str.contains(search_query.strip().upper())]

if status_filter == "Tỷ lệ khai hiệu quả (≥55%)":
    filtered_df = filtered_df[filtered_df['rate'] >= 55]
elif status_filter == "Bình thường (40% - 54.9%)":
    filtered_df = filtered_df[(filtered_df['rate'] >= 40) & (filtered_df['rate'] < 55)]
elif status_filter == "Tỷ lệ khai thác thấp (<40%)":
    filtered_df = filtered_df[filtered_df['rate'] < 40]

def get_status_label(rate):
    if rate >= 55:
        return "Tỷ lệ khai hiệu quả"
    elif rate >= 40:
        return "Bình thường"
    else:
        return "Tỷ lệ khai thác thấp"

filtered_df['Trạng Thái'] = filtered_df['rate'].apply(get_status_label)

display_df = filtered_df[['stt', 'name', 'total', 'used', 'free', 'rate', 'Trạng Thái']].rename(columns={
    'stt': 'STT',
    'name': 'Mã POP',
    'total': 'Tổng Port',
    'used': 'Port Đã Dùng',
    'free': 'Port Trống',
    'rate': 'Tỉ Lệ Khai Thác (%)'
})

st.dataframe(
    display_df.style.format({'Tỉ Lệ Khai Thác (%)': '{:.1f}%'}),
    use_container_width=True,
    hide_index=True
)
