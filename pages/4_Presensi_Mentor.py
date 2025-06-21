import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from utils.auth_utils import require_mentor

# --- Cek Login dan Role ---
require_mentor()
mentor_id = st.session_state.get("mentor_id")

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

# --- Load Mentee Sesuai Mentor ---
def load_mentees():
    df = pd.DataFrame(mentee_ws.get_all_records())
    df['mentor_id'] = pd.to_numeric(df['mentor_id'], errors='coerce').fillna(0).astype(int)
    df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
    return df[df['mentor_id'] == mentor_id]

# --- Simpan Presensi ---
# Fungsi simpan_presensi diperbarui untuk menerima 'status_kehadiran'
def simpan_presensi(mentee_id, tanggal, pertemuan, status_kehadiran):
    try:
        rows = presensi_ws.get_all_values()
        next_id = 1
        if len(rows) > 1:
            # Pastikan ID kolom pertama (indeks 0) dan hanya ambil yang digit
            ids = [int(row[0]) for row in rows[1:] if len(row) > 0 and row[0].isdigit()]
            if ids: # Hanya jika ada ID yang valid
                next_id = max(ids) + 1
        
        # Perhatikan urutan kolom: ID, mentee_id, tanggal, pertemuan, status_kehadiran
        presensi_ws.append_row([next_id, int(mentee_id), tanggal, int(pertemuan), status_kehadiran])
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan presensi mentee ID {mentee_id}: {e}")
        return False

# --- UI ---
st.title("📝 Form Presensi Mentee oleh Mentor")
st.info(f"Anda login sebagai Mentor (ID: {mentor_id})")

mentees = load_mentees()
if mentees.empty:
    st.warning("Belum ada mentee dalam kelompok Anda.")
    st.stop()

pertemuan = st.number_input("Pertemuan ke-", min_value=1, step=1)
tanggal = st.date_input("Tanggal", value=datetime.today())
st.markdown("### Daftar Mentee dan Kehadiran")

# Opsi status kehadiran
status_options = ["Hadir", "Sakit", "Izin", "Alfa"]
kehadiran_dict = {}

for idx, row in mentees.iterrows():
    mentee_id = row['id']
    nama = row['nama']
    kelompok = row.get('kelompok', '-')
    
    # Menggunakan st.radio untuk pilihan status kehadiran
    selected_status = st.radio(
        f"Status Kehadiran {nama} (Kelompok {kelompok})",
        options=status_options,
        index=0, # Default: Hadir
        key=f"status_{mentee_id}",
        horizontal=True # Tampilkan pilihan secara horizontal
    )
    kehadiran_dict[mentee_id] = selected_status

if st.button("💾 Simpan Presensi"):
    if not kehadiran_dict:
        st.error("Tidak ada mentee yang dipilih.")
    else:
        all_ok = True
        for mentee_id, status_kehadiran in kehadiran_dict.items():
            if not simpan_presensi(mentee_id, tanggal.strftime("%Y-%m-%d"), pertemuan, status_kehadiran):
                all_ok = False
        if all_ok:
            st.success("Presensi berhasil disimpan.")
            st.rerun()