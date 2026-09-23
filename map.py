import streamlit as st
import re
import json
import os
import glob

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="Hệ thống GIS Lưới Điện", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Tối ưu CSS giao diện tràn toàn bộ màn hình
st.markdown("""
    <style>
        .block-container { padding: 0rem !important; max-width: 100% !important; }
        header, footer { visibility: hidden; }
        iframe { width: 100% !important; height: 100vh !important; border: none !important; }
    </style>
""", unsafe_allow_html=True)

# 2. Hàm đọc file KML từ đường dẫn tệp
@st.cache_data
def parse_kml_from_path(file_path):
    points = []
    lines = []
    if not os.path.exists(file_path):
        return points, lines
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        raw_pts = re.findall(r'<Point>.*?<coordinates>\s*([^\s<]+)', content, re.DOTALL)
        for p_str in raw_pts:
            p = p_str.strip().split(',')
            if len(p) >= 2:
                try:
                    points.append([float(p[1]), float(p[0])])
                except ValueError:
                    continue

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
        st.error(f"Lỗi đọc file {file_path}: {e}")
    return points, lines

# 3. Tìm & gộp các file KML
cot_pts = []
day_lines = []
tram_pts = []

cot_files = sorted(glob.glob("cot_dien*.kml"))
for f_path in cot_files:
    pts, _ = parse_kml_from_path(f_path)
    cot_pts.extend(pts)

day_files = glob.glob("*day*.kml") + glob.glob("duong_day*.kml")
for f_path in set(day_files):
    _, lines = parse_kml_from_path(f_path)
    day_lines.extend(lines)

tram_files = glob.glob("*tram*.kml") + glob.glob("tram_bien_ap*.kml")
for f_path in set(tram_files):
    pts, _ = parse_kml_from_path(f_path)
    tram_pts.extend(pts)

all_pts = cot_pts + tram_pts
if all_pts:
    center_lat = sum(p[0] for p in all_pts) / len(all_pts)
    center_lng = sum(p[1] for p in all_pts) / len(all_pts)
else:
    center_lat, center_lng = 22.675, 106.260

