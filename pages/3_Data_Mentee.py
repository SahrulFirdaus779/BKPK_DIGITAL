import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils.auth_utils import require_admin, require_login # Pastikan ini mengarah ke fungsi yang benar

# --- Cek Login dan Role Admin ---
# Hanya admin yang bisa mengelola data mentee secara penuh (CRUD)
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
mentee_ws = SHEET.worksheet("mentee")
mentor_ws = SHEET.worksheet("mentor") # Perlu akses ke sheet mentor untuk dropdown mentor

# --- Fungsi (Menggunakan st.cache_data untuk data) ---
@st.cache_data(ttl=60) # Cache data mentee selama 60 detik
def load_mentee_data():
    try:
        df = pd.DataFrame(mentee_ws.get_all_records())
        if 'id' in df.columns:
            df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
        if 'mentor_id' in df.columns:
            df['mentor_id'] = pd.to_numeric(df['mentor_id'], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"Gagal memuat data mentee: {e}")
        return pd.DataFrame() # Kembalikan DataFrame kosong jika gagal

@st.cache_data(ttl=60) # Cache data mentor map selama 60 detik
def load_mentor_map():
    try:
        df = pd.DataFrame(mentor_ws.get_all_records())
        df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
        return dict(zip(df['id'], df['nama']))
    except Exception as e:
        st.error(f"Gagal memuat data mentor untuk peta: {e}")
        return {}


def get_next_mentee_id():
    try:
        data = mentee_ws.get_all_values()
        if len(data) > 1: # Periksa apakah ada baris data selain header
            # Mengambil ID dari kolom pertama, mengabaikan yang kosong atau non-digit
            ids = [int(row[0]) for row in data[1:] if row and row[0] and str(row[0]).isdigit()]
            if ids:
                return max(ids) + 1
        return 1 # Jika tidak ada data atau hanya header, mulai dari 1
    except Exception as e:
        st.error(f"Gagal mendapatkan ID mentee berikutnya: {e}")
        return 1

def tambah_mentee(nama, kelompok, mentor_id):
    try:
        next_id = get_next_mentee_id()
        mentee_ws.append_row([next_id, nama, kelompok, int(mentor_id)])
        load_mentee_data.clear() # Hapus cache setelah perubahan
        return True
    except Exception as e:
        st.error(f"Gagal menambahkan mentee: {e}")
        return False

# Fungsi untuk mendapatkan nomor baris fisik di sheet (untuk mentee)
def get_mentee_physical_row_index(df_index):
    # Baris pertama di sheet adalah header (indeks 0 di df)
    # Jadi, jika df_index = 0 (baris pertama data di df), di sheet adalah baris 2
    return df_index + 2

def update_mentee(df_index, nama, kelompok, mentor_id):
    try:
        physical_row = get_mentee_physical_row_index(df_index)
        
        # Ambil seluruh baris yang ada untuk memastikan ID tidak berubah
        current_row_values = mentee_ws.row_values(physical_row)

        # Pastikan list cukup panjang sebelum mengakses indeks
        # ID (kolom A - indeks 0), Nama (B - indeks 1), Kelompok (C - indeks 2), Mentor_ID (D - indeks 3)
        if len(current_row_values) < 4: 
            current_row_values.extend([''] * (4 - len(current_row_values))) 

        current_row_values[1] = nama       # Kolom B (nama)
        current_row_values[2] = kelompok   # Kolom C (kelompok)
        current_row_values[3] = int(mentor_id) # Kolom D (mentor_id)
        
        # Perbarui seluruh baris di Google Sheets
        mentee_ws.update(f'A{physical_row}', [current_row_values])
        load_mentee_data.clear() # Hapus cache setelah perubahan
        return True
    except Exception as e:
        st.error(f"Gagal memperbarui mentee: {e}")
        return False

def hapus_mentee(df_index):
    try:
        physical_row = get_mentee_physical_row_index(df_index)
        mentee_ws.delete_rows(int(physical_row))
        load_mentee_data.clear() # Hapus cache setelah perubahan
        return True
    except Exception as e:
        st.error(f"Gagal menghapus mentee: {e}")
        return False

# --- UI Halaman Utama ---
st.title("🧑‍🎓 Manajemen Data Mentee")
st.markdown("Halaman ini memungkinkan Anda untuk menambah, melihat, mengedit, dan menghapus data mentee.")

st.divider()

# Memuat data terbaru
mentee_data = load_mentee_data()
mentor_map = load_mentor_map()

# Tampilkan Data Mentee
st.subheader("Daftar Mentee Aktif")
if mentee_data.empty:
    st.info("Tidak ada data mentee yang tersedia.")
else:
    # Gabungkan nama mentor ke dalam DataFrame untuk tampilan yang lebih baik
    mentee_data['Nama Mentor'] = mentee_data['mentor_id'].map(mentor_map).fillna('Tidak Ditemukan')
    st.dataframe(mentee_data[['id', 'nama', 'kelompok', 'Nama Mentor']].set_index('id'), use_container_width=True, hide_index=False)

st.divider()

