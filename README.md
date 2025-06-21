.
├── .streamlit/
│   └── secrets.toml          # Opsi konfigurasi rahasia Streamlit (untuk deployment Cloud)
├── app.py                    # Halaman utama aplikasi Streamlit
├── service_account.json      # File kredensial Google Sheets API (penting untuk lokal)
├── setup_sheets.py           # Skrip bantu untuk membuat struktur Google Sheets
├── assets/
│   ├── bkpk.png              # Logo BKPK
│   ├── Menzo.png             # Gambar Menzo
│   └── galeri2.png           # Gambar galeri kegiatan
├── pages/                    # Folder berisi halaman-halaman Streamlit terpisah
│   ├── 0_Login.py            # Halaman login pengguna
│   ├── 1_Dashboard.py        # Dashboard utama (Admin & Mentor)
│   ├── 2_Data_Mentor.py      # Manajemen data mentor (Admin Only)
│   ├── 3_Data_Mentee.py      # Manajemen data mentee (Admin & Mentor)
│   ├── 4_Presensi_Mentor.py  # Form input presensi oleh mentor (Mentor Only)
│   └── 5_Statistik.py        # Laporan dan statistik presensi (Admin & Mentor)
└── utils/
    └── auth_utils.py         # Fungsi-fungsi bantu untuk autentikasi dan otorisasi
