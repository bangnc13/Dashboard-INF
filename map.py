import streamlit as st
import re
import json

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="Hệ thống GIS Lưới Điện", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Tối ưu CSS giao diện tràn màn hình
st.markdown("""
    <style>
        .block-container { padding: 0rem !important; max-width: 100% !important; }
        header, footer { visibility: hidden; }
        iframe { width: 100% !important; height: 95vh !important; border: none !important; }
    </style>
""", unsafe_allow_html=True)

# 2. Hàm xử lý đọc file KML dung lượng lớn bằng Regex
@st.cache_data
def parse_all_kml(file_bytes):
    """Trích xuất 100% tọa độ điểm (Point) và đường (LineString) từ dữ liệu KML"""
    points = []
    lines = []
    if not file_bytes:
        return points, lines
    try:
        content = file_bytes.decode('utf-8', errors='ignore')
        
        # Bóc tách tất cả các điểm Point (Cột / Trạm)
        raw_pts = re.findall(r'<Point>.*?<coordinates>\s*([^\s<]+)', content, re.DOTALL)
        for p_str in raw_pts:
            p = p_str.strip().split(',')
            if len(p) >= 2:
                try:
                    points.append([float(p[1]), float(p[0])]) # Lưu dạng [lat, lng]
                except ValueError:
                    continue

        # Bóc tách tất cả các tuyến LineString (Đường dây)
        raw_lines = re.findall(r'<LineString>.*?<coordinates>\s*(.*?)\s*</coordinates>', content, re.DOTALL)
        for l_str in raw_lines:
            path = []
            for pt in l_str.strip().split():
                p = pt.split(',')
                if len(p) >= 2:
                    try:
                        path.append([float(p[1]), float(p[0])])
                    except ValueError:
                        continue
            if len(path) >= 2:
                lines.append(path)

    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu KML: {e}")
    return points, lines

# 3. Thanh điều hướng Sidebar
with st.sidebar:
    st.title("⚡ Quản lý Lưới điện GIS")
    st.markdown("---")
    # Tải nhiều file Cột điện cùng lúc (cot_dien_1, cot_dien_2,...)
    files_cot = st.file_uploader(
        "1. File Cột điện (.kml)", 
        type=['kml'], 
        accept_multiple_files=True,
        help="Giữ Ctrl hoặc dùng chuột quét chọn cùng lúc các file cot_dien_1, cot_dien_2,..."
    )
    file_day = st.file_uploader("2. File Đường dây (.kml)", type=['kml'])
    file_tram = st.file_uploader("3. File Trạm biến áp (.kml)", type=['kml'])

# 4. Xử lý & Gộp dữ liệu tải lên
cot_pts = []
if files_cot:
    for f in files_cot:
        pts, _ = parse_all_kml(f.read())
        cot_pts.extend(pts)

_, day_lines = parse_all_kml(file_day.read()) if file_day else ([], [])
tram_pts, _ = parse_all_kml(file_tram.read()) if file_tram else ([], [])

# Hiển thị thông số đếm dữ liệu
if cot_pts or day_lines or tram_pts:
    st.sidebar.success(f"Đã nạp: {len(cot_pts):,} Cột | {len(day_lines):,} Tuyến | {len(tram_pts):,} Trạm")

# Tính toán vị trí trung tâm tự động
all_pts = cot_pts + tram_pts
if all_pts:
    center_lat = sum(p[0] for p in all_pts) / len(all_pts)
    center_lng = sum(p[1] for p in all_pts) / len(all_pts)
else:
    center_lat, center_lng = 22.675, 106.260

# 5. Mã HTML/JavaScript vẽ bản đồ Leaflet + Street View
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
    <style>
        #map {{ width: 100%; height: 100vh; margin: 0; padding: 0; }}
        body {{ margin: 0; padding: 0; }}
        .leaflet-popup-content {{
            width: 310px !important;
            margin: 8px 12px !important;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        // Khởi tạo bản đồ
        var map = L.map('map').setView([{center_lat}, {center_lng}], 13);

        // Nguồn ảnh bản đồ Google Maps (Lớp Vệ tinh Hybrid & Giao thông)
        var googleHybrid = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}', {{
            maxZoom: 20,
            subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
        }}).addTo(map);

        var googleRoads = L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}', {{
            maxZoom: 20
        }});

        // Hàm tạo cửa sổ nhúng Street View trực tiếp 360 độ
        function getInlineStreetView(lat, lng, title) {{
            var iframeUrl = "https://maps.google.com/maps?q=&layer=c&cbll=" + lat + "," + lng + "&cbp=12,0,0,0,0&panoid=&ie=UTF8&output=svembed";
            return "<div style='font-family: sans-serif;'>" +
                   "<b style='font-size:14px; color:#1a73e8;'>" + title + "</b><br>" +
                   "<span style='font-size:11px; color:#666;'>Tọa độ: " + lat.toFixed(5) + ", " + lng.toFixed(5) + "</span><br>" +
                   "<iframe src='" + iframeUrl + "' width='300' height='200' style='border:1px solid #ccc; border-radius:6px; margin-top:6px;' allowfullscreen></iframe>" +
                   "</div>";
        }}

        // Sự kiện click bất kỳ trên bản đồ để xem phố
        map.on('click', function(e) {{
            var lat = e.latlng.lat;
            var lng = e.latlng.lng;
            L.popup({{maxWidth: 340}})
                .setLatLng(e.latlng)
                .setContent(getInlineStreetView(lat, lng, "📍 Góc nhìn Street View"))
                .openOn(map);
        }});

        // 1. Hiển thị Lớp Đường dây
        var linesData = {json.dumps(day_lines)};
        linesData.forEach(function(path) {{
            L.polyline(path, {{color: '#ff3333', weight: 3, opacity: 0.9}}).addTo(map);
        }});

        // 2. Gom nhóm & Vẽ 100% Cột điện (Gộp từ tất cả các file)
        var cotData = {json.dumps(cot_pts)};
        var cotMarkers = L.markerClusterGroup({{
            chunkedLoading: true,
            maxClusterRadius: 40
        }});

        cotData.forEach(function(pt) {{
            var marker = L.circleMarker(pt, {{
                radius: 3, 
                color: '#0066ff', 
                fillColor: '#0066ff', 
                fillOpacity: 0.8
            }}).bindPopup(getInlineStreetView(pt[0], pt[1], "⚡ Cột điện"), {{maxWidth: 340}});
            cotMarkers.addLayer(marker);
        }});
        map.addLayer(cotMarkers);

        // 3. Hiển thị Lớp Trạm biến áp
        var tramData = {json.dumps(tram_pts)};
        tramData.forEach(function(pt) {{
            L.circleMarker(pt, {{
                radius: 6, 
                color: '#ffffff', 
                weight: 1, 
                fillColor: '#ff4400', 
                fillOpacity: 1
            }}).bindPopup(getInlineStreetView(pt[0], pt[1], "🏭 Trạm biến áp"), {{maxWidth: 340}}).addTo(map);
        }});

        // Bảng chuyển đổi nền bản đồ
        var baseMaps = {{
            "Vệ tinh Google": googleHybrid,
            "Giao thông Google": googleRoads
        }};
        L.control.layers(baseMaps).addTo(map);
    </script>
</body>
</html>
"""

# 6. Hiển thị lên giao diện Streamlit
st.components.v1.html(html_code, height=900)
