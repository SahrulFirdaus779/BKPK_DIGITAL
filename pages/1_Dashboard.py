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

@st.cache_data(ttl=3600) # Cache data selama 1 jam untuk mencegah panggilan API berlebihan
def load_data():
    try:
        CREDS = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
        CLIENT = gspread.authorize(CREDS)
        SHEET = CLIENT.open("Presensi Mentoring STT NF") # Ganti dengan nama spreadsheet Anda

        mentor_data = pd.DataFrame(SHEET.worksheet("mentor").get_all_records())
        mentee_data = pd.DataFrame(SHEET.worksheet("mentee").get_all_records())
        presensi_data = pd.DataFrame(SHEET.worksheet("presensi").get_all_records())
        
        return mentor_data, mentee_data, presensi_data
    except FileNotFoundError:
        st.error("Error: File 'service_account.json' tidak ditemukan di direktori proyek. Pastikan file ada.")
        st.stop()
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat data dari Google Sheets: {e}. Pastikan kredensial service account benar dan Google Sheets API aktif.")
        st.stop()

# Gunakan spinner saat memuat data
with st.spinner(""):
    mentor_df, mentee_df, presensi_df = load_data()


# --- Konversi tipe data numerik dan olah status_kehadiran ---
# Kolom 'id', 'mentor_id', 'mentee_id', 'pertemuan' tetap numerik
for df_var in ['mentor_df', 'mentee_df', 'presensi_df']:
    df = locals()[df_var] # Dapatkan DataFrame dari variabel lokal
    for col in ['id', 'mentor_id', 'mentee_id', 'pertemuan']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    locals()[df_var] = df # Perbarui DataFrame di variabel lokal

# Olah kolom 'status_kehadiran' di presensi_df
if 'status_kehadiran' in presensi_df.columns:
    presensi_df['hadir_hitung'] = presensi_df['status_kehadiran'].apply(lambda x: 1 if x == 'Hadir' else 0)
else:
    st.warning("Kolom 'status_kehadiran' tidak ditemukan di data presensi. Pastikan Google Sheet sudah diperbarui.")
    presensi_df['hadir_hitung'] = 0 # Fallback jika kolom tidak ada

# Konversi kolom 'tanggal' ke datetime untuk filter dan analisis tren
if 'tanggal' in presensi_df.columns:
    presensi_df['tanggal'] = pd.to_datetime(presensi_df['tanggal'], errors='coerce')
    presensi_df = presensi_df.dropna(subset=['tanggal']) # Hapus baris dengan tanggal yang tidak valid
else:
    st.warning("Kolom 'tanggal' tidak ditemukan di data presensi. Fitur filter tanggal dan tren tidak akan berfungsi.")

# --- Header Halaman ---
st.title(f"📊 Dashboard {role}")
st.write(f"Selamat datang, **{user_name}**! 👋")

st.divider()

# --- Filter Global (untuk Admin dan Mentor jika relevan) ---
st.sidebar.header("Filter Data")
min_date = presensi_df['tanggal'].min().date() if not presensi_df.empty else pd.to_datetime('2023-01-01').date()
max_date = presensi_df['tanggal'].max().date() if not presensi_df.empty else pd.to_datetime('2024-12-31').date()

date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    presensi_df_filtered = presensi_df[(presensi_df['tanggal'] >= start_date) & (presensi_df['tanggal'] <= end_date)]
else:
    presensi_df_filtered = presensi_df.copy()
    st.sidebar.info("Pilih rentang tanggal untuk memfilter data.")

# --- Pesan Kosong yang Lebih Informatif ---
if presensi_df_filtered.empty:
    st.warning("Maaf, tidak ada data presensi yang ditemukan dalam rentang tanggal yang dipilih. Coba rentang tanggal lain atau pastikan data telah dicatat.")


