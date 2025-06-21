import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils.auth_utils import require_admin

# --- Cek Login dan Role Admin ---
require_admin()

# --- Setup Google Sheets ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    CREDS = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    CLIENT = gspread.authorize(CREDS)
    SHEET = CLIENT.open(st.secrets["sheet_name"])
    mentor_ws = SHEET.worksheet("mentor")
except Exception as e:
    st.error(f"Gagal mengakses Google Sheets: {e}. Pastikan kredensial service account benar di `secrets.toml` dan Google Sheets API aktif.")
    st.stop()

# --- Fungsi ---
def load_data():
    df = pd.DataFrame(mentor_ws.get_all_records())
    if 'id' in df.columns:
        df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
    return df

def tambah_mentor(nama, email):
    try:
        data = mentor_ws.get_all_values()
        next_id = 1
        if len(data) > 1:
            ids = [int(row[0]) for row in data[1:] if row[0].isdigit()]
            next_id = max(ids) + 1
        mentor_ws.append_row([next_id, nama, email])
        return True
    except Exception as e:
        st.error(f"Gagal menambahkan mentor: {e}")
        return False

def update_mentor(row_index, nama, email):
    try:
        mentor_ws.update(f'B{row_index+2}', nama)
        mentor_ws.update(f'C{row_index+2}', email)
        return True
    except Exception as e:
        st.error(f"Gagal memperbarui mentor: {e}")
        return False

def hapus_mentor(row_index):
    try:
        mentor_ws.delete_rows(row_index + 2)
        return True
    except Exception as e:
        st.error(f"Gagal menghapus mentor: {e}")
        return False

# --- UI ---
st.title("👨‍🏫 Manajemen Data Mentor")
data = load_data()

if data.empty:
    st.warning("Tidak ada data mentor.")
else:
    st.dataframe(data)

st.markdown("### ➕ Tambah Mentor Baru")
with st.form("form_tambah"):
    nama_baru = st.text_input("Nama Mentor")
    email_baru = st.text_input("Email")
    submit = st.form_submit_button("Tambah")
    if submit and nama_baru and email_baru:
        if tambah_mentor(nama_baru, email_baru):
            st.success("Mentor berhasil ditambahkan.")
            st.rerun() # Diperbarui: st.experimental_rerun() -> st.rerun()

st.markdown("---")
st.markdown("### ✏️ Edit / Hapus Mentor")
if not data.empty:
    mentor_options = {row['id']: row['nama'] for idx, row in data.iterrows()}
    selected_id = st.selectbox("Pilih mentor", list(mentor_options.keys()), format_func=lambda x: mentor_options[x])
    selected_row = data[data['id'] == selected_id].iloc[0]
    idx = selected_row.name

    nama_edit = st.text_input("Nama", value=selected_row['nama'], key="edit_nama")
    email_edit = st.text_input("Email", value=selected_row['email'], key="edit_email")
    col1, col2 = st.columns(2)
    if col1.button("💾 Simpan Perubahan"):
        if update_mentor(idx, nama_edit, email_edit):
            st.success("Data mentor diperbarui.")
            st.rerun() # Diperbarui: st.experimental_rerun() -> st.rerun()
    if col2.button("🗑️ Hapus Mentor"):
        if st.confirm("Yakin ingin menghapus mentor ini?"):
            if hapus_mentor(idx):
                st.success("Mentor dihapus.")
                st.rerun() # Diperbarui: st.experimental_rerun() -> st.rerun()