import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils.auth_utils import require_login, require_admin, require_mentor

# --- Cek Login ---
require_login()

role = st.session_state.get("role")
mentor_id = st.session_state.get("mentor_id")

# --- Setup Google Sheets ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    CREDS = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
    CLIENT = gspread.authorize(CREDS)
    SHEET = CLIENT.open("Presensi Mentoring STT NF")
    mentee_ws = SHEET.worksheet("mentee")
    mentor_ws = SHEET.worksheet("mentor")
except Exception as e:
    st.error(f"Gagal membuka Google Sheets: {e}")
    st.stop()

# --- Load Data ---
def load_data():
    df = pd.DataFrame(mentee_ws.get_all_records())
    for col in ['id', 'mentor_id']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    return df

def load_mentor_map():
    df = pd.DataFrame(mentor_ws.get_all_records())
    df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
    return dict(zip(df['id'], df['nama']))

def tambah_mentee(nama, kelompok, mentor_id):
    try:
        rows = mentee_ws.get_all_values()
        next_id = 1
        if len(rows) > 1:
            ids = [int(row[0]) for row in rows[1:] if row[0].isdigit()]
            next_id = max(ids) + 1
        mentee_ws.append_row([next_id, nama, kelompok, int(mentor_id)])
        return True
    except Exception as e:
        st.error(f"Gagal menambahkan mentee: {e}")
        return False

def update_mentee(row_index, nama, kelompok, mentor_id):
    try:
        mentee_ws.update(f'B{row_index+2}', nama)
        mentee_ws.update(f'C{row_index+2}', kelompok)
        mentee_ws.update(f'D{row_index+2}', int(mentor_id))
        return True
    except Exception as e:
        st.error(f"Gagal memperbarui mentee: {e}")
        return False

def hapus_mentee(row_index):
    try:
        mentee_ws.delete_rows(row_index + 2)
        return True
    except Exception as e:
        st.error(f"Gagal menghapus mentee: {e}")
        return False

# --- UI ---
st.title("🧑‍🎓 Manajemen Data Mentee")
data = load_data()
mentor_map = load_mentor_map()

if role == "Mentor":
    require_mentor()
    st.subheader("👥 Data Kelompok Saya")
    kelompok_saya = data[data['mentor_id'] == mentor_id]
    if kelompok_saya.empty:
        st.info("Belum ada mentee dalam kelompok Anda.")
    else:
        display_kelompok_saya = kelompok_saya.copy()
        display_kelompok_saya['Nama Mentor'] = display_kelompok_saya['mentor_id'].map(mentor_map)
        st.dataframe(display_kelompok_saya[['id', 'nama', 'kelompok', 'Nama Mentor']], use_container_width=True)

elif role == "Admin":
    require_admin()
    st.dataframe(data)
    st.markdown("### ➕ Tambah Mentee Baru")
    with st.form("form_tambah_mentee"):
        nama_baru = st.text_input("Nama Mentee")
        kelompok_baru = st.text_input("Kelompok")
        if mentor_map:
            mentor_pilihan = st.selectbox("Pilih Mentor", options=list(mentor_map.keys()), format_func=lambda x: mentor_map[x])
        else:
            st.warning("Tidak ada data mentor. Harap tambahkan mentor terlebih dahulu di halaman Data Mentor.")
            mentor_pilihan = None
            
        submit = st.form_submit_button("Tambah")
        if submit and nama_baru and kelompok_baru and mentor_pilihan is not None:
            if tambah_mentee(nama_baru, kelompok_baru, mentor_pilihan):
                st.success("Mentee berhasil ditambahkan.")
                st.rerun() # Diperbarui: st.experimental_rerun() -> st.rerun()

    st.markdown("---")
    st.markdown("### ✏️ Edit / Hapus Mentee")
    if not data.empty:
        mentee_options = {row['id']: row['nama'] for idx, row in data.iterrows()}
        selected_id = st.selectbox("Pilih mentee", list(mentee_options.keys()), format_func=lambda x: mentee_options[x])
        selected_row = data[data['id'] == selected_id].iloc[0]
        idx = selected_row.name

        nama_edit = st.text_input("Nama", value=selected_row['nama'], key="edit_nama")
        kelompok_edit = st.text_input("Kelompok", value=selected_row['kelompok'], key="edit_kelompok")
        
        if mentor_map and selected_row['mentor_id'] in mentor_map:
            mentor_edit_index = list(mentor_map.keys()).index(selected_row['mentor_id'])
            mentor_edit = st.selectbox("Pilih Mentor", list(mentor_map.keys()), index=mentor_edit_index, format_func=lambda x: mentor_map[x], key="edit_mentor")
        else:
            st.warning("Data mentor tidak lengkap atau mentee ini tidak memiliki mentor yang valid.")
            mentor_edit = None

        col1, col2 = st.columns(2)
        if col1.button("💾 Simpan Perubahan"):
            if nama_edit and kelompok_edit and mentor_edit is not None:
                if update_mentee(idx, nama_edit, kelompok_edit, mentor_edit):
                    st.success("Data mentee diperbarui.")
                    st.rerun() # Diperbarui: st.experimental_rerun() -> st.rerun()
            else:
                st.error("Nama, Kelompok, dan Mentor tidak boleh kosong.")
        if col2.button("🗑️ Hapus Mentee"):
            if st.confirm("Yakin ingin menghapus mentee ini?"):
                if hapus_mentee(idx):
                    st.success("Mentee dihapus.")
                    st.rerun() # Diperbarui: st.experimental_rerun() -> st.rerun()
    else:
        st.info("Tidak ada mentee untuk diedit atau dihapus.")
else:
    st.error("Peran tidak dikenali.")