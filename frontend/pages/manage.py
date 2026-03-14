import streamlit as st
import requests

API = "http://localhost:8000"

st.title("⚙️ Manage Ports")

cashflow = {cf["type"]: cf["amount"] for cf in requests.get(f"{API}/cashflow").json()}
ports = requests.get(f"{API}/ports").json()

# --- แสดง Cash & Profit ---
col1, col2 = st.columns(2)
with col1:
    st.metric("💰 Cash", f"{cashflow.get('cash', 0):,.2f} ฿")
with col2:
    st.metric("📈 Cash Flow (Profit)", f"{cashflow.get('profit', 0):,.2f} ฿")

st.divider()

# --- แสดง Ports ---
st.subheader("Ports")

if not ports:
    st.info("ยังไม่มี Port — เพิ่ม Port ใหม่ได้ด้านล่าง")
else:
    cols = st.columns(min(len(ports), 4))
    for i, port in enumerate(ports):
        with cols[i % 4]:
            with st.container(border=True):
                st.markdown(f"### {port['name']}")
                st.write(f"Invested: {port['invested']:,.2f} ฿")
                st.write(f"Profit: {port['profit']:,.2f} ฿")

                # แก้ Invested
                with st.popover("💼 แก้ Invested"):
                    new_invested = st.number_input(
                        "Invested ใหม่ (฿)", min_value=0.0, value=port["invested"], key=f"invested_{port['id']}"
                    )
                    if st.button("บันทึก", key=f"save_invested_{port['id']}"):
                        resp = requests.put(f"{API}/ports/{port['id']}/invested", params={"amount": new_invested})
                        if resp.status_code == 200:
                            st.rerun()
                        else:
                            st.error(resp.json().get("detail", "Error"))

                # แก้ Profit
                with st.popover("✏️ แก้ Profit"):
                    new_profit = st.number_input(
                        "Profit ใหม่ (฿)", min_value=0.0, value=port["profit"], key=f"profit_{port['id']}"
                    )
                    if st.button("บันทึก", key=f"save_profit_{port['id']}"):
                        requests.put(f"{API}/ports/{port['id']}/profit", params={"amount": new_profit})
                        st.rerun()

                # โอน Profit → Cash Flow (Profit)
                with st.popover("💸 โอนไป Profit"):
                    transfer_amt = st.number_input(
                        "จำนวน (฿)", min_value=0.0, max_value=max(port["profit"], 0.01),
                        value=0.0, key=f"transfer_{port['id']}"
                    )
                    if st.button("โอน", key=f"do_transfer_{port['id']}"):
                        if transfer_amt > 0:
                            resp = requests.post(
                                f"{API}/ports/{port['id']}/transfer-to-profit", params={"amount": transfer_amt}
                            )
                            if resp.status_code == 200:
                                st.rerun()
                            else:
                                st.error(resp.json().get("detail", "Error"))

                # แก้ไขลูกศร
                with st.popover("🔗 ลูกศร"):
                    aw = st.checkbox("⬜ Cash → Port (ลงทุน)", value=port["arrow_white"], key=f"aw_{port['id']}")
                    ag = st.checkbox("🟩 Profit → Port (เติมทุน)", value=port["arrow_green"], key=f"ag_{port['id']}")
                    ao = st.checkbox("🟧 Port → Profit (โอนกำไร)", value=port["arrow_orange"], key=f"ao_{port['id']}")
                    if st.button("บันทึกลูกศร", key=f"save_arrows_{port['id']}"):
                        requests.put(f"{API}/ports/{port['id']}/arrows", json={
                            "arrow_white": aw, "arrow_green": ag, "arrow_orange": ao
                        })
                        st.rerun()

                if st.button("🗑️ ลบ", key=f"del_{port['id']}"):
                    requests.delete(f"{API}/ports/{port['id']}")
                    st.rerun()

st.divider()

# --- เพิ่ม Port ใหม่ ---
st.subheader("➕ เพิ่ม Port ใหม่")
with st.form("add_port"):
    name = st.text_input("ชื่อ Port")
    c1, c2 = st.columns(2)
    invested = c1.number_input("Invested (฿)", min_value=0.0, value=0.0)
    profit = c2.number_input("Profit (฿)", min_value=0.0, value=0.0)
    st.markdown("**ลูกศร**")
    a1, a2, a3 = st.columns(3)
    aw = a1.checkbox("⬜ Cash → Port")
    ag = a2.checkbox("🟩 Profit → Port")
    ao = a3.checkbox("🟧 Port → Profit")
    if st.form_submit_button("เพิ่ม Port"):
        if name:
            resp = requests.post(f"{API}/ports", json={
                "name": name, "invested": invested, "profit": profit,
                "arrow_white": aw, "arrow_green": ag, "arrow_orange": ao
            })
            if resp.status_code == 200:
                st.rerun()
            else:
                st.error(resp.json().get("detail", "Error"))
        else:
            st.warning("กรุณาใส่ชื่อ Port")

# --- อัปเดต Cash / Profit ---
st.divider()
st.subheader("💵 อัปเดต Cash / Profit")
with st.form("update_cf"):
    c1, c2 = st.columns(2)
    new_cash = c1.number_input("Cash (฿)", value=cashflow.get("cash", 0.0))
    new_profit = c2.number_input("Profit (฿)", value=cashflow.get("profit", 0.0))
    if st.form_submit_button("อัปเดต"):
        requests.put(f"{API}/cashflow/cash", params={"amount": new_cash})
        requests.put(f"{API}/cashflow/profit", params={"amount": new_profit})
        st.rerun()
