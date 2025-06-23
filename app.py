import streamlit as st
from PIL import Image
from datetime import datetime
import base64 # Import modul base64

# --- Inisialisasi session_state ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'email' not in st.session_state:
    st.session_state.email = None
if 'mentor_id' not in st.session_state:
    st.session_state.mentor_id = None

# --- Fungsi untuk mengonversi gambar ke Base64 ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            ext = image_path.split('.')[-1].lower()
            mime_type = f"image/{'jpeg' if ext == 'jpg' else ext}" # Asumsi jpeg jika .jpg
            return f"data:{mime_type};base64,{base64.b64encode(img_file.read()).decode()}"
    except FileNotFoundError:
        st.error(f"Error: Gambar tidak ditemukan di {image_path}. Pastikan path dan nama file benar.")
        return ""
    except Exception as e:
        st.error(f"Error saat mengonversi gambar {image_path} ke Base64: {e}")
        return ""

# Dapatkan URL Base64 untuk gambar hero
hero_bg_base64_url = get_base64_image("assets/hero_bg.jpg")

# Konfigurasi Halaman
st.set_page_config(page_title="BKPK STT NF", page_icon="assets/bkpk.png", layout="wide")

# --- GUARD CLAUSE UNTUK PENGGUNA YANG SUDAH LOGIN ---
# Jika sudah login, alihkan langsung ke halaman dashboard utama
if st.session_state.get("logged_in"):
    st.switch_page("pages/1_Dashboard.py")
# --- AKHIR GUARD CLAUSE ---

# --- CSS Kustom (Hanya untuk halaman publik ini) ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Poppins', sans-serif;
    color: var(--text-color); /* Pastikan teks default mengikuti tema */
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 16px;
}}

/* Navbar */
nav {{
    background: var(--background-color-secondary);
    backdrop-filter: blur(8px);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 10px 24px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
    margin-top: 12px;
    margin-bottom: 20px;
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 15px;
}}

nav a {{
    text-decoration: none !important;
    color: var(--text-color); /* Teks navigasi adaptif */
    font-weight: 600;
    transition: all 0.3s ease;
    padding: 6px 12px;
    border-radius: 6px;
}}

nav a:hover {{
    background-color: var(--background-color-hover); /* Background hover adaptif */
    transform: scale(1.05);
}}

/* Hero button (untuk "Masuk ke Sistem Presensi") */
.hero-btn {{
    display: inline-block;
    margin-top: 12px;
    padding: 12px 24px;
    background: linear-gradient(to right, #0d6efd, #0a58ca); /* Tetap warna solid untuk branding */
    color: #ffffff !important; /* Pastikan selalu putih untuk kontras dengan gradient */
    border-radius: 8px;
    font-weight: 600;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
    transition: transform 0.3s ease;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.4);
    text-decoration: none !important;
}}

.hero-btn:hover {{
    transform: translateY(-3px);
}}

h1 {{
    color: var(--primary-color); /* Gunakan warna primer Streamlit */
    text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
}}
h4 {{
    color: var(--text-color); /* Gunakan warna teks Streamlit */
}}
h2 {{
    color: var(--primary-color); /* Gunakan warna primer Streamlit */
    font-weight: 700;
}}

section {{
    background-color: var(--background-color-secondary); /* Gunakan variabel Streamlit */
    padding: 32px;
    border-radius: 12px;
    margin-bottom: 20px;
    border-left: 3px solid #0d6efd; /* Garis aksen biru untuk setiap bagian */
}}

/* --- Hero Section Disederhanakan untuk Memastikan Gambar Muncul --- */
.hero-section-with-bg {{
    position: relative; /* Penting untuk overlay */
    min-height: 500px; /* Sesuaikan tinggi hero section */
    border-radius: 16px;
    margin-bottom: 20px;
    display: flex; /* Untuk memusatkan konten */
    align-items: center;
    justify-content: center;
    text-align: center;
    overflow: hidden; /* Pastikan gambar tidak meluber */

    /* Latar belakang gambar - MENGGUNAKAN BASE64 DI SINI */
    background-image: url("{hero_bg_base64_url}");
    background-position: center center;
    background-repeat: no-repeat;
    background-size: cover;
    background-attachment: scroll; /* Mulai dengan 'scroll' agar lebih robust */
}}