# 4. Mã HTML/JS TỐI ƯU HIỆU NĂNG - KHÔNG ĐỘ TRỄ
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet-rotate@0.2.8/dist/leaflet-rotate-src.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
    
    <style>
        #map {{ width: 100%; height: 100vh; margin: 0; padding: 0; }}
        body {{ margin: 0; padding: 0; }}
        .leaflet-popup-content {{
            width: 310px !important;
            margin: 8px 12px !important;
        }}
        
        .gps-button, .north-button {{
            background-color: #ffffff;
            border: 2px solid rgba(0,0,0,0.2);
            border-radius: 4px;
            width: 34px;
            height: 34px;
            line-height: 30px;
            text-align: center;
            cursor: pointer;
            font-size: 18px;
            box-shadow: 0 1px 5px rgba(0,0,0,0.4);
            user-select: none;
            margin-bottom: 5px;
        }}
        .gps-button:hover, .north-button:hover {{
            background-color: #f4f4f4;
        }}
        .gps-active {{
            background-color: #e6f2ff !important;
            border-color: #1a73e8 !important;
        }}

        /* Bỏ transition để xoay siêu tốc không trễ độ phân giải */
        .user-heading-icon {{
            transform-origin: 30px 30px;
            will-change: transform;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map', {{
            rotate: true,
            touchRotate: true,
            rotateControl: false,
            bearing: 0
        }}).setView([{center_lat}, {center_lng}], 13);

        var googleHybrid = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}', {{
            maxZoom: 20,
            subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
        }}).addTo(map);

        var googleRoads = L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}', {{
            maxZoom: 20
        }});

        var userMarker = null;
        var userAccuracyCircle = null;
        var watchId = null;
        var isTracking = false;
        
        // Các biến tối ưu hóa tần số xoay (Frame Loop)
        var rawHeading = 0;
        var smoothedHeading = 0;
        var isRendering = false;

        function createHeadingIcon() {{
            var svg = '<svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">' +
                      '<path d="M30 30 L15 3 A 30 30 0 0 1 45 3 Z" fill="#1a73e8" fill-opacity="0.45" stroke="#1a73e8" stroke-width="0.5"/>' +
                      '<circle cx="30" cy="30" r="7" fill="#1a73e8" stroke="#ffffff" stroke-width="2"/>' +
                      '</svg>';
            return L.divIcon({{
                html: '<div id="headingIconElem" class="user-heading-icon">' + svg + '</div>',
                className: '',
                iconSize: [60, 60],
                iconAnchor: [30, 30]
            }});
        }}

        // Vòng lặp render đồng bộ với tần số quét màn hình (60Hz / 120Hz)
        function updateRotationLoop() {{
            if (!isTracking) {{
                isRendering = false;
                return;
            }}

            // Thuật toán làm mượt chống giật rung (Low-pass filter)
            var diff = rawHeading - smoothedHeading;
            if (diff < -180) diff += 360;
            if (diff > 180) diff -= 360;
            
            // Hệ số 0.35 giúp xoay phản hồi tức thì nhưng vẫn mượt
            smoothedHeading += diff * 0.35;
            if (smoothedHeading < 0) smoothedHeading += 360;
            if (smoothedHeading >= 360) smoothedHeading -= 360;

            // Đổi vị trí trực tiếp bằng DOM style biến đổi (Nhanh gấp 10 lần gán lại Icon)
            var iconElem = document.getElementById('headingIconElem');
            if (iconElem) {{
                iconElem.style.transform = 'rotate(' + smoothedHeading + 'deg)';
            }}

            requestAnimationFrame(updateRotationLoop);
        }}

        // Lắng nghe cảm biến la bàn
        function handleOrientation(event) {{
            var heading = null;
            if (event.webkitCompassHeading) {{
                heading = event.webkitCompassHeading;
            }} else if (event.absolute === true || event.type === 'deviceorientationabsolute') {{
                heading = 360 - event.alpha;
            }} else if (event.alpha !== null) {{
                heading = 360 - event.alpha;
            }}

            if (heading !== null) {{
                rawHeading = (heading + 360) % 360;
                if (!isRendering) {{
                    isRendering = true;
                    requestAnimationFrame(updateRotationLoop);
                }}
            }}
        }}

        // Controls
        var customControls = L.control({{position: 'topleft'}});
        customControls.onAdd = function(map) {{
            var container = L.DomUtil.create('div');
            
            var gpsBtn = L.DomUtil.create('div', 'gps-button', container);
            gpsBtn.innerHTML = '🎯';
            gpsBtn.title = 'Bật/Tắt GPS';
            L.DomEvent.disableClickPropagation(gpsBtn);
            gpsBtn.onclick = function() {{
                if (!isTracking) startGPS(gpsBtn);
                else stopGPS(gpsBtn);
            }};

            var northBtn = L.DomUtil.create('div', 'north-button', container);
            northBtn.innerHTML = '🧭';
            northBtn.title = 'Xoay bản đồ lại hướng Bắc';
            L.DomEvent.disableClickPropagation(northBtn);
            northBtn.onclick = function() {{
                map.setBearing(0);
            }};

            return container;
        }};
        customControls.addTo(map);

        function startGPS(btnElement) {{
            if (!navigator.geolocation) {{
                alert("Thiết bị không hỗ trợ GPS.");
                return;
            }}

            if ('ondeviceorientationabsolute' in window) {{
                window.addEventListener('deviceorientationabsolute', handleOrientation, true);
            }} else if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function') {{
                DeviceOrientationEvent.requestPermission()
                    .then(permissionState => {{
                        if (permissionState === 'granted') {{
                            window.addEventListener('deviceorientation', handleOrientation, true);
                        }}
                    }})
                    .catch(console.error);
            }} else {{
                window.addEventListener('deviceorientation', handleOrientation, true);
            }}

            btnElement.classList.add('gps-active');
            isTracking = true;

            watchId = navigator.geolocation.watchPosition(
                function(position) {{
                    var lat = position.coords.latitude;
                    var lng = position.coords.longitude;
                    var accuracy = position.coords.accuracy;

                    if (userMarker) {{
                        userMarker.setLatLng([lat, lng]);
                        userAccuracyCircle.setLatLng([lat, lng]);
                        userAccuracyCircle.setRadius(accuracy);
                    }} else {{
                        userMarker = L.marker([lat, lng], {{
                            icon: createHeadingIcon()
                        }}).addTo(map).bindPopup("<b>📍 Vị trí hiện tại</b><br>Độ chính xác: ±" + Math.round(accuracy) + "m");

                        userAccuracyCircle = L.circle([lat, lng], {{
                            radius: accuracy,
                            color: '#1a73e8',
                            weight: 1,
                            fillColor: '#1a73e8',
                            fillOpacity: 0.12
                        }}).addTo(map);

                        map.setView([lat, lng], 17);
                    }}
                }},
                function(error) {{
                    alert("Lỗi GPS: " + error.message);
                    stopGPS(btnElement);
                }},
                {{
                    enableHighAccuracy: true,
                    maximumAge: 0,
                    timeout: 10000
                }}
            );
        }}

        function stopGPS(btnElement) {{
            if (watchId !== null) {{
                navigator.geolocation.clearWatch(watchId);
                watchId = null;
            }}
            window.removeEventListener('deviceorientationabsolute', handleOrientation, true);
            window.removeEventListener('deviceorientation', handleOrientation, true);
            
            if (userMarker) {{
                map.removeLayer(userMarker);
                map.removeLayer(userAccuracyCircle);
                userMarker = null;
                userAccuracyCircle = null;
            }}
            btnElement.classList.remove('gps-active');
            isTracking = false;
            isRendering = false;
        }}

        // --- BẢN ĐỒ KML & STREET VIEW ---
        function getInlineStreetView(lat, lng, title) {{
            var iframeUrl = "https://maps.google.com/maps?q=&layer=c&cbll=" + lat + "," + lng + "&cbp=12,0,0,0,0&panoid=&ie=UTF8&output=svembed";
            return "<div style='font-family: sans-serif;'>" +
                   "<b style='font-size:14px; color:#1a73e8;'>" + title + "</b><br>" +
                   "<span style='font-size:11px; color:#666;'>Tọa độ: " + lat.toFixed(5) + ", " + lng.toFixed(5) + "</span><br>" +
                   "<iframe src='" + iframeUrl + "' width='300' height='200' style='border:1px solid #ccc; border-radius:6px; margin-top:6px;' allowfullscreen></iframe>" +
                   "</div>";
        }}

        map.on('click', function(e) {{
            var lat = e.latlng.lat;
            var lng = e.latlng.lng;
            L.popup({{maxWidth: 340}})
                .setLatLng(e.latlng)
                .setContent(getInlineStreetView(lat, lng, "📍 Góc nhìn Street View"))
                .openOn(map);
        }});

        // 1. Đường dây
        var linesData = {json.dumps(day_lines)};
        linesData.forEach(function(path) {{
            L.polyline(path, {{color: '#ff3333', weight: 3, opacity: 0.9}}).addTo(map);
        }});

        // 2. Cột điện
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

        // 3. Trạm biến áp
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

        var baseMaps = {{
            "Vệ tinh Google": googleHybrid,
            "Giao thông Google": googleRoads
        }};
        L.control.layers(baseMaps).addTo(map);
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=950)
