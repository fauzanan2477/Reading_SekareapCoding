import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.optimize import linprog

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS PALET PREMIUM
# ==========================================
st.set_page_config(page_title="Sistem Pakar MBG", layout="wide")

st.markdown("""
    <style>
    /* Background utama dan warna teks dasar */
    .stApp { background-color: #F8F9FA; color: #2D3142; }
    .block-container { padding-top: 2rem; max-width: 1100px; }
    
    /* Box putih untuk membagi seksi (White & Silver) */
    .white-box { background-color: #FFFFFF; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(45,49,66,0.08); margin-top: 15px; margin-bottom: 20px; border: 1px solid #BFC0C0; color: #2D3142;}
    
    /* Konfigurasi Tabs menu */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 30px; border-bottom: 2px solid #BFC0C0; background-color: #FFFFFF; padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { font-weight: 800; font-size: 1.15rem; color: #4F5D75; background-color: transparent; border: none; }
    .stTabs [aria-selected="true"] { color: #EF8354; border-bottom: 4px solid #EF8354; }
    
    /* Tipografi */
    h1, h2, h3, h4, p { color: #2D3142 !important; }
    .white-box li { color: #4F5D75; } 
    
    /* Hero Section Header */
    .hero-title { font-size: 3.2rem; font-weight: 900; color: #2D3142 !important; line-height: 1.2; margin-bottom: 15px; text-align: center; }
    .hero-title span { color: #EF8354 !important; }
    .hero-subtitle { font-size: 1.2rem; color: #4F5D75 !important; font-weight: 500; text-align: center; margin-bottom: 30px;}
    
    /* Kartu Hasil Akhir (Menggunakan gradasi Jet Black ke Blue Slate) */
    .result-card { background: linear-gradient(135deg, #2D3142, #4F5D75); color: white !important; border-radius: 12px; padding: 30px; text-align: center; margin: 20px 0px; box-shadow: 0 5px 15px rgba(0,0,0,0.2);}
    .result-card h2 { color: #EF8354 !important; font-size: 3.5rem; margin: 0; font-weight: 900;}
    .result-card p { color: #FFFFFF !important; font-size: 1.1rem; margin: 0; font-weight: bold; letter-spacing: 1px;}
    
    /* Warna tombol utama bawaan Streamlit (Primary Button) */
    div.stButton > button:first-child { background-color: #EF8354; color: #FFFFFF; border: none; border-radius: 8px; font-weight: bold; }
    div.stButton > button:first-child:hover { background-color: #D67145; color: #FFFFFF; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HERO SECTION
# ==========================================
st.markdown("""
<div class="hero-title">Sistem Optimasi Logistik<br><span>Makan Bergizi Gratis (MBG)</span></div>
<div class="hero-subtitle">Integrasi Ilmu Gizi Biometrik dan Aljabar Linier (Metode Simpleks Dua Fase)</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATABASE (SESSION STATE) & FUNGSI
# ==========================================
if 'database_bahan' not in st.session_state:
    st.session_state['database_bahan'] = pd.DataFrame({
        "Gunakan": [True, True, True, True, False, True], 
        "Bahan Makanan": ["Nasi Putih", "Telur Ayam", "Tempe Murni", "Sayur Bayam", "Susu Sapi", "Daging Ayam"],
        "Harga (Rp)": [1500, 2800, 1500, 1000, 2000, 4500], 
        "Kalori (Kkal)": [130.0, 155.0, 193.0, 23.0, 61.0, 165.0],
        "Protein (g)": [2.7, 13.0, 19.0, 2.9, 3.2, 31.0],
        "Lemak (g)": [0.3, 11.0, 11.0, 0.4, 3.3, 3.6],
        "Karbohidrat (g)": [28.6, 1.1, 9.4, 3.6, 4.8, 0.0],
        "Batas Maksimal (g)": [250.0, 100.0, 100.0, 150.0, 200.0, 150.0] 
    })

if 'target_kalori' not in st.session_state:
    st.session_state.update({
        'target_kalori': 1800.0, 'target_protein': 45.0, 'target_lemak': 40.0, 'target_karbo': 202.5,
        'nilai_aktivitas': 1.55, 'nilai_bmr': 1161.0, 'pembagi_waktu': 1,
        'rumus_amb_teks': r"\text{AMB (P)} = 16.97 Wt + 161.8 Ht + 371.2",
        'rumus_amb_angka': r"\text{AMB (P)} = (16.97 \times 30.0) + (161.8 \times 1.35) + 371.2"
    })

# Fungsi Optimasi untuk dieksekusi di Tab 2
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

# ==========================================
# 4. MENU NAVBAR (TABS)
# ==========================================
tab_gizi, tab_aljabar, tab_manual, tab_docs = st.tabs([
    "1. Kalkulator Gizi", 
    "2. Eksekusi Optimasi", 
    "3. Langkah Manual (Sangat Detail)", 
    "4. Dokumentasi Rumus"
])

# --- HALAMAN 1: KALKULATOR GIZI ---
with tab_gizi:
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### 👦 Penentuan Vektor Konstanta Gizi (B)")
    st.write("Sistem menghitung target Makronutrien anak berdasarkan **Persamaan AMB Schofield** dan tingkat aktivitas fisik (Merujuk pada Jurnal Brawijaya).")
    
    kolom1, kolom2 = st.columns(2)
    with kolom1:
        umur_anak = st.number_input("Umur Anak (Tahun)", min_value=1, max_value=18, value=10)
        jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        tingkat_aktivitas = st.selectbox("Tingkat Aktivitas Fisik (Olahraga)", [
            "Sangat Jarang (Pasif / Tidak olahraga)",
            "Jarang (Olahraga ringan 1-3 hari/minggu)",
            "Cukup (Olahraga sedang 3-5 hari/minggu)",
            "Sering (Olahraga berat 6-7 hari/minggu)",
            "Sangat Sering (Atlet / Fisik ekstra)"
        ], index=2)
        
    with kolom2:
        berat_badan = st.number_input("Berat Badan / Wt (kg)", min_value=5.0, value=30.0)
        tinggi_badan = st.number_input("Tinggi Badan / Ht (cm)", min_value=50.0, value=135.0)
        skenario_waktu = st.selectbox("Target Pemenuhan Gizi (Skenario)", [
            "1 Hari Penuh (Persis Jurnal UB)", 
            "1x Makan Siang (Program MBG - Dibagi 3)"
        ])
    
    if st.button("Hitung Target & Simpan", type="primary"):
        # 1. Menentukan Pengali Aktivitas
        if tingkat_aktivitas == "Sangat Jarang (Pasif / Tidak olahraga)": pengali_aktivitas = 1.2
        elif tingkat_aktivitas == "Jarang (Olahraga ringan 1-3 hari/minggu)": pengali_aktivitas = 1.375
        elif tingkat_aktivitas == "Cukup (Olahraga sedang 3-5 hari/minggu)": pengali_aktivitas = 1.55
        elif tingkat_aktivitas == "Sering (Olahraga berat 6-7 hari/minggu)": pengali_aktivitas = 1.725
        else: pengali_aktivitas = 1.9

        # 2. Rumus AMB Schofield
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

        # 3. Kebutuhan Makro
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
        st.success(f"Target Gizi diperbarui ({skenario_waktu})! Lanjut ke Tab 2.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- HALAMAN 2: EKSEKUSI OPTIMASI & GRAFIK ---
with tab_aljabar:
    st.markdown('<div class="white-box" style="border-left: 5px solid #EF8354;">', unsafe_allow_html=True)
    st.write("#### 🎯 Target Gizi Saat Ini (Syarat Matriks Batas Bawah):")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Kalori Minimal", f"{st.session_state['target_kalori']} Kkal")
    k2.metric("Protein (Min 10%)", f"{st.session_state['target_protein']} Gram")
    k3.metric("Lemak (Min 20%)", f"{st.session_state['target_lemak']} Gram")
    k4.metric("Karbo (Min 45%)", f"{st.session_state['target_karbo']} Gram")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### 🛒 Pilihan Bahan Makanan")
    st.write("Centang kolom **Gunakan** dan atur **Batas Maksimal** sebelum melakukan kalkulasi.")
    
    # Editor Tabel Input (Bisa dicentang dan diubah batas maksimalnya)
    tabel_interaktif = st.data_editor(st.session_state['database_bahan'], num_rows="dynamic", use_container_width=True, hide_index=True)
    st.session_state['database_bahan'] = tabel_interaktif
    
    if st.button("🚀 Kalkulasi Biaya Termurah", type="primary", use_container_width=True):
        bahan_terpilih = tabel_interaktif[tabel_interaktif["Gunakan"] == True].copy()
        
        if len(bahan_terpilih) < 2:
            st.error("⚠️ Centang minimal 2 bahan makanan untuk komputasi matriks.")
        else:
            solusi = jalankan_optimasi(bahan_terpilih, st.session_state['target_kalori'], st.session_state['target_protein'], st.session_state['target_lemak'], st.session_state['target_karbo'], batas_bawah_satuan=0.0)
            
            if solusi.success:
                # Menampilkan Harga Optimasi
                st.markdown(f"""
                <div class="result-card">
                    <p>Total Biaya Paling Minimum (Titik Optimal)</p>
                    <h2>Rp {solusi.fun:,.0f}</h2>
                    <p>Solusi Makanan Termurah Sesuai Target Waktu</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Menampilkan Tabel Statis (Tidak bisa diubah)
                st.write("### ⚖️ Vektor Rekomendasi Takaran")
                hasil_gram = solusi.x * 100 
                array_harga = pd.to_numeric(bahan_terpilih["Harga (Rp)"]).values
                tabel_hasil = pd.DataFrame({
                    "Bahan Makanan": bahan_terpilih["Bahan Makanan"].values,
                    "Takaran Disarankan": [f"{g:,.0f} Gram" for g in hasil_gram],
                    "Biaya Realisasi": [f"Rp {(g/100)*h:,.0f}" for g, h in zip(hasil_gram, array_harga)]
                })
                # st.table membuat tabel ini statis dan tidak dapat diubah nilainya
                st.table(tabel_hasil[solusi.x > 0.01].reset_index(drop=True))
                
                # Menampilkan Grafik Plotly di bawah Tabel
                st.write("---")
                st.write("### 📈 Analisis Pengujian Nilai Minimal Variabel (Sesuai Jurnal)")
                st.write("Grafik di bawah ini memanipulasi batas minimal porsi untuk membuktikan bahwa melonggarkan paksaan porsi minimal akan memperluas daerah *feasible* dan menurunkan total biaya pengeluaran.")
                
                rentang_minimal = [1.0, 0.8, 0.6, 0.4, 0.2, 0.1]
                hasil_simulasi = []
                
                for batas_min in rentang_minimal:
                    sol_sim = jalankan_optimasi(bahan_terpilih, st.session_state['target_kalori'], st.session_state['target_protein'], st.session_state['target_lemak'], st.session_state['target_karbo'], batas_bawah_satuan=batas_min)
                    if sol_sim.success:
                        hasil_g_sim = sol_sim.x * 100
                        df_hasil_sim = pd.DataFrame({
                            "Bahan Makanan": bahan_terpilih["Bahan Makanan"].values,
                            "Takaran Disarankan": [f"{g:,.0f} Gram" for g in hasil_g_sim],
                            "Biaya Realisasi": [f"Rp {(g/100)*h:,.0f}" for g, h in zip(hasil_g_sim, array_harga)]
                        })
                        hasil_simulasi.append({
                            "nilai_x": batas_min,
                            "biaya": sol_sim.fun,
                            "tabel": df_hasil_sim[sol_sim.x > 0.01].reset_index(drop=True)
                        })
                
                if hasil_simulasi:
                    x_vals = [str(d['nilai_x']) for d in hasil_simulasi] 
                    y_vals = [d['biaya'] for d in hasil_simulasi]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=x_vals, y=y_vals, mode='lines+markers', name='Biaya Minimum',
                        marker=dict(size=12, color='#EF8354'), line=dict(width=4, color='#4F5D75')
                    ))
                    
                    fig.update_layout(
                        title="Pergerakan Penurunan Biaya terhadap Nilai Minimal Variabel",
                        xaxis_title="Nilai Minimal Variabel Jumlah Makanan (Satuan)",
                        yaxis_title="Biaya Minimum / Nilai Z (Rp)",
                        hovermode="x unified", plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', font=dict(color='#2D3142')
                    )
                    fig.update_xaxes(categoryorder='array', categoryarray=x_vals, gridcolor='#BFC0C0')
                    fig.update_yaxes(gridcolor='#BFC0C0')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.write("#### 🔍 Detail Vektor Makanan per Titik Grafik")
                    opsi_dropdown = {f"Nilai Variabel X = {d['nilai_x']}  ->  Total Biaya: Rp {d['biaya']:,.0f}": d for d in hasil_simulasi}
                    titik_pilihan = st.selectbox("Pilih Titik Pengujian:", list(opsi_dropdown.keys()))
                    if titik_pilihan:
                        st.table(opsi_dropdown[titik_pilihan]['tabel'])
            else:
                st.error("🚨 SPL Infeasible: Matriks gagal terpenuhi. Coba perbesar 'Batas Maksimal (g)' atau tambahkan variasi lauk.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- HALAMAN 3: LANGKAH MANUAL (SANGAT DETAIL SESUAI JURNAL) ---
with tab_manual:
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
        st.caption("📌 *Ini adalah Tableau Initial Fase 1 yang sudah ter-substitusi.*")
        
        st.markdown("""
        **🔄 Proses Lanjutan Fase 1 (Operasi Baris Elementer):**
        Sistem komputer melakukan iterasi (Pivot) pada matriks di atas dengan tahapan:
        1. **Menentukan Kolom Masuk (Entering Variable):** Mencari nilai paling positif pada baris $W$.
        2. **Menentukan Baris Keluar (Leaving Variable):** Menghitung Rasio = Nilai Kanan (NK) dibagi nilai Kolom Masuk, lalu memilih rasio terkecil.
        3. **Eliminasi Gauss-Jordan:** Mengubah elemen pivot menjadi 1, dan elemen di atas/bawahnya menjadi 0.
        4. Mengulang langkah 1-3 hingga seluruh elemen baris $W \le 0$ (semua variabel $R$ hilang).
        """)
        
        # ------------------ TAHAP 5 ------------------
        st.write("---")
        st.write("#### TAHAP 5: Eksekusi Fase 2 (Optimasi Biaya Minimum)")
        st.write("Setelah semua kolom $R$ berhasil dibuang, fungsi harga asli ($Z$) dikembalikan ke dalam matriks untuk iterasi Fase 2.")
        
        header_fase2 = ["Basis"] + [f"x{i+1}" for i in range(len(bahan_aktif))] + ["S1", "S2", "S3", "S4", "NK"]
        baris_Z_fase2 = ["Z (Biaya)"] + [int(baris['Harga (Rp)']) for i, baris in bahan_aktif.iterrows()] + [0, 0, 0, 0, 0]
        
        df_fase2 = pd.DataFrame([baris_Z_fase2], columns=header_fase2)
        st.dataframe(df_fase2, use_container_width=True, hide_index=True)
        st.caption("📌 *Sistem akan melanjutkan proses iterasi/pivot pada tabel transisi ini hingga mendapatkan nilai Z (Biaya) yang paling kecil. Hasil akhir ditampilkan di Tab 2.*")

    st.markdown('</div>', unsafe_allow_html=True)

# --- HALAMAN 4: DOKUMENTASI (RUMUS) ---
with tab_docs:
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### 📖 Integrasi Matriks Aljabar")
    st.latex(r"\text{Fungsi Minimum: } Z = \mathbf{C}^T \mathbf{X} \quad | \quad \text{Kendala: } \mathbf{A}\mathbf{X} \ge \mathbf{B}")
    
    st.write("Penjelasan Variabel Ruang Vektor:")
    st.markdown("""
    - $C$ : Vektor harga makanan.
    - $X$ : Vektor penyelesaian (batas maksimum takaran makanan).
    - $A$ : Matriks kandungan gizi.
    - $B$ : Vektor target batas bawah nutrisi ($NK$).
    """)
    st.markdown('</div>', unsafe_allow_html=True)
