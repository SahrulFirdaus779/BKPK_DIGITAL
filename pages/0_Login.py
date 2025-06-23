import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time # Untuk simulasi loading atau jeda
from PIL import Image # Tambahkan import ini untuk gambar

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

# --- Pengalihan Halaman Jika Sudah Login (PENTING!) ---
# Pindahkan logika ini ke bagian paling atas setelah inisialisasi session_state
# Ini adalah perbaikan untuk masalah "kembali meminta login saat di-refresh"
# Setiap halaman yang dilindungi (seperti Dashboard, Data Mentor, dll.)
# HARUS memiliki kode ini di BAGIAN PALING ATAS setelah inisialisasi session_state.
if st.session_state.get("logged_in"):
    st.switch_page("app.py") # Mengalihkan ke app.py jika sudah login

# Konfigurasi Halaman (Dipindahkan ke sini agar dieksekusi sebelum konten lain)
st.set_page_config(page_title="Login Presensi Mentoring", page_icon="🔑", layout="centered")


# CSS Styling (bisa diimpor atau didefinisikan di sini)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
    color: var(--text-color); /* Pastikan teks default mengikuti tema */
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
    box-shadow: 2px 2px 5px rgba(0,0,0,0.2); /* Efek bayangan tombol */
}
.stButton>button:hover {
    background-color: #0a58ca;
    transform: translateY(-2px);
    box-shadow: 3px 3px 8px rgba(0,0,0,0.3);
}
.stTextInput>div>div>input {
    border-radius: 8px;
    border: 1px solid var(--border-color); /* Border adaptif tema */
    padding: 8px 12px;
    background-color: var(--background-color-secondary); /* Background input adaptif */
    color: var(--text-color); /* Warna teks input adaptif */
}
.stSelectbox>div>div>div {
    border-radius: 8px;
    border: 1px solid var(--border-color); /* Border adaptif tema */
    padding: 4px 12px;
    background-color: var(--background-color-secondary); /* Background selectbox adaptif */
    color: var(--text-color); /* Warna teks selectbox adaptif */
}
.login-form-container {
    padding: 30px;
    border-radius: 15px;
    background-color: var(--background-color-secondary); /* Latar belakang form adaptif */
    box-shadow: 0 10px 20px rgba(0,0,0,0.15); /* Bayangan form */
    border: 1px solid var(--border-color);
}
h1 {
    color: var(--primary-color);
    text-align: center; /* Pusatkan judul */
}
/* CSS untuk pembungkus gambar */
.login-image-wrapper { /* Nama kelas baru untuk div pembungkus gambar */
    border-radius: 15px; /* Sesuaikan dengan border-radius form */
    overflow: hidden; /* Penting agar gambar memotong di sudut border-radius */
    box-shadow: 0 10px 20px rgba(0,0,0,0.15); /* Bayangan gambar */
    border: 1px solid var(--border-color); /* Border gambar adaptif tema */
    display: flex; /* Menggunakan flexbox untuk memusatkan gambar secara vertikal dalam wrapper */
    align-items: center; /* Memusatkan secara vertikal */
    justify-content: center; /* Memusatkan secara horizontal */
    height: 100%; /* Pastikan wrapper mengisi tinggi kolom */
    max-height: 400px; /* BATASI TINGGI MAKSIMUM GAMBAR */
}
/* Memaksa gambar di dalam wrapper agar pas */
.login-image-wrapper img {
    object-fit: contain; /* Pastikan seluruh gambar terlihat dalam batas wrapper */
    width: 100%;
    height: 100%;
}
.st-emotion-cache-1r6dm5c { /* Menghilangkan padding utama Streamlit jika mengganggu */
    padding-top: 0rem;
    padding-bottom: 0rem;
}
</style>
""", unsafe_allow_html=True)


# --- Setup Google Sheets ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
mentor_df = pd.DataFrame() # Inisialisasi kosong
CLIENT = None
SHEET = None

# Menggunakan st.cache_resource untuk menyimpan koneksi dan data mentor
# Ini akan mencegah koneksi ulang dan pembacaan data berulang setiap refresh
@st.cache_resource(ttl=3600) # Cache selama 1 jam
def get_google_sheet_data():
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open("Presensi Mentoring STT NF") # Ganti dengan nama spreadsheet Anda

        # Muat data mentor
        df = pd.DataFrame(sheet.worksheet("mentor").get_all_records())
        df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
        return client, sheet, df
    except FileNotFoundError:
        st.error("Error: File 'service_account.json' tidak ditemukan di direktori proyek. Pastikan file ada.")
        st.stop()
    except Exception as e:
        st.error(f"Gagal terhubung ke Google Sheet: {e}. Pastikan kredensial service account benar dan Google Sheets API aktif.")
        st.stop()
    return None, None, pd.DataFrame() # Return kosong jika ada error

CLIENT, SHEET, mentor_df = get_google_sheet_data()


# --- Tampilan Form Login ---
st.title("🔐 Login Presensi Mentoring")
st.markdown("---") # Garis pemisah

# Menggunakan kolom untuk layout berdampingan
col1, col2 = st.columns([1.5, 0.5]) # Rasio kolom diubah: Form lebih lebar, Gambar jauh lebih sempit

with col1:
    st.subheader("Masuk ke Sistem") # Dipindahkan ke dalam container

    email = st.text_input("Email", key="login_email")
    role = st.selectbox("Masuk sebagai", ["Admin", "Mentor"], key="login_role")
    login_button = st.button("Login", key="do_login", use_container_width=True)

    if login_button:
        if role == "Admin":
            # Ganti dengan email admin yang sebenarnya jika berbeda
            if email == "admin@sttnf.ac.id": 
                st.session_state.logged_in = True
                st.session_state.role = "Admin"
                st.session_state.user_name = "Admin"
                st.session_state.email = email
                st.success("Login Admin berhasil. Mengalihkan...")
                time.sleep(1) # Beri waktu pengguna melihat pesan sukses
                st.rerun() # Gunakan st.rerun() setelah mengubah session state
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
                        st.success(f"Login sebagai {match.iloc[0]['nama']} berhasil. Mengalihkan...")
                        time.sleep(1) # Beri waktu pengguna melihat pesan sukses
                        st.rerun() # Gunakan st.rerun() setelah mengubah session state
                    else:
                        st.error("Email Mentor tidak ditemukan.")
                else:
                    st.error("Data mentor tidak dapat dimuat. Cek koneksi Google Sheets.")
            else:
                st.error("Email harus diisi.")
    
    st.markdown("</div>", unsafe_allow_html=True) # Tutup login-form-container

# Kolom kedua untuk gambar Menzo
with col2:
    st.markdown("<div class='login-image-wrapper'>", unsafe_allow_html=True) # Tambahkan div pembungkus
    try:
        menzo_image = Image.open("assets/Menzoo2.png") # Pastikan path gambar benar
        st.image(menzo_image, caption="Yuk gabung bareng Menzo !", width=230)
    except FileNotFoundError:
        st.warning("Gambar 'assets/Menzo.png' tidak ditemukan. Pastikan path sudah benar.")
    except Exception as e:
        st.warning(f"Error loading Menzo image: {e}")
    st.markdown("</div>", unsafe_allow_html=True) # Tutup div pembungkus

# Tombol untuk kembali ke halaman utama jika pengguna belum login
if not st.session_state.logged_in:
    if st.button("Kembali ke Beranda Umum", key="back_to_home_login_page", type="secondary", use_container_width=True):
        st.switch_page("app.py")