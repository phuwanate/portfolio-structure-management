import streamlit as st

st.set_page_config(page_title="Portfolio Structure", layout="wide")

overview = st.Page("pages/overview.py", title="Overview", icon="📊", default=True)
manage = st.Page("pages/manage.py", title="Manage Ports", icon="⚙️")

pg = st.navigation([overview, manage])
pg.run()
