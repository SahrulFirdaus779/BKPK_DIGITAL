import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time # Untuk simulasi loading atau jeda

# --- Inisialisasi session_state ---
# Ini penting untuk memastikan kunci-kunci ada bahkan di awal aplikasi
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'email' not in st.session_state:
    st.session_state.email = None
if 'mentor_id' not in st.session_state:
    st.session_state.mentor_id = None

# Jika sudah login, alihkan langsung ke halaman utama (app.py)
# Ini mencegah pengguna yang sudah login untuk kembali ke halaman login
if st.session_state.get("logged_in"):
    st.switch_page("app.py")

# --- Setup Google Sheets ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
mentor_df = pd.DataFrame() # Inisialisasi kosong
CLIENT = None
SHEET = None

try:
    # Selalu coba membaca dari service_account.json
    CREDS = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
    CLIENT = gspread.authorize(CREDS)
    SHEET = CLIENT.open("Presensi Mentoring STT NF") # Ganti dengan nama spreadsheet Anda

    # Muat data mentor hanya jika koneksi berhasil
    mentor_df = pd.DataFrame(SHEET.worksheet("mentor").get_all_records())
    mentor_df['id'] = pd.to_numeric(mentor_df['id'], errors='coerce').fillna(0).astype(int)

except FileNotFoundError:
    st.error("Error: File 'service_account.json' tidak ditemukan di direktori proyek. Pastikan file ada.")
    st.stop()
except Exception as e:
    st.error(f"Gagal terhubung ke Google Sheet: {e}. Pastikan kredensial service account benar dan Google Sheets API aktif.")
    st.stop()

# --- Tampilan Form Login ---
st.set_page_config(page_title="Login Presensi Mentoring", page_icon="🔑", layout="centered")

# CSS Styling (bisa diimpor atau didefinisikan di sini)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}
.stButton>button {
    background-color: #0d6efd;
    color: white;
    font-weight: 600;
    border-radius: 8px;
    padding: 10px 20px;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color: #0a58ca;
    transform: translateY(-2px);
}
.stTextInput>div>div>input {
    border-radius: 8px;
    border: 1px solid #ccc;
    padding: 8px 12px;
}
.stSelectbox>div>div>div {
    border-radius: 8px;
    border: 1px solid #ccc;
    padding: 4px 12px;
}
</style>
""", unsafe_allow_html=True)


st.title("🔐 Login Presensi Mentoring")
st.markdown("Silakan login sesuai peran Anda.")

email = st.text_input("Email", key="login_email")
role = st.selectbox("Masuk sebagai", ["Admin", "Mentor"], key="login_role")
login_button = st.button("Login", key="do_login")

if login_button:
    if role == "Admin":
        if email == "admin@sttnf.ac.id": # Contoh email admin
            st.session_state.logged_in = True
            st.session_state.role = "Admin"
            st.session_state.user_name = "Admin"
            st.session_state.email = email
            st.success("Login Admin berhasil.")
            time.sleep(1) # Beri waktu pengguna melihat pesan sukses
            st.switch_page("app.py")
        else:
            st.error("Email Admin salah.")
    elif role == "Mentor":
        if email:
            if not mentor_df.empty:
                match = mentor_df[mentor_df['email'] == email]
                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.role = "Mentor"
                    st.session_state.user_name = match.iloc[0]['nama']
                    st.session_state.email = email
                    st.session_state.mentor_id = match.iloc[0]['id']
                    st.success(f"Login sebagai {match.iloc[0]['nama']} berhasil.")
                    time.sleep(1) # Beri waktu pengguna melihat pesan sukses
                    st.switch_page("app.py")
                else:
                    st.error("Email Mentor tidak ditemukan.")
            else:
                st.error("Data mentor tidak dapat dimuat. Cek koneksi Google Sheets.")
        else:
            st.error("Email harus diisi.")

# Tombol untuk kembali ke halaman utama jika pengguna belum login
if not st.session_state.logged_in:
    if st.button("Kembali ke Beranda Umum", key="back_to_home_login_page"):
        st.switch_page("app.py")