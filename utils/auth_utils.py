import streamlit as st

def require_login():
    """Mengalihkan pengguna ke halaman login jika belum login."""
    if not st.session_state.get("logged_in"):
        st.warning("Anda harus login untuk mengakses halaman ini.")
        st.switch_page("pages/0_Login.py")
        st.stop() # Penting untuk menghentikan eksekusi script saat redireksi

def require_admin():
    """Memastikan pengguna adalah Admin, mengalihkan jika tidak."""
    require_login() # Pastikan sudah login dulu
    if st.session_state.get("role") != "Admin":
        st.error("Anda tidak memiliki izin untuk mengakses halaman ini. Hanya Admin yang diizinkan.")
        st.switch_page("app.py") # Atau halaman lain yang sesuai
        st.stop()

def require_mentor():
    """Memastikan pengguna adalah Mentor, mengalihkan jika tidak."""
    require_login() # Pastikan sudah login dulu
    if st.session_state.get("role") != "Mentor":
        st.error("Anda tidak memiliki izin untuk mengakses halaman ini. Hanya Mentor yang diizinkan.")
        st.switch_page("app.py") # Atau halaman lain yang sesuai
        st.stop()