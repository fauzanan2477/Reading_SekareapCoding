import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.optimize import linprog
import uuid  

# ==============================
# 1. KONFIGURASI HALAMAN & CSS 
# ==============================
st.set_page_config(page_title="Sistem Pakar MBG", layout="wide")

st.markdown("""
 <style>
 /* Latar Belakang Utama Aplikasi (Warna 1) */
 .stApp { 
     background-color: #2D3142; 
     color: #FFFFFF; 
 }
 
 /* Gaya Judul Besar Mendominasi (Di Tab Beranda) */
 .hero-title-large { 
     font-size: 3.5rem; 
     font-weight: 900; 
     color: #FFFFFF; 
     text-align: center; 
     margin-top: 4vh; 
     line-height: 1.3;
 }
 .hero-title-large span { color: #EF8354; } 
 
 /* Gaya Petunjuk Formal */
 .instruction-text {
     font-size: 1.2rem;
     color: #BFC0C0; 
     text-align: center;
     margin-top: 20px;
     margin-bottom: 50px;
     font-weight: 500;
     letter-spacing: 0.5px;
     animation: blink 2s infinite; 
 }
 @keyframes blink {
     0% { opacity: 0.4; }
     50% { opacity: 1; }
     100% { opacity: 0.4; }
 }

 /* Gaya Judul Mengecil Jadi Header (Di Tab Lain) */
 .header-title-small { 
     font-size: 1.8rem; 
     font-weight: 800; 
     color: #FFFFFF; 
     text-align: left; 
     margin-bottom: 20px;
     border-bottom: 2px solid #4F5D75;
     padding-bottom: 10px;
 }
 .header-title-small span { color: #EF8354; }

 /* Gaya Tab Navigasi Menu */
 .stTabs [data-baseweb="tab-list"] { 
     justify-content: center; 
     gap: 20px; 
     background-color: #4F5D75; 
     padding: 8px; 
     border-radius: 8px; 
 }
 .stTabs [data-baseweb="tab"] { 
     font-weight: 700; 
     color: #BFC0C0; 
 }
 .stTabs [aria-selected="true"] { 
     color: #EF8354 !important; 
 }
 /* Menghapus latar belakang batang hitam atas */
 header {
     background-color: transparent !important;
     background: transparent !important;
     box-shadow: none !important;
 }
 
 /* Memastikan tombol menu garis tiga tetap kelihatan dan warnanya putih agar kontras */
 div[data-testid="stToolbar"] {
     background: transparent !important;
 }
 </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATABASE (SESSION STATE)
# ==========================================
if 'database_bahan' not in st.session_state:
    st.session_state['database_bahan'] = pd.DataFrame({
        "ID": [str(uuid.uuid4()) for _ in range(6)], 
        "Gunakan": [True, True, True, True, False, True], 
        "Bahan Makanan": ["Nasi Putih", "Telur Ayam", "Tempe Murni", "Sayur Bayam", "Susu Sapi", "Daging Ayam"],
        "Harga (Rp)": [1500, 2800, 1500, 1000, 2000, 4500], 
        "Kalori (Kkal)": [130.0, 155.0, 193.0, 23.0, 61.0, 165.0],
        "Protein (g)": [2.7, 13.0, 19.0, 2.9, 3.2, 31.0],
        "Lemak (g)": [0.3, 11.0, 11.0, 0.4, 3.3, 3.6],
        "Karbohidrat (g)": [28.6, 1.1, 9.4, 3.6, 4.8, 0.0],
        "Batas Maksimal (g)": [250.0, 100.0, 100.0, 150.0, 200.0, 150.0] 
    })


if "ID" not in st.session_state['database_bahan'].columns:
    st.session_state['database_bahan']["ID"] = [str(uuid.uuid4()) for _ in range(len(st.session_state['database_bahan']))]

if 'target_kalori' not in st.session_state:
    st.session_state.update({
        'target_kalori': 1800.0, 'target_protein': 45.0, 'target_lemak': 40.0, 'target_karbo': 202.5,
        'nilai_aktivitas': 1.55, 'nilai_bmr': 1161.0, 'pembagi_waktu': 1,
        'rumus_amb_teks': r"\text{AMB (P)} = 16.97 Wt + 161.8 Ht + 371.2",
        'rumus_amb_angka': r"\text{AMB (P)} = (16.97 \times 30.0) + (161.8 \times 1.35) + 371.2"
    })


if 'form_biodata' not in st.session_state:
    st.session_state['form_biodata'] = {
        'umur': 10,
        'jk': 0, 
        'aktivitas': 2,
        'bb': 30.0,
        'tb': 135.0,
        'waktu': 0 
    }

# ============================
# 4. SISTEM NAVIGASI HALAMAN 
# =============================

if 'halaman' not in st.session_state:
    st.session_state['halaman'] = 'beranda'
if 'hitung_sukses' not in st.session_state:
    st.session_state['hitung_sukses'] = False

# --- SITUS UTAMA / BERANDA ---
if st.session_state['halaman'] == 'beranda':
    st.write("##")
    st.write("##")
    
    st.markdown("""
        <div class="hero-title-large">
            Sistem Pakar Optimasi Anggaran<br><span>Makan Bergizi Gratis (MBG)</span>
        </div>
        <div class="instruction-text" style="margin-bottom: 40px;">
            Silakan pilih modul di bawah ini untuk memulai komputasi sistem pakar
        </div>
    """, unsafe_allow_html=True)
    
    kolom_tombol1, kolom_tombol2, kolom_tombol3 = st.columns(3)
    
    with kolom_tombol1:
        if st.button("Kalkulator & Optimasi Gizi", use_container_width=True, type="primary"):
            st.session_state['halaman'] = 'kalkulator'
            st.rerun()
            
    with kolom_tombol2:
        if st.button("Langkah Perhitungan Manual", use_container_width=True):
            st.session_state['halaman'] = 'manual'
            st.rerun()
    with kolom_tombol3:
        if st.button("Rumus Lengkap", use_container_width=True):
            st.session_state['halaman'] = 'dokumentasi'
            st.rerun()

# --- MODUL KALKULATOR GIZI & OPTIMASI AL JABAR ---
elif st.session_state['halaman'] == 'kalkulator':
    if st.button("⬅️ Kembali ke Beranda Utama"):
        st.session_state['halaman'] = 'beranda'
        st.rerun()
        
    st.markdown('<div class="header-title-small">Sistem Pakar <span>MBG</span></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### Penentuan Vektor Konstanta Gizi (B)")

    st.write("Sistem menghitung target Makronutrien anak berdasarkan **Persamaan AMB Schofield** dan tingkat aktivitas fisik (Merujuk pada Jurnal Brawijaya).")
    
    kolom1, kolom2 = st.columns(2)
    
    with kolom1:
        umur_anak = st.number_input("Umur Anak (Tahun)", min_value=1, max_value=18, value=st.session_state['form_biodata']['umur'])
        jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"], index=st.session_state['form_biodata']['jk'])
        tingkat_aktivitas = st.selectbox("Tingkat Aktivitas Fisik (Olahraga)", [
            "Sangat Jarang (Pasif / Tidak olahraga)",
            "Jarang (Olahraga ringan 1-3 hari/minggu)",
            "Cukup (Olahraga sedang 3-5 hari/minggu)",
            "Sering (Olahraga berat 6-7 hari/minggu)",
            "Sangat Sering (Atlet / Fisik ekstra)"
        ], index=st.session_state['form_biodata']['aktivitas'])
        
    with kolom2:
        berat_badan = st.number_input("Berat Badan / Wt (kg)", min_value=5.0, value=st.session_state['form_biodata']['bb'])
        tinggi_badan = st.number_input("Tinggi Badan / Ht (cm)", min_value=50.0, value=st.session_state['form_biodata']['tb'])
        skenario_waktu = st.selectbox("Target Pemenuhan Gizi (Skenario)", [
            "1 Hari Penuh (Sesuai Jurnal Referensi)", 
            "1x Makan (Program MBG - Dibagi 3)"
        ], index=st.session_state['form_biodata']['waktu'])
    
    if st.button("Hitung Target & Simpan", type="primary"):
        
        st.session_state['form_biodata'] = {
            'umur': umur_anak,
            'jk': 0 if jenis_kelamin == "Laki-laki" else 1,
            'aktivitas': [
                "Sangat Jarang (Pasif / Tidak olahraga)",
                "Jarang (Olahraga ringan 1-3 hari/minggu)",
                "Cukup (Olahraga sedang 3-5 hari/minggu)",
                "Sering (Olahraga berat 6-7 hari/minggu)",
                "Sangat Sering (Atlet / Fisik ekstra)"
            ].index(tingkat_aktivitas),
            'bb': berat_badan,
            'tb': tinggi_badan,
            # [PERBAIKAN 3] Menyamakan string teks persis dengan opsi dropdown agar tidak reset
            'waktu': 0 if skenario_waktu == "1 Hari Penuh (Sesuai Jurnal Referensi)" else 1
        }
        
        if tingkat_aktivitas == "Sangat Jarang (Pasif / Tidak olahraga)": pengali_aktivitas = 1.2
        elif tingkat_aktivitas == "Jarang (Olahraga ringan 1-3 hari/minggu)": pengali_aktivitas = 1.375
        elif tingkat_aktivitas == "Cukup (Olahraga sedang 3-5 hari/minggu)": pengali_aktivitas = 1.55
        elif tingkat_aktivitas == "Sering (Olahraga berat 6-7 hari/minggu)": pengali_aktivitas = 1.725
        else: pengali_aktivitas = 1.9

        tinggi_meter = tinggi_badan / 100.0 
        
        if jenis_kelamin == "Laki-laki":
            label_jk = "L"
            if umur_anak <= 3:
                koef_berat, koef_tinggi, konstanta = 0.167, 1517.4, -617.6
            elif umur_anak <= 10:
                koef_berat, koef_tinggi, konstanta = 19.6, 130.3, 414.9
            else: 
                koef_berat, koef_tinggi, konstanta = 16.25, 137.2, 515.5
        else:
            label_jk = "P"
            if umur_anak <= 3:
                koef_berat, koef_tinggi, konstanta = 16.25, 1023.2, -413.5
            elif umur_anak <= 10:
                koef_berat, koef_tinggi, konstanta = 16.97, 161.8, 371.2
            else: 
                koef_berat, koef_tinggi, konstanta = 8.365, 465.0, 200.0

        bmr_dihitung = (koef_berat * berat_badan) + (koef_tinggi * tinggi_meter) + konstanta
        tanda_konstanta = "+" if konstanta > 0 else "-"
        
        teks_rumus = fr"\text{{AMB ({label_jk})}} = {koef_berat} Wt + {koef_tinggi} Ht {tanda_konstanta} {abs(konstanta)}"
        angka_rumus = fr"\text{{AMB ({label_jk})}} = ({koef_berat} \times {berat_badan}) + ({koef_tinggi} \times {tinggi_meter}) {tanda_konstanta} {abs(konstanta)}"

        pembagi = 1 if "1 Hari Penuh" in skenario_waktu else 3
        
        kebutuhan_kalori = (bmr_dihitung * pengali_aktivitas) / pembagi
        kebutuhan_protein = (kebutuhan_kalori * 0.10) / 4 
        kebutuhan_lemak = (kebutuhan_kalori * 0.20) / 9 
        kebutuhan_karbo = (kebutuhan_kalori * 0.45) / 4 
        
        st.session_state.update({
            'nilai_bmr': round(bmr_dihitung, 1), 'nilai_aktivitas': pengali_aktivitas, 'pembagi_waktu': pembagi,
            'target_kalori': round(kebutuhan_kalori, 1), 'target_protein': round(kebutuhan_protein, 1),
            'target_lemak': round(kebutuhan_lemak, 1), 'target_karbo': round(kebutuhan_karbo, 1),
            'rumus_amb_teks': teks_rumus, 'rumus_amb_angka': angka_rumus
        })
        st.success(f"Target Gizi diperbarui ({skenario_waktu})! ")
        st.session_state['halaman'] = 'hasil_kalkulasi'
        st.rerun()
        st.session_state['hitung_sukses'] = True
    st.markdown('</div>', unsafe_allow_html=True)

# --- HALAMAN 2: EKSEKUSI OPTIMASI ---
elif st.session_state['halaman'] == 'hasil_kalkulasi':
    if st.button("⬅️ Kembali ke Input Data"):
        st.session_state['halaman'] = 'kalkulator'
        st.rerun()
        
    st.markdown('<div class="header-title-small">Sistem Pakar <span>MBG</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="white-box" style="border-left: 5px solid #e1b12c;">', unsafe_allow_html=True)
    st.write("####  Target Gizi Saat Ini (Syarat Matriks Batas Bawah):")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Kalori Minimal", f"{st.session_state['target_kalori']} Kkal")
    k2.metric("Protein (Min 10%)", f"{st.session_state['target_protein']} Gram")
    k3.metric("Lemak (Min 20%)", f"{st.session_state['target_lemak']} Gram")
    k4.metric("Karbo (Min 45%)", f"{st.session_state['target_karbo']} Gram")
    st.markdown('</div>', unsafe_allow_html=True)
  
    st.write("###  Porsi Menu Makan Bergizi Gratis (MBG)")
    
    # FORM TAMBAH LAUK BARU
    with st.expander("➕ Tambah Menu Makanan / Lauk Baru Custom"):
        st.write("Masukkan detail bahan makanan baru untuk dimasukkan ke dalam daftar kalkulasi:")
        c_nama, c_harga = st.columns([2, 1])
        with c_nama:
            nama_baru = st.text_input("Nama Makanan / Lauk Baru:", placeholder="Contoh: Daging Sapi, Tahu, Ikan Kembung")
        with c_harga:
            harga_baru = st.number_input("Harga per 100 Gram (Rp):", min_value=0.0, value=15.0, step=1.0)
            
        g1, g2, g3, g4 = st.columns(4)
        with g1: kalori_baru = st.number_input("Kalori (Kkal/100g):", min_value=0.0, value=2.5, step=0.1)
        with g2: protein_baru = st.number_input("Protein (g/100g):", min_value=0.0, value=0.2, step=0.01)
        with g3: lemak_baru = st.number_input("Lemak (g/100g):", min_value=0.0, value=0.1, step=0.01)
        with g4: karbo_baru = st.number_input("Karbohidrat (g/100g):", min_value=0.0, value=0.0, step=0.01)
            
        if st.button(" Masukkan Makanan ke Daftar", type="primary"):
            if nama_baru.strip() != "":
                # [PERBAIKAN 2] Mengembalikan key ke "Harga (Rp)" agar tidak membuat kolom duplikat
                df_baru = pd.DataFrame({
                    "ID": [str(uuid.uuid4())], 
                    "Gunakan": [True], 
                    "Bahan Makanan": [nama_baru],
                    "Harga (Rp)": [harga_baru], 
                    "Kalori (Kkal)": [kalori_baru],
                    "Protein (g)": [protein_baru],
                    "Lemak (g)": [lemak_baru],
                    "Karbohidrat (g)": [karbo_baru],
                    "Batas Maksimal (g)": [150.0]
                })
                st.session_state['database_bahan'] = pd.concat([st.session_state['database_bahan'], df_baru], ignore_index=True)
                st.session_state['halaman'] = 'kalkulator'
                st.success(f"Berhasil menambahkan '{nama_baru}' ke dalam menu pilihan!")
                st.rerun()
            else:
                st.error("Nama makanan tidak boleh kosong!")

    st.write("---") 
    st.write("Gunakan tombol +/- untuk mengatur porsi, dan klik tombol rincian untuk melihat kandungan gizi lauk.")
      
    # ==========================================
    # FUNGSI CALLBACK MENGHAPUS BERDASARKAN ID 
    # ==========================================
    def hapus_bahan_callback(id_to_drop):
        df_sekarang = st.session_state['database_bahan']
        # Filter keluar baris yang memiliki ID tersebut
        st.session_state['database_bahan'] = df_sekarang[df_sekarang["ID"] != id_to_drop].reset_index(drop=True)

    list_gunakan = []
    list_batas_maksimal = []
     
    database_aktif = st.session_state['database_bahan']
    total_bahan = len(database_aktif)
      
    # Melakukan looping per 3 bahan makanan sekaligus untuk membuat baris baru
    for i in range(0, total_bahan, 3):
         # Membuat 3 kolom horizontal berdampingan di satu baris
         kolom_card = st.columns(3)
         
         
         for j in range(3):
             idx_bahan = i + j
             if idx_bahan < total_bahan:
                 row = database_aktif.iloc[idx_bahan]
                 unique_uid = str(row["ID"]) 
                 
                 
                 with kolom_card[j]:
                     
                     with st.container(border=True):
                     
                         
                         c_nama, c_aktif = st.columns([3, 1])
                         with c_nama:
                             st.markdown(f"##### **{row['Bahan Makanan']}**")
                         with c_aktif:
                             status_aktif = st.checkbox("Pakai", value=row["Gunakan"], key=f"chk_{unique_uid}", label_visibility="collapsed")
                             list_gunakan.append(status_aktif)
                         
                         
                         porsi_maks = st.number_input(
                             "Batas Maksimal (Gram):",
                             min_value=0.0,
                             max_value=1000.0,
                             value=float(row["Batas Maksimal (g)"]),
                             step=50.0,
                             key=f"num_{unique_uid}"
                         )
                         list_batas_maksimal.append(porsi_maks)
                     
                         
                         c_pop, c_del = st.columns([4, 1])
                         
                         with c_pop:
                             with st.popover("📋 Detail & Edit Gizi", use_container_width=True):
                                 st.markdown(f"####  Nilai Gizi {row['Bahan Makanan']}")
                                 edit_harga = st.number_input(f"Harga (Rp/100g)", min_value=0, value=int(row["Harga (Rp)"]), key=f"hrg_{unique_uid}")
                                 edit_kalori = st.number_input(f"Kalori (Kkal/100g)", min_value=0.0, value=float(row["Kalori (Kkal)"]), key=f"kal_{unique_uid}")
                                 edit_protein = st.number_input(f"Protein (g/100g)", min_value=0.0, value=float(row["Protein (g)"]), key=f"pro_{unique_uid}")
                                 edit_lemak = st.number_input(f"Lemak (g/100g)", min_value=0.0, value=float(row["Lemak (g)"]), key=f"lem_{unique_uid}")
                                 edit_karbo = st.number_input(f"Karbohidrat (g/100g)", min_value=0.0, value=float(row["Karbohidrat (g)"]), key=f"kar_{unique_uid}")
                                 
                                 # [PERBAIKAN 2] Menyamakan update ke key "Harga (Rp)" asli agar Manual Tabel ter-update
                                 st.session_state['database_bahan'].at[idx_bahan, "Harga (Rp)"] = edit_harga
                                 st.session_state['database_bahan'].at[idx_bahan, "Kalori (Kkal)"] = edit_kalori
                                 st.session_state['database_bahan'].at[idx_bahan, "Protein (g)"] = edit_protein
                                 st.session_state['database_bahan'].at[idx_bahan, "Lemak (g)"] = edit_lemak
                                 st.session_state['database_bahan'].at[idx_bahan, "Karbohidrat (g)"] = edit_karbo
                                 
                         with c_del:
                             # TOMBOL HAPUS MENGGUNAKAN ID UID
                             st.button("🗑️", key=f"del_{unique_uid}", use_container_width=True, help="Hapus menu dari daftar", on_click=hapus_bahan_callback, args=(unique_uid,))

    
    st.session_state['database_bahan']['Gunakan'] = list_gunakan
    st.session_state['database_bahan']['Batas Maksimal (g)'] = list_batas_maksimal

    def jalankan_optimasi(df_pilihan, kal, pro, lem, kar, batas_bawah_satuan=0.0):
        array_harga = pd.to_numeric(df_pilihan["Harga (Rp)"]).fillna(0).values
        matriks_gizi = df_pilihan[["Kalori (Kkal)", "Protein (g)", "Lemak (g)", "Karbohidrat (g)"]].apply(pd.to_numeric).fillna(0).values
        
        batas_bounds = []
        for p in pd.to_numeric(df_pilihan["Batas Maksimal (g)"]).fillna(1000).values:
            max_val = p / 100.0
            b_bawah = batas_bawah_satuan if batas_bawah_satuan <= max_val else max_val
            batas_bounds.append((b_bawah, max_val))
            
        A_kiri = -1 * matriks_gizi.T
        B_kanan = -1 * np.array([kal, pro, lem, kar])
        return linprog(array_harga, A_ub=A_kiri, b_ub=B_kanan, bounds=batas_bounds, method='highs')

    if st.button(" Kalkulasi Biaya Termurah", type="primary", use_container_width=True):
        bahan_terpilih = st.session_state['database_bahan'][st.session_state['database_bahan']["Gunakan"] == True].copy()
        
        if len(bahan_terpilih) < 2:
            st.error("⚠️ Centang minimal 2 bahan makanan untuk komputasi matriks.")
        else:
            # ---> TABEL RINGKASAN DICETAK DI SINI <---
            st.write("---")
            st.write("### Ringkasan Bahan Makanan Terpilih")
            st.write("Berikut adalah menu yang masuk ke dalam komputasi sistem sebelum dioptimasi:")
            
            
            df_ringkasan = bahan_terpilih.drop(columns=["ID", "Gunakan"])
            st.dataframe(df_ringkasan, use_container_width=True, hide_index=True)

            # [PERBAIKAN 2] Memanggil kolom "Harga (Rp)" agar match dengan perbaikan sebelumnya
            array_harga = pd.to_numeric(bahan_terpilih["Harga (Rp)"], errors='coerce').fillna(0).values
            matriks_gizi = bahan_terpilih[["Kalori (Kkal)", "Protein (g)", "Lemak (g)", "Karbohidrat (g)"]].apply(pd.to_numeric, errors='coerce').fillna(0).values
            
            
            batas_maksimal = [(0, p/100.0) for p in pd.to_numeric(bahan_terpilih["Batas Maksimal (g)"], errors='coerce').fillna(1000).values]
            
            
            A_kiri = -1 * matriks_gizi.T
            B_kanan = -1 * np.array([st.session_state['target_kalori'], st.session_state['target_protein'], st.session_state['target_lemak'], st.session_state['target_karbo']])
            
            try:
                solusi = linprog(array_harga, A_ub=A_kiri, b_ub=B_kanan, bounds=batas_maksimal, method='highs')
                
                if solusi.success:
                     
                    st.markdown(f"""
                    <div class="result-card" style="background-color: #EF8354; padding: 20px; border-radius: 10px; color: white; text-align: center; margin-top: 20px; margin-bottom: 20px;">
                        <p style="margin: 0; font-size: 1.2rem; font-weight: bold; color: white !important;">Total Biaya Paling Minimum (Titik Optimal)</p>
                        <h2 style="margin: 0; font-size: 3rem; font-weight: 900; color: white !important;">Rp {solusi.fun:,.0f}</h2>
                        <p style="margin: 0; color: white !important;">Solusi Makanan Termurah Sesuai Target Waktu</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('<div class="white-box">', unsafe_allow_html=True)
                    st.write("### ⚖️ Vektor Rekomendasi Takaran")
                    hasil_gram = solusi.x * 100 
                    tabel_hasil = pd.DataFrame({
                        "Bahan Makanan": bahan_terpilih["Bahan Makanan"].values,
                        "Takaran Disarankan": [f"{g:,.0f} Gram" for g in hasil_gram],
                        "Biaya Realisasi": [f"Rp {(g/100)*h:,.0f}" for g, h in zip(hasil_gram, array_harga)]
                    })
                    st.table(tabel_hasil[solusi.x > 0.01].reset_index(drop=True))
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.write("---")
                    st.write("###  Analisis Pemenuhan Gizi (Target vs Realisasi)")
                    
                    total_kal_riil = sum((g/100) * k for g, k in zip(hasil_gram, pd.to_numeric(bahan_terpilih["Kalori (Kkal)"]).values))
                    total_pro_riil = sum((g/100) * p for g, p in zip(hasil_gram, pd.to_numeric(bahan_terpilih["Protein (g)"]).values))
                    total_lem_riil = sum((g/100) * l for g, l in zip(hasil_gram, pd.to_numeric(bahan_terpilih["Lemak (g)"]).values))
                    total_kar_riil = sum((g/100) * c for g, c in zip(hasil_gram, pd.to_numeric(bahan_terpilih["Karbohidrat (g)"]).values))
                    
                    kategori = ['Protein (g)', 'Lemak (g)', 'Karbohidrat (g)']
                    target_gizi = [st.session_state['target_protein'], st.session_state['target_lemak'], st.session_state['target_karbo']]
                    realisasi_gizi = [total_pro_riil, total_lem_riil, total_kar_riil]
                    
                    fig_bar = go.Figure(data=[
                        go.Bar(name='Target Minimal', x=kategori, y=target_gizi, marker_color='#BFC0C0'),
                        go.Bar(name='Realisasi (Hasil Optimasi)', x=kategori, y=realisasi_gizi, marker_color='#EF8354')
                    ])
                    fig_bar.update_layout(
                        barmode='group',
                        title="Perbandingan Target vs Realisasi Makronutrien (Gram)",
                        plot_bgcolor='#2D3142', paper_bgcolor='#2D3142', font=dict(color='#FFFFFF'),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

                    st.write("---")
                    st.write("###  Analisis Sensitivitas (Sesuai Jurnal Universitas Brawijaya)")
                    st.write("Grafik di bawah ini memanipulasi batas minimal porsi untuk membuktikan bahwa melonggarkan syarat porsi minimal akan memperluas daerah *feasible* (menurunkan total biaya).")
                    
                    rentang_minimal = [1.0, 0.8, 0.6, 0.4, 0.2, 0.1]
                    hasil_simulasi = []
                    
                    for batas_min in rentang_minimal:
                        sol_sim = jalankan_optimasi(bahan_terpilih, st.session_state['target_kalori'], st.session_state['target_protein'], st.session_state['target_lemak'], st.session_state['target_karbo'], batas_bawah_satuan=batas_min)
                        if sol_sim.success:
                            hasil_simulasi.append({
                                "nilai_x": batas_min,
                                "biaya": sol_sim.fun
                            })
                    
                    if hasil_simulasi:
                        x_vals = [f"Batas {d['nilai_x']}" for d in hasil_simulasi] 
                        y_vals = [d['biaya'] for d in hasil_simulasi]
                        
                        fig_line = go.Figure()
                        fig_line.add_trace(go.Scatter(
                            x=x_vals, y=y_vals, mode='lines+markers', name='Biaya Minimum',
                            marker=dict(size=12, color='#EF8354'), line=dict(width=4, color='#BFC0C0')
                        ))
                        
                        fig_line.update_layout(
                            title="Pergerakan Penurunan Biaya terhadap Pelonggaran Batas Porsi",
                            xaxis_title="Skenario Batas Minimal Porsi (Semakin ke Kanan Semakin Longgar)",
                            yaxis_title="Biaya Minimum (Rp)",
                            hovermode="x unified", plot_bgcolor='#2D3142', paper_bgcolor='#2D3142', font=dict(color='#FFFFFF')
                        )
                        fig_line.update_xaxes(categoryorder='array', categoryarray=x_vals, gridcolor='#4F5D75')
                        fig_line.update_yaxes(gridcolor='#4F5D75')
                        st.plotly_chart(fig_line, use_container_width=True)

                else:
                    st.error("🚨 SPL Infeasible: Matriks gagal terpenuhi. Coba perbesar 'Batas Maksimal (g)' atau tambahkan variasi lauk.")
            except Exception as e:
                st.error(f"Error komputasi: {e}")

# --- HALAMAN 3: LANGKAH MANUAL (SANGAT DETAIL SESUAI JURNAL) ---
elif st.session_state['halaman'] == 'manual':
    if st.button("⬅️ Kembali ke Beranda Utama"):
        st.session_state['halaman'] = 'beranda'
        st.rerun()
    st.markdown('<div class="header-title-small">Sistem Pakar <span>MBG</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### ✍️ Simulasi Pemodelan Aljabar Linier")
    st.write("Proses di bawah ini menjabarkan komputasi yang terjadi di balik layar, mengacu pada tahapan Metode Simpleks Dua Fase di Jurnal Universitas Brawijaya.")
    
    # ------------------ TAHAP 1 ------------------
    st.write("---")
    st.write("#### TAHAP 1: Penentuan Konstanta Gizi (Vektor B)")
    st.markdown("**1. Angka Metabolisme Basal (AMB) - Persamaan Schofield**")
    st.latex(st.session_state['rumus_amb_teks'])
    st.latex(st.session_state['rumus_amb_angka'] + f" = {st.session_state['nilai_bmr']} \\text{{ Kkal}}")
    
    st.markdown("**2. Total Energy Expenditure (TEE)**")
    st.latex(r"TEE = AMB \times \text{Faktor Aktivitas (PAL)}")
    st.latex(f"TEE = {st.session_state['nilai_bmr']} \\times {st.session_state['nilai_aktivitas']} = {round(st.session_state['nilai_bmr'] * st.session_state['nilai_aktivitas'], 1)} \\text{{ Kkal}}")
    
    st.markdown("**3. Target Kalori Akhir (K)**")
    if st.session_state['pembagi_waktu'] == 1:
        st.latex(f"K = TEE = {st.session_state['target_kalori']} \\text{{ Kkal}}")
    else:
        st.latex(f"K = \\frac{{TEE}}{{3}} = {st.session_state['target_kalori']} \\text{{ Kkal}}")
    
    st.markdown("**4. Distribusi Batas Bawah Gizi (10% Pro, 20% Lemak, 45% Karbo)**")
    st.latex(r"\text{Protein (P)} = \frac{10\% \times K}{4} = " + str(st.session_state['target_protein']) + r" \text{ g}")
    st.latex(r"\text{Lemak (L)} = \frac{20\% \times K}{9} = " + str(st.session_state['target_lemak']) + r" \text{ g}")
    st.latex(r"\text{Karbo (C)} = \frac{45\% \times K}{4} = " + str(st.session_state['target_karbo']) + r" \text{ g}")
    
    bahan_aktif = st.session_state['database_bahan'][st.session_state['database_bahan']["Gunakan"] == True].reset_index(drop=True)
    
    if len(bahan_aktif) >= 2:
        nama_nutrisi = ["Kalori (Kkal)", "Protein (g)", "Lemak (g)", "Karbohidrat (g)"]
        batas_nutrisi = [st.session_state['target_kalori'], st.session_state['target_protein'], st.session_state['target_lemak'], st.session_state['target_karbo']]
        
        # ------------------ TAHAP 2 ------------------
        st.write("---")
        st.write("#### TAHAP 2: Pembentukan Model Matematika")
        st.write("Pemodelan fungsi tujuan untuk meminimalkan biaya ($Z$), dan fungsi kendala nutrisi minimal ($\ge$).")
        
        rumus_Z = " + ".join([f"{int(baris['Harga (Rp)'])}x_{i+1}" for i, baris in bahan_aktif.iterrows()])
        st.latex(r"\text{Fungsi Tujuan: Min } Z = " + rumus_Z)
        
        st.write("**Fungsi Kendala:**")
        for i, nutrisi in enumerate(nama_nutrisi):
            rumus_kendala = " + ".join([f"{baris[nutrisi]}x_{j+1}" for j, baris in bahan_aktif.iterrows()])
            st.latex(rumus_kendala + f" \ge {batas_nutrisi[i]}")
        
        # ------------------ TAHAP 3 ------------------
        st.write("---")
        st.write("#### TAHAP 3: Bentuk Standar (Kanonik)")
        st.write("Agar menjadi persamaan linear ($=$), setiap kendala $\ge$ harus dikurangi Variabel Surplus ($S$) dan ditambah Variabel Semu/Artificial ($R$).")
        for i, nutrisi in enumerate(nama_nutrisi):
            rumus_kanonik = " + ".join([f"{baris[nutrisi]}x_{j+1}" for j, baris in bahan_aktif.iterrows()])
            st.latex(rumus_kanonik + f" - S_{i+1} + R_{i+1} = {batas_nutrisi[i]}")
        
        # ------------------ TAHAP 4 ------------------
        st.write("---")
        st.write("#### TAHAP 4: Eksekusi Fase 1 (Mencari Solusi Fisibel)")
        st.write("Pada Fase 1, nilai uang ($Z$) diabaikan sementara. Tujuan diubah untuk **meminimalkan variabel fiktif $R$** hingga habis ($W=0$).")
        st.latex(r"\text{Fungsi Tujuan Fase 1: Min } W = R_1 + R_2 + R_3 + R_4")
        
        header_kolom = ["Basis"] + [f"x{i+1}" for i in range(len(bahan_aktif))] + ["S1", "S2", "S3", "S4", "R1", "R2", "R3", "R4", "NK"]
        data_tableau = []
        
        # Menyusun baris matriks secara dinamis
        for i, nutrisi in enumerate(nama_nutrisi):
            baris = [f"R{i+1}"] + bahan_aktif[nutrisi].tolist()
            kolom_surplus = [0]*4; kolom_surplus[i] = -1
            kolom_artificial = [0]*4; kolom_artificial[i] = 1
            baris.extend(kolom_surplus + kolom_artificial + [batas_nutrisi[i]])
            data_tableau.append(baris)
            
        # Baris W adalah penjumlahan seluruh koefisien fungsi kendala
        baris_W = ["W (Fase 1)"] + [sum(bahan_aktif.loc[j, nama_nutrisi]) for j in range(len(bahan_aktif))]
        baris_W.extend([-1, -1, -1, -1, 0, 0, 0, 0, sum(batas_nutrisi)])
        data_tableau.append(baris_W)
        
        df_tableau = pd.DataFrame(data_tableau, columns=header_kolom)
        st.dataframe(df_tableau.style.format(precision=1), use_container_width=True, hide_index=True)
        st.caption(" *Ini adalah Tableau Initial Fase 1 yang sudah ter-substitusi.*")
        
        st.markdown("""
        **🔄 Proses Lanjutan Fase 1 (Operasi Baris Elementer):**
        Sistem komputer melakukan iterasi (Pivot) pada matriks di atas dengan tahapan:
        1. **Menentukan Kolom Masuk (Entering Variable):** Mencari nilai paling positif pada baris $W$.
        2. **Menentukan Baris Keluar (Leaving Variable):** Menghitung Rasio = Nilai Kanan (NK) dibagi nilai Kolom Masuk, lalu memilih rasio terkecil.
        3. **Eliminasi Gauss-Jordan:** Mengubah elemen pivot menjadi 1, dan elemen di atas/bawahnya menjadi 0.
        4. Mengulang langkah 1-3 hingga seluruh elemen baris $W \le 0$ (semua variabel $R$ hilang).
        """)
        
        # ------------------ TAHAP 5 ------------------
        # PERBAIKAN: Melengkapi langkah manual yang sempat hilang
        st.write("---")
        st.write("#### TAHAP 5: Eksekusi Fase 2 (Optimasi Biaya Minimum)")
        st.write("Setelah semua kolom $R$ berhasil dibuang, fungsi harga asli ($Z$) dikembalikan ke dalam matriks untuk iterasi Fase 2.")
        
        header_fase2 = ["Basis"] + [f"x{i+1}" for i in range(len(bahan_aktif))] + ["S1", "S2", "S3", "S4", "NK"]
        baris_Z_fase2 = ["Z (Biaya)"] + [int(baris['Harga (Rp)']) for i, baris in bahan_aktif.iterrows()] + [0, 0, 0, 0, 0]
        
        df_fase2 = pd.DataFrame([baris_Z_fase2], columns=header_fase2)
        st.dataframe(df_fase2, use_container_width=True, hide_index=True)
        st.caption(" *Sistem akan melanjutkan proses iterasi/pivot pada tabel transisi ini hingga mendapatkan nilai Z (Biaya) yang paling kecil. Hasil akhir ditampilkan di Tab 2.*")

        # ------------------ TAHAP 6 ------------------
        st.write("---")
        st.write("#### TAHAP 6: Pembentukan Grafik Analisis Sensitivitas")
        st.write("Grafik analisis sensitivitas dibentuk dengan melakukan iterasi ulang terhadap model Simpleks menggunakan nilai batas bawah porsi ($X_{min}$) yang dimanipulasi secara bertahap (descending).")
        st.markdown("""
        **Langkah-langkah Pembuatan Grafik:**
        1. Menetapkan himpunan skenario batas minimal porsi, misalnya $X_{min} \in \{1.0, 0.8, 0.6, 0.4, 0.2, 0.1\}$.
        2. Menyelesaikan ulang model Simpleks (Fase 1 dan Fase 2) untuk setiap nilai $X_{min}$ pada himpunan tersebut.
        3. Mencatat hasil akhir dari Fungsi Tujuan ($Z_{min}$) atau total biaya termurah pada setiap skenario iterasi.
        4. Memetakan hasil ke dalam koordinat Kartesius di mana Sumbu X adalah nilai batas minimal porsi ($X_{min}$) secara menurun, dan Sumbu Y adalah nilai $Z$ (Biaya).
        5. Menarik garis tren untuk menganalisis sifat *feasibility* daerah penyelesaian. Penurunan paksaan batas porsi akan memperluas daerah fisibel, sehingga menghasilkan biaya minimum yang lebih rendah.
        """)

    st.markdown('</div>', unsafe_allow_html=True)

# --- HALAMAN 4: DOKUMENTASI (RUMUS) ---
elif st.session_state['halaman'] == 'dokumentasi':
    if st.button("⬅️ Kembali ke Beranda Utama"):
        st.session_state['halaman'] = 'beranda'
        st.rerun()
        
    st.markdown('<div class="header-title-small">Sistem Pakar <span>MBG</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    
    st.write("###  Integrasi Matriks Aljabar")
    st.latex(r"\text{Fungsi Minimum: } Z = \mathbf{C}^T \mathbf{X} \quad | \quad \text{Kendala: } \mathbf{A}\mathbf{X} \ge \mathbf{B}")
    
    st.write("Penjelasan Variabel Ruang Vektor:")
    st.markdown("""
    - $C$ : Vektor harga makanan.
    - $X$ : Vektor penyelesaian (batas maksimum takaran makanan).
    - $A$ : Matriks kandungan gizi.
    - $B$ : Vektor target batas bawah nutrisi ($NK$).
    """)
    
    st.write("---")
    st.write("###  Persamaan Angka Metabolisme Basal (AMB) Schofield")
    st.write("Persamaan Schofield digunakan untuk mengestimasi kebutuhan energi dasar anak dan remaja berdasarkan usia, jenis kelamin, serta berat badan ($Wt$) dan tinggi badan ($Ht$) dalam meter.")
    st.markdown("""
    **Laki-laki:**
    - $\le 3$ Tahun: $AMB = 0.167 Wt + 1517.4 Ht - 617.6$
    - $4 - 10$ Tahun: $AMB = 19.6 Wt + 130.3 Ht + 414.9$
    - $11 - 18$ Tahun: $AMB = 16.25 Wt + 137.2 Ht + 515.5$

    **Perempuan:**
    - $\le 3$ Tahun: $AMB = 16.25 Wt + 1023.2 Ht - 413.5$
    - $4 - 10$ Tahun: $AMB = 16.97 Wt + 161.8 Ht + 371.2$
    - $11 - 18$ Tahun: $AMB = 8.365 Wt + 465.0 Ht + 200.0$
    """)
    
    st.write("---")
    st.write("###  Total Energy Expenditure (TEE)")
    st.write("TEE adalah total kalori yang dibutuhkan dalam sehari, dikalkulasikan dengan mengalikan AMB dengan faktor aktivitas fisik atau *Physical Activity Level* (PAL).")
    st.latex(r"TEE = AMB \times PAL")
    st.markdown("""
    **Ketentuan Nilai Physical Activity Level (PAL):**
    - Sangat Jarang / Pasif = $1.2$
    - Jarang (Olahraga ringan 1-3 hari/minggu) = $1.375$
    - Cukup (Olahraga sedang 3-5 hari/minggu) = $1.55$
    - Sering (Olahraga berat 6-7 hari/minggu) = $1.725$
    - Sangat Sering (Atlet / Fisik ekstra) = $1.9$
    """)

    st.markdown('</div>', unsafe_allow_html=True)