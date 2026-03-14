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

/* Dialog fade-in + slide-up animation */
@keyframes dialogFadeIn {
    from { opacity: 0; transform: translateY(24px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
div[role="dialog"] {
    animation: dialogFadeIn 0.35s ease-out;
}

/* Prevent white flash on Streamlit rerun */
.stApp, .main, section[data-testid="stMain"],
div[data-testid="stAppViewContainer"],
div[data-testid="stAppViewBlockContainer"] {
    background-color: #0e1117 !important;
}
html, body {
    background-color: #0e1117 !important;
}
[data-testid="stSkeleton"] {
    display: none !important;
}

/* Hide Streamlit colored header line / toolbar decoration */
header[data-testid="stHeader"] {
    background: transparent !important;
    border-bottom: none !important;
}
div[data-testid="stDecoration"],
div[data-testid="stToolbar"] ~ div[style*="background"] {
    display: none !important;
}
div[data-testid="stStatusWidget"] {
    visibility: hidden !important;
}
</style>
""", unsafe_allow_html=True)

# --- Global "SAVED" toast ---
if st.session_state.get("show_toast"):
    toast_msg = st.session_state.pop("show_toast")
    import streamlit.components.v1 as components
    components.html(f"""
    <script>
    (function() {{
        var doc = window.parent.document;
        var old = doc.getElementById('kiro-toast');
        if (old) old.remove();
        var d = doc.createElement('div');
        d.id = 'kiro-toast';
        d.textContent = '{toast_msg}';
        d.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%) scale(0.8);z-index:999999;pointer-events:none;font-size:2.5rem;font-weight:700;color:rgba(200,200,200,0.7);letter-spacing:6px;opacity:0;transition:opacity 0.4s ease,transform 0.4s ease;';
        doc.body.appendChild(d);
        requestAnimationFrame(function() {{
            d.style.opacity = '1';
            d.style.transform = 'translate(-50%,-50%) scale(1)';
            setTimeout(function() {{
                d.style.opacity = '0';
                d.style.transform = 'translate(-50%,-50%) scale(1.15)';
                setTimeout(function() {{ d.remove(); }}, 500);
            }}, 1400);
        }});
    }})();
    </script>
    """, height=0)

overview = st.Page("pages/overview.py", title="Overview", icon="📊", default=True)
manage = st.Page("pages/manage.py", title="Manage Ports", icon="⚙️")
assets = st.Page("pages/assets.py", title="Asset Tracking", icon="🏦")

pg = st.navigation([overview, manage, assets])
pg.run()
