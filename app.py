import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(
    page_title="Dashboard Báo cáo Vận hành POP - Chi nhánh TQG",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS cho giao diện hiện đại, bóng bẩy
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .header-banner {
        background-color: #0f172a;
        color: white;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 20px;
    }
    .status-good {
        background-color: #d1fae5;
        color: #047857;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 12px;
    }
    .status-normal {
        background-color: #f1f5f9;
        color: #334155;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 12px;
    }
    .status-low {
        background-color: #ffe4e6;
        color: #be123c;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Dữ liệu mặc định ban đầu
DEFAULT_KPI_HEADERS = ['26-W35', '26-W36', '26-W37', '26-W38', '26-T9', 'PLAN M1', '+ / - PLAN']

DEFAULT_KPI_ROWS = [
    {"STT": 1, "Chỉ Số KPIs": "Số lượng sự cố (Slg)", "26-W35": "13", "26-W36": "16", "26-W37": "28", "26-W38": "23", "26-T9": "54", "PLAN M1": "50", "+ / - PLAN": "+4"},
    {"STT": 2, "Chỉ Số KPIs": "KHG ảnh hưởng/ sự cố (Slg)", "26-W35": "21.00", "26-W36": "16.00", "26-W37": "17.70", "26-W38": "14.20", "26-T9": "16.80", "PLAN M1": "16", "+ / - PLAN": "+1"},
    {"STT": 3, "Chỉ Số KPIs": "Số lượng KHG ảnh hưởng (Slg)", "26-W35": "276", "26-W36": "255", "26-W37": "495", "26-W38": "326", "26-T9": "326", "PLAN M1": "800", "+ / - PLAN": "-474"},
    {"STT": 4, "Chỉ Số KPIs": "Thời gian XLSC trung bình (phút)", "26-W35": "89", "26-W36": "180", "26-W37": "128", "26-W38": "169", "26-T9": "169", "PLAN M1": "120", "+ / - PLAN": "+49"},
    {"STT": 5, "Chỉ Số KPIs": "Thời gian gián đoạn TB (phút)", "26-W35": "99", "26-W36": "178", "26-W37": "164", "26-W38": "212", "26-T9": "212", "PLAN M1": "170", "+ / - PLAN": "+42"},
    {"STT": 6, "Chỉ Số KPIs": "SAIDI (phút)", "26-W35": "0.79", "26-W36": "1.32", "26-W37": "2.36", "26-W38": "2.01", "26-T9": "2.01", "PLAN M1": "5.0", "+ / - PLAN": "-3.0"},
    {"STT": 7, "Chỉ Số KPIs": "Tỷ lệ KHG ảnh hưởng (%)", "26-W35": "0.80%", "26-W36": "0.74%", "26-W37": "1.44%", "26-W38": "0.95%", "26-T9": "0.95%", "PLAN M1": "3.00%", "+ / - PLAN": "-2.1%"}
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

def process_excel(uploaded_file):
    try:
        xls = pd.ExcelFile(uploaded_file)
        sheet_name = 'BC' if 'BC' in xls.sheet_names else xls.sheet_names[0]
        df_sheet = pd.read_excel(xls, sheet_name=sheet_name, header=None)

        extracted_pops = []

        # Quét từng hàng tìm mã POP dạng TQGP...
        for idx, row in df_sheet.iterrows():
            row_str = row.astype(str).values
            for col_i, val in enumerate(row_str):
                val_clean = str(val).strip().upper()
                if val_clean.startswith('TQGP') and len(val_clean) <= 10:
                    try:
                        # Lấy các giá trị số sau mã POP
                        nums = []
                        for next_col in range(col_i + 1, min(len(row_str), col_i + 8)):
                            v_str = str(row_str[next_col]).replace(',', '').strip()
                            try:
                                v_num = float(v_str)
                                if v_num > 0:
                                    nums.append(v_num)
                            except ValueError:
                                pass

                        if len(nums) >= 2:
                            total_p = max(nums[0], nums[1])
                            used_p = min(nums[0], nums[1])
                            extracted_pops.append({
                                'stt': len(extracted_pops) + 1,
                                'name': val_clean,
                                'total': int(total_p),
                                'used': int(used_p)
                            })
                    except Exception:
                        pass

        if extracted_pops:
            df_new = pd.DataFrame(extracted_pops)
            df_new['free'] = df_new['total'] - df_new['used']
            df_new['rate'] = (df_new['used'] / df_new['total']) * 100
            st.session_state['pop_df'] = df_new
            st.success(f"Đã cập nhật thành công {len(extracted_pops)} trạm POP từ file Excel!")
        else:
            st.warning("Không tìm thấy cấu trúc dữ liệu TQGP hợp lệ trong file Excel tải lên. Sử dụng dữ liệu mặc định.")
    except Exception as e:
        st.error(f"Lỗi khi đọc file Excel: {str(e)}")

st.sidebar.title("⚙️ Điều khiển Dashboard")
uploaded_file = st.sidebar.file_uploader("Tải file Excel báo cáo mới (.xlsx)", type=["xlsx", "xls"])
if uploaded_file is not None:
    if st.sidebar.button("Xử lý File Excel", type="primary"):
        process_excel(uploaded_file)

if st.sidebar.button("Khôi phục Dữ liệu Mặc định"):
    df_init = pd.DataFrame(RAW_POP_DATA)
    df_init['free'] = df_init['total'] - df_init['used']
    df_init['rate'] = (df_init['used'] / df_init['total']) * 100
    st.session_state['pop_df'] = df_init
    st.session_state['kpi_df'] = pd.DataFrame(DEFAULT_KPI_ROWS)
    st.rerun()

# Header Banner
st.markdown("""
<div class="header-banner">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0; font-size: 24px; font-weight: 800;">📈 DASHBOARD PHÒNG KĨ THUẬT - CHI NHÁNH TQG</h1>
            <p style="margin: 5px 0 0 0; color: #94a3b8; font-size: 13px;">Sheet dữ liệu: <b>BC</b> | Tự động phân tích và trực quan hóa chỉ số POP</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

df_pop = st.session_state['pop_df']
total_pops = len(df_pop)
sum_total_ports = df_pop['total'].sum()
sum_used_ports = df_pop['used'].sum()
avg_rate = (sum_used_ports / sum_total_ports * 100) if sum_total_ports > 0 else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="TỔNG SỐ TRẠM POP (TQG)", value=f"{total_pops} POPs", delta="TQGP001 - TQGP038")

with col2:
    st.metric(label="TỈ LỆ KHAI THÁC TB", value=f"{avg_rate:.1f}%", delta=f"{sum_used_ports:,} / {sum_total_ports:,} Port")

with col3:
    st.metric(label="SỰ CỐ T9 (26-T9)", value="54 sự cố", delta="+4 so với Plan (50)", delta_color="inverse")

with col4:
    st.metric(label="CHỈ SỐ SAIDI (26-T9)", value="2.01 phút", delta="-3.0 phút so với Plan (5.0)", delta_color="normal")

st.markdown("---")

st.subheader("📋 Bảng Báo Cáo Chỉ Số KPIs Vận Hành (2026)")
st.dataframe(
    st.session_state['kpi_df'],
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# Top 5 Best và Worst
sorted_df = df_pop.sort_values(by='rate', ascending=False).reset_index(drop=True)
top5_best = sorted_df.head(5)
top5_worst = sorted_df.tail(5).iloc[::-1]

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🏆 Top 5 POP Có Tỉ Lệ Khai Thác Tốt Nhất")
    for idx, row in top5_best.iterrows():
        st.markdown(f"""
        <div style="background-color: white; padding: 10px 15px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <b style="color: #0f172a;">#{idx+1}. {row['name']}</b>
                <div style="font-size: 12px; color: #64748b;">Port: <b>{row['used']:,}</b> / {row['total']:,}</div>
            </div>
            <div style="text-align: right;">
                <span class="status-good">{row['rate']:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.subheader("⚠️ Top 5 POP Có Tỉ Lệ Khai Thác Thấp Nhất")
    for idx, row in top5_worst.iterrows():
        st.markdown(f"""
        <div style="background-color: white; padding: 10px 15px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <b style="color: #0f172a;">#{idx+1}. {row['name']}</b>
                <div style="font-size: 12px; color: #64748b;">Port: <b>{row['used']:,}</b> / {row['total']:,}</div>
            </div>
            <div style="text-align: right;">
                <span class="status-low">{row['rate']:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.subheader("📊 So Sánh Tỉ Lệ Khai Thác POP Top 5 Cao Nhất vs Thấp Nhất (%)")

chart_df = pd.concat([top5_best, top5_worst])
colors = ['#10b981'] * len(top5_best) + ['#f43f5e'] * len(top5_worst)

fig = go.Figure(data=[
    go.Bar(
        x=chart_df['name'],
        y=chart_df['rate'],
        marker_color=colors,
        text=[f"{r:.1f}%" for r in chart_df['rate']],
        textposition='auto'
    )
])

fig.update_layout(
    yaxis=dict(title='Tỉ lệ khai thác (%)', range=[0, 100]),
    xaxis=dict(title='Mã Trạm POP'),
    margin=dict(l=20, r=20, t=30, b=20),
    height=350,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(248,250,252,1)'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader(f"📑 Danh Sách Chi Tiết {len(df_pop)} POP")

# Filter controls
col_search, col_filter, col_export = st.columns([2, 2, 1])

with col_search:
    search_query = st.text_input("🔍 Tìm Mã POP...", placeholder="Nhập tên POP (ví dụ: TQGP001)")

with col_filter:
    status_filter = st.selectbox(
        "🏷️ Lọc theo hiệu suất khai thác",
        ["Tất cả trạng thái", "Tỷ lệ khai hiệu quả (≥55%)", "Bình thường (40% - 54.9%)", "Tỷ lệ khai thác thấp (<40%)"]
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
filtered_df['rate'] = filtered_df['rate'].map('{:.1f}%'.format)

# Format cột cho đẹp
display_df = filtered_df[['stt', 'name', 'total', 'used', 'free', 'rate', 'Trạng Thái']].rename(columns={
    'stt': 'STT',
    'name': 'Mã POP',
    'total': 'Tổng Port',
    'used': 'Port Đã Dùng',
    'free': 'Port Trống',
    'rate': 'Tỉ Lệ Khai Thác (%)'
})

st.dataframe(display_df, use_container_width=True, hide_index=True)

csv_data = display_df.to_csv(index=False).encode('utf-8-sig')

with col_export:
    st.download_button(
        label="📥 Xuất CSV",
        data=csv_data,
        file_name="Bao_Cao_Chi_Tiet_POP_TQG.csv",
        mime="text/csv",
        use_container_width=True
    )