if role == "Admin":
    # --- Kartu Statistik ---
    st.header("Ringkasan Data Umum")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👨‍🏫 Total Mentor", len(mentor_df))
    with col2:
        st.metric("🧑‍🎓 Total Mentee", len(mentee_df))
    with col3:
        st.metric("🗓️ Total Presensi Dicatat", len(presensi_df_filtered))

    st.divider()

    # --- Grafik Kehadiran per Pertemuan (Admin) ---
    st.header("Analisis Kehadiran Mentee")
    st.subheader("📈 Rata-rata Kehadiran Mentee per Pertemuan")
    if not presensi_df_filtered.empty and 'hadir_hitung' in presensi_df_filtered.columns:
        avg_hadir_per_pertemuan = presensi_df_filtered.groupby("pertemuan")["hadir_hitung"].mean().reset_index()
        avg_hadir_per_pertemuan['Rata-rata Kehadiran (%)'] = avg_hadir_per_pertemuan['hadir_hitung'] * 100
        fig_avg = px.bar(avg_hadir_per_pertemuan, x="pertemuan", y="Rata-rata Kehadiran (%)",
                         title="Distribusi Rata-rata Kehadiran Mentee per Pertemuan",
                         labels={"pertemuan": "Pertemuan Ke-", "Rata-rata Kehadiran (%)": "Rata-rata Kehadiran (%)"},
                         text_auto=True)
        fig_avg.update_traces(marker_color='#6495ED')
        fig_avg.update_layout(xaxis_title="Pertemuan", yaxis_title="Rata-rata Kehadiran (%)")
        st.plotly_chart(fig_avg, use_container_width=True)
        st.caption("Grafik ini hanya menghitung status 'Hadir' untuk rata-rata kehadiran.")

        st.subheader("📊 Distribusi Status Kehadiran Keseluruhan")
        status_counts = presensi_df_filtered['status_kehadiran'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Jumlah']
        fig_pie = px.pie(status_counts, values='Jumlah', names='Status',
                         title='Persentase Status Kehadiran Global',
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

        # --- Tren Kehadiran Keseluruhan dari Waktu ke Waktu (Admin) ---

        st.subheader("📉 Tren Rata-rata Kehadiran Mingguan")
        if 'tanggal' in presensi_df_filtered.columns:
            presensi_df_filtered['tanggal'] = pd.to_datetime(presensi_df_filtered['tanggal'])

            # Mengubah pengelompokan menjadi mingguan
            presensi_df_filtered['minggu_tahun'] = presensi_df_filtered['tanggal'].dt.to_period('W').astype(str)
            avg_hadir_minggu = presensi_df_filtered.groupby('minggu_tahun')['hadir_hitung'].mean().reset_index()
            avg_hadir_minggu['Rata-rata Kehadiran (%)'] = avg_hadir_minggu['hadir_hitung'] * 100

            # Urutkan berdasarkan minggu_tahun untuk plot yang benar
            avg_hadir_minggu = avg_hadir_minggu.sort_values('minggu_tahun')

            fig_tren = px.line(avg_hadir_minggu, x='minggu_tahun', y='Rata-rata Kehadiran (%)',
                            title='Tren Rata-rata Kehadiran Mentee Mingguan',
                            labels={'minggu_tahun': 'Minggu', 'Rata-rata Kehadiran (%)': 'Rata-rata Kehadiran (%)'})
            fig_tren.update_traces(mode='markers+lines', marker_size=8, line_shape='spline')
            # Jika Anda menggunakan Streamlit, Anda akan menggunakan ini:
            st.plotly_chart(fig_tren, use_container_width=True)
        else:
            print("Kolom 'tanggal' tidak tersedia untuk menampilkan tren kehadiran.") # Mengganti st.info dengan print untuk non-Streamlit


        st.subheader("📉 Tren Rata-rata Kehadiran Bulanan")
        if 'tanggal' in presensi_df_filtered.columns:
            presensi_df_filtered['bulan_tahun'] = presensi_df_filtered['tanggal'].dt.to_period('M').astype(str)
            avg_hadir_bulan = presensi_df_filtered.groupby('bulan_tahun')['hadir_hitung'].mean().reset_index()
            avg_hadir_bulan['Rata-rata Kehadiran (%)'] = avg_hadir_bulan['hadir_hitung'] * 100
            
            # Urutkan berdasarkan bulan_tahun untuk plot yang benar
            avg_hadir_bulan = avg_hadir_bulan.sort_values('bulan_tahun')

            fig_tren = px.line(avg_hadir_bulan, x='bulan_tahun', y='Rata-rata Kehadiran (%)',
                               title='Tren Rata-rata Kehadiran Mentee Bulanan',
                               labels={'bulan_tahun': 'Bulan', 'Rata-rata Kehadiran (%)': 'Rata-rata Kehadiran (%)'})
            fig_tren.update_traces(mode='markers+lines', marker_size=8, line_shape='spline')
            st.plotly_chart(fig_tren, use_container_width=True)
        else:
            st.info("Kolom 'tanggal' tidak tersedia untuk menampilkan tren kehadiran.")

        # --- Tabel Ringkasan Mentor Terbaik/Terendah (Admin) ---
        st.subheader("🏆 Performa Mentor Berdasarkan Rata-rata Kehadiran Kelompok")
        if not presensi_df_filtered.empty and not mentee_df.empty:
            presensi_with_mentor = presensi_df_filtered.merge(mentee_df[['id', 'mentor_id']], left_on='mentee_id', right_on='id', suffixes=('', '_mentee_id_drop'))
            presensi_with_mentor = presensi_with_mentor.merge(mentor_df[['id', 'nama']], left_on='mentor_id', right_on='id', suffixes=('', '_mentor_id_drop'))
            
            avg_hadir_per_mentor = presensi_with_mentor.groupby(['mentor_id', 'nama'])['hadir_hitung'].mean().reset_index()
            avg_hadir_per_mentor['Rata-rata Kehadiran (%)'] = avg_hadir_per_mentor['hadir_hitung'] * 100
            avg_hadir_per_mentor = avg_hadir_per_mentor.sort_values('Rata-rata Kehadiran (%)', ascending=False)

            st.write("**Top 5 Mentor (Berdasarkan Rata-rata Kehadiran Kelompok):**")
            st.dataframe(avg_hadir_per_mentor.head(5).drop(columns=['mentor_id', 'hadir_hitung']).rename(columns={'nama': 'Nama Mentor'}), use_container_width=True)
            
            st.write("**5 Mentor Terendah (Berdasarkan Rata-rata Kehadiran Kelompok):**")
            st.dataframe(avg_hadir_per_mentor.tail(5).drop(columns=['mentor_id', 'hadir_hitung']).rename(columns={'nama': 'Nama Mentor'}), use_container_width=True)
        else:
            st.info("Data tidak cukup untuk menampilkan performa mentor.")


        st.divider()
        st.header("Detail Data Admin")
        with st.expander("Lihat Data Mentor"):
            st.dataframe(mentor_df, use_container_width=True)
        with st.expander("Lihat Data Mentee"):
            st.dataframe(mentee_df, use_container_width=True)
        with st.expander("Lihat Data Presensi Lengkap (Disaring oleh Tanggal)"):
            # Implementasi sederhana filter/pencarian di sini jika diperlukan
            search_query_admin = st.text_input("Cari di Presensi (Nama Mentee/Status):", key="search_admin")
            presensi_display = presensi_df_filtered.merge(mentee_df[['id', 'nama']], left_on='mentee_id', right_on='id', suffixes=('', '_mentee'))
            
            if search_query_admin:
                presensi_display = presensi_display[
                    presensi_display['nama'].str.contains(search_query_admin, case=False, na=False) |
                    presensi_display['status_kehadiran'].str.contains(search_query_admin, case=False, na=False)
                ]
            
            st.dataframe(presensi_display.drop(columns=['id_mentee']), use_container_width=True)
            st.caption("Anda dapat mengetik di kotak pencarian di atas untuk memfilter tabel ini.")

    else:
        st.info("Belum ada data presensi atau kolom 'status_kehadiran' tidak ditemukan untuk menampilkan analisis.")

elif role == "Mentor":
    st.header(f"Dashboard Mentor: {user_name}")
    st.write(f"ID Mentor Anda: **{mentor_id}**")
    
    mentee_saya = mentee_df[mentee_df["mentor_id"] == mentor_id]
    
    # Filter presensi_df_filtered untuk kelompok mentor ini
    presensi_saya_filtered = presensi_df_filtered[presensi_df_filtered["mentee_id"].isin(mentee_saya["id"])]

    # Gunakan kolom untuk metrik
    col_mentor_metric1, col_mentor_metric2 = st.columns(2)
    with col_mentor_metric1:
        st.metric("Jumlah Mentee di Kelompok Anda", len(mentee_saya))
    with col_mentor_metric2:
        jumlah_pertemuan_dilakukan = presensi_saya_filtered['pertemuan'].nunique()
        st.metric("Jumlah Pertemuan Dilakukan", jumlah_pertemuan_dilakukan)
    
    st.divider()

    if not presensi_saya_filtered.empty and 'hadir_hitung' in presensi_saya_filtered.columns:
        st.subheader("📈 Rata-rata Kehadiran Kelompok Anda per Pertemuan")
        avg_hadir_kelompok = presensi_saya_filtered.groupby("pertemuan")["hadir_hitung"].mean().reset_index()
        avg_hadir_kelompok['Rata-rata Kehadiran (%)'] = avg_hadir_kelompok['hadir_hitung'] * 100
        fig_kelompok_avg = px.bar(avg_hadir_kelompok, x="pertemuan", y="Rata-rata Kehadiran (%)",
                                  title="Rata-rata Kehadiran Kelompok Mentoring",
                                  labels={"pertemuan": "Pertemuan Ke-", "Rata-rata Kehadiran (%)": "Rata-rata Kehadiran (%)"},
                                  text_auto=True)
        fig_kelompok_avg.update_traces(marker_color='#FF7F50')
        fig_kelompok_avg.update_layout(xaxis_title="Pertemuan", yaxis_title="Rata-rata Kehadiran (%)")
        st.plotly_chart(fig_kelompok_avg, use_container_width=True)
        st.caption("Grafik ini hanya menghitung status 'Hadir' untuk rata-rata kehadiran kelompok Anda.")


        st.subheader("📊 Distribusi Status Kehadiran Kelompok Anda")
        status_counts_kelompok = presensi_saya_filtered['status_kehadiran'].value_counts().reset_index()
        status_counts_kelompok.columns = ['Status', 'Jumlah']
        fig_pie_kelompok = px.pie(status_counts_kelompok, values='Jumlah', names='Status',
                                   title='Persentase Status Kehadiran Kelompok',
                                   color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie_kelompok.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie_kelompok, use_container_width=True)

        st.divider()
        st.subheader("📋 Detail Presensi Kelompok Anda")
        presensi_detail = presensi_saya_filtered.merge(mentee_saya[['id', 'nama']], left_on='mentee_id', right_on='id', suffixes=('', '_mentee'))
        presensi_detail = presensi_detail[['tanggal', 'pertemuan', 'nama', 'status_kehadiran']]
        
        # Terapkan pemformatan kondisional
        def highlight_status(s):
            if s == 'Hadir':
                return 'background-color: #D4EDDA; color: #155724' # Hijau muda, teks hijau tua
            elif s == 'Alfa': # Ini adalah "Alfa" Anda
                return 'background-color: #F8D7DA; color: #721C24' # Merah muda, teks merah tua
            elif s == 'Izin':
                return 'background-color: #FFF3CD; color: #856404' # Kuning muda, teks kuning tua
            else:
                return ''

        st.dataframe(
            presensi_detail.rename(columns={'nama': 'Nama Mentee', 'status_kehadiran': 'Status Kehadiran'})
            .style.applymap(highlight_status, subset=['Status Kehadiran']),
            use_container_width=True
        )

        st.subheader("👤 Kehadiran Mentee Individual")
        if not mentee_saya.empty:
            selected_mentee_name = st.selectbox(
                "Pilih Mentee untuk Melihat Detail Kehadiran:",
                options=['-- Pilih Semua Mentee --'] + mentee_saya['nama'].tolist(),
                key="select_mentee_detail"
            )

            if selected_mentee_name != '-- Pilih Semua Mentee --':
                selected_mentee_id = mentee_saya[mentee_saya['nama'] == selected_mentee_name]['id'].iloc[0]
                mentee_presensi_filtered = presensi_saya_filtered[presensi_saya_filtered['mentee_id'] == selected_mentee_id]
                
                if not mentee_presensi_filtered.empty:
                    st.write(f"**Riwayat Kehadiran {selected_mentee_name}:**")
                    st.dataframe(
                        mentee_presensi_filtered[['tanggal', 'pertemuan', 'status_kehadiran']]
                        .rename(columns={'status_kehadiran': 'Status Kehadiran'}),
                        use_container_width=True
                    )
                else:
                    st.info(f"Belum ada data presensi untuk {selected_mentee_name} dalam rentang tanggal ini.")
            else:
                st.info("Pilih nama mentee dari daftar di atas untuk melihat detail kehadirannya.")
        else:
            st.info("Belum ada mentee yang terdaftar di kelompok Anda.")

        st.subheader("🚫 Mentee dengan Absensi Terbanyak (Status 'Alfa')")
        if not presensi_saya_filtered.empty:
            # Hitung jumlah 'Alfa' per mentee
            absensi_counts = presensi_saya_filtered[presensi_saya_filtered['status_kehadiran'] == 'Alfa'] \
                                .groupby('mentee_id')['status_kehadiran'].count().reset_index()
            absensi_counts.columns = ['mentee_id', 'Jumlah Alfa']
            
            if not absensi_counts.empty:
                # Gabungkan dengan nama mentee
                absensi_counts = absensi_counts.merge(mentee_saya[['id', 'nama']], left_on='mentee_id', right_on='id', suffixes=('', '_mentee_name_drop'))
                absensi_counts = absensi_counts.sort_values('Jumlah Alfa', ascending=False)
                st.dataframe(absensi_counts[['nama', 'Jumlah Alfa']].rename(columns={'nama': 'Nama Mentee'}), use_container_width=True)
            else:
                st.info("Semua mentee dalam kelompok Anda hadir sempurna!")
        else:
            st.info("Belum ada data presensi untuk menghitung absensi mentee.")

    else:
        st.info("Belum ada data presensi untuk kelompok Anda atau kolom 'status_kehadiran' tidak ditemukan untuk analisis.")
else:
    st.error("Peran tidak dikenali.")

st.divider()

# Add logout and home buttons in a more organized way
col_btns_1, col_btns_2 = st.columns([0.15, 0.85])
with col_btns_1:
    if st.button("🚪 Logout"):
        st.session_state["logged_in"] = False
        st.session_state["role"] = None
        st.session_state["user_name"] = None
        st.session_state["mentor_id"] = None
        st.success("Anda telah berhasil logout.")
        st.switch_page("app.py")
with col_btns_2:
    st.button("🏠 Kembali ke Beranda Utama", on_click=lambda: st.switch_page("app.py"))