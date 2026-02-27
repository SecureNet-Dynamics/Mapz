#!/usr/bin/env python3
"""
Definitive build script for gps_map.html
Verified source boundaries from 'gps_map copy.html' (9881 lines):
  - Image items: lines 209-3522 (0-indexed 208:3522)
  - markersList + markers JS: lines 3551-9878 (0-indexed 3550:9878)
"""

input_file = "/home/sadaqaty/Projects/Mapz-/gps_map copy.html"
output_file = "/home/sadaqaty/Projects/Mapz-/gps_map.html"

with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

assert len(lines) > 9000, f"Source file too short: {len(lines)} lines"

HEADER = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Sakhawat Ali: A Journey of Discovery</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Outfit:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        /* === CORE LAYOUT === */
        :root {
            --bg-dark: #0a0c10;
            --sidebar-bg: rgba(10, 14, 22, 0.99);
            --sidebar-width: 360px;
            --accent-gold: #d4af37;
            --glass-border: rgba(212, 175, 55, 0.2);
            --text-main: #e0e0e0;
            --text-dim: #888;
            --ham-size: 48px;
        }
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html, body {
            height: 100%; width: 100%;
            overflow: hidden;
            background: var(--bg-dark);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            touch-action: manipulation;
        }
        #container {
            display: flex;
            flex-direction: row;
            height: 100vh;
            width: 100vw;
            overflow: hidden;
        }

        /* === SIDEBAR === */
        #sidebar {
            width: var(--sidebar-width);
            min-width: var(--sidebar-width);
            height: 100vh;
            display: flex;
            flex-direction: column;
            background: var(--sidebar-bg);
            border-right: 1px solid var(--glass-border);
            z-index: 1000;  /* must be > Leaflet max (~700) */
            overflow: hidden;
            transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            will-change: transform;
        }

        /* === MAP === */
        #map-container {
            flex: 1;
            height: 100vh;
            min-width: 0;
            position: relative;
        }
        #map {
            width: 100%;
            height: 100%;
        }

        /* === HAMBURGER BUTTON === */
        #ham-btn {
            display: none;
            position: fixed;
            top: 14px;
            left: 14px;
            z-index: 1100;  /* above sidebar and map */
            width: var(--ham-size);
            height: var(--ham-size);
            background: rgba(10, 14, 22, 0.92);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            cursor: pointer;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            gap: 5px;
            padding: 12px;
            backdrop-filter: blur(10px);
            transition: background 0.2s;
        }
        #ham-btn:hover { background: rgba(212,175,55,0.15); }
        #ham-btn span {
            display: block;
            width: 100%;
            height: 2px;
            background: var(--accent-gold);
            border-radius: 2px;
            transition: all 0.3s ease;
            transform-origin: center;
        }
        /* Animated X when open */
        body.sidebar-open #ham-btn span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
        body.sidebar-open #ham-btn span:nth-child(2) { opacity: 0; transform: scaleX(0); }
        body.sidebar-open #ham-btn span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

        /* === MOBILE OVERLAY === */
        #sidebar-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.65);
            z-index: 900;  /* above map, below sidebar */
            backdrop-filter: blur(2px);
            opacity: 0;
            pointer-events: none;  /* CRITICAL: don't block touch/click when hidden */
            transition: opacity 0.35s ease;
        }
        body.sidebar-open #sidebar-overlay {
            opacity: 1;
            pointer-events: auto;  /* allow clicks on overlay to close sidebar */
        }

        /* === SIDEBAR HEADER === */
        .sidebar-header {
            padding: 22px 18px;
            border-bottom: 1px solid var(--glass-border);
            background: linear-gradient(180deg, rgba(212,175,55,0.08) 0%, transparent 100%);
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .sidebar-header-text h1 {
            font-family: 'Outfit', sans-serif;
            font-size: 20px;
            font-weight: 700;
            color: var(--accent-gold);
            letter-spacing: 3px;
            text-transform: uppercase;
        }
        .sidebar-header-text p {
            font-size: 9px;
            color: var(--text-dim);
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-top: 3px;
        }
        /* Close X inside sidebar on mobile */
        #sidebar-close {
            display: none;
            background: none;
            border: none;
            color: var(--text-dim);
            font-size: 20px;
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 6px;
            transition: color 0.2s;
        }
        #sidebar-close:hover { color: var(--accent-gold); }

        /* === SEARCH === */
        .search-wrapper {
            padding: 10px 14px;
            border-bottom: 1px solid var(--glass-border);
            flex-shrink: 0;
        }
        #search {
            width: 100%;
            padding: 9px 13px;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--glass-border);
            border-radius: 8px;
            color: var(--text-main);
            font-size: 13px;
            outline: none;
        }
        #search::placeholder { color: var(--text-dim); }
        #search:focus { border-color: var(--accent-gold); }

        /* === IMAGE LIST === */
        #images-list {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            scrollbar-width: thin;
            scrollbar-color: var(--accent-gold) transparent;
            -webkit-overflow-scrolling: touch;
        }
        .image-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 9px 11px;
            border-radius: 10px;
            border: 1px solid var(--glass-border);
            background: rgba(255,255,255,0.02);
            cursor: pointer;
            transition: border-color 0.2s, background 0.2s, transform 0.2s;
        }
        .image-item:hover, .image-item:active {
            border-color: var(--accent-gold);
            background: rgba(212,175,55,0.06);
            transform: translateX(4px);
        }
        .image-thumb {
            width: 52px; height: 52px;
            border-radius: 7px;
            overflow: hidden;
            border: 1px solid var(--glass-border);
            flex-shrink: 0;
        }
        .image-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
        .image-info { overflow: hidden; }
        .image-info h4 {
            font-family: 'Outfit', sans-serif;
            font-size: 12px;
            color: var(--accent-gold);
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
            margin-bottom: 2px;
        }
        .image-info p {
            font-size: 10px; color: var(--text-dim);
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }

        /* === LEAFLET DARK THEME === */
        .leaflet-container { background: #0a0c10 !important; }
        .leaflet-popup-content-wrapper {
            background: rgba(10,14,22,0.95) !important;
            color: var(--text-main) !important;
            border: 1px solid var(--accent-gold);
            border-radius: 12px !important;
            box-shadow: 0 10px 40px rgba(0,0,0,0.7);
        }
        .leaflet-popup-tip { background: var(--accent-gold) !important; }
        .leaflet-control-zoom a {
            background: rgba(10,14,22,0.9) !important;
            color: var(--accent-gold) !important;
            border-color: var(--glass-border) !important;
        }
        .leaflet-control-attribution {
            background: rgba(10,14,22,0.65) !important;
            color: var(--text-dim) !important;
        }
        .leaflet-control-attribution a { color: var(--accent-gold) !important; }

        /* === LOADING SCREEN === */
        #loader {
            position: fixed; inset: 0;
            background: var(--bg-dark);
            z-index: 9999;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            transition: opacity 0.8s ease;
            pointer-events: none;
        }
        .spinner {
            width: 44px; height: 44px;
            border: 3px solid rgba(212,175,55,0.15);
            border-top-color: var(--accent-gold);
            border-radius: 50%;
            animation: spin 0.9s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        #loader p {
            margin-top: 16px;
            font-family: 'Outfit', sans-serif;
            font-size: 11px;
            color: var(--accent-gold);
            letter-spacing: 3px;
            text-transform: uppercase;
        }

        /* === MOBILE RESPONSIVE === */
        @media (max-width: 768px) {
            #ham-btn { display: flex; }
            #sidebar-close { display: block; }
            #sidebar-overlay { display: block; }
            #sidebar {
                position: fixed;
                top: 0; left: 0;
                height: 100vh;
                width: min(320px, 85vw);
                min-width: 0;
                transform: translateX(-105%);
                box-shadow: 8px 0 40px rgba(0,0,0,0.7);
            }
            body.sidebar-open #sidebar {
                transform: translateX(0);
            }
            #map-container {
                width: 100vw;
            }
            /* Shift zoom controls up to avoid ham button overlap */
            .leaflet-top.leaflet-right { top: 14px; right: 14px; }
        }
    </style>
