import streamlit as st
import requests
import pandas as pd

API = "http://localhost:8000"

st.title("🏦 Asset Tracking")

ports = requests.get(f"{API}/ports").json()

if not ports:
    st.warning("ยังไม่มี Port — ไปเพิ่มที่หน้า Manage Ports ก่อน")
else:
    # --- Add Snapshot ---
    st.subheader("📝 บันทึกข้อมูล Port")

    port_options = {p["name"]: p for p in ports}

    selected_name = st.selectbox("เลือก Port", list(port_options.keys()))
    port = port_options[selected_name]

    c1, c2, c3 = st.columns(3)
    c1.metric("Invested", f"{port['invested']:,.2f} ฿")
    c2.metric("Profit", f"{port['profit']:,.2f} ฿")
    c3.metric("Total", f"{port['invested'] + port['profit']:,.2f} ฿")

    with st.form("add_snapshot"):
        comment = st.text_input("Comment (ไม่บังคับ)", placeholder="เช่น เพิ่มทุน, ตลาดขึ้น...")
        if st.form_submit_button("✦ Add Data"):
            resp = requests.post(f"{API}/asset-snapshots", json={
                "port_id": port["id"], "comment": comment
            })
            if resp.status_code == 200:
                st.success(f"บันทึก {selected_name} สำเร็จ")
                st.rerun()
            else:
                st.error(resp.json().get("detail", "Error"))

    st.divider()

    # --- Snapshot Table ---
    st.subheader("📋 ประวัติการบันทึก")

    snapshots = requests.get(f"{API}/asset-snapshots").json()

    if not snapshots:
        st.info("ยังไม่มีข้อมูล — กด Add Data เพื่อเริ่มบันทึก")
    else:
        table_data = []
        for s in snapshots:
            if s["port_name"] == "Total Asset":
                continue
            table_data.append({
                "Date": s["date"][:19].replace("T", " "),
                "Port": s["port_name"],
                "Invested (฿)": f"{s['invested']:,.2f}",
                "Profit (฿)": f"{s['profit']:,.2f}",
                "Total (฿)": f"{s['total']:,.2f}",
                "Comment": s.get("comment", ""),
            })

        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Delete snapshot
        with st.expander("🗑 ลบรายการ"):
            options = {
                f"{s['date'][:19].replace('T', ' ')} — {s['port_name']} — {s['total']:,.2f} ฿": s["id"]
                for s in snapshots
                if s["port_name"] != "Total Asset"
            }
            selected = st.selectbox("เลือกรายการที่จะลบ", list(options.keys()))
            if st.button("ลบ"):
                requests.delete(f"{API}/asset-snapshots/{options[selected]}")
                st.rerun()

# === Payoff CF Profit ===
st.divider()
st.subheader("💸 Payoff CF Profit")

cashflow = {cf["type"]: cf["amount"] for cf in requests.get(f"{API}/cashflow").json()}
cf_profit = cashflow.get("profit", 0)
st.metric("Cash Flow (Profit) คงเหลือ", f"{cf_profit:,.2f} ฿")

with st.form("add_payoff"):
    payoff_amt = st.number_input("จำนวนที่จะ Payoff (฿)", min_value=0.0, value=0.0, step=100.0)
    payoff_comment = st.text_input("Comment (ไม่บังคับ)", placeholder="เช่น ถอนกำไร, จ่ายค่าใช้จ่าย...", key="payoff_comment")
    if st.form_submit_button("↗ Payoff"):
        if payoff_amt > 0:
            resp = requests.post(f"{API}/payoffs", json={"amount": payoff_amt, "comment": payoff_comment})
            if resp.status_code == 200:
                st.success(f"Payoff {payoff_amt:,.2f} ฿ สำเร็จ")
                st.rerun()
            else:
                st.error(resp.json().get("detail", "Error"))
        else:
            st.warning("กรุณาใส่จำนวนมากกว่า 0")

# Payoff history table
payoffs = requests.get(f"{API}/payoffs").json()
if payoffs:
    st.markdown("**ประวัติ Payoff**")
    payoff_data = []
    total_payoff = 0
    for p in payoffs:
        total_payoff += p["amount"]
        payoff_data.append({
            "Date": p["date"][:19].replace("T", " "),
            "Amount (฿)": f"{p['amount']:,.2f}",
            "Comment": p.get("comment", ""),
        })
    payoff_df = pd.DataFrame(payoff_data)
    st.dataframe(payoff_df, use_container_width=True, hide_index=True)
    st.metric("รวม Payoff ทั้งหมด", f"{total_payoff:,.2f} ฿")

    with st.expander("🗑 ลบรายการ Payoff"):
        payoff_options = {
            f"{p['date'][:19].replace('T', ' ')} — {p['amount']:,.2f} ฿": p["id"]
            for p in payoffs
        }
        sel = st.selectbox("เลือกรายการที่จะลบ", list(payoff_options.keys()), key="del_payoff")
        if st.button("ลบ", key="btn_del_payoff"):
            requests.delete(f"{API}/payoffs/{payoff_options[sel]}")
            st.rerun()
