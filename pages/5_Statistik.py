import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
import io
from oauth2client.service_account import ServiceAccountCredentials
from utils.auth_utils import require_login

# --- Cek Login ---
require_login()
role = st.session_state.get("role")
mentor_id = st.session_state.get("mentor_id")
user_name = st.session_state.get("user_name") # Ambil nama pengguna untuk tampilan

# --- Setup Google Sheets ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    CREDS = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
    CLIENT = gspread.authorize(CREDS)
    SHEET = CLIENT.open("Presensi Mentoring STT NF")
    presensi_df = pd.DataFrame(SHEET.worksheet("presensi").get_all_records())
    mentee_df = pd.DataFrame(SHEET.worksheet("mentee").get_all_records())
    mentor_df = pd.DataFrame(SHEET.worksheet("mentor").get_all_records()) # Perlu untuk filter dan nama mentor
except Exception as e:
    st.error(f"Gagal mengakses Google Sheets: {e}")
    st.stop()

# --- Konversi numerik dan olah status_kehadiran ---
# Daftar nama variabel DataFrame yang akan diolah
list_of_dfs_to_process = [presensi_df, mentee_df, mentor_df] # Ini adalah daftar OBJEK DataFrame
# Sekarang, iterasi langsung OBJEK DataFrame-nya, BUKAN string namanya di locals()
for df_to_process in list_of_dfs_to_process:
    for col in ['id', 'mentee_id', 'mentor_id', 'pertemuan']:
        if col in df_to_process.columns:
            df_to_process[col] = pd.to_numeric(df_to_process[col], errors='coerce').fillna(0).astype(int)

# Olah kolom 'status_kehadiran' di presensi_df
if 'status_kehadiran' in presensi_df.columns:
    presensi_df['is_hadir'] = presensi_df['status_kehadiran'].apply(lambda x: 1 if x == 'Hadir' else 0)
else:
    st.warning("Kolom 'status_kehadiran' tidak ditemukan di data presensi. Pastikan Google Sheet sudah diperbarui.")
    presensi_df['is_hadir'] = 0 # Fallback

# Gabungkan mentee_df dengan nama mentor untuk memudahkan analisis
if 'mentor_id' in mentee_df.columns and 'id' in mentor_df.columns and 'nama' in mentor_df.columns:
    mentor_names = mentor_df.set_index('id')['nama'].to_dict()
    mentee_df['nama_mentor'] = mentee_df['mentor_id'].map(mentor_names)
else:
    mentee_df['nama_mentor'] = 'Tidak Diketahui' # Fallback

# --- Filter Berdasarkan Role ---
st.title(f"📊 Statistik Presensi {user_name if role=='Mentor' else ''}")

filtered_presensi_df = presensi_df.copy()
filtered_mentee_df = mentee_df.copy()

if role == "Mentor":
    filtered_mentee_df = mentee_df[mentee_df['mentor_id'] == mentor_id]
    filtered_presensi_df = presensi_df[presensi_df['mentee_id'].isin(filtered_mentee_df['id'])]
    if filtered_mentee_df.empty:
        st.info("Belum ada mentee dalam kelompok Anda untuk ditampilkan statistiknya.")
        st.stop()
elif role == "Admin":
    # Admin melihat semua data, tidak perlu filter awal
    pass
else:
    st.error("Peran tidak dikenali.")
    st.stop()

