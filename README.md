# Sistem Presensi dan Pembinaan Karakter Mentoring BKPK STT Nurul Fikri

## Daftar Isi
- [Tentang Proyek](#tentang-proyek)
- [Fitur Utama](#fitur-utama)
- [Persyaratan Sistem](#persyaratan-sistem)
- [Instalasi dan Setup Lokal](#instalasi-dan-setup-lokal)
  - [1. Kloning Repositori](#1-kloning-repositori)
  - [2. Instalasi Dependensi](#2-instalasi-dependensi)
  - [3. Konfigurasi Google Sheets API](#3-konfigurasi-google-sheets-api)
  - [4. Menyiapkan Spreadsheet Google](#4-menyiapkan-spreadsheet-google)
  - [5. Menjalankan Aplikasi Streamlit](#5-menjalankan-aplikasi-streamlit)
- [Struktur Proyek](#struktur-proyek)
- [Panduan Penggunaan](#panduan-penggunaan)
  - [Akses Aplikasi](#akses-aplikasi)
  - [Peran Pengguna](#peran-pengguna)
- [Deployment ke Streamlit Cloud (Opsional)](#deployment-ke-streamlit-cloud-opsional)
- [Kontribusi](#kontribusi)
- [Lisensi](#lisensi)
- [Kontak](#kontak)

---

## Tentang Proyek

Sistem Presensi dan Pembinaan Karakter Mentoring BKPK STT Nurul Fikri adalah aplikasi berbasis web yang dibangun menggunakan Streamlit. Proyek ini bertujuan untuk memfasilitasi pengelolaan kegiatan mentoring, presensi mentee, serta pemantauan data mentor dan mentee secara terpusat. Aplikasi ini dilengkapi dengan sistem login multi-peran (Admin dan Mentor) dan terintegrasi dengan Google Sheets sebagai basis data.

## Fitur Utama

* **Halaman Beranda Interaktif:** Menampilkan informasi umum BKPK, program unggulan, galeri kegiatan, dan kontak.
* **Sistem Login Multi-Peran:**
    * **Admin:** Memiliki akses penuh untuk mengelola data mentor dan mentee, serta melihat statistik dan laporan presensi keseluruhan.
    * **Mentor:** Dapat melihat daftar mentee di kelompoknya, mengisi presensi mentoring, dan melihat statistik kehadiran kelompoknya.
* **Manajemen Data Mentor (Admin Only):** Menambah, mengedit, dan menghapus data mentor.
* **Manajemen Data Mentee (Admin & Mentor):**
    * **Admin:** Menambah, mengedit, menghapus, dan menugaskan mentee ke mentor tertentu.
    * **Mentor:** Melihat daftar mentee yang ditugaskan kepadanya.
* **Input Presensi Mentoring (Mentor Only):** Formulir intuitif untuk mentor mencatat kehadiran mentee per pertemuan.
* **Dashboard dan Statistik:**
    * **Admin:** Ringkasan total mentor, mentee, dan presensi, serta grafik kehadiran mentee per pertemuan secara keseluruhan.
    * **Mentor:** Statistik kehadiran spesifik untuk kelompok mentoring mereka.
* **Ekspor Data:** Kemampuan untuk mengunduh rekap presensi dalam format Excel.
* **Integrasi Google Sheets:** Semua data disimpan dan diambil dari Google Sheets, memudahkan pengelolaan data tanpa perlu database terpisah.

## Persyaratan Sistem

* Python 3.8+
* `pip` (manajer paket Python)

## Instalasi dan Setup Lokal

Ikuti langkah-langkah di bawah ini untuk mengatur dan menjalankan aplikasi di lingkungan lokal Anda.

### 1. Kloning Repositori

```bash
git clone [https://github.com/yourusername/your-repo-name.git](https://github.com/yourusername/your-repo-name.git)
cd your-repo-name