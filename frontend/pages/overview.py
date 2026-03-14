import streamlit as st
import streamlit.components.v1 as components
import requests
import math

API = "http://localhost:8000"

st.title("📊 Portfolio Structure Overview")

ports = requests.get(f"{API}/ports").json()
cashflow = {cf["type"]: cf["amount"] for cf in requests.get(f"{API}/cashflow").json()}

num_ports = len(ports)

if num_ports == 0:
    st.info("ยังไม่มี Port — ไปเพิ่มที่หน้า Manage Ports")
else:
    col_left, col_right = st.columns([3, 2])

    # ===== LEFT: Structure Diagram =====
    with col_left:
        box_w = 120
        box_h = 60
        gap = 20
        total_ports_w = num_ports * box_w + (num_ports - 1) * gap
        svg_w = total_ports_w + 60
        svg_h = 380

        start_x = 30
        cash_y = svg_h - 50
        profit_y = 20
        port_y = 160

        svg = f'<svg width="{svg_w}" height="{svg_h}" xmlns="http://www.w3.org/2000/svg">'
        svg += '''
        <defs>
          <marker id="ah-white" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="white"/>
          </marker>
          <marker id="ah-green" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#4CAF50"/>
          </marker>
          <marker id="ah-orange" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#FF9800"/>
          </marker>
        </defs>
        '''

        # Cash Flow (Profit) box - top
        svg += f'''
        <rect x="{start_x}" y="{profit_y}" width="{total_ports_w}" height="36" rx="6"
              fill="#0d1b3e" stroke="#2196F3" stroke-width="2"/>
        <text x="{start_x + total_ports_w/2}" y="{profit_y + 23}" text-anchor="middle"
              fill="#64B5F6" font-size="13" font-weight="bold">Cash Flow (Profit)</text>
        '''

        # Cash box - bottom
        svg += f'''
        <rect x="{start_x}" y="{cash_y}" width="{total_ports_w}" height="36" rx="6"
              fill="#1a1a2e" stroke="#444" stroke-width="1.5"/>
        <text x="{start_x + total_ports_w/2}" y="{cash_y + 23}" text-anchor="middle"
              fill="white" font-size="13" font-weight="bold">Cash</text>
        '''

        for i, port in enumerate(ports):
            px = start_x + i * (box_w + gap)
            cx = px + box_w / 2

            svg += f'''
            <rect x="{px}" y="{port_y}" width="{box_w}" height="{box_h}" rx="8"
                  fill="#1a1a2e" stroke="#555" stroke-width="1.5"/>
            <text x="{cx}" y="{port_y + box_h/2 + 5}" text-anchor="middle"
                  fill="white" font-size="12" font-weight="bold">{port["name"]}</text>
            '''

            if port.get("arrow_white"):
                x = cx - 15
                svg += f'''
                <line x1="{x}" y1="{cash_y}" x2="{x}" y2="{port_y + box_h}"
                      stroke="white" stroke-width="2" marker-end="url(#ah-white)"/>
                '''
            if port.get("arrow_green"):
                x = cx
                svg += f'''
                <line x1="{x}" y1="{profit_y + 36}" x2="{x}" y2="{port_y}"
                      stroke="#4CAF50" stroke-width="2" marker-end="url(#ah-green)"/>
                '''
            if port.get("arrow_orange"):
                x = cx + 15
                svg += f'''
                <line x1="{x}" y1="{port_y}" x2="{x}" y2="{profit_y + 36}"
                      stroke="#FF9800" stroke-width="2" marker-end="url(#ah-orange)"/>
                '''

        svg += '</svg>'

        diagram_html = f'''
        <div style="display:flex; justify-content:center; background:#0e1117; padding:15px; border-radius:10px; overflow-x:auto;">
            {svg}
        </div>
        '''
        components.html(diagram_html, height=420, scrolling=True)

    # ===== RIGHT: Pie Chart =====
    with col_right:
        total_invested = sum(p["invested"] for p in ports)
        colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF",
                  "#FF9F40", "#C9CBCF", "#7BC8A4", "#E7E9ED", "#F7464A"]

        if total_invested == 0:
            st.info("ยังไม่มีเงินลงทุน")
        else:
            # Build pie data for JS
            pie_data = []
            for i, port in enumerate(ports):
                if port["invested"] <= 0:
                    continue
                pct = port["invested"] / total_invested * 100
                pie_data.append({
                    "name": port["name"],
                    "pct": round(pct, 1),
                    "invested": port["invested"],
                    "color": colors[i % len(colors)]
                })

            import json
            pie_json = json.dumps(pie_data)

            pie_html = f'''
            <div style="background:#0e1117; padding:15px; border-radius:10px; text-align:center;">
                <div style="color:#ccc; font-size:16px; font-weight:bold; margin-bottom:10px;">
                    Investment Allocation
                </div>
                <div style="position:relative; display:inline-block;">
                    <canvas id="pieChart" width="300" height="300"></canvas>
                    <div id="tooltip" style="
                        display:none; position:absolute; background:rgba(0,0,0,0.85);
                        color:white; padding:8px 12px; border-radius:6px; font-size:13px;
                        pointer-events:none; white-space:nowrap; z-index:10;
                    "></div>
                </div>
                <div id="legend" style="margin-top:10px; text-align:left; padding:0 10px;"></div>
            </div>
            <script>
            const data = {pie_json};
            const canvas = document.getElementById('pieChart');
            const ctx = canvas.getContext('2d');
            const tooltip = document.getElementById('tooltip');
            const legend = document.getElementById('legend');
            const cx = 150, cy = 150, r = 120;
            const slices = [];

            let startAngle = -Math.PI / 2;
            const MIN_ANGLE = 0.06;  // ~3.4 degrees minimum so small slices are visible
            let totalAngle = 2 * Math.PI;

            // Calculate raw angles and find how many need minimum
            let rawAngles = data.map(d => d.pct / 100 * 2 * Math.PI);
            let smallCount = rawAngles.filter(a => a < MIN_ANGLE && a > 0).length;
            let extraNeeded = rawAngles.reduce((sum, a) => sum + (a > 0 && a < MIN_ANGLE ? MIN_ANGLE - a : 0), 0);
            let largeTotal = rawAngles.reduce((sum, a) => sum + (a >= MIN_ANGLE ? a : 0), 0);

            let displayAngles = rawAngles.map(a => {{
                if (a <= 0) return 0;
                if (a < MIN_ANGLE) return MIN_ANGLE;
                return a - (extraNeeded * a / largeTotal);
            }});

            data.forEach((d, i) => {{
                const angle = displayAngles[i];
                if (angle <= 0) return;
                const endAngle = startAngle + angle;
                slices.push({{ ...d, startAngle, endAngle }});
                startAngle = endAngle;
            }});

            function drawPie(hoverIdx) {{
                ctx.clearRect(0, 0, 300, 300);
                slices.forEach((s, i) => {{
                    ctx.beginPath();
                    ctx.moveTo(cx, cy);
                    ctx.arc(cx, cy, i === hoverIdx ? r + 6 : r, s.startAngle, s.endAngle);
                    ctx.closePath();
                    ctx.fillStyle = s.color;
                    ctx.fill();
                    ctx.strokeStyle = '#0e1117';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }});
            }}

            drawPie(-1);

            // Legend
            let legendHtml = '<div style="display:flex; flex-wrap:wrap; gap:6px 20px;">';
            data.forEach(d => {{
                legendHtml += `<div style="display:flex;align-items:center;gap:5px;">
                    <span style="width:12px;height:12px;border-radius:2px;background:${{d.color}};display:inline-block;"></span>
                    <span style="color:#ccc;font-size:12px;">${{d.name}}</span>
                </div>`;
            }});
            legendHtml += '</div>';
            legend.innerHTML = legendHtml;

            canvas.addEventListener('mousemove', (e) => {{
                const rect = canvas.getBoundingClientRect();
                const mx = e.clientX - rect.left;
                const my = e.clientY - rect.top;
                const dx = mx - cx, dy = my - cy;
                const dist = Math.sqrt(dx*dx + dy*dy);
                let angle = Math.atan2(dy, dx);
                if (angle < -Math.PI/2) angle += 2*Math.PI;

                let found = -1;
                if (dist <= r + 6) {{
                    for (let i = 0; i < slices.length; i++) {{
                        let sa = slices[i].startAngle, ea = slices[i].endAngle;
                        if (angle >= sa && angle < ea) {{ found = i; break; }}
                    }}
                }}

                if (found >= 0) {{
                    const s = slices[found];
                    tooltip.style.display = 'block';
                    tooltip.style.left = (mx + 15) + 'px';
                    tooltip.style.top = (my - 10) + 'px';
                    tooltip.innerHTML = `<b>${{s.name}}</b><br>${{s.pct}}% (${{s.invested.toLocaleString()}} ฿)`;
                    canvas.style.cursor = 'pointer';
                }} else {{
                    tooltip.style.display = 'none';
                    canvas.style.cursor = 'default';
                }}
                drawPie(found);
            }});

            canvas.addEventListener('mouseleave', () => {{
                tooltip.style.display = 'none';
                drawPie(-1);
            }});
            </script>
            '''
            components.html(pie_html, height=420, scrolling=False)

    # ===== BOTTOM: Dashboard Summary =====
    st.divider()

    # Cash & Profit metrics
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

    # Port detail table
    import pandas as pd

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