</head>
<body>
    <!-- Loading Overlay -->
    <div id="loader">
        <div class="spinner"></div>
        <p>Honoring the Journey&hellip;</p>
    </div>

    <!-- Hamburger Button (mobile only) -->
    <button id="ham-btn" aria-label="Open menu" aria-expanded="false">
        <span></span><span></span><span></span>
    </button>

    <!-- Mobile overlay (tap to close) -->
    <div id="sidebar-overlay"></div>

    <div id="container">
        <!-- Sidebar -->
        <div id="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-header-text">
                    <h1>Sakhawat Ali</h1>
                    <p>Digital Legacy &amp; Photographic Journey</p>
                </div>
                <button id="sidebar-close" aria-label="Close menu">&#10005;</button>
            </div>
            <div class="search-wrapper">
                <input type="text" id="search" placeholder="&#128269; Search photos&hellip;" />
            </div>
            <div id="images-list">
"""

MIDDLE = """\
            </div><!-- /#images-list -->
        </div><!-- /#sidebar -->

        <!-- Map -->
        <div id="map-container">
            <div id="map"></div>
        </div>
    </div><!-- /#container -->

    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <script>
        // ── Map bounds (lock to one world copy) ───────────────────
        var WORLD_BOUNDS = L.latLngBounds(L.latLng(-80, -180), L.latLng(80, 180));

        // ── Map init ──────────────────────────────────────────
        var map = L.map('map', {
            zoomControl: false,
            inertia: true,
            inertiaDeceleration: 2400,
            inertiaMaxSpeed: 1500,
            easeLinearity: 0.25,
            maxBounds: WORLD_BOUNDS,
            maxBoundsViscosity: 1.0,
            minZoom: 1,
            worldCopyJump: false
        }).setView([20, 10], 2);

        // Tile layer - no wrapping
        var tileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            subdomains: 'abcd',
            noWrap: true,
            attribution: '&copy; <a href="https://carto.com">CARTO</a>'
        }).addTo(map);

        L.control.zoom({ position: 'topright' }).addTo(map);
        L.control.scale({ position: 'bottomright', imperial: false }).addTo(map);

        // Auto-fit helper: call after container has real size
        function fitToWorld() {
            map.invalidateSize({ animate: false });
            map.fitBounds(WORLD_BOUNDS, { padding: [2, 2], animate: false });
            // Set dynamic minZoom so user can't zoom out further than world-fit
            var curZoom = map.getZoom();
            map.setMinZoom(Math.max(1, Math.floor(curZoom)));
        }

        var markersList = [];
"""

FOOTER = """\
        // ── Search ────────────────────────────────────────────────
        document.getElementById('search').addEventListener('input', function(e) {
            var q = e.target.value.toLowerCase();
            document.querySelectorAll('#images-list .image-item').forEach(function(item) {
                var text = item.textContent.toLowerCase();
                item.style.display = text.includes(q) ? '' : 'none';
            });
        });

        // ── Hamburger / Sidebar toggle ────────────────────────────
        function openSidebar() {
            document.body.classList.add('sidebar-open');
            document.getElementById('ham-btn').setAttribute('aria-expanded', 'true');
            // Prevent body scroll when sidebar is open on mobile
            document.body.style.overflow = 'hidden';
        }
        function closeSidebar() {
            document.body.classList.remove('sidebar-open');
            document.getElementById('ham-btn').setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
        }
        var hamBtn = document.getElementById('ham-btn');
        var sidebarOverlay = document.getElementById('sidebar-overlay');
        var sidebarCloseBtn = document.getElementById('sidebar-close');

        // Use both click and touchend for broadest mobile support
        ['click', 'touchend'].forEach(function(evt) {
            hamBtn.addEventListener(evt, function(e) {
                e.preventDefault();
                e.stopPropagation();
                document.body.classList.contains('sidebar-open') ? closeSidebar() : openSidebar();
            }, { passive: false });
            sidebarOverlay.addEventListener(evt, function(e) {
                e.preventDefault();
                closeSidebar();
            }, { passive: false });
            sidebarCloseBtn.addEventListener(evt, function(e) {
                e.preventDefault();
                closeSidebar();
            }, { passive: false });
        });

        // Close sidebar on mobile when user clicks a map item and map pans
        document.querySelectorAll('#images-list .image-item').forEach(function(item) {
            item.addEventListener('click', function() {
                if (window.innerWidth <= 768) closeSidebar();
            });
        });

        // ── Finalise ──────────────────────────────────────────────
        window.addEventListener('load', function() {
            // Step 1: give the browser time to paint the flex layout, then
            // measure real container size and fit world to it.
            setTimeout(function() {
                fitToWorld();
            }, 300);
            // Step 2: second pass after fonts/tiles settle
            setTimeout(function() {
                fitToWorld();
                var loader = document.getElementById('loader');
                if (loader) {
                    loader.style.opacity = '0';
                    setTimeout(function() { loader.remove(); }, 800);
                }
            }, 800);
        });
        window.addEventListener('resize', function() {
            clearTimeout(window._resizeTimer);
            window._resizeTimer = setTimeout(function() {
                fitToWorld();
                if (window.innerWidth > 768) document.body.classList.remove('sidebar-open');
            }, 250);
        });
    </script>
</body>
</html>
"""

# ── Slice source ──────────────────────────────────────────────────────────────
# Image items: lines 209-3519 (1-indexed) → 208:3519 (0-indexed)
# IMPORTANT: lines 3520-3524 in the original are closing tags + old #map div
# that belong to the original sidebar structure. We exclude them and use our
# own MIDDLE template which provides the correct closing structure.
raw_items_html = "".join(lines[208:3519])

# ── Deduplicate image-item blocks ────────────────────────────────────────────
# The source has every photo listed twice. We split on the opening tag of each
# item, deduplicate by the <h4> filename, and rejoin unique blocks only.
import re as _re

item_blocks = _re.split(r'(?=\s*<div[^>]*class="image-item")', raw_items_html)
seen_names = set()
unique_blocks = []
for block in item_blocks:
    name_match = _re.search(r'<h4>(.*?)</h4>', block)
    if name_match:
        name = name_match.group(1).strip()
        if name in seen_names:
            continue  # skip the duplicate
        seen_names.add(name)
    unique_blocks.append(block)

items_html = "".join(unique_blocks)
print(f"  Unique items after dedup: {len(seen_names)}")

# Marker creation + sidebar click/hover handlers:
# starts at 'var markersList = [];' (line 3551) → index 3550
# ends before the last </script> (line 9879) → use index 9878
markers_js = "".join(lines[3550:9878])

# ── Write output ──────────────────────────────────────────────────────────────
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(HEADER)
    f.write(items_html)
    f.write(MIDDLE)
    f.write(markers_js)
    f.write(FOOTER)

# ── Verify ────────────────────────────────────────────────────────────────────
import os
size = os.path.getsize(output_file)
built_lines = open(output_file, encoding='utf-8', errors='ignore').readlines()
item_count = sum(1 for l in built_lines if 'class="image-item"' in l)
map_line = next((i+1 for i, l in enumerate(built_lines) if 'id="map-container"' in l), None)
container_line = next((i+1 for i, l in enumerate(built_lines) if 'id="container"' in l and '<div' in l), None)
print(f"Output: {output_file}")
print(f"  Size : {size/1024/1024:.2f} MB")
print(f"  Lines: {len(built_lines)}")
print(f"  Items: {item_count}")
print(f"  #container at line: {container_line}")
print(f"  #map-container at line: {map_line}")
print("Done.")