# --- Merge dan Statistik ---
if not filtered_presensi_df.empty and not filtered_mentee_df.empty:
    df_merged = filtered_presensi_df.merge(filtered_mentee_df[['id', 'nama', 'kelompok', 'nama_mentor']],
                                       left_on="mentee_id", right_on="id", suffixes=("", "_mentee_info"))
    
    # --- Statistik Umum ---
    st.subheader("Ringkasan Kehadiran")
    total_presensi_dicatat = len(df_merged)
    total_hadir = df_merged['is_hadir'].sum()
    st.metric("Total Data Presensi Dicatat", total_presensi_dicatat)
    st.metric("Total Kehadiran 'Hadir'", total_hadir)

    # --- Grafik Kehadiran per Pertemuan (Hanya Hadir) ---
    st.subheader("📈 Rata-rata Kehadiran per Pertemuan (Status 'Hadir')")
    avg_kehadiran_per_pertemuan = df_merged.groupby("pertemuan")["is_hadir"].mean().reset_index()
    avg_kehadiran_per_pertemuan['Rata-rata Kehadiran (%)'] = avg_kehadiran_per_pertemuan['is_hadir'] * 100
    fig1 = px.bar(avg_kehadiran_per_pertemuan, x="pertemuan", y="Rata-rata Kehadiran (%)",
                  title="Rata-rata Kehadiran (Hanya Status 'Hadir')",
                  labels={"pertemuan": "Pertemuan Ke-", "Rata-rata Kehadiran (%)": "Rata-rata Kehadiran (%)"},
                  text_auto=True, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig1)

    # --- Distribusi Status Kehadiran per Pertemuan (Stacked Bar Chart) ---
    st.subheader("📊 Distribusi Status Kehadiran per Pertemuan")
    status_per_pertemuan = df_merged.groupby(["pertemuan", "status_kehadiran"]).size().reset_index(name='Jumlah')
    fig2 = px.bar(status_per_pertemuan, x="pertemuan", y="Jumlah", color="status_kehadiran",
                  title="Jumlah Mentee berdasarkan Status Kehadiran per Pertemuan",
                  labels={"pertemuan": "Pertemuan Ke-", "Jumlah": "Jumlah Mentee", "status_kehadiran": "Status Kehadiran"},
                  category_orders={"status_kehadiran": ["Hadir", "Sakit", "Izin", "Alfa"]},
                  text_auto=True, color_discrete_sequence=px.colors.qualitative.D3)
    fig2.update_layout(barmode='stack', xaxis_title="Pertemuan Ke-", yaxis_title="Jumlah Mentee")
    st.plotly_chart(fig2)

    # --- Distribusi Status Kehadiran Keseluruhan (Pie Chart) ---
    st.subheader("🥧 Distribusi Status Kehadiran Keseluruhan")
    total_status_counts = df_merged['status_kehadiran'].value_counts().reset_index()
    total_status_counts.columns = ['Status', 'Jumlah']
    fig3 = px.pie(total_status_counts, values='Jumlah', names='Status',
                  title='Persentase Keseluruhan Status Kehadiran',
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig3.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig3)

    # --- Rekap Kehadiran per Mentee ---
    st.subheader("📋 Rekap Kehadiran Mentee (Detail Status)")
    rekap_detail = df_merged.pivot_table(index=["mentee_id", "nama"],
                                         columns="status_kehadiran",
                                         values="is_hadir",
                                         aggfunc='count',
                                         fill_value=0).reset_index()

    rekap_detail.columns.name = None

    for status in ["Hadir", "Sakit", "Izin", "Alfa"]:
        if status not in rekap_detail.columns:
            rekap_detail[status] = 0
            
    total_pertemuan_tercatat = df_merged["pertemuan"].nunique()
    
    if 'Hadir' in rekap_detail.columns and total_pertemuan_tercatat > 0:
        rekap_detail["% Hadir Murni"] = (rekap_detail["Hadir"] / total_pertemuan_tercatat * 100).round(2)
    else:
        rekap_detail["% Hadir Murni"] = 0

    if role == "Admin":
        rekap_detail = rekap_detail.merge(filtered_mentee_df[['id', 'nama_mentor']], left_on='mentee_id', right_on='id', how='left', suffixes=('', '_mentee_name'))
        rekap_detail = rekap_detail.drop(columns='id_mentee_name')
        cols_order = ['mentee_id', 'nama', 'nama_mentor', 'Hadir', 'Sakit', 'Izin', 'Alfa', '% Hadir Murni']
        rekap_detail = rekap_detail[cols_order]
        st.dataframe(rekap_detail.rename(columns={
            'nama': 'Nama Mentee',
            'Hadir': 'Jml Hadir',
            'Sakit': 'Jml Sakit',
            'Izin': 'Jml Izin',
            'Alfa': 'Jml Alfa',
            '% Hadir Murni': '% Hadir'
        }), use_container_width=True)
    else:
        st.dataframe(rekap_detail.rename(columns={
            'nama': 'Nama Mentee',
            'Hadir': 'Jml Hadir',
            'Sakit': 'Jml Sakit',
            'Izin': 'Jml Izin',
            'Alfa': 'Jml Alfa',
            '% Hadir Murni': '% Hadir'
        }), use_container_width=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        rekap_detail.to_excel(writer, index=False, sheet_name="Rekap Presensi Detail")
    st.download_button("📥 Unduh Rekap Detail Excel", data=output.getvalue(), file_name="rekap_presensi_detail.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("Tidak ada data presensi yang tersedia untuk membuat statistik.")