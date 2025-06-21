# setup_sheets.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time

# --- Konfigurasi ---
SPREADSHEET_NAME = "Presensi Mentoring STT NF" # Ganti dengan nama spreadsheet Anda
SERVICE_ACCOUNT_FILE = "service_account.json"

# --- Setup Google Sheets ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    CREDS = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPE)
    CLIENT = gspread.authorize(CREDS)
    
    # Coba buka spreadsheet, jika tidak ada, buat baru
    try:
        SHEET = CLIENT.open(SPREADSHEET_NAME)
        print(f"Spreadsheet '{SPREADSHEET_NAME}' sudah ada.")
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Spreadsheet '{SPREADSHEET_NAME}' tidak ditemukan. Membuat yang baru...")
        SHEET = CLIENT.create(SPREADSHEET_NAME)
        # Penting: Setelah membuat, Anda perlu secara manual membagikan spreadsheet ini
        # dengan alamat email Service Account Anda (di service_account.json)
        # dan berikan izin "Editor". Tanpa ini, skrip tidak akan bisa menulis.
        print(f"Spreadsheet '{SPREADSHEET_NAME}' berhasil dibuat.")
        print(f"**PENTING: Mohon bagikan spreadsheet ini dengan email Service Account Anda '{CREDS.client_email}' dan berikan izin 'Editor'.**")
        input("Tekan Enter setelah Anda membagikan spreadsheet dan menekan izin. (Mungkin perlu beberapa detik untuk propagate)")

    # Periksa dan buat/reset worksheet
    worksheets_to_create = {
        "mentor": ["id", "nama", "email"],
        "mentee": ["id", "nama", "kelompok", "mentor_id"],
        "presensi": ["id", "mentee_id", "mentor_id", "nama_mentor", "tanggal", "pertemuan", "hadir"]
    }

    for ws_name, headers in worksheets_to_create.items():
        try:
            worksheet = SHEET.worksheet(ws_name)
            print(f"Worksheet '{ws_name}' sudah ada. Membersihkan (clear) dan menambahkan header...")
            worksheet.clear() # Membersihkan konten yang ada
            worksheet.append_row(headers) # Menambahkan header
        except gspread.exceptions.WorksheetNotFound:
            print(f"Worksheet '{ws_name}' tidak ditemukan. Membuat yang baru dan menambahkan header...")
            worksheet = SHEET.add_worksheet(title=ws_name, rows="1", cols=str(len(headers)))
            worksheet.append_row(headers)
        except Exception as e:
            print(f"Error saat memproses worksheet '{ws_name}': {e}")

    print("\nSetup Google Sheets Selesai.")
    print("Pastikan untuk mengisi data dummy di worksheet 'mentor' dan 'mentee' secara manual.")
    print("Contoh data 'mentor':")
    print("id,nama,email")
    print("1,Mentor A,mentor.a@sttnf.ac.id")
    print("2,Mentor B,mentor.b@sttnf.ac.id")

except FileNotFoundError:
    print(f"Error: File '{SERVICE_ACCOUNT_FILE}' tidak ditemukan.")
    print("Pastikan Anda telah mengunduhnya dari Google Cloud Console dan menempatkannya di direktori yang sama.")
except Exception as e:
    print(f"Terjadi kesalahan: {e}")
    print("Pastikan Google Sheets API dan Google Drive API diaktifkan di Google Cloud Console.")