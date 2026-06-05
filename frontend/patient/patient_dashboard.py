import streamlit as st

def render(username):
    st.markdown(f"""
    <div style="padding: 2rem; background: white; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
        <h1 style="color: #0b2545; font-family: 'Fraunces', serif;">Welcome back, {username}</h1>
        <p style="color: #6b8aab;">This is your personal health portal. Here you can view your diagnostic history and upcoming appointments.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Health Score", "88/100", "↑ 2%")
    with col2:
        st.metric("Next Checkup", "In 12 days")
    with col3:
        st.metric("Active Protocols", "2")

    st.subheader("Your Recent Activity")
    st.info("No recent alerts. Your latest Heart Risk assessment was 'Low'.")
    
    if st.button("Sign Out", key="patient_signout"):
        from auth.session_manager import clear_session
        clear_session()
        st.session_state.portal = None
        st.rerun()
