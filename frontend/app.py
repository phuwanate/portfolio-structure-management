import streamlit as st

st.set_page_config(page_title="Portfolio Structure", layout="wide")

# Global button style — blue glow + scale on hover
st.markdown("""
<style>
/* All Streamlit buttons */
div.stButton > button,
div[data-testid="stFormSubmitButton"] > button,
button[kind="secondary"],
button[kind="primary"] {
    background-color: #1a1a2e !important;
    color: #64B5F6 !important;
    border: 1px solid #2196F3 !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
    font-weight: 500 !important;
    min-width: 140px !important;
    width: 100% !important;
    justify-content: center !important;
}
div.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover,
button[kind="secondary"]:hover,
button[kind="primary"]:hover {
    background-color: #2196F3 !important;
    color: #fff !important;
    transform: scale(1.05);
    box-shadow: 0 0 14px rgba(33,150,243,0.5) !important;
    border-color: #64B5F6 !important;
}
div.stButton > button:active,
div[data-testid="stFormSubmitButton"] > button:active {
    transform: scale(0.97);
}

/* Popover trigger buttons */
button[data-testid="stPopoverButton"] {
    background-color: #1a1a2e !important;
    color: #64B5F6 !important;
    border: 1px solid #2196F3 !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
    min-width: 140px !important;
    width: 100% !important;
    justify-content: center !important;
}
button[data-testid="stPopoverButton"]:hover {
    background-color: #2196F3 !important;
    color: #fff !important;
    transform: scale(1.05);
    box-shadow: 0 0 14px rgba(33,150,243,0.5) !important;
}
</style>
""", unsafe_allow_html=True)

overview = st.Page("pages/overview.py", title="Overview", icon="📊", default=True)
manage = st.Page("pages/manage.py", title="Manage Ports", icon="⚙️")
assets = st.Page("pages/assets.py", title="Asset Tracking", icon="🏦")

pg = st.navigation([overview, manage, assets])
pg.run()
