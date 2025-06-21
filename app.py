import streamlit as st
from PIL import Image
from datetime import datetime

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


# Konfigurasi Halaman
st.set_page_config(page_title="BKPK STT NF", page_icon="assets/bkpk.png", layout="wide")

# CSS Kustom (tidak ada perubahan)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 16px;
}
a {
    text-decoration: none;
}

/* Navbar */
nav {
    background: linear-gradient(to right, #e0f2ff, #f0f9ff);
    backdrop-filter: blur(8px);
    border: 1px solid #cce4ff;
    border-radius: 16px;
    padding: 10px 24px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
    margin-top: 12px;
    margin-bottom: 20px;
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 15px;
}

nav a {
    text-decoration: none !important;
    color: #0a4275;
    font-weight: 600;
    transition: all 0.3s ease;
    padding: 6px 12px;
    border-radius: 6px;
}

nav a:hover {
    background-color: #d7ecff;
    transform: scale(1.05);
}

/* Hero button */
.hero-btn {
    display: inline-block;
    margin-top: 12px;
    padding: 12px 24px;
    background: linear-gradient(to right, #0d6efd, #0a58ca);
    color: #ffffff !important;
    border-radius: 8px;
    font-weight: 600;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
    transition: transform 0.3s ease;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.4);
    text-decoration: none !important;
}

.hero-btn:hover {
    transform: translateY(-3px);
}

h1 {
    color: #0d6efd;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
}
h4 {
    color: #444;
}
h2 {
    color: #0a58ca;
    font-weight: 700;
}

section {
    background-color: #f8f9fc;
    padding: 32px;
    border-radius: 12px;
    margin-bottom: 20px;
}

/* Kontak grid */
.kontak-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.kontak-item {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.kontak-item a {
    color: #0d6efd;
    text-decoration: none;
    font-weight: 500;
}

.kontak-item a:hover {
    text-decoration: underline;
}

@media only screen and (max-width: 768px) {
    nav {
        flex-direction: column;
        align-items: center;
    }

    nav a {
        margin: 6px 0;
    }

    .hero-btn {
        width: 80%;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='container'>", unsafe_allow_html=True)

# Header (Lokasi tetap di awal, sebelum konten utama)
cols = st.columns([1, 6])
with cols[0]:
    try:
        logo = Image.open("assets/bkpk.png")
        st.image(logo, width=100)
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

# --- Logika untuk menampilkan/menyembunyikan navbar dan konten berdasarkan status login ---
if st.session_state.logged_in:
    # Sidebar untuk pengguna yang sudah login
    st.sidebar.title("Dashboard")
    st.sidebar.markdown(f"Selamat datang **{st.session_state.user_name}** ({st.session_state.role})")
    st.sidebar.markdown("---")

    # Navigasi sidebar dinamis berdasarkan peran
    st.sidebar.page_link("pages/1_Dashboard.py", label="Dashboard Utama", icon="🏠")
    if st.session_state.role == "Admin":
        st.sidebar.page_link("pages/2_Data_Mentor.py", label="Data Mentor", icon="🧑‍🏫")
        st.sidebar.page_link("pages/3_Data_Mentee.py", label="Data Mentee", icon="🧑‍🎓")
        st.sidebar.page_link("pages/5_Statistik.py", label="Laporan & Statistik", icon="📊")
    elif st.session_state.role == "Mentor":
        st.sidebar.page_link("pages/3_Data_Mentee.py", label="Kelola Mentee Saya", icon="👥")
        st.sidebar.page_link("pages/4_Presensi_Mentor.py", label="Input Presensi", icon="📝")
        st.sidebar.page_link("pages/5_Statistik.py", label="Statistik Kelompok", icon="📈")

    st.sidebar.markdown("---")
    if st.sidebar.button("Keluar", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.user_name = None
        st.session_state.email = None
        st.session_state.mentor_id = None
        st.success("Anda telah keluar.")
        st.rerun()

    # Navbar utama di bagian atas konten (untuk pengguna yang sudah login)
    st.markdown("""
    <nav>
        <a href="#beranda">Beranda</a>
        <a href="#tentang-kami">Tentang Kami</a>
        <a href="#program">Program</a>
        <a href="#galeri">Galeri</a>
        <a href="#kontak">Kontak</a>
    </nav>
    <hr>
    """, unsafe_allow_html=True) # Menambahkan <hr> untuk pemisah navigasi dan hero section

    # Hero Section untuk pengguna yang sudah login
    st.markdown(f"""
    <div style='
        text-align:center;
        background: linear-gradient(145deg, #dbeafe, #f0f9ff);
        padding: 40px 20px;
        border-radius: 16px;'
        id='beranda'>
        <h2>Selamat Datang di Sistem BKPK STT NF, {st.session_state.user_name} !</h2>
        <p>Anda telah berhasil masuk sebagai {st.session_state.role}.</p>
        <p>Gunakan navigasi sidebar untuk mengakses fitur sesuai peran Anda.</p>
    </div>
    <hr>
    """, unsafe_allow_html=True)

# --- Konten Sistem Presensi (Hanya terlihat jika login) ---
    st.header("Dashboard Sistem", anchor="dashboard")
    st.info("Area ini akan menampilkan ringkasan atau poin masuk ke dashboard sistem presensi Anda.")

    if st.session_state.role == "Admin":
        st.write("Selamat datang Admin! Anda memiliki akses penuh ke fitur manajemen data dan laporan.")
        # Ubah di sini: Hapus on_click dan gunakan pola if st.button
        if st.button("Pergi ke Dashboard Admin"):
            st.switch_page("pages/1_Dashboard.py")
    elif st.session_state.role == "Mentor":
        st.write(f"Selamat datang Mentor {st.session_state.user_name}! Anda dapat mengelola presensi mentoring Anda.")
        # Ubah di sini: Hapus on_click dan gunakan pola if st.button
        if st.button("Pergi ke Halaman Input Presensi"):
            st.switch_page("pages/4_Presensi_Mentor.py")
    else:
        st.warning("Peran Anda tidak dikenali. Silakan hubungi admin.")

    # Sisa konten yang sudah ada (Tentang Kami, Program, Galeri, Kontak)
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
            st.image("assets/Menzo.png", caption="I'm Menzo", use_container_width=True)
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
    for i, (icon, desc) in enumerate(programs):
        with cols[i % 3]:
            st.markdown(f"""
    <div style='background-color: #f0f8ff; padding: 12px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.05);'>
        <strong>{icon} {desc.split(' ',1)[0]}</strong><br>{desc}
    </div>
    """, unsafe_allow_html=True)

    st.header("Galeri Kegiatan", anchor="galeri")
    try:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.image("assets/galeri2.png", caption="Mentoring", width=250)
        with col2:
            st.image("assets/galeri2.png", caption="Pelatihan", width=250)
        with col3:
            st.image("assets/galeri2.png", caption="Baksos", width=250)
    except FileNotFoundError:
        st.warning("Gambar 'assets/galeri2.png' tidak ditemukan.")
    except Exception as e:
            st.warning(f"Error loading image: {e}")

    st.header("Apa Kata Alumni")
    cols = st.columns(2)
    with cols[0]:
        st.markdown("""
        <div style='background-color: #e7f3ff; padding: 20px; border-radius: 10px; box-shadow: 0 3px 10px rgba(0,0,0,0.05);'>
        <em>“BKPK membentuk karakter dan meningkatkan kepekaan sosial saya.”</em><br>
        <strong>- Ahmad Rafi, Alumni 2022</strong>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown("""
        <div style='background-color: #fff0f6; padding: 20px; border-radius: 10px; box-shadow: 0 3px 10px rgba(0,0,0,0.05);'>
        <em>“Saya tumbuh secara spiritual dan organisasi di BKPK.”</em><br>
        <strong>- Nabila Hanun, Alumni 2021</strong>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div id='kontak'>
        <h2 style='text-align:center; color:black !important;'>Hubungi Kami</h2>
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

    st.markdown("---")
    tahun = datetime.now().year
    st.markdown(f"<p style='text-align: center; color:#6c757d;'>© {tahun} BKPK STT Nurul Fikri | TIM Kencore </p>", unsafe_allow_html=True)


else:
    # --- Konten untuk pengguna BELUM login ---
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
    """, unsafe_allow_html=True) # Menambahkan <hr> untuk pemisah navigasi dan hero section

    st.markdown("""
    <div style='
        text-align:center;
        background: linear-gradient(145deg, #f0f9ff, #dbeafe);
        padding: 40px 20px;
        border-radius: 16px;'
        id='beranda'>
        <h2>Selamat Datang di Portal BKPK STT NF</h2>
        <p>Silakan login untuk mengakses Sistem Presensi dan Pembinaan Karakter.</p>
    </div>
    <hr>
    """, unsafe_allow_html=True)


    # Tombol login kembali di bawah (seperti permintaan Anda)
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
    for i, (icon, desc) in enumerate(programs):
        with cols[i % 3]:
            st.markdown(f"""
    <div style='background-color: #f0f8ff; padding: 12px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.05);'>
        <strong>{icon} {desc.split(' ',1)[0]}</strong><br>{desc}
    </div>
    """, unsafe_allow_html=True)

    st.header("Galeri Kegiatan", anchor="galeri")
    try:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.image("assets/galeri2.png", caption="Mentoring", width=250)
        with col2:
            st.image("assets/galeri2.png", caption="Pelatihan", width=250)
        with col3:
            st.image("assets/galeri2.png", caption="Baksos", width=250)
    except FileNotFoundError:
        st.warning("Gambar 'assets/galeri2.png' tidak ditemukan.")
    except Exception as e:
            st.warning(f"Error loading image: {e}")

    st.header("Apa Kata Alumni")
    cols = st.columns(2)
    with cols[0]:
        st.markdown("""
        <div style='background-color: #e7f3ff; padding: 20px; border-radius: 10px; box-shadow: 0 3px 10px rgba(0,0,0,0.05);'>
        <em>“BKPK membentuk karakter dan meningkatkan kepekaan sosial saya.”</em><br>
        <strong>- Ahmad Rafi, Alumni 2022</strong>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown("""
        <div style='background-color: #fff0f6; padding: 20px; border-radius: 10px; box-shadow: 0 3px 10px rgba(0,0,0,0.05);'>
        <em>“Saya tumbuh secara spiritual dan organisasi di BKPK.”</em><br>
        <strong>- Nabila Hanun, Alumni 2021</strong>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div id='kontak'>
        <h2 style='text-align:center; color:#0d6efd;'>Hubungi Kami</h2>
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

    st.markdown("---")
    tahun = datetime.now().year
    st.markdown(f"<p style='text-align: center; color:#6c757d;'>© {tahun} BKPK STT Nurul Fikri | TIM Kencore </p>", unsafe_allow_html=True)


st.markdown("</div>", unsafe_allow_html=True)