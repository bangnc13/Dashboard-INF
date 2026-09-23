import streamlit as st
import re
import json

st.set_page_config(page_title="Hệ thống GIS Lưới Điện", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        .block-container { padding: 0rem !important; max-width: 100% !important; }
        header, footer { visibility: hidden; }
        iframe { width: 100% !important; height: 95vh !important; border: none !important; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def parse_all_kml(file_bytes):
    """Trích xuất 100% toàn bộ điểm và đường dây từ file KML"""
    points = []
    lines = []
    if not file_bytes:
        return points, lines
    try:
        content = file_bytes.decode('utf-8', errors='ignore')
        
        # 1. Đọc TOÀN BỘ các điểm Point
        raw_pts = re.findall(r'<Point>.*?<coordinates>\s*([^\s<]+)', content, re.DOTALL)
        for p_str in raw_pts:
            p = p_str.strip().split(',')
            if len(p) >= 2:
                try:
                    points.append([float(p[1]), float(p[0])]) # [lat, lng]
                except ValueError:
                    continue

        # 2. Đọc TOÀN BỘ các tuyến LineString
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

# Sidebar Tải file
with st.sidebar:
    st.title("⚡ Quản lý Lưới điện GIS")
    st.markdown("---")
    file_cot = st.file_uploader("1. File Cột điện (.kml)", type=['kml'])
    file_day = st.file_uploader("2. File Đường dây (.kml)", type=['kml'])
    file_tram = st.file_uploader("3. File Trạm biến áp (.kml)", type=['kml'])

cot_pts, _ = parse_all_kml(file_cot.read()) if file_cot else ([], [])
_, day_lines = parse_all_kml(file_day.read()) if file_day else ([], [])
tram_pts, _ = parse_all_kml(file_tram.read()) if file_tram else ([], [])

if cot_pts or day_lines or tram_pts:
    st.sidebar.success(f"Đã nạp: {len(cot_pts):,} Cột | {len(day_lines):,} Tuyến | {len(tram_pts):,} Trạm")

all_pts = cot_pts + tram_pts
if all_pts:
    center_lat = sum(p[0] for p in all_pts) / len(all_pts)
    center_lng = sum(p[1] for p in all_pts) / len(all_pts)
else:
    center_lat, center_lng = 22.675, 106.260

# Template HTML kết hợp MarkerCluster & Google Street View
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
        .streetview-btn {{
            display: inline-block;
            padding: 6px 12px;
            background-color: #1a73e8;
            color: white !important;
            text-decoration: none;
            border-radius: 4px;
            font-family: sans-serif;
            font-size: 13px;
            font-weight: bold;
            margin-top: 5px;
        }}
        .streetview-btn:hover {{
            background-color: #1557b0;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([{center_lat}, {center_lng}], 13);

        // Nguồn Vệ tinh Google Hybrid
        var googleHybrid = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}', {{
            maxZoom: 20,
            subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
        }}).addTo(map);

        var googleRoads = L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}', {{
            maxZoom: 20
        }});

        // Hàm tạo liên kết Google Street View
        function getStreetViewPopup(lat, lng, title) {{
            var svUrl = "https://www.google.com/maps?q=&layer=c&cbll=" + lat + "," + lng;
            return "<b>" + title + "</b><br>Tọa độ: " + lat.toFixed(5) + ", " + lng.toFixed(5) + "<br>" +
                   "<a href='" + svUrl + "' target='_blank' class='streetview-btn'>📷 Xem Street View (Xem phố)</a>";
        }}

        // Click bất kỳ trên bản đồ để xem phố tại điểm đó
        map.on('click', function(e) {{
            var lat = e.latlng.lat;
            var lng = e.latlng.lng;
            L.popup()
                .setLatLng(e.latlng)
                .setContent(getStreetViewPopup(lat, lng, "Vị trí đã chọn"))
                .openOn(map);
        }});

        // 1. Vẽ Đường dây
        var linesData = {json.dumps(day_lines)};
        linesData.forEach(function(path) {{
            L.polyline(path, {{color: '#ff3333', weight: 3, opacity: 0.9}}).addTo(map);
        }});

        // 2. Gom nhóm & Vẽ Cột điện
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
            }}).bindPopup(getStreetViewPopup(pt[0], pt[1], "Cột điện"));
            cotMarkers.addLayer(marker);
        }});
        map.addLayer(cotMarkers);

        // 3. Vẽ Trạm biến áp
        var tramData = {json.dumps(tram_pts)};
        tramData.forEach(function(pt) {{
            L.circleMarker(pt, {{
                radius: 6, 
                color: '#ffffff', 
                weight: 1, 
                fillColor: '#ff4400', 
                fillOpacity: 1
            }}).bindPopup(getStreetViewPopup(pt[0], pt[1], "Trạm biến áp")).addTo(map);
        }});

        // Điều khiển lớp bản đồ
        var baseMaps = {{
            "Vệ tinh Google": googleHybrid,
            "Giao thông Google": googleRoads
        }};
        L.control.layers(baseMaps).addTo(map);
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=900)