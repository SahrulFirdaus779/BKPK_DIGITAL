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

# --- Fungsi Logout ---
def show_logout_button():
    st.sidebar.markdown("---") # Tambahkan garis pemisah di sidebar
    if st.sidebar.button("Keluar", key="logout_button"):
        st.session_state.clear() # Hapus semua sesi
        st.success("Anda telah berhasil keluar.")
        # Mengarahkan kembali ke halaman utama (login page)
        # Asumsi halaman utama adalah 'Home.py' atau semacamnya
        st.switch_page("app.py") # Ganti "Home.py" dengan nama file halaman utama Anda

# Panggil fungsi logout di awal script
show_logout_button()

# --- Setup Google Sheets dan Caching Data ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

@st.cache_data(ttl=300) # Cache data selama 5 menit
def load_google_sheet_data():
    """Memuat semua DataFrame dari Google Sheets dengan caching."""
    try:
        CREDS = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
        CLIENT = gspread.authorize(CREDS)
        SHEET = CLIENT.open("Presensi Mentoring STT NF")
        
        presensi_df_raw = pd.DataFrame(SHEET.worksheet("presensi").get_all_records())
        mentee_df_raw = pd.DataFrame(SHEET.worksheet("mentee").get_all_records())
        mentor_df_raw = pd.DataFrame(SHEET.worksheet("mentor").get_all_records())
        
        return presensi_df_raw, mentee_df_raw, mentor_df_raw
    except Exception as e:
        st.error(f"Gagal mengakses Google Sheets: {e}")
        st.stop()
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame() # Return empty DFs on failure

# Muat data dari Google Sheets
presensi_df_raw, mentee_df_raw, mentor_df_raw = load_google_sheet_data()

# Buat salinan untuk preprocessing agar tidak memodifikasi data cache
presensi_df = presensi_df_raw.copy()
mentee_df = mentee_df_raw.copy()
mentor_df = mentor_df_raw.copy()

# --- Preprocessing Data ---
# Konversi numerik untuk semua DataFrame yang relevan
for df_name, df_obj in [('presensi_df', presensi_df), ('mentee_df', mentee_df), ('mentor_df', mentor_df)]:
    cols_to_convert = ['id', 'mentee_id', 'mentor_id', 'pertemuan']
    for col in cols_to_convert:
        if col in df_obj.columns:
            df_obj[col] = pd.to_numeric(df_obj[col], errors='coerce').fillna(0).astype(int)

# Olah kolom 'status_kehadiran' di presensi_df
if 'status_kehadiran' in presensi_df.columns:
    presensi_df['is_hadir'] = presensi_df['status_kehadiran'].apply(lambda x: 1 if x == 'Hadir' else 0)
else:
    st.warning("Kolom 'status_kehadiran' tidak ditemukan di data presensi. Pastikan Google Sheet sudah diperbarui.")
    presensi_df['is_hadir'] = 0 # Fallback

# Gabungkan mentee_df dengan nama mentor
if 'mentor_id' in mentee_df.columns and 'id' in mentor_df.columns and 'nama' in mentor_df.columns:
    # Buat dictionary nama mentor dari mentor_df untuk mapping
    mentor_names = mentor_df.set_index('id')['nama'].to_dict()
    mentee_df['nama_mentor'] = mentee_df['mentor_id'].map(mentor_names)
else:
    mentee_df['nama_mentor'] = 'Tidak Diketahui' # Fallback

# --- Judul Halaman ---
st.title(f"📊 Statistik Presensi")
st.info(f"Halo, **{user_name}**! Anda login sebagai **{role}**.")

# --- Filter Data Berdasarkan Role dan Pilihan Pengguna ---
filtered_presensi_df = presensi_df.copy()
filtered_mentee_df = mentee_df.copy()

if role == "Mentor":
    filtered_mentee_df = mentee_df[mentee_df['mentor_id'] == mentor_id].copy()
    filtered_presensi_df = presensi_df[presensi_df['mentee_id'].isin(filtered_mentee_df['id'])].copy()
    
    if filtered_mentee_df.empty:
        st.info("Belum ada mentee dalam kelompok Anda untuk ditampilkan statistiknya.")
        st.stop()

elif role == "Admin":
    st.sidebar.subheader("Filter Data (Admin)")
    
    # Filter Mentor
    all_mentors_option = ['Semua Mentor'] + sorted(mentor_df['nama'].unique().tolist())
    selected_mentor_name = st.sidebar.selectbox("Pilih Mentor:", all_mentors_option, key="filter_mentor_admin")

    selected_mentor_id_for_filter = None
    if selected_mentor_name != 'Semua Mentor':
        # Pastikan mentor_df tidak kosong sebelum mencari ID
        if not mentor_df.empty and selected_mentor_name in mentor_df['nama'].values:
            selected_mentor_id_for_filter = mentor_df[mentor_df['nama'] == selected_mentor_name]['id'].iloc[0]
        else:
            st.sidebar.warning("Mentor tidak ditemukan dalam data master.")

    # Filter Mentee berdasarkan pilihan mentor
    if selected_mentor_id_for_filter is not None:
        filtered_mentee_df = mentee_df[mentee_df['mentor_id'] == selected_mentor_id_for_filter].copy()
    else:
        filtered_mentee_df = mentee_df.copy() # Tampilkan semua mentee jika "Semua Mentor"

    # Filter Presensi berdasarkan mentee yang sudah difilter
    filtered_presensi_df = presensi_df[presensi_df['mentee_id'].isin(filtered_mentee_df['id'])].copy()

    if filtered_mentee_df.empty or filtered_presensi_df.empty:
        st.info(f"Tidak ada data mentee atau presensi yang tersedia untuk kriteria filter yang dipilih ({selected_mentor_name}).")
        st.stop()
        
else:
    st.error("Peran tidak dikenali.")
    st.stop()

