presensi_mentoring_streamlit/
│
├── app.py                         ✅ ← (file utama navigasi & deskripsi)
├── service_account.json           🔐 Google API credential
├── pages/
│   ├── 1_Dashboard.py             📊 Statistik global
│   ├── 2_Data_Mentor.py           👨‍🏫 CRUD mentor
│   ├── 3_Data_Mentee.py           👥 CRUD mentee
│   ├── 4_Presensi_Mentor.py       📝 Presensi
│   └── 5_Statistik.py             📈 Statistik kehadiran


update

presensi_mentoring_streamlit/
├── app.py                         ✅ Halaman utama
├── service_account.json
├── pages/
│   ├── 0_Login.py                ✅ Login (halaman pertama)
│   ├── 1_Dashboard.py
│   ├── 2_Data_Mentor.py
│   ├── 3_Data_Mentee.py
│   ├── 4_Presensi_Mentor.py
│   └── 5_Statistik.py



| Aktor  | Email yang digunakan           | Role yang dipilih |
| ------ | ------------------------------ | ----------------- |
| Admin  | `admin@sttnf.ac.id`            | Admin             |
| Mentor | Email yang ada di sheet mentor | Mentor            |


(new_streamlit_env)