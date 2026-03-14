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
    @st.fragment
    def port_cards_section():
        # Compact cards — click to open actions
        cols = st.columns(min(len(ports), 4))
        # Track which card was clicked THIS run
        clicked_port_id = None
        for i, port in enumerate(ports):
            with cols[i % 4]:
                if st.button(
                    f"**{port['name']}**\n\nInvested: {port['invested']:,.2f} ฿\n\nProfit: {port['profit']:,.2f} ฿",
                    key=f"card_{port['id']}",
                    use_container_width=True,
                ):
                    clicked_port_id = port["id"]

        # --- Dialog for selected port ---
        port = next((p for p in ports if p["id"] == clicked_port_id), None)

        if port:
            @st.dialog(f"⚙️ {port['name']}", width="large")
            def port_actions():
                p = port
                c1, c2, c3 = st.columns(3)
                c1.metric("Invested", f"{p['invested']:,.2f} ฿")
                c2.metric("Profit", f"{p['profit']:,.2f} ฿")
                c3.metric("Total", f"{p['invested'] + p['profit']:,.2f} ฿")

                st.divider()

                col_a, col_b = st.columns(2)

                with col_a:
                    st.markdown("📊 Invested")
                    new_invested = st.number_input(
                        "Invested ใหม่ (฿)", min_value=0.0, value=p["invested"], key="dlg_invested"
                    )

                with col_b:
                    st.markdown("📝 Profit")
                    new_profit = st.number_input(
                        "Profit ใหม่ (฿)", min_value=0.0, value=p["profit"], key="dlg_profit"
                    )

                st.divider()

                col_c, col_d = st.columns(2)

                with col_c:
                    st.markdown("↗️ โอนไป CF")
                    transfer_amt = st.number_input(
                        "จำนวน (฿)", min_value=0.0, max_value=max(p["profit"], 0.01),
                        value=0.0, key="dlg_transfer"
                    )

                with col_d:
                    st.markdown("⛓️ ลูกศร")
                    aw = st.checkbox("⬜ Cash → Port", value=p["arrow_white"], key="dlg_aw")
                    ag = st.checkbox("🟩 Profit → Port", value=p["arrow_green"], key="dlg_ag")
                    ao = st.checkbox("🟧 Port → Profit", value=p["arrow_orange"], key="dlg_ao")

                st.divider()

                btn1, btn2 = st.columns(2)
                with btn1:
                    if st.button("💾 บันทึก", key="dlg_save_all", use_container_width=True):
                        err = False
                        # 1) บันทึก Invested
                        resp = requests.put(f"{API}/ports/{p['id']}/invested", params={"amount": new_invested})
                        if resp.status_code != 200:
                            st.error(resp.json().get("detail", "Error"))
                            err = True
                        # 2) บันทึก Profit
                        resp = requests.put(f"{API}/ports/{p['id']}/profit", params={"amount": new_profit})
                        if resp.status_code != 200:
                            st.error(resp.json().get("detail", "Error"))
                            err = True
                        # 3) บันทึกลูกศร
                        requests.put(f"{API}/ports/{p['id']}/arrows", json={
                            "arrow_white": aw, "arrow_green": ag, "arrow_orange": ao
                        })
                        # 4) โอนไป CF ทำสุดท้าย — เพื่อให้ profit ถูก set ก่อนแล้วค่อยหักออก
                        if transfer_amt > 0:
                            resp = requests.post(
                                f"{API}/ports/{p['id']}/transfer-to-profit", params={"amount": transfer_amt}
                            )
                            if resp.status_code != 200:
                                st.error(resp.json().get("detail", "Error"))
                                err = True
                        if not err:
                            st.session_state["show_toast"] = "SAVED"
                            st.rerun()
                with btn2:
                    if st.button("🗑 ลบ Port นี้", key="dlg_delete", use_container_width=True):
                        requests.delete(f"{API}/ports/{p['id']}")
                        st.session_state["show_toast"] = "DELETED"
                        st.rerun()
            port_actions()

    port_cards_section()

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
                st.session_state["show_toast"] = "SAVED"
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
        st.session_state["show_toast"] = "SAVED"
        st.rerun()
