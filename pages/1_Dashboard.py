import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils.auth_utils import require_login

# --- Cek Login ---
require_login()

role = st.session_state.get("role")
mentor_id = st.session_state.get("mentor_id")
user_name = st.session_state.get("user_name")

# --- Setup Google Sheets ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
mentor_df = pd.DataFrame()
mentee_df = pd.DataFrame()
presensi_df = pd.DataFrame()
CLIENT = None
SHEET = None

try:
    CREDS = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    CLIENT = gspread.authorize(CREDS)
    SHEET = CLIENT.open(st.secrets["sheet_name"])

    mentor_df = pd.DataFrame(SHEET.worksheet("mentor").get_all_records())
    mentee_df = pd.DataFrame(SHEET.worksheet("mentee").get_all_records())
    presensi_df = pd.DataFrame(SHEET.worksheet("presensi").get_all_records())

# Hapus FileNotFoundError
except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat data dari Google Sheets: {e}. Pastikan kredensial service account benar di `secrets.toml` dan Google Sheets API aktif.")
    st.stop()

# --- Konversi tipe data numerik dan olah status_kehadiran ---
# Kolom 'id', 'mentor_id', 'mentee_id', 'pertemuan' tetap numerik
for df_var in ['mentor_df', 'mentee_df', 'presensi_df']:
    df = locals()[df_var] # Get DataFrame from local variables
    for col in ['id', 'mentor_id', 'mentee_id', 'pertemuan']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    locals()[df_var] = df # Update DataFrame in local variables

# OLah kolom 'status_kehadiran' di presensi_df
if 'status_kehadiran' in presensi_df.columns:
    # Buat kolom numerik 'hadir_hitung' untuk perhitungan rata-rata (Hadir=1, Lainnya=0)
    presensi_df['hadir_hitung'] = presensi_df['status_kehadiran'].apply(lambda x: 1 if x == 'Hadir' else 0)
else:
    st.warning("Kolom 'status_kehadiran' tidak ditemukan di data presensi. Pastikan Google Sheet sudah diperbarui.")
    presensi_df['hadir_hitung'] = 0 # Fallback jika kolom tidak ada

# --- Header Halaman ---
st.title(f"📊 Dashboard {role}")
st.markdown(f"Selamat datang di dashboard, **{user_name}**!")

if role == "Admin":
    # --- Kartu Statistik ---
    col1, col2, col3 = st.columns(3)
    col1.metric("👨‍🏫 Total Mentor", len(mentor_df))
    col2.metric("🧑‍🎓 Total Mentee", len(mentee_df))
    col3.metric("🗓️ Total Presensi Dicatat", len(presensi_df)) # Ubah teks

    # --- Grafik Kehadiran per Pertemuan (Admin) ---
    st.subheader("📈 Rata-rata Kehadiran Mentee per Pertemuan (Hanya Status 'Hadir')")
    if not presensi_df.empty and 'hadir_hitung' in presensi_df.columns:
        # Rata-rata kehadiran dihitung dari 'hadir_hitung'
        avg_hadir_per_pertemuan = presensi_df.groupby("pertemuan")["hadir_hitung"].mean().reset_index()
        avg_hadir_per_pertemuan['Rata-rata Kehadiran (%)'] = avg_hadir_per_pertemuan['hadir_hitung'] * 100
        fig_avg = px.bar(avg_hadir_per_pertemuan, x="pertemuan", y="Rata-rata Kehadiran (%)",
                         title="Rata-rata Kehadiran Mentee (Hanya Hadir)",
                         labels={"pertemuan": "Pertemuan Ke-", "Rata-rata Kehadiran (%)": "Rata-rata Kehadiran (%)"},
                         text_auto=True) # Tambahkan label nilai di atas bar
        fig_avg.update_traces(marker_color='skyblue')
        st.plotly_chart(fig_avg)

        # --- Distribusi Status Kehadiran Keseluruhan (Admin) ---
        st.subheader("📊 Distribusi Status Kehadiran Keseluruhan")
        status_counts = presensi_df['status_kehadiran'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Jumlah']
        fig_pie = px.pie(status_counts, values='Jumlah', names='Status',
                         title='Persentase Status Kehadiran',
                         color_discrete_sequence=px.colors.qualitative.Pastel) # Warna yang lebih lembut
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie)

    else:
        st.info("Belum ada data presensi atau kolom 'status_kehadiran' tidak ditemukan.")

elif role == "Mentor":
    st.subheader(f"📋 Data Kelompok Mentor: {user_name} (ID: {mentor_id})")
    mentee_saya = mentee_df[mentee_df["mentor_id"] == mentor_id]
    st.metric("Jumlah Mentee di Kelompok Anda", len(mentee_saya))

    presensi_saya = presensi_df[presensi_df["mentee_id"].isin(mentee_saya["id"])]

    if not presensi_saya.empty and 'hadir_hitung' in presensi_saya.columns:
        # Rata-rata kehadiran per pertemuan untuk kelompok mentor
        st.subheader("📈 Rata-rata Kehadiran Kelompok Anda per Pertemuan (Hanya Status 'Hadir')")
        avg_hadir_kelompok = presensi_saya.groupby("pertemuan")["hadir_hitung"].mean().reset_index()
        avg_hadir_kelompok['Rata-rata Kehadiran (%)'] = avg_hadir_kelompok['hadir_hitung'] * 100
        fig_kelompok_avg = px.bar(avg_hadir_kelompok, x="pertemuan", y="Rata-rata Kehadiran (%)",
                                 title="Rata-rata Kehadiran Kelompok Anda",
                                 labels={"pertemuan": "Pertemuan Ke-", "Rata-rata Kehadiran (%)": "Rata-rata Kehadiran (%)"},
                                 text_auto=True)
        fig_kelompok_avg.update_traces(marker_color='lightcoral')
        st.plotly_chart(fig_kelompok_avg)

        # --- Distribusi Status Kehadiran Kelompok (Mentor) ---
        st.subheader("📊 Distribusi Status Kehadiran Kelompok Anda")
        status_counts_kelompok = presensi_saya['status_kehadiran'].value_counts().reset_index()
        status_counts_kelompok.columns = ['Status', 'Jumlah']
        fig_pie_kelompok = px.pie(status_counts_kelompok, values='Jumlah', names='Status',
                                  title='Persentase Status Kehadiran Kelompok Anda',
                                  color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie_kelompok.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie_kelompok)

        st.subheader("📋 Detail Presensi Kelompok Anda")
        # Gabungkan dengan nama mentee
        presensi_detail = presensi_saya.merge(mentee_saya[['id', 'nama']], left_on='mentee_id', right_on='id', suffixes=('', '_mentee'))
        # Tampilkan kolom status_kehadiran
        presensi_detail = presensi_detail[['tanggal', 'pertemuan', 'nama', 'status_kehadiran']]
        st.dataframe(presensi_detail.rename(columns={'nama': 'Nama Mentee', 'status_kehadiran': 'Status Kehadiran'}), use_container_width=True)

    else:
        st.info("Belum ada data presensi untuk kelompok Anda atau kolom 'status_kehadiran' tidak ditemukan.")
else:
    st.error("Peran tidak dikenali.")

st.markdown("---")
# Add a logout button
if st.button("Logout"):
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["user_name"] = None
    st.session_state["mentor_id"] = None
    st.success("Anda telah berhasil logout.")
    st.switch_page("app.py")

st.button("Kembali ke Beranda Utama", on_click=lambda: st.switch_page("app.py"))