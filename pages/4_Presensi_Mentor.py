import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from utils.auth_utils import require_mentor # Pastikan require_mentor tersedia

# --- Cek Login dan Role ---
require_mentor()
mentor_id = st.session_state.get("mentor_id")

# --- Fungsi Logout untuk Sidebar ---
def show_logout_button():
    if st.sidebar.button("Keluar", key="logout_button"):
        st.session_state.clear() # Hapus semua sesi
        st.success("Anda telah berhasil keluar.")
        # Mengarahkan kembali ke halaman utama (login page)
        # Asumsi halaman utama adalah 'Home.py' atau semacamnya
        st.switch_page("app.py") # Ganti "Home.py" dengan nama file halaman utama Anda

# Panggil fungsi logout agar muncul di sidebar
show_logout_button()

# --- Setup Google Sheets ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    CREDS = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
    CLIENT = gspread.authorize(CREDS)
    SHEET = CLIENT.open("Presensi Mentoring STT NF")
    mentee_ws = SHEET.worksheet("mentee")
    presensi_ws = SHEET.worksheet("presensi")
except Exception as e:
    st.error(f"Gagal membuka Google Sheets: {e}")
    st.stop()

# --- Load Data Mentee (dengan caching untuk performa) ---
@st.cache_data(ttl=300) # Cache data selama 5 menit
def load_mentees(current_mentor_id):
    """
    Memuat data mentee yang terkait dengan mentor yang sedang login.
    """
    df = pd.DataFrame(mentee_ws.get_all_records())
    
    # Konversi kolom 'id' dan 'mentor_id' ke numerik, tangani error dan NaN
    for col in ['id', 'mentor_id']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # Filter mentee berdasarkan mentor_id yang sedang login
    return df[df['mentor_id'] == current_mentor_id]

# --- Simpan Presensi ---
def simpan_presensi(mentee_id, tanggal, pertemuan, status_kehadiran):
    """
    Menyimpan catatan presensi ke Google Sheet.
    """
    try:
        rows = presensi_ws.get_all_values()
        next_id = 1
        if len(rows) > 1: # Jika ada baris selain header
            # Ambil semua ID dari kolom pertama (indeks 0) dan filter yang valid
            # Pastikan row[0] tidak kosong sebelum str.isdigit()
            ids = [int(row[0]) for row in rows[1:] if len(row) > 0 and row[0] and str(row[0]).isdigit()]
            if ids: # Pastikan ada ID yang berhasil diambil
                next_id = max(ids) + 1
        
        # Urutan kolom: ID (otomatis), mentee_id, tanggal, pertemuan, status_kehadiran
        presensi_ws.append_row([next_id, int(mentee_id), tanggal, int(pertemuan), status_kehadiran])
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan presensi mentee ID {mentee_id}: {e}")
        return False

# --- UI Halaman Presensi ---
st.title("📝 Form Presensi Mentee")
st.info(f"Anda login sebagai Mentor (ID: **{mentor_id}**)")

# Muat data mentee untuk mentor ini (akan menggunakan cache)
mentees = load_mentees(mentor_id)

if mentees.empty:
    st.warning("Belum ada mentee dalam kelompok Anda. Silakan tambahkan mentee di halaman Manajemen Data Mentee.")
    st.stop() # Hentikan eksekusi jika tidak ada mentee

st.markdown("---")
st.subheader("Detail Pertemuan")
col_pertemuan, col_tanggal = st.columns(2)
with col_pertemuan:
    pertemuan = st.number_input("Pertemuan ke-", min_value=1, step=1, value=1, key="input_pertemuan")
with col_tanggal:
    tanggal = st.date_input("Tanggal", value=datetime.today(), key="input_tanggal")

st.markdown("---")
st.subheader("Daftar Mentee dan Kehadiran")

# Opsi status kehadiran
status_options = ["Hadir", "Sakit", "Izin", "Alfa"]
kehadiran_dict = {}

# Tampilkan form presensi untuk setiap mentee
for idx, row in mentees.iterrows():
    mentee_id = row['id']
    nama = row['nama']
    kelompok = row.get('kelompok', '-') # Gunakan .get() dengan default jika 'kelompok' bisa tidak ada
    
    # Menggunakan st.expander untuk merapikan tampilan, terutama jika daftar mentee panjang
    with st.expander(f"**{nama}** (ID: {mentee_id}, Kelompok: {kelompok})"):
        selected_status = st.radio(
            f"Pilih status kehadiran untuk {nama}:",
            options=status_options,
            index=0, # Default: Hadir (indeks 0)
            key=f"status_radio_{mentee_id}", # Key unik sangat penting untuk setiap widget
            horizontal=True
        )
        kehadiran_dict[mentee_id] = selected_status

st.markdown("---")
if st.button("💾 Simpan Presensi", use_container_width=True):
    if not kehadiran_dict:
        st.error("Tidak ada mentee yang terdaftar atau dipilih untuk presensi.")
    else:
        success_count = 0
        fail_count = 0
        failed_mentees_info = []

        for mentee_id, status_kehadiran in kehadiran_dict.items():
            # Dapatkan nama mentee untuk feedback yang lebih baik
            mentee_nama_for_feedback = mentees[mentees['id'] == mentee_id]['nama'].iloc[0] if not mentees[mentees['id'] == mentee_id].empty else f"ID {mentee_id}"
            
            if simpan_presensi(mentee_id, tanggal.strftime("%Y-%m-%d"), pertemuan, status_kehadiran):
                success_count += 1
            else:
                fail_count += 1
                failed_mentees_info.append(mentee_nama_for_feedback)

        if success_count > 0:
            st.success(f"✅ Presensi berhasil disimpan untuk **{success_count}** mentee.")
        if fail_count > 0:
            st.error(f"❌ Gagal menyimpan presensi untuk **{fail_count}** mentee: {', '.join(failed_mentees_info)}.")
        
        # Selalu rerun setelah submit untuk membersihkan form dan update UI
        # Ini akan memaksa load_mentees() dari cache jika TTL belum habis, atau dari sheet jika sudah habis.
        st.rerun()