import streamlit as st
import os
import csv
import cv2
import hashlib
from ultralytics import YOLO

# Konfigurasi Halaman & Tema Warna Global
st.set_page_config(
    page_title="PixelTag Studio - Universal Microstock AI",
    page_icon="💎",
    layout="centered"
)

st.markdown('''
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white; border-radius: 8px; padding: 0.6rem 1.5rem; font-weight: 600; border: none;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }
    .stButton>button:hover { opacity: 0.9; }
    .stat-card { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; text-align: center; }
    </style>
''', unsafe_allow_html=True)

# Inisialisasi Database Pengguna & Statistik Bisnis
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "pancaadmin@pixeltagstudio.com": {
            "password": hashlib.sha256("Monyet888!".encode()).hexdigest(), 
            "role": "admin", 
            "tier": "Pro"
        }
    }

if 'app_stats' not in st.session_state:
    st.session_state.app_stats = {
        "total_files_processed": 1420,
        "revenue_daily": 27.0,
        "revenue_monthly": 810.0,
        "revenue_yearly": 9720.0
    }

if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None

# --- SIDEBAR: PORTAL AUTENTIKASI & PROFIL PENGGUNA ---
st.sidebar.markdown("### 🔐 Portal Akun PixelTag Studio")

if st.session_state.logged_in_user is None:
    auth_mode = st.sidebar.radio("Pilih Aksi:", ["Masuk (Login)", "Daftar Akun Baru (Sign Up)"])
    
    if auth_mode == "Masuk (Login)":
        email_input = st.sidebar.text_input("Email")
        pass_input = st.sidebar.text_input("Kata Sandi", type="password")
        if st.sidebar.button("Masuk"):
            hashed_pass = hashlib.sha256(pass_input.encode()).hexdigest()
            if email_input in st.session_state.users_db and st.session_state.users_db[email_input]["password"] == hashed_pass:
                st.session_state.logged_in_user = email_input
                st.rerun()
            else:
                st.sidebar.error("Email atau Kata Sandi salah!")
    else:
        new_email = st.sidebar.text_input("Email Baru")
        new_pass = st.sidebar.text_input("Buat Kata Sandi", type="password")
        if st.sidebar.button("Daftar Sekarang"):
            if new_email in st.session_state.users_db:
                st.sidebar.error("Email sudah terdaftar!")
            elif new_email and new_pass:
                st.session_state.users_db[new_email] = {
                    "password": hashlib.sha256(new_pass.encode()).hexdigest(),
                    "role": "user",
                    "tier": "Free"
                }
                st.sidebar.success("Pendaftaran berhasil! Silakan masuk.")
            else:
                st.sidebar.warning("Harap isi semua kolom.")
else:
    current_email = st.session_state.logged_in_user
    user_info = st.session_state.users_db[current_email]
    
    st.sidebar.markdown(f"**Profil:** `{current_email}`")
    
    if user_info["tier"] == "Pro":
        st.sidebar.markdown("### 💎 Status: `PRO SUBSCRIBER`")
        st.sidebar.success("Akses tanpa batas aktif.")
    else:
        st.sidebar.markdown("### 🛡️ Status: `FREE MEMBER`")
        st.sidebar.warning("Batas: Maksimal 5 file per sesi.")
        st.sidebar.markdown("[🔗 Upgrade ke PRO ($9/bln)](https://your-lemonsqueezy-checkout-link.com)")
        
        if st.sidebar.button("Simulasikan Pembayaran Berhasil (Tes Pro)"):
            st.session_state.users_db[current_email]["tier"] = "Pro"
            st.session_state.app_stats["revenue_monthly"] += 9.0
            st.rerun()

    if st.sidebar.button("Keluar (Logout)"):
        st.session_state.logged_in_user = None
        st.rerun()

# --- HALAMAN UTAMA APLIKASI ---
st.markdown("<h1 style='text-align: center; color: #818cf8;'>💎 PixelTag Studio</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Mesin Generator Metadata Otomatis Berbasis AI untuk Kreator Global</p>", unsafe_allow_html=True)
st.divider()

if st.session_state.logged_in_user is None:
    st.info("👋 Silakan **Masuk (Login)** atau **Daftar Akun** terlebih dahulu melalui panel di sebelah kiri untuk mulai menggunakan generator AI.")
else:
    current_user = st.session_state.logged_in_user
    user_info = st.session_state.users_db[current_user]
    
    if user_info["role"] == "admin":
        st.markdown("### 📊 Admin Executive Dashboard & Business Insights")
        
        col1, col2, col3, col4 = st.columns(4)
        total_users = len(st.session_state.users_db)
        pro_users = sum(1 for u in st.session_state.users_db.values() if u["tier"] == "Pro")
        
        with col1:
            st.markdown(f"<div class='stat-card'><h4>Total Pengguna</h4><h2>{total_users}</h2></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='stat-card'><h4>Pengguna PRO</h4><h2>{pro_users}</h2></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='stat-card'><h4>Pendapatan Bulan Ini</h4><h2>${st.session_state.app_stats['revenue_monthly']}</h2></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div class='stat-card'><h4>Total Berkas AI</h4><h2>{st.session_state.app_stats['total_files_processed']}</h2></div>", unsafe_allow_html=True)
            
        st.markdown("---")
        
        with st.expander("⚙️ Admin Manager (Kelola Hak Akses Administrator)"):
            target_email_admin = st.selectbox("Pilih Pengguna untuk Diubah Role-nya:", list(st.session_state.users_db.keys()))
            current_role = st.session_state.users_db[target_email_admin]["role"]
            st.write(f"Status Role Saat Ini: **{current_role.upper()}**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Jadikan Admin"):
                    st.session_state.users_db[target_email_admin]["role"] = "admin"
                    st.success(f"Berhasil! {target_email_admin} sekarang adalah Administrator.")
                    st.rerun()
            with col_b:
                if st.button("Turunkan jadi User Biasa"):
                    if target_email_admin != "pancaadmin@pixeltagstudio.com":
                        st.session_state.users_db[target_email_admin]["role"] = "user"
                        st.warning(f"Hak admin dicabut dari {target_email_admin}.")
                        st.rerun()
                    else:
                        st.error("Admin utama sistem tidak dapat diturunkan!")

        with st.expander("📄 Pratinjau Laporan Kinerja Bulanan Otomatis"):
            st.markdown(f'''
            * **Periode Laporan:** Bulan Berjalan (Automated Business Summary)
            * **Total Pengguna Aktif:** {total_users} Akun ({pro_users} Berlangganan Pro)
            * **Total Aset Diproses AI:** {st.session_state.app_stats['total_files_processed']} Berkas Media
            * **Total Pendapatan Kotor:** ${st.session_state.app_stats['revenue_monthly']} USD
            * *Catatan Sistem:* Laporan siap dikirimkan otomatis ke email administrator setiap akhir bulan.
            ''')

        st.divider()

    st.markdown("### 📤 Unggah Berkas Media Anda")
    uploaded_files = st.file_uploader(
        "Seret & Letakkan foto atau video produk Anda di sini (JPG, PNG, WEBP, MP4, MOV)", 
        type=['jpg', 'jpeg', 'png', 'webp', 'mp4', 'mov'], 
        accept_multiple_files=True
    )

    if uploaded_files:
        if user_info["tier"] == "Free" and len(uploaded_files) > 5:
            st.error("❌ Batas kuota Free Tier terlampaui! Maksimal 5 file per sesi. Silakan upgrade ke akun PRO.")
        else:
            if st.button("🚀 Mulai Proses AI & Hasilkan Metadata"):
                with st.spinner("🤖 AI sedang menganalisis gambar/video dan merapikan standar SEO..."):
                    
                    output_folder = "temp_files"
                    os.makedirs(output_folder, exist_ok=True)
                    model = YOLO('yolov8s.pt')
                    csv_filename = "pixeltag_studio_metadata.csv"
                    
                    with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                        writer.writerow(['Filename', 'Description', 'Keywords'])
                        
                        for uploaded_file in uploaded_files:
                            file_path = os.path.join(output_folder, uploaded_file.name)
                            with open(file_path, "wb") as f_out:
                                f_out.write(uploaded_file.getbuffer())
                                
                            results = model(file_path, conf=0.5, verbose=False)
                            tags = ['commercial use', 'stock photo', 'isolated', 'object', 'studio shot']
                            
                            for r in results:
                                for box in r.boxes:
                                    label = model.names[int(box.cls[0])]
                                    if label not in tags:
                                        tags.append(label.replace('_', ' '))
                                        
                            tags = list(dict.fromkeys(tags))
                            desc = f"Professional stock asset of {tags[0]} for commercial and e-commerce presentation."
                            writer.writerow([uploaded_file.name, desc, ", ".join(tags[:49])])
                            
                            st.session_state.app_stats['total_files_processed'] += 1
                    
                    st.success("✨ Analisis Selesai! Data metadata Anda telah dioptimasi.")
                    
                    with open(csv_filename, "rb") as file_dl:
                        st.download_button(
                            label="📥 Unduh File CSV Siap Unggah",
                            data=file_dl,
                            file_name="pixeltag_studio_metadata.csv",
                            mime="text/csv"
                        )