# --- Form Tambah Mentee Baru ---
st.subheader("➕ Tambah Mentee Baru")
with st.form("form_tambah_mentee", clear_on_submit=True):
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        nama_baru = st.text_input("Nama Mentee", placeholder="Masukkan nama lengkap mentee")
    with col_input2:
        kelompok_baru = st.text_input("Kelompok", placeholder="Contoh: A1")
    
    selected_mentor_id_add = None
    if mentor_map:
        # Menambahkan 'Pilih Mentor' sebagai opsi pertama
        mentor_options_for_select = {0: "--- Pilih Mentor ---"}
        mentor_options_for_select.update(mentor_map)

        selected_mentor_id_add = st.selectbox(
            "Pilih Mentor",
            options=list(mentor_options_for_select.keys()),
            format_func=lambda x: mentor_options_for_select[x]
        )
    else:
        st.warning("Tidak ada data mentor. Harap tambahkan mentor terlebih dahulu di halaman Data Mentor.")
        
    st.markdown("Pastikan data mentee diisi dengan lengkap.")
    submit = st.form_submit_button("Tambahkan Mentee")
    
    if submit:
        if not nama_baru or not kelompok_baru or selected_mentor_id_add is None or selected_mentor_id_add == 0:
            st.warning("Nama, Kelompok, dan Mentor tidak boleh kosong.")
        else:
            if tambah_mentee(nama_baru, kelompok_baru, selected_mentor_id_add):
                st.success(f"Mentee '{nama_baru}' berhasil ditambahkan.")
                st.rerun()
            else:
                st.error("Gagal menambahkan mentee. Mohon coba lagi.")

st.divider()

# --- Bagian Edit / Hapus Mentee ---
st.subheader("✏️ Edit atau Hapus Mentee")
if not mentee_data.empty:
    mentee_options = {row['id']: row['nama'] for idx, row in mentee_data.iterrows()}
    
    selected_id = st.selectbox(
        "Pilih Mentee yang Ingin Diedit/Dihapus:",
        options=list(mentee_options.keys()),
        format_func=lambda x: f"{mentee_options[x]} (ID: {x})", # Tampilkan nama dan ID
        key="select_mentee_edit_delete"
    )
    
    # Ambil baris yang dipilih dari DataFrame yang dimuat
    selected_row_data = mentee_data[mentee_data['id'] == selected_id].iloc[0]
    # 'df_idx_for_update_delete' adalah index baris DataFrame pandas
    df_idx_for_update_delete = selected_row_data.name 

    st.markdown(f"**Anda memilih:** {selected_row_data['nama']} (ID: {selected_row_data['id']})")

    # --- FORM UNTUK EDIT DATA ---
    with st.form("form_edit_data_mentee"): 
        nama_edit = st.text_input("Nama", value=selected_row_data['nama'], key="edit_nama_mentee")
        kelompok_edit = st.text_input("Kelompok", value=selected_row_data['kelompok'], key="edit_kelompok_mentee")
        
        selected_mentor_id_edit = None
        if mentor_map:
            # Pastikan mentor_id mentee yang dipilih ada di mentor_map
            initial_mentor_index = list(mentor_map.keys()).index(selected_row_data['mentor_id']) if selected_row_data['mentor_id'] in mentor_map else 0 # Default ke opsi pertama jika tidak ditemukan
            
            selected_mentor_id_edit = st.selectbox(
                "Pilih Mentor",
                options=list(mentor_map.keys()),
                format_func=lambda x: mentor_map[x],
                index=initial_mentor_index,
                key="edit_mentor_mentee"
            )
        else:
            st.warning("Tidak ada data mentor yang tersedia untuk dipilih.")
            
        # Tombol submit untuk EDIT
        if st.form_submit_button("💾 Simpan Perubahan", type="primary"):
            if not nama_edit or not kelompok_edit or selected_mentor_id_edit is None:
                st.warning("Nama, Kelompok, dan Mentor tidak boleh kosong.")
            else:
                if update_mentee(df_idx_for_update_delete, nama_edit, kelompok_edit, selected_mentor_id_edit):
                    st.success(f"Data mentee '{nama_edit}' berhasil diperbarui.")
                    st.rerun()
                else:
                    st.error("Gagal memperbarui mentee. Mohon coba lagi.")
    
    # --- TOMBOL HAPUS DAN LOGIKA KONFIRMASI DILUAR FORM EDIT ---
    if 'delete_mentee_confirm' not in st.session_state:
        st.session_state.delete_mentee_confirm = False

    col_del_btn, _ = st.columns([0.3, 0.7]) 
    with col_del_btn:
        delete_button_triggered = st.button("🗑️ Hapus Mentee", key="trigger_delete_mentee_flow", type="secondary")

    if delete_button_triggered:
        st.session_state.delete_mentee_confirm = True 

    if st.session_state.delete_mentee_confirm:
        st.warning(f"Anda yakin ingin menghapus mentee '{selected_row_data['nama']}' (ID: {selected_row_data['id']})? Tindakan ini tidak dapat dibatalkan.")
        col_confirm_del1, col_confirm_del2 = st.columns(2)
        with col_confirm_del1:
            if st.button("✅ Ya, Hapus Sekarang!", key="confirm_delete_mentee_yes_final"):
                if hapus_mentee(df_idx_for_update_delete):
                    st.success("Mentee berhasil dihapus.")
                    st.session_state.delete_mentee_confirm = False 
                    st.rerun()
                else:
                    st.error("Gagal menghapus mentee. Mohon coba lagi.")
        with col_confirm_del2:
            if st.button("❌ Tidak, Batalkan", key="confirm_delete_mentee_no_final"):
                st.session_state.delete_mentee_confirm = False 
                st.info("Penghapusan dibatalkan.")
                st.rerun() 

else:
    st.info("Tidak ada mentee untuk diedit atau dihapus.")