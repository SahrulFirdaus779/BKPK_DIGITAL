# pages/2_Data_Mentor.py
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils.auth_utils import require_admin # Pastikan ini mengarahkan ke fungsi yang benar

# --- Cek Login dan Role Admin ---
require_admin()

# --- Setup Google Sheets ---
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Menggunakan st.cache_resource untuk koneksi gspread agar tidak menginisialisasi ulang
@st.cache_resource
def get_gspread_client():
    try:
        CREDS = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
        CLIENT = gspread.authorize(CREDS)
        return CLIENT.open("Presensi Mentoring STT NF") # Ganti dengan nama spreadsheet Anda
    except FileNotFoundError:
        st.error("Error: File 'service_account.json' tidak ditemukan di direktori proyek. Pastikan file ada.")
        st.stop()
    except Exception as e:
        st.error(f"Terjadi kesalahan saat menginisialisasi koneksi Google Sheets: {e}. Pastikan kredensial service account benar dan Google Sheets API aktif.")
        st.stop()

SHEET = get_gspread_client()
mentor_ws = SHEET.worksheet("mentor")

# --- Fungsi (Menggunakan st.cache_data untuk data) ---
@st.cache_data(ttl=60) # Cache data mentor selama 60 detik
def load_data():
    try:
        df = pd.DataFrame(mentor_ws.get_all_records())
        if 'id' in df.columns:
            df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"Gagal memuat data mentor: {e}")
        return pd.DataFrame() # Kembalikan DataFrame kosong jika gagal

def get_next_id():
    try:
        data = mentor_ws.get_all_values()
        if len(data) > 1: # Periksa apakah ada baris data selain header
            ids = [int(row[0]) for row in data[1:] if row[0].isdigit()]
            return max(ids) + 1
        return 1 # Jika tidak ada data atau hanya header, mulai dari 1
    except Exception as e:
        st.error(f"Gagal mendapatkan ID berikutnya: {e}")
        return 1

def tambah_mentor(nama, email):
    try:
        next_id = get_next_id()
        mentor_ws.append_row([next_id, nama, email])
        st.cache_data.clear() # Hapus cache setelah perubahan
        return True
    except Exception as e:
        st.error(f"Gagal menambahkan mentor: {e}")
        return False

# Fungsi untuk mendapatkan nomor baris fisik di sheet
def get_physical_row_index(df_index):
    # Baris pertama di sheet adalah header (indeks 0 di df)
    # Jadi, jika df_index = 0 (baris pertama data di df), di sheet adalah baris 2
    return df_index + 2

def update_mentor(df_index, nama, email):
    try:
        physical_row = get_physical_row_index(df_index)
        # Mengambil semua nilai di baris tersebut
        current_row_values = mentor_ws.row_values(physical_row)
        
        # Asumsikan kolom id di A, nama di B, email di C
        # Pastikan list cukup panjang sebelum mengakses indeks
        if len(current_row_values) < 3: # Memastikan ada setidaknya kolom A, B, C
            # Jika kolom belum ada, tambahkan placeholder atau tangani sesuai kebutuhan
            current_row_values.extend([''] * (3 - len(current_row_values))) 

        current_row_values[1] = nama # Kolom B (indeks 1)
        current_row_values[2] = email # Kolom C (indeks 2)
        
        # Perbarui baris di Google Sheets
        # Mengupdate seluruh baris dari kolom A
        mentor_ws.update(f'A{physical_row}', [current_row_values])
        st.cache_data.clear() # Hapus cache setelah perubahan
        return True
    except Exception as e:
        st.error(f"Gagal memperbarui mentor: {e}")
        return False

def hapus_mentor(df_index):
    try:
        physical_row = get_physical_row_index(df_index)
        # PASTIKAN physical_row adalah tipe int standar Python
        mentor_ws.delete_rows(int(physical_row))
        st.cache_data.clear() # Hapus cache setelah perubahan
        return True
    except Exception as e:
        st.error(f"Gagal menghapus mentor: {e}")
        return False

# --- UI Halaman Utama ---
st.title("👨‍🏫 Manajemen Data Mentor")
st.markdown("Halaman ini memungkinkan Anda untuk menambah, melihat, mengedit, dan menghapus data mentor.")
st.divider()

# Memuat data terbaru
data = load_data()

# Tampilkan Data Mentor
st.subheader("Daftar Mentor Aktif")
if data.empty:
    st.info("Tidak ada data mentor yang tersedia.")
else:
    # Optimasi tampilan dataframe
    st.dataframe(data.set_index('id'), use_container_width=True, hide_index=False)

st.divider()

# --- Form Tambah Mentor Baru ---
st.subheader("➕ Tambah Mentor Baru")
with st.form("form_tambah", clear_on_submit=True): # clear_on_submit untuk mengosongkan input setelah submit
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        nama_baru = st.text_input("Nama Mentor", placeholder="Masukkan nama lengkap")
    with col_input2:
        email_baru = st.text_input("Email", placeholder="mentor@example.com")
    
    st.markdown("Pastikan nama dan email mentor unik.")
    submit = st.form_submit_button("Tambahkan Mentor")
    
    if submit:
        if not nama_baru or not email_baru:
            st.warning("Nama dan Email tidak boleh kosong.")
        else:
            # Opsional: Tambahkan validasi format email sederhana
            if "@" not in email_baru or "." not in email_baru:
                st.warning("Format email tidak valid.")
            else:
                if tambah_mentor(nama_baru, email_baru):
                    st.success(f"Mentor '{nama_baru}' berhasil ditambahkan.")
                    st.rerun()
                else:
                    st.error("Gagal menambahkan mentor. Mohon coba lagi.")

st.divider()

# --- Bagian Edit / Hapus Mentor ---
st.subheader("✏️ Edit atau Hapus Mentor")
if not data.empty:
    mentor_options = {row['id']: row['nama'] for idx, row in data.iterrows()}
    
    selected_id = st.selectbox(
        "Pilih Mentor yang Ingin Diedit/Dihapus:",
        options=list(mentor_options.keys()),
        format_func=lambda x: f"{mentor_options[x]} (ID: {x})", # Tampilkan nama dan ID
        key="select_mentor_edit_delete"
    )
    
    # Ambil baris yang dipilih dari DataFrame yang dimuat
    selected_row_data = data[data['id'] == selected_id].iloc[0]
    # 'df_idx_for_update_delete' adalah index baris DataFrame pandas
    df_idx_for_update_delete = selected_row_data.name 

    st.markdown(f"**Anda memilih:** {selected_row_data['nama']} (ID: {selected_row_data['id']})")

    # --- FORM UNTUK EDIT DATA ---
    # Tombol "Simpan Perubahan" HARUS di dalam form ini
    with st.form("form_edit_data_mentor"): # Ubah key form agar lebih spesifik
        nama_edit = st.text_input("Nama", value=selected_row_data['nama'], key="edit_nama_mentor")
        email_edit = st.text_input("Email", value=selected_row_data['email'], key="edit_email_mentor")
        
        # Tombol submit untuk EDIT (ini adalah st.form_submit_button)
        if st.form_submit_button("💾 Simpan Perubahan", type="primary"):
            if not nama_edit or not email_edit:
                st.warning("Nama dan Email tidak boleh kosong.")
            else:
                if update_mentor(df_idx_for_update_delete, nama_edit, email_edit):
                    st.success(f"Data mentor '{nama_edit}' berhasil diperbarui.")
                    st.rerun()
                else:
                    st.error("Gagal memperbarui mentor. Mohon coba lagi.")
    
    # --- TOMBOL HAPUS DAN LOGIKA KONFIRMASI DILUAR FORM EDIT ---
    # Inisialisasi state jika belum ada
    if 'delete_confirm' not in st.session_state:
        st.session_state.delete_confirm = False

    # Tombol "Hapus Mentor" ini adalah st.button() biasa,
    # dan HARUS ditempatkan di luar st.form() yang lain.
    col_del_btn, _ = st.columns([0.3, 0.7]) # Kolom untuk tombol hapus
    with col_del_btn:
        delete_button_triggered = st.button("🗑️ Hapus Mentor", key="trigger_delete_flow", type="secondary")

    if delete_button_triggered:
        st.session_state.delete_confirm = True # Set state untuk menampilkan konfirmasi
        # Tidak perlu st.rerun() di sini, karena konfirmasi akan muncul di bawah

    # Logika konfirmasi dan tombol "Ya/Tidak" HARUS di luar form edit data
    if st.session_state.delete_confirm:
        st.warning(f"Anda yakin ingin menghapus mentor '{selected_row_data['nama']}' (ID: {selected_row_data['id']})? Tindakan ini tidak dapat dibatalkan.")
        col_confirm_del1, col_confirm_del2 = st.columns(2)
        with col_confirm_del1:
            # Ini juga st.button() biasa
            if st.button("✅ Ya, Hapus Sekarang!", key="confirm_delete_yes_final"):
                if hapus_mentor(df_idx_for_update_delete):
                    st.success("Mentor berhasil dihapus.")
                    st.session_state.delete_confirm = False # Reset state
                    st.rerun()
                else:
                    st.error("Gagal menghapus mentor. Mohon coba lagi.")
        with col_confirm_del2:
            # Ini juga st.button() biasa
            if st.button("❌ Tidak, Batalkan", key="confirm_delete_no_final"):
                st.session_state.delete_confirm = False # Reset state
                st.info("Penghapusan dibatalkan.")
                st.rerun() # Refresh untuk menghilangkan pesan konfirmasi

else:
    st.info("Tidak ada mentor untuk diedit atau dihapus.")