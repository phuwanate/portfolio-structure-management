import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import pandas as pd

API = "http://localhost:8000"

st.title("📊 Portfolio Structure Overview")

ports = requests.get(f"{API}/ports").json()
cashflow = {cf["type"]: cf["amount"] for cf in requests.get(f"{API}/cashflow").json()}
num_ports = len(ports)

if num_ports == 0:
    st.info("ยังไม่มี Port — ไปเพิ่มที่หน้า Manage Ports")
else:
    # ===== TOP: Dashboard Summary (compact) =====
    st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1rem; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem; }
    [data-testid="stMetric"] { padding-bottom: 0; margin-bottom: -1rem; }
    </style>
    """, unsafe_allow_html=True)

    total_invested = sum(p["invested"] for p in ports)
    total_profit = sum(p["profit"] for p in ports)
    cash_amt = cashflow.get("cash", 0)
    profit_amt = cashflow.get("profit", 0)
    total_assets = cash_amt + profit_amt + total_invested + total_profit

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("💰 Cash", f"{cash_amt:,.2f} ฿")
    m2.metric("📈 CF Profit", f"{profit_amt:,.2f} ฿")
    m3.metric("💼 Total Invested", f"{total_invested:,.2f} ฿")
    m4.metric("📊 Total Port Profit", f"{total_profit:,.2f} ฿")
    m5.metric("🏦 Total Assets", f"{total_assets:,.2f} ฿")

    st.divider()

    col_left, col_right = st.columns([3, 2])

    # ===== LEFT: Structure Diagram =====
    with col_left:
        box_w, box_h, gap = 120, 60, 20
        total_ports_w = num_ports * box_w + (num_ports - 1) * gap
        svg_w = total_ports_w + 60
        svg_h = 380
        start_x = 30
        cash_y = svg_h - 50
        profit_y = 20
        port_y = 160

        svg = f'<svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" '
        svg += 'xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">'
        svg += '''<defs>
          <filter id="glow-blue" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="4" result="blur"/>
            <feFlood flood-color="#2196F3" flood-opacity="0.4"/>
            <feComposite in2="blur" operator="in"/>
            <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <filter id="glow-green" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="4" result="blur"/>
            <feFlood flood-color="#4BC0C0" flood-opacity="0.4"/>
            <feComposite in2="blur" operator="in"/>
            <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <marker id="ah-white" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="white"/></marker>
          <marker id="ah-green" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#4CAF50"/></marker>
          <marker id="ah-orange" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#FF9800"/></marker>
        </defs>'''
        svg += f'''
        <rect x="{start_x}" y="{profit_y}" width="{total_ports_w}" height="36" rx="6"
              fill="#0d1b3e" stroke="#2196F3" stroke-width="2" filter="url(#glow-blue)"/>
        <text x="{start_x + total_ports_w/2}" y="{profit_y + 23}" text-anchor="middle"
              fill="#64B5F6" font-size="13" font-weight="bold">Cash Flow (Profit)</text>
        <rect x="{start_x}" y="{cash_y}" width="{total_ports_w}" height="36" rx="6"
              fill="#0a2e1a" stroke="#4BC0C0" stroke-width="2" filter="url(#glow-green)"/>
        <text x="{start_x + total_ports_w/2}" y="{cash_y + 23}" text-anchor="middle"
              fill="#4BC0C0" font-size="13" font-weight="bold">Cash</text>'''

        for i, port in enumerate(ports):
            px = start_x + i * (box_w + gap)
            cx = px + box_w / 2
            svg += f'''
            <rect x="{px}" y="{port_y}" width="{box_w}" height="{box_h}" rx="8"
                  fill="#1a1a2e" stroke="#555" stroke-width="1.5"/>
            <text x="{cx}" y="{port_y + box_h/2 + 5}" text-anchor="middle"
                  fill="white" font-size="12" font-weight="bold">{port["name"]}</text>'''
            if port.get("arrow_white"):
                x = cx - 15
                svg += f'<line x1="{x}" y1="{cash_y}" x2="{x}" y2="{port_y + box_h}" stroke="white" stroke-width="2" marker-end="url(#ah-white)"/>'
            if port.get("arrow_green"):
                x = cx
                svg += f'<line x1="{x}" y1="{profit_y + 36}" x2="{x}" y2="{port_y}" stroke="#4CAF50" stroke-width="2" marker-end="url(#ah-green)"/>'
            if port.get("arrow_orange"):
                x = cx + 15
                svg += f'<line x1="{x}" y1="{port_y}" x2="{x}" y2="{profit_y + 36}" stroke="#FF9800" stroke-width="2" marker-end="url(#ah-orange)"/>'

        svg += '</svg>'
        diagram_html = f'''
        <div style="display:flex; justify-content:center; background:#0e1117; padding:15px; border-radius:10px;">
            {svg}
        </div>'''
        components.html(diagram_html, height=svg_h + 40, scrolling=False)

    # ===== RIGHT: Pie Chart =====
    with col_right:
        total_invested = sum(p["invested"] for p in ports)
        colors = ["#36A2EB","#4BC0C0","#9966FF","#FF9F40","#FFCE56",
                  "#FF6384","#7BC8A4","#C9CBCF","#E7E9ED","#F7464A"]
        if total_invested == 0:
            st.info("ยังไม่มีเงินลงทุน")
        else:
            pie_data = []
            for i, port in enumerate(ports):
                if port["invested"] <= 0:
                    continue
                pct = port["invested"] / total_invested * 100
                pie_data.append({"name": port["name"], "pct": round(pct, 1),
                                 "invested": port["invested"], "color": colors[i % len(colors)]})
            pie_json = json.dumps(pie_data)
            pie_html = f'''
            <div style="background:#0e1117; padding:15px; border-radius:10px; text-align:center;">
                <div style="color:#64B5F6; font-size:14px; font-weight:bold; margin-bottom:10px; letter-spacing:1px;">
                    Investment Allocation
                </div>
                <div style="position:relative; display:inline-block;">
                    <canvas id="pieChart" width="300" height="300"></canvas>
                    <div id="tooltip" style="display:none; position:absolute; background:rgba(13,27,62,0.95);
                        color:#64B5F6; padding:8px 14px; border-radius:8px; font-size:13px; border:1px solid #2196F3;
                        pointer-events:none; white-space:nowrap; z-index:10; backdrop-filter:blur(4px);"></div>
                </div>
                <div id="legend" style="margin-top:10px; text-align:left; padding:0 10px;"></div>
            </div>
            <script>
            const data = {pie_json};
            const canvas = document.getElementById('pieChart');
            const ctx = canvas.getContext('2d');
            const tooltip = document.getElementById('tooltip');
            const legend = document.getElementById('legend');
            const cx = 150, cy = 150, r = 110;
            const slices = [];
            let startAngle = -Math.PI / 2;
            const MIN_ANGLE = 0.06;
            let rawAngles = data.map(d => d.pct / 100 * 2 * Math.PI);
            let extraNeeded = rawAngles.reduce((sum, a) => sum + (a > 0 && a < MIN_ANGLE ? MIN_ANGLE - a : 0), 0);
            let largeTotal = rawAngles.reduce((sum, a) => sum + (a >= MIN_ANGLE ? a : 0), 0);
            let displayAngles = rawAngles.map(a => {{
                if (a <= 0) return 0; if (a < MIN_ANGLE) return MIN_ANGLE;
                return a - (extraNeeded * a / largeTotal);
            }});
            data.forEach((d, i) => {{
                const angle = displayAngles[i]; if (angle <= 0) return;
                slices.push({{ ...d, startAngle, endAngle: startAngle + angle }}); startAngle += angle;
            }});
            function drawPie(h) {{
                ctx.clearRect(0, 0, 300, 300);
                // Outer glow ring
                ctx.beginPath();
                ctx.arc(cx, cy, r + 8, 0, Math.PI * 2);
                ctx.strokeStyle = 'rgba(33,150,243,0.15)';
                ctx.lineWidth = 3;
                ctx.stroke();
                slices.forEach((s, i) => {{
                    const isHover = i === h;
                    const offset = isHover ? 6 : 0;
                    const midAngle = (s.startAngle + s.endAngle) / 2;
                    const ox = Math.cos(midAngle) * offset;
                    const oy = Math.sin(midAngle) * offset;
                    ctx.beginPath();
                    ctx.moveTo(cx + ox, cy + oy);
                    ctx.arc(cx + ox, cy + oy, r, s.startAngle, s.endAngle);
                    ctx.closePath();
                    ctx.fillStyle = s.color;
                    ctx.fill();
                    ctx.strokeStyle = '#1a1a2e';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                    if (isHover) {{
                        ctx.save();
                        ctx.shadowColor = s.color;
                        ctx.shadowBlur = 15;
                        ctx.beginPath();
                        ctx.moveTo(cx + ox, cy + oy);
                        ctx.arc(cx + ox, cy + oy, r, s.startAngle, s.endAngle);
                        ctx.closePath();
                        ctx.fillStyle = s.color;
                        ctx.fill();
                        ctx.restore();
                    }}
                }});
                // Center circle for donut effect
                ctx.beginPath();
                ctx.arc(cx, cy, r * 0.45, 0, Math.PI * 2);
                ctx.fillStyle = '#0e1117';
                ctx.fill();
                ctx.strokeStyle = 'rgba(33,150,243,0.2)';
                ctx.lineWidth = 1.5;
                ctx.stroke();
            }}
            drawPie(-1);
            let lh = '<div style="display:flex;flex-wrap:wrap;gap:6px 20px;">';
            data.forEach(d => {{ lh += `<div style="display:flex;align-items:center;gap:5px;">
                <span style="width:10px;height:10px;border-radius:50%;background:${{d.color}};display:inline-block;
                       box-shadow:0 0 4px ${{d.color}};"></span>
                <span style="color:#8899aa;font-size:11px;">${{d.name}}</span></div>`; }});
            legend.innerHTML = lh + '</div>';
            canvas.addEventListener('mousemove', (e) => {{
                const rect = canvas.getBoundingClientRect();
                const mx = e.clientX - rect.left, my = e.clientY - rect.top;
                const dx = mx - cx, dy = my - cy, dist = Math.sqrt(dx*dx + dy*dy);
                let angle = Math.atan2(dy, dx); if (angle < -Math.PI/2) angle += 2*Math.PI;
                let f = -1;
                if (dist <= r + 6 && dist > r * 0.45) {{ for (let i = 0; i < slices.length; i++) {{
                    if (angle >= slices[i].startAngle && angle < slices[i].endAngle) {{ f = i; break; }} }} }}
                if (f >= 0) {{
                    tooltip.style.display = 'block'; tooltip.style.left = (mx+15)+'px'; tooltip.style.top = (my-10)+'px';
                    tooltip.innerHTML = `<b style="color:${{slices[f].color}}">${{slices[f].name}}</b><br><span style="color:#ccc">${{slices[f].pct}}% (${{slices[f].invested.toLocaleString()}} ฿)</span>`;
                    canvas.style.cursor = 'pointer';
                }} else {{ tooltip.style.display = 'none'; canvas.style.cursor = 'default'; }}
                drawPie(f);
            }});
            canvas.addEventListener('mouseleave', () => {{ tooltip.style.display = 'none'; drawPie(-1); }});
            </script>'''
            components.html(pie_html, height=420, scrolling=False)

    # ===== Line Chart =====
    st.divider()
    st.subheader("📈 Asset Growth Trend")
    try:
        snap_resp = requests.get(f"{API}/asset-snapshots")
        snap_resp.raise_for_status()
        snapshots = snap_resp.json()
    except Exception:
        snapshots = []

    if not snapshots:
        st.info("ยังไม่มีข้อมูล — ไปบันทึกที่หน้า Asset Tracking")
    else:
        chart_df = pd.DataFrame(snapshots)
        chart_df["date"] = pd.to_datetime(chart_df["date"], format="ISO8601")
        chart_df["day"] = chart_df["date"].dt.strftime("%m-%d")
        chart_df = chart_df.sort_values("date")
        chart_df = chart_df.drop_duplicates(subset=["day", "port_name"], keep="last")

        port_names = sorted([n for n in chart_df["port_name"].unique() if n != "Total Asset"])
        all_names = port_names + (["Total Asset"] if "Total Asset" in chart_df["port_name"].values else [])
        labels = sorted(chart_df["day"].unique())

        line_colors = ["#36A2EB","#4BC0C0","#9966FF","#FF9F40","#FFCE56",
                       "#7BC8A4","#C9CBCF","#E7E9ED","#F7464A","#66BB6A"]
        total_color = "#FF6384"

        # Build full datasets as JSON arrays
        all_datasets = []
        for i, name in enumerate(all_names):
            sub = chart_df[chart_df["port_name"] == name].set_index("day")
            values = [float(sub.loc[d, "total"]) if d in sub.index else None for d in labels]
            is_total = name == "Total Asset"
            color = total_color if is_total else line_colors[i % len(line_colors)]
            all_datasets.append({
                "label": name,
                "fullData": values,
                "borderColor": color,
                "backgroundColor": color,
                "borderDash": [6, 4] if is_total else [],
                "borderWidth": 2.5 if is_total else 2,
                "pointRadius": 3,
                "pointHitRadius": 10,
                "pointHoverRadius": 8,
                "pointHoverBorderWidth": 2,
                "pointHoverBorderColor": "#fff",
                "tension": 0.3,
                "fill": False,
            })

        labels_json = json.dumps(labels)
        datasets_json = json.dumps(all_datasets)

        line_html = f'''
        <style>html,body{{margin:0;padding:0;overflow:hidden;height:100%;}}
        .ctrl-btn{{background:#1a1a2e;border:1px solid #2196F3;padding:5px 10px;border-radius:6px;cursor:pointer;
            display:flex;align-items:center;gap:3px;transition:all 0.2s ease;}}
        .ctrl-btn:hover{{background:#2196F3;transform:scale(1.12);box-shadow:0 0 12px rgba(33,150,243,0.5);}}
        .ctrl-btn:hover svg{{stroke:#fff;}}
        .ctrl-btn:hover span{{color:#fff;}}
        .ctrl-btn:active{{transform:scale(0.95);}}</style>
        <div style="background:#0e1117;padding:15px;border-radius:10px;position:relative;">
            <div style="position:relative;width:100%;height:340px;">
                <canvas id="lineChart"></canvas>
            </div>
            <div style="display:flex;justify-content:flex-end;align-items:center;gap:6px;margin-top:6px;">
                <button id="panLeft" class="ctrl-btn" title="Pan Left">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64B5F6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg></button>
                <button id="zoomIn" class="ctrl-btn" title="Zoom In">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64B5F6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg></button>
                <button id="zoomOut" class="ctrl-btn" title="Zoom Out">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64B5F6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="8" y1="11" x2="14" y2="11"/></svg></button>
                <button id="panRight" class="ctrl-btn" title="Pan Right">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64B5F6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg></button>
                <button id="resetZoom" class="ctrl-btn" title="Reset Zoom">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64B5F6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
                    <span style="color:#64B5F6;font-size:11px;">Reset</span></button>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
        <script>
        const allLabels = {labels_json};
        const allDatasets = {datasets_json};
        const totalLen = allLabels.length;
        let viewStart = 0;
        let viewEnd = totalLen;
        const MIN_WINDOW = 3;

        function getSlicedData() {{
            return {{
                labels: allLabels.slice(viewStart, viewEnd),
                datasets: allDatasets.map(ds => ({{
                    ...ds,
                    data: ds.fullData.slice(viewStart, viewEnd)
                }}))
            }};
        }}

        const ctx = document.getElementById('lineChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'line',
            data: getSlicedData(),
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                resizeDelay: 0,
                animation: {{ duration: 200 }},
                interaction: {{ mode: 'nearest', intersect: true }},
                plugins: {{
                    legend: {{
                        labels: {{ color: '#ccc', usePointStyle: true, pointStyle: 'circle', padding: 16 }}
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(13,27,62,0.95)',
                        titleColor: '#64B5F6',
                        bodyColor: '#ccc',
                        borderColor: '#2196F3',
                        borderWidth: 1,
                        padding: 10,
                        cornerRadius: 8,
                        callbacks: {{
                            label: function(c) {{
                                return c.dataset.label + ': ' + c.parsed.y.toLocaleString(undefined, {{minimumFractionDigits:2, maximumFractionDigits:2}}) + ' ฿';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        ticks: {{ color: '#8899aa', maxRotation: 45 }},
                        grid: {{ color: 'rgba(255,255,255,0.05)' }}
                    }},
                    y: {{
                        ticks: {{
                            color: '#8899aa',
                            callback: function(v) {{ return v.toLocaleString() + ' ฿'; }}
                        }},
                        grid: {{ color: 'rgba(255,255,255,0.08)' }}
                    }}
                }},
                onHover: function(evt, elements) {{
                    evt.chart.canvas.style.cursor = elements.length ? 'pointer' : 'default';
                }}
            }},
            plugins: [{{
                id: 'glowEffect',
                beforeDatasetsDraw(chart) {{
                    const ctx = chart.ctx;
                    chart.data.datasets.forEach((ds, i) => {{
                        const m = chart.getDatasetMeta(i);
                        if (!m.hidden && chart._active && chart._active.length && chart._active[0].datasetIndex === i) {{
                            ctx.save();
                            ctx.shadowColor = ds.borderColor;
                            ctx.shadowBlur = 16;
                            ctx.strokeStyle = ds.borderColor;
                            ctx.lineWidth = (ds.borderWidth || 2) + 2;
                            ctx.beginPath();
                            const pts = m.data;
                            for (let j = 0; j < pts.length; j++) {{
                                if (pts[j].skip) continue;
                                if (j === 0) ctx.moveTo(pts[j].x, pts[j].y);
                                else ctx.lineTo(pts[j].x, pts[j].y);
                            }}
                            ctx.stroke();
                            ctx.restore();
                        }}
                    }});
                }}
            }}]
        }});

        function updateChart() {{
            const d = getSlicedData();
            chart.data.labels = d.labels;
            d.datasets.forEach((ds, i) => {{ chart.data.datasets[i].data = ds.data; }});
            chart.update();
        }}

        document.getElementById('zoomIn').addEventListener('click', () => {{
            const window = viewEnd - viewStart;
            if (window <= MIN_WINDOW) return;
            const shrink = Math.max(1, Math.floor(window * 0.15));
            viewStart = Math.min(viewStart + shrink, viewEnd - MIN_WINDOW);
            viewEnd = Math.max(viewEnd - shrink, viewStart + MIN_WINDOW);
            updateChart();
        }});
        document.getElementById('zoomOut').addEventListener('click', () => {{
            const expand = Math.max(1, Math.floor((viewEnd - viewStart) * 0.2));
            viewStart = Math.max(0, viewStart - expand);
            viewEnd = Math.min(totalLen, viewEnd + expand);
            updateChart();
        }});
        document.getElementById('panLeft').addEventListener('click', () => {{
            const step = Math.max(1, Math.floor((viewEnd - viewStart) * 0.2));
            if (viewStart <= 0) return;
            const shift = Math.min(step, viewStart);
            viewStart -= shift;
            viewEnd -= shift;
            updateChart();
        }});
        document.getElementById('panRight').addEventListener('click', () => {{
            const step = Math.max(1, Math.floor((viewEnd - viewStart) * 0.2));
            if (viewEnd >= totalLen) return;
            const shift = Math.min(step, totalLen - viewEnd);
            viewStart += shift;
            viewEnd += shift;
            updateChart();
        }});
        document.getElementById('resetZoom').addEventListener('click', () => {{
            viewStart = 0;
            viewEnd = totalLen;
            updateChart();
        }});
        </script>'''
        components.html(line_html, height=420, scrolling=False)
   

    # ===== Port Details Table =====
    st.divider()
    st.subheader("📋 Port Details")
    table_data = []
    for p in ports:
        alloc = (p["invested"] / total_invested * 100) if total_invested > 0 else 0
        table_data.append({
            "Port": p["name"],
            "Invested (฿)": f"{p['invested']:,.2f}",
            "Profit (฿)": f"{p['profit']:,.2f}",
            "Allocation (%)": f"{alloc:,.1f}%",
        })
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