# --- Gabungkan DataFrame untuk Analisis ---
if not filtered_presensi_df.empty and not filtered_mentee_df.empty:
    df_merged = filtered_presensi_df.merge(filtered_mentee_df[['id', 'nama', 'kelompok', 'nama_mentor']],
                                           left_on="mentee_id", right_on="id", suffixes=("", "_mentee_info"))
    
    # Tampilkan navigasi menggunakan tabs
    tab1, tab2, tab3 = st.tabs(["Ringkasan Umum", "Tren Kehadiran", "Rekap Detail Mentee"])

    with tab1:
        st.subheader("Ringkasan Kehadiran Keseluruhan")
        col_total_presensi, col_total_hadir = st.columns(2)
        with col_total_presensi:
            st.metric("Total Data Presensi Dicatat", len(df_merged))
        with col_total_hadir:
            st.metric("Total Kehadiran 'Hadir'", df_merged['is_hadir'].sum())
        
        st.markdown("---")
        st.subheader("🥧 Distribusi Status Kehadiran Keseluruhan")
        total_status_counts = df_merged['status_kehadiran'].value_counts().reset_index()
        total_status_counts.columns = ['Status', 'Jumlah']
        fig3 = px.pie(total_status_counts, values='Jumlah', names='Status',
                      title='Persentase Keseluruhan Status Kehadiran',
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig3.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.subheader("📈 Rata-rata Kehadiran per Pertemuan (Status 'Hadir')")
        # Pastikan ada data sebelum menghitung rata-rata
        if not df_merged.empty and 'pertemuan' in df_merged.columns and 'is_hadir' in df_merged.columns:
            avg_kehadiran_per_pertemuan = df_merged.groupby("pertemuan")["is_hadir"].mean().reset_index()
            avg_kehadiran_per_pertemuan['Rata-rata Kehadiran (%)'] = (avg_kehadiran_per_pertemuan['is_hadir'] * 100).round(2)
            fig1 = px.bar(avg_kehadiran_per_pertemuan, x="pertemuan", y="Rata-rata Kehadiran (%)",
                          title="Rata-rata Kehadiran (Hanya Status 'Hadir')",
                          labels={"pertemuan": "Pertemuan Ke-", "Rata-rata Kehadiran (%)": "Rata-rata Kehadiran (%)"},
                          text_auto=True, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Tidak ada data untuk menghitung rata-rata kehadiran per pertemuan.")

        st.markdown("---")
        st.subheader("📊 Distribusi Status Kehadiran per Pertemuan")
        if not df_merged.empty and 'pertemuan' in df_merged.columns and 'status_kehadiran' in df_merged.columns:
            status_per_pertemuan = df_merged.groupby(["pertemuan", "status_kehadiran"]).size().reset_index(name='Jumlah')
            fig2 = px.bar(status_per_pertemuan, x="pertemuan", y="Jumlah", color="status_kehadiran",
                          title="Jumlah Mentee berdasarkan Status Kehadiran per Pertemuan",
                          labels={"pertemuan": "Pertemuan Ke-", "Jumlah": "Jumlah Mentee", "status_kehadiran": "Status Kehadiran"},
                          category_orders={"status_kehadiran": ["Hadir", "Sakit", "Izin", "Alfa"]},
                          text_auto=True, color_discrete_sequence=px.colors.qualitative.D3)
            fig2.update_layout(barmode='stack', xaxis_title="Pertemuan Ke-", yaxis_title="Jumlah Mentee")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Tidak ada data untuk melihat distribusi status kehadiran per pertemuan.")


    with tab3:
        st.subheader("📋 Rekap Kehadiran Mentee (Detail Status)")
        if not df_merged.empty:
            rekap_detail = df_merged.pivot_table(index=["mentee_id", "nama"],
                                                  columns="status_kehadiran",
                                                  values="is_hadir",
                                                  aggfunc='count',
                                                  fill_value=0).reset_index()

            rekap_detail.columns.name = None

            # Pastikan semua status ada sebagai kolom, jika tidak, tambahkan dengan nilai 0
            for status in ["Hadir", "Sakit", "Izin", "Alfa"]:
                if status not in rekap_detail.columns:
                    rekap_detail[status] = 0
                    
            total_pertemuan_tercatat = df_merged["pertemuan"].nunique()
            
            if 'Hadir' in rekap_detail.columns and total_pertemuan_tercatat > 0:
                rekap_detail["% Hadir Murni"] = (rekap_detail["Hadir"] / total_pertemuan_tercatat * 100).round(2)
            else:
                rekap_detail["% Hadir Murni"] = 0

            if role == "Admin":
                # Merge dengan nama mentor untuk tampilan admin
                # Pastikan 'id' di filtered_mentee_df dan 'mentee_id' di rekap_detail adalah kolom yang benar
                rekap_detail = rekap_detail.merge(filtered_mentee_df[['id', 'nama_mentor']], 
                                                left_on='mentee_id', right_on='id', how='left')
                rekap_detail = rekap_detail.drop(columns='id') # Hapus kolom 'id' yang duplikat
                cols_order = ['mentee_id', 'nama', 'nama_mentor', 'Hadir', 'Sakit', 'Izin', 'Alfa', '% Hadir Murni']
                rekap_detail = rekap_detail[cols_order]
                st.dataframe(rekap_detail.rename(columns={
                    'nama': 'Nama Mentee',
                    'Hadir': 'Jml Hadir',
                    'Sakit': 'Jml Sakit',
                    'Izin': 'Jml Izin',
                    'Alfa': 'Jml Alfa',
                    '% Hadir Murni': '% Hadir',
                    'nama_mentor': 'Mentor' # Rename for clarity
                }), use_container_width=True)
            else: # Role Mentor
                st.dataframe(rekap_detail.rename(columns={
                    'nama': 'Nama Mentee',
                    'Hadir': 'Jml Hadir',
                    'Sakit': 'Jml Sakit',
                    'Izin': 'Jml Izin',
                    'Alfa': 'Jml Alfa',
                    '% Hadir Murni': '% Hadir'
                }), use_container_width=True)

            # --- Tombol Unduh Excel ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                rekap_detail.to_excel(writer, index=False, sheet_name="Rekap Presensi Detail")
            st.download_button("📥 Unduh Rekap Detail Excel", data=output.getvalue(), file_name="rekap_presensi_detail.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        else:
            st.info("Tidak ada data presensi yang tersedia untuk rekap detail mentee.")

else:
    st.info("Tidak ada data presensi yang tersedia untuk membuat statistik.")