.hero-section-overlay {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.4); /* Overlay gelap semi-transparan */
    z-index: 1; /* Di atas gambar, di bawah konten */
}}

.hero-section-content {{
    position: relative; /* Penting agar konten di atas overlay */
    z-index: 2;
    color: white; /* Teks di atas overlay akan selalu putih */
    padding: 80px 20px; /* Padding untuk konten */
    width: 100%;
    box-sizing: border-box;
}}

.hero-section-content h2,
.hero-section-content p {{
    color: white !important; /* Paksa H2 di hero tetap putih */
    text-shadow: 2px 2px 4px rgba(0,0,0,0.7); /* Bayangan teks agar lebih terbaca */
}}
/* --- Akhir Hero Section Disederhanakan --- */


/* Program Item Card Styling */
.program-item-card {{
    background-color: var(--background-color-secondary); /* Menggunakan variabel Streamlit */
    border: 1px solid var(--border-color); /* Menggunakan variabel Streamlit */
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    min-height: 180px;
}}

.program-item-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
}}

.program-item-card strong {{
    font-size: 1.3em;
    margin-bottom: 10px;
    color: var(--primary-color);
}}


/* Kontak grid */
.kontak-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
    margin-top: 20px;
}}

.kontak-item {{
    background: var(--background-color-secondary); /* Menggunakan variabel Streamlit */
    border: 1px solid var(--border-color); /* Menggunakan variabel Streamlit */
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    color: var(--text-color);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.kontak-item:hover {{
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}}

.kontak-item a {{
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
}}

.kontak-item a:hover {{
    text-decoration: underline;
    color: #0a58ca;
}}

/* Alumni Review Cards */
.alumni-review-card {{
    background-color: var(--background-color-secondary); /* Menggunakan variabel Streamlit */
    border: 1px solid var(--border-color); /* Menggunakan variabel Streamlit */
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    color: var(--text-color);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.alumni-review-card:hover {{
    transform: scale(1.02);
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}}

/* Footer */
.footer-text {{
    text-align: center;
    color: var(--text-color-secondary);
}}

@media only screen and (max-width: 768px) {{
    nav {{
        flex-direction: column;
        align-items: center;
    }}

    nav a {{
        margin: 6px 0;
    }}

    .hero-btn {{
        width: 80%;
    }}
}}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='container'>", unsafe_allow_html=True)

# Header (Lokasi tetap di awal, sebelum konten utama)
cols = st.columns([1.5, 6])
with cols[0]:
    try:
        logo = Image.open("assets/bkpk.png")
        st.image(logo, width=180)
    except FileNotFoundError:
        st.warning("Logo 'assets/bkpk.png' tidak ditemukan. Pastikan path sudah benar.")
    except Exception as e:
        st.warning(f"Error loading logo: {e}")

with cols[1]:
    st.markdown("""
    <h1 style='margin-bottom:0;'>BKPK STT Terpadu Nurul Fikri</h1>
    <h4 style='margin-top:0;'>Badan Koordinasi Pembentukan Karakter Mahasiswa</h4>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True) # Garis pemisah

# --- KONTEN UNTUK PENGGUNA BELUM LOGIN (Satu-satunya konten di app.py) ---
# Navbar tetap di atas logo, tapi hanya berisi menu statis
st.markdown("""
<nav>
    <a href="#beranda">Beranda</a>
    <a href="#tentang-kami">Tentang Kami</a>
    <a href="#program">Program</a>
    <a href="#galeri">Galeri</a>
    <a href="#kontak">Kontak</a>
</nav>
<hr>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class='hero-section-with-bg'>
    <div class='hero-section-overlay'></div>
    <div class='hero-section-content' id='beranda'>
        <h2>Selamat Datang di Portal BKPK STT NF</h2>
        <p>Silakan login untuk mengakses Sistem Presensi dan Pembinaan Karakter.</p>
    </div>
</div>
<hr>
""", unsafe_allow_html=True)


# Tombol login kembali di bawah
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔐 Masuk ke Sistem Presensi", use_container_width=True, type="primary"):
        st.switch_page("pages/0_Login.py")

# Menampilkan bagian publik dari app.py (Tentang Kami, Program, Galeri, Kontak)
st.header("Tentang Kami", anchor="tentang-kami")
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("""
<section>
BKPK STT NF adalah organisasi kampus yang berfokus pada pembinaan karakter mahasiswa STT Nurul Fikri.
Kami menjadi wadah integrasi nilai-nilai keislaman, kepemimpinan, dan profesionalisme.

### Visi
Menjadi organisasi pembinaan karakter terbaik berbasis nilai-nilai Islam.

### Misi
- Menanamkan nilai keislaman dalam kehidupan kampus
- Mengembangkan jiwa kepemimpinan dan tanggung jawab
- Menjadi sarana pembinaan yang profesional dan inspiratif
</section>
""", unsafe_allow_html=True)
with col2:
    try:
        st.image("assets/Menzo.png", caption="I'm Menzo", width=250)
    except FileNotFoundError:
        st.warning("Gambar 'assets/Menzo.png' tidak ditemukan.")
    except Exception as e:
        st.warning(f"Error loading image: {e}")

st.header("Program Unggulan", anchor="program")
cols = st.columns(3)
programs = [
    ("🌱 Mentoring", "Bimbingan pekanan untuk pembinaan karakter dan spiritualitas."),
    ("📚 Pelatihan", "Workshop kepemimpinan, manajemen waktu, dan dakwah digital."),
    ("🏆 Lomba", "Kompetisi internal seperti lomba ceramah, poster dakwah, dll."),
    ("🤝 Bakti Sosial", "Kegiatan sosial seperti santunan yatim dan bersih masjid."),
    ("🕌 Kajian Islam", "Kajian rutin dengan pemateri internal dan eksternal."),
    ("🛠️ Kaderisasi", "Program regenerasi dan penguatan kader BKPK.")
]
for i, (icon_text, desc) in enumerate(programs):
    with cols[i % 3]:
        st.markdown(f"""
<div class='program-item-card'>
    <strong>{icon_text}</strong>
    <p>{desc}</p>
</div>
""", unsafe_allow_html=True)

st.header("Galeri Kegiatan", anchor="galeri")
try:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("assets/galeri3.jpg", caption="MENTORING", width=250)
    with col2:
        st.image("assets/galeri1.png", caption="APMI", width=250)
    with col3:
        st.image("assets/galeri2.png", caption="PELATIHAN", width=250)
except FileNotFoundError:
    st.warning("Gambar galeri tidak ditemukan. Pastikan path sudah benar.")
except Exception as e:
    st.warning(f"Error loading gallery image: {e}")

st.header("Apa Kata Alumni")
cols = st.columns(2)
with cols[0]:
    st.markdown("""
    <div class='alumni-review-card'>
    <em>“BKPK membentuk karakter dan meningkatkan kepekaan sosial saya.”</em><br>
    <strong>- Ahmad Rafi, Alumni 2022</strong>
    </div>
    """, unsafe_allow_html=True)
with cols[1]:
    st.markdown("""
    <div class='alumni-review-card'>
    <em>“Saya tumbuh secara spiritual dan organisasi di BKPK.”</em><br>
    <strong>- Nabila Hanun, Alumni 2021</strong>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div id='kontak'>
    <h2 style='text-align:center;'>Hubungi Kami</h2>
    <div class='kontak-grid'>
        <div class='kontak-item'>
            <p>📍 <strong>Alamat:</strong><br>Sekretariat BKPK, Gedung STT NF Lantai 2</p>
        </div>
        <div class='kontak-item'>
            <p>📧 <strong>Email:</strong><br><a href='mailto:bkpk@sttnf.ac.id'>bkpk@sttnf.ac.id</a></p>
        </div>
        <div class='kontak-item'>
            <p>📱 <strong>WhatsApp:</strong><br><a href='https://wa.me/6281234567890' target='_blank'>0812-3456-7890</a></p>
        </div>
        <div class='kontak-item'>
            <p>📸 <strong>Instagram:</strong><br><a href='https://instagram.com/bkpksttnf' target='_blank'>@bkpksttnf</a></p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer (di luar blok if/else agar selalu ada)
st.markdown("---")
tahun = datetime.now().year
st.markdown(f"<p class='footer-text'>© {tahun} BKPK STT Nurul Fikri | TIM Kencore </p>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)