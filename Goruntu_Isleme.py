import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
from PIL import Image, ImageTk, ImageEnhance
import numpy as np
import matplotlib.pyplot as plt
from functools import partial
import mediapipe as mp
import math

class GoruntuIsleme:
    def __init__(self):
        self.pencere = tk.Tk()
        self.pencere.title("Görüntü İşleme")
        
        # Ana scrollbar container oluştur
        self.main_container = tk.Frame(self.pencere)
        self.main_container.pack(fill='both', expand=True)
        
        # Scrollbar'ları ekle
        self.v_scrollbar = tk.Scrollbar(self.main_container)
        self.v_scrollbar.pack(side='right', fill='y')
        
        self.h_scrollbar = tk.Scrollbar(self.main_container, orient='horizontal')
        self.h_scrollbar.pack(side='bottom', fill='x')
        
        # Canvas oluştur ve scrollbar'ları bağla
        self.canvas_container = tk.Canvas(self.main_container)
        self.canvas_container.pack(side='left', fill='both', expand=True)
        
        # Scrollbar'ları canvas'a bağla
        self.canvas_container.configure(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )
        self.v_scrollbar.configure(command=self.canvas_container.yview)
        self.h_scrollbar.configure(command=self.canvas_container.xview)
        
        # Ana frame'i canvas içine yerleştir
        self.ana_frame = tk.Frame(self.canvas_container)
        self.canvas_container.create_window((0, 0), window=self.ana_frame, anchor='nw')
        
        # Pencere boyutunu daha büyük ayarla ve tam ekranda başlat
        self.pencere.geometry("1400x900")
        self.pencere.state('zoomed')  # Windows'ta tam ekran mod
        
        # Ana container frame oluştur (3x3 grid için)
        self.ana_frame = tk.Frame(self.ana_frame)
        self.ana_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Sol frame
        self.sol_frame = tk.Frame(self.ana_frame)
        self.sol_frame.configure(width=200)
        self.sol_frame.grid_propagate(False)

        self.sol_frame.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        
        # Sağ frame
        self.sag_frame = tk.Frame(self.ana_frame)
        self.sag_frame.grid(row=1, column=2, padx=5, pady=5, sticky='nsew')
        
        # Üst frame
        self.ust_frame = tk.Frame(self.ana_frame)
        self.ust_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='nsew')
        
        # Alt frame
        self.alt_frame = tk.Frame(self.ana_frame)
        self.alt_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky='nsew')
        
        # Orta frame (Canvas için)
        self.orta_frame = tk.Frame(self.ana_frame)
        self.orta_frame.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')
        
        # Canvas'ı orta frame'e ekle
        self.canvas = tk.Canvas(self.orta_frame)
        self.canvas.pack(expand=True)
        self.canvas.bind("<Button-1>", self.canvas_click)
        
        # Grid ağırlıklarını ayarla - bütün paneller görünsün
        self.ana_frame.grid_columnconfigure(0, weight=1)
        self.ana_frame.grid_columnconfigure(1, weight=5)  # Orta panel daha geniş
        self.ana_frame.grid_columnconfigure(2, weight=1)

        self.ana_frame.grid_rowconfigure(0, weight=1)
        self.ana_frame.grid_rowconfigure(1, weight=1)
        self.ana_frame.grid_rowconfigure(2, weight=1)
        
        # Görüntü değişkeni
        self.goruntu = None
        
        # Orijinal görüntüyü saklamak için yeni değişken
        self.orijinal_goruntu = None
        
        # Perspektif düzeltme için değişkenler
        self.perspektif_noktalar = []
        self.perspektif_duzeltme_aktif = False
        
        # Butonlar için frame'i üst frame'e taşıyalım
        self.buton_frame = tk.Frame(self.ust_frame)
        self.buton_frame.pack(fill='x', padx=5, pady=5)
        
        # Butonları yan yana yerleştirmek için side='left' kullanıyoruz
        self.yukle_buton = tk.Button(
            self.buton_frame,
            text="Görüntü Yükle",
            command=self.goruntu_yukle
        )
        self.yukle_buton.pack(side='left', padx=5)
        
        # El Hareketi ile Parlaklık butonu
        self.el_parlaklik_buton = tk.Button(
            self.buton_frame,
            text="El Hareketi ile Parlaklık",
            command=self.el_parlaklik_penceresi_ac
        )
        self.el_parlaklik_buton.pack(side='left', padx=5)
        
        self.gri_buton = tk.Button(
            self.buton_frame,
            text="Resmi Griye Çevir",
            command=self.gri_tonla
        )
        self.gri_buton.pack(side='left', padx=5)
        
        self.negatif_buton = tk.Button(
            self.buton_frame,
            text="Resim Negatifi",
            command=self.negatif_al
        )
        self.negatif_buton.pack(side='left', padx=5)
        
        self.perspektif_buton = tk.Button(
            self.buton_frame,
            text="Perspektif Düzeltme",
            command=self.perspektif_duzeltme
        )
        self.perspektif_buton.pack(side='left', padx=5)
        
        
        # Konservatif Filtreleme butonu
        self.konservatif_filtre_buton = tk.Button(
            self.buton_frame,
            text="Konservatif Filtre",
            command=self.hizli_konservatif_filtre
        )
        
        # Crimmins Speckle giderme butonu
        self.crimmins_filtre_buton = tk.Button(
            self.buton_frame,
            text="Crimmins Filtre",
            command=self.hizli_crimmins_filtre
        )
        
        # FFT Low-Pass Filter butonu
        self.fft_lowpass_buton = tk.Button(
            self.buton_frame,
            text="FFT Low-Pass Filter",
            command=self.fft_lowpass_filtre
        )
        
        # FFT High-Pass Filter butonu
        self.fft_highpass_buton = tk.Button(
            self.buton_frame,
            text="FFT High-Pass Filter",
            command=self.fft_highpass_filtre
        )
        
        # Butonları düzenle

        self.konservatif_filtre_buton.pack(side='left', padx=5)
        self.crimmins_filtre_buton.pack(side='left', padx=5)
        self.fft_lowpass_buton.pack(side='left', padx=5)
        self.fft_highpass_buton.pack(side='left', padx=5)
        
        
        self.orijinal_buton = tk.Button(
            self.buton_frame,
            text="Orijinal Görüntü",
            command=self.orijinale_don
        )
        self.orijinal_buton.pack(side='left', padx=5)
        
        self.kaydet_buton = tk.Button(
            self.buton_frame,
            text="Görüntü Kaydet",
            command=self.goruntu_kaydet
        )
        self.kaydet_buton.pack(side='left', padx=5)
        
        self.histogram_buton = tk.Button(
            self.buton_frame,
            text="Histogram Göster",
            command=self.histogram_goster
        )
        self.histogram_buton.pack(side='left', padx=5)
        
        self.histogram_esitle_buton = tk.Button(
            self.buton_frame,
            text="Histogram Eşitle",
            command=self.histogram_esitle
        )
        self.histogram_esitle_buton.pack(side='left', padx=5)
        
        # Filtre işlemleri için LabelFrame
        self.filtre_frame = tk.LabelFrame(self.sag_frame, text="Filtre Ayarları", padx=5, pady=5)
        self.filtre_frame.pack(fill='x', padx=5, pady=5)
        
        # Ortalama (Mean) Filtre Ayarları
        self.mean_filtre_label = tk.Label(self.filtre_frame, text="Ortalama Filtre Boyutu:")
        self.mean_filtre_label.pack()
        
        # X ve Y boyutları için frame
        self.mean_xy_frame = tk.Frame(self.filtre_frame)
        self.mean_xy_frame.pack(fill='x', padx=5, pady=5)
        
        # X boyutu için giriş
        self.mean_x_label = tk.Label(self.mean_xy_frame, text="X:")
        self.mean_x_label.pack(side='left', padx=5)
        self.mean_x_entry = tk.Entry(self.mean_xy_frame, width=5)
        self.mean_x_entry.pack(side='left', padx=5)
        self.mean_x_entry.insert(0, "5")
        
        # Y boyutu için giriş
        self.mean_y_label = tk.Label(self.mean_xy_frame, text="Y:")
        self.mean_y_label.pack(side='left', padx=5)
        self.mean_y_entry = tk.Entry(self.mean_xy_frame, width=5)
        self.mean_y_entry.pack(side='left', padx=5)
        self.mean_y_entry.insert(0, "5")
        
        # Ortalama filtre uygula butonu
        self.mean_filtre_buton = tk.Button(
            self.filtre_frame,
            text="Ortalama Filtre Uygula",
            command=self.ortalama_filtre_uygula
        )
        self.mean_filtre_buton.pack(padx=5, pady=5)
        
        
        
        # Medyan (Median) Filtre Ayarları
        self.median_filtre_label = tk.Label(self.filtre_frame, text="Medyan Filtre Boyutu:")
        self.median_filtre_label.pack(pady=(10, 0))
        
        # Medyan filtre boyutunu girmek için text kutusu
        self.median_boyut_frame = tk.Frame(self.filtre_frame)
        self.median_boyut_frame.pack(fill='x', padx=5, pady=5)
        
        self.median_boyut_label = tk.Label(self.median_boyut_frame, text="Boyut (3-21, tek sayı):")
        self.median_boyut_label.pack(side='left', padx=5)
        self.median_boyut_entry = tk.Entry(self.median_boyut_frame, width=5)
        self.median_boyut_entry.pack(side='left', padx=5)
        self.median_boyut_entry.insert(0, "5")
        
        # Slider için değer etiketi
        self.median_slider_value = tk.StringVar()
        self.median_slider_value.set("5")
        
        # Medyan filtre için slider
        self.median_slider_label = tk.Label(self.filtre_frame, text="Boyut Seçin:")
        self.median_slider_label.pack()
        self.median_slider = tk.Scale(
            self.filtre_frame,
            from_=3,
            to=21,
            orient='horizontal',
            resolution=2,  # Sadece tek sayılar için
            length=200,
            variable=self.median_slider_value,
            command=self.update_median_entry
        )
        self.median_slider.pack(padx=5)
        
        # Medyan filtre uygula butonu
        self.median_filtre_buton = tk.Button(
            self.filtre_frame,
            text="Medyan Filtre Uygula",
            command=self.medyan_filtre_uygula
        )
        self.median_filtre_buton.pack(padx=5, pady=5)
        
        # Band geçiren/durduran filtreler için ayarlar
        self.band_filtre_label = tk.Label(self.filtre_frame, text="Band Filtre Ayarları:")
        self.band_filtre_label.pack(pady=(10, 0))
        
        # D1 (alt sınır) için ayarlar
        self.band_d1_frame = tk.Frame(self.filtre_frame)
        self.band_d1_frame.pack(fill='x', padx=5, pady=5)
        
        self.band_d1_label = tk.Label(self.band_d1_frame, text="D1 (Alt Sınır):")
        self.band_d1_label.pack(side='left', padx=5)
        self.band_d1_entry = tk.Entry(self.band_d1_frame, width=5)
        self.band_d1_entry.pack(side='left', padx=5)
        self.band_d1_entry.insert(0, "20")
        
        # D2 (üst sınır) için ayarlar
        self.band_d2_frame = tk.Frame(self.filtre_frame)
        self.band_d2_frame.pack(fill='x', padx=5, pady=5)
        
        self.band_d2_label = tk.Label(self.band_d2_frame, text="D2 (Üst Sınır):")
        self.band_d2_label.pack(side='left', padx=5)
        self.band_d2_entry = tk.Entry(self.band_d2_frame, width=5)
        self.band_d2_entry.pack(side='left', padx=5)
        self.band_d2_entry.insert(0, "50")
        
        # Band geçiren filtre butonu
        self.band_geciren_buton = tk.Button(
            self.filtre_frame,
            text="Band Geçiren Filtre Uygula",
            command=self.band_geciren_filtre
        )
        self.band_geciren_buton.pack(padx=5, pady=5)
        
        # Band durduran filtre butonu
        self.band_durduran_buton = tk.Button(
            self.filtre_frame,
            text="Band Durduran Filtre Uygula",
            command=self.band_durduran_filtre
        )
        self.band_durduran_buton.pack(padx=5, pady=5)
        
        # Butterworth filtreler için ayarlar
        self.butterworth_label = tk.Label(self.filtre_frame, text="Butterworth Filtre Ayarları:")
        self.butterworth_label.pack(pady=(10, 0))
        
        # D0 (kesim frekansı) için ayarlar
        self.butterworth_d0_frame = tk.Frame(self.filtre_frame)
        self.butterworth_d0_frame.pack(fill='x', padx=5, pady=5)
        
        self.butterworth_d0_label = tk.Label(self.butterworth_d0_frame, text="D0 (Kesim Frekansı):")
        self.butterworth_d0_label.pack(side='left', padx=5)
        self.butterworth_d0_entry = tk.Entry(self.butterworth_d0_frame, width=5)
        self.butterworth_d0_entry.pack(side='left', padx=5)
        self.butterworth_d0_entry.insert(0, "30")
        
        # n (filtre derecesi) için ayarlar
        self.butterworth_n_frame = tk.Frame(self.filtre_frame)
        self.butterworth_n_frame.pack(fill='x', padx=5, pady=5)
        
        self.butterworth_n_label = tk.Label(self.butterworth_n_frame, text="n (Filtre Derecesi):")
        self.butterworth_n_label.pack(side='left', padx=5)
        self.butterworth_n_entry = tk.Entry(self.butterworth_n_frame, width=5)
        self.butterworth_n_entry.pack(side='left', padx=5)
        self.butterworth_n_entry.insert(0, "2")
        
        # Butterworth alçak geçiren filtre butonu
        self.butterworth_lpf_buton = tk.Button(
            self.filtre_frame,
            text="Butterworth Alçak Geçiren Filtre",
            command=self.butterworth_alcak_geciren_filtre
        )
        self.butterworth_lpf_buton.pack(padx=5, pady=5)
        
        # Butterworth yüksek geçiren filtre butonu
        self.butterworth_hpf_buton = tk.Button(
            self.filtre_frame,
            text="Butterworth Yüksek Geçiren Filtre",
            command=self.butterworth_yuksek_geciren_filtre
        )
        self.butterworth_hpf_buton.pack(padx=5, pady=5)
        
        # Gaussian filtreler için ayarlar
        self.gaussian_label = tk.Label(self.filtre_frame, text="Gaussian Filtre Ayarları:")
        self.gaussian_label.pack(pady=(10, 0))
        
        # D0 (standart sapma) için ayarlar
        self.gaussian_d0_frame = tk.Frame(self.filtre_frame)
        self.gaussian_d0_frame.pack(fill='x', padx=5, pady=5)
        
        self.gaussian_d0_label = tk.Label(self.gaussian_d0_frame, text="D0 (Standart Sapma):")
        self.gaussian_d0_label.pack(side='left', padx=5)
        self.gaussian_d0_entry = tk.Entry(self.gaussian_d0_frame, width=5)
        self.gaussian_d0_entry.pack(side='left', padx=5)
        self.gaussian_d0_entry.insert(0, "30")
        
        # Gaussian alçak geçiren filtre butonu
        self.gaussian_lpf_buton = tk.Button(
            self.filtre_frame,
            text="Gaussian Alçak Geçiren Filtre",
            command=self.gaussian_alcak_geciren_filtre
        )
        self.gaussian_lpf_buton.pack(padx=5, pady=5)
        
        # Gaussian yüksek geçiren filtre butonu
        self.gaussian_hpf_buton = tk.Button(
            self.filtre_frame,
            text="Gaussian Yüksek Geçiren Filtre",
            command=self.gaussian_yuksek_geciren_filtre
        )
        self.gaussian_hpf_buton.pack(padx=5, pady=5)
        
        # Homomorfik filtre için ayarlar
        self.homomorfik_label = tk.Label(self.filtre_frame, text="Homomorfik Filtre Ayarları:")
        self.homomorfik_label.pack(pady=(10, 0))
        
        # D0 (kesim frekansı) için ayarlar
        self.homomorfik_d0_frame = tk.Frame(self.filtre_frame)
        self.homomorfik_d0_frame.pack(fill='x', padx=5, pady=2)
        
        self.homomorfik_d0_label = tk.Label(self.homomorfik_d0_frame, text="D0 (Kesim Frekansı):")
        self.homomorfik_d0_label.pack(side='left', padx=5)
        self.homomorfik_d0_entry = tk.Entry(self.homomorfik_d0_frame, width=5)
        self.homomorfik_d0_entry.pack(side='left', padx=5)
        self.homomorfik_d0_entry.insert(0, "30")
        
        # H_L (alçak frekans kazancı) için ayarlar
        self.homomorfik_hl_frame = tk.Frame(self.filtre_frame)
        self.homomorfik_hl_frame.pack(fill='x', padx=5, pady=2)
        
        self.homomorfik_hl_label = tk.Label(self.homomorfik_hl_frame, text="H_L (Alçak Frekans Kazancı):")
        self.homomorfik_hl_label.pack(side='left', padx=5)
        self.homomorfik_hl_entry = tk.Entry(self.homomorfik_hl_frame, width=5)
        self.homomorfik_hl_entry.pack(side='left', padx=5)
        self.homomorfik_hl_entry.insert(0, "0.5")
        
        # H_H (yüksek frekans kazancı) için ayarlar
        self.homomorfik_hh_frame = tk.Frame(self.filtre_frame)
        self.homomorfik_hh_frame.pack(fill='x', padx=5, pady=2)
        
        self.homomorfik_hh_label = tk.Label(self.homomorfik_hh_frame, text="H_H (Yüksek Frekans Kazancı):")
        self.homomorfik_hh_label.pack(side='left', padx=5)
        self.homomorfik_hh_entry = tk.Entry(self.homomorfik_hh_frame, width=5)
        self.homomorfik_hh_entry.pack(side='left', padx=5)
        self.homomorfik_hh_entry.insert(0, "2.0")
        
        # C (keskinlik) için ayarlar
        self.homomorfik_c_frame = tk.Frame(self.filtre_frame)
        self.homomorfik_c_frame.pack(fill='x', padx=5, pady=2)
        
        self.homomorfik_c_label = tk.Label(self.homomorfik_c_frame, text="C (Keskinlik):")
        self.homomorfik_c_label.pack(side='left', padx=5)
        self.homomorfik_c_entry = tk.Entry(self.homomorfik_c_frame, width=5)
        self.homomorfik_c_entry.pack(side='left', padx=5)
        self.homomorfik_c_entry.insert(0, "1.0")
        
        # Homomorfik filtre butonu
        self.homomorfik_buton = tk.Button(
            self.filtre_frame,
            text="Homomorfik Filtre Uygula",
            command=self.homomorfik_filtre_uygula
        )
        self.homomorfik_buton.pack(padx=5, pady=5)
        
        # Buradan Sobel filtresi ayarları kaldırıldı
        
        # Gauss Filtresi Ayarları
        self.gauss_frame = tk.LabelFrame(self.sag_frame, text="Gauss Filtresi Ayarları")
        self.gauss_frame.pack(fill='x', padx=5, pady=5)
        
        # Gauss Filtresi Boyutu
        self.gauss_boyut_label = tk.Label(self.gauss_frame, text="Filtre Boyutu:")
        self.gauss_boyut_label.pack(padx=5, pady=2)
        
        # Frame for filter size options
        self.gauss_boyut_frame = tk.Frame(self.gauss_frame)
        self.gauss_boyut_frame.pack(padx=5, pady=2)
        
        # Radio buttons for common Gaussian filter sizes
        self.gauss_boyut_var = tk.StringVar(value="5")
        self.gauss_boyut_3 = tk.Radiobutton(self.gauss_boyut_frame, text="3x3", variable=self.gauss_boyut_var, value="3")
        self.gauss_boyut_3.grid(row=0, column=0, padx=5)
        self.gauss_boyut_5 = tk.Radiobutton(self.gauss_boyut_frame, text="5x5", variable=self.gauss_boyut_var, value="5")
        self.gauss_boyut_5.grid(row=0, column=1, padx=5)
        self.gauss_boyut_7 = tk.Radiobutton(self.gauss_boyut_frame, text="7x7", variable=self.gauss_boyut_var, value="7")
        self.gauss_boyut_7.grid(row=0, column=2, padx=5)
        self.gauss_boyut_9 = tk.Radiobutton(self.gauss_boyut_frame, text="9x9", variable=self.gauss_boyut_var, value="9")
        self.gauss_boyut_9.grid(row=0, column=3, padx=5)
        
        # Sigma değeri seçimi
        self.gauss_sigma_label = tk.Label(self.gauss_frame, text="Sigma Değeri:")
        self.gauss_sigma_label.pack(padx=5, pady=2)
        
        # Sigma entry ve slider
        self.gauss_sigma_entry = tk.Entry(self.gauss_frame, width=8)
        self.gauss_sigma_entry.pack(padx=5, pady=2)
        self.gauss_sigma_entry.insert(0, "1.0") # Varsayılan değer
        
        self.gauss_sigma_slider_label = tk.Label(self.gauss_frame, text="Sigma (0.1-5.0):")
        self.gauss_sigma_slider_label.pack(padx=5, pady=2)
        
        self.gauss_sigma_slider = tk.Scale(self.gauss_frame, from_=0.1, to=5.0, resolution=0.1, orient="horizontal")
        self.gauss_sigma_slider.pack(fill="x", padx=5, pady=2)
        self.gauss_sigma_slider.set(1.0) # Varsayılan değer
        self.gauss_sigma_slider.config(command=self.update_gauss_sigma_entry)
        
        # Gauss filtre uygulama butonu
        self.gauss_uygula_buton = tk.Button(
            self.gauss_frame,
            text="Gauss Filtreyi Uygula",
            command=self.gauss_filtre_uygula
        )
        self.gauss_uygula_buton.pack(padx=5, pady=5)
        
        # RGB frame'i sağ frame'e taşı
        self.rgb_frame = tk.LabelFrame(self.sag_frame, text="Resmi R G B Kanallarına Ayırma", padx=5, pady=5)
        self.rgb_frame.pack(fill='x', padx=5, pady=5)
        
        # Radyo butonlar için değişken
        self.kanal_secimi = tk.StringVar()
        self.kanal_secimi.set('kirmizi')  # Varsayılan değeri kırmızı olarak değiştir
        
        # RGB Radyo butonları (orijinal butonu kaldırıldı)
        self.r_radio = tk.Radiobutton(
            self.rgb_frame,
            text="Kırmızı Kanal",
            variable=self.kanal_secimi,
            value='mavi',
            command=self.kanal_sec
        )
        self.r_radio.pack(padx=5)
        
        self.g_radio = tk.Radiobutton(
            self.rgb_frame,
            text="Yeşil Kanal",
            variable=self.kanal_secimi,
            value='yesil',
            command=self.kanal_sec
        )
        self.g_radio.pack(padx=5)
        
        self.b_radio = tk.Radiobutton(
            self.rgb_frame,
            text="Mavi Kanal",
            variable=self.kanal_secimi,
            value='kirmizi',
            command=self.kanal_sec
        )
        self.b_radio.pack(padx=5)
        
        # Parlaklık ayarı için LabelFrame
        self.parlaklik_frame = tk.LabelFrame(self.sol_frame, text="Parlaklık Ayarı", padx=5, pady=5)
        self.parlaklik_frame.pack(fill='x', padx=5, pady=5)
        
        # Parlaklık slider'ı
        self.parlaklik_slider = tk.Scale(
            self.parlaklik_frame,
            from_=0,
            to=100,
            orient='horizontal',
            length=200,
            label="Parlaklık Değeri"
        )
        self.parlaklik_slider.pack(padx=5)
        self.parlaklik_slider.set(50)  # Varsayılan değer
        
        # Parlaklık uygula butonu
        self.parlaklik_buton = tk.Button(
            self.parlaklik_frame,
            text="Parlaklık Uygula",
            command=self.parlaklik_ayarla
        )
        self.parlaklik_buton.pack(padx=5)
        
        # Eşikleme ayarı için LabelFrame
        self.esikleme_frame = tk.LabelFrame(self.sag_frame, text="Eşikleme Ayarı", padx=5, pady=5)
        self.esikleme_frame.pack(fill='x', padx=5, pady=5)
        
        # Eşik değeri slider'ı
        self.esik_slider = tk.Scale(
            self.esikleme_frame,
            from_=0,
            to=255,
            orient='horizontal',
            length=200,
            label="Eşik Değeri"
        )
        self.esik_slider.pack(padx=5)
        self.esik_slider.set(150)  # Varsayılan değer
        
        # Eşikleme uygula butonu
        self.esik_buton = tk.Button(
            self.esikleme_frame,
            text="Eşikleme Uygula",
            command=self.esikleme_uygula
        )
        self.esik_buton.pack(padx=5)
        
        # Bilgi etiketi
        self.bilgi_label = tk.Label(self.alt_frame, text="Görüntü boyutları: ")
        self.bilgi_label.pack(pady=5)
        
        # Kontrast işlemleri için LabelFrame
        self.kontrast_frame = tk.LabelFrame(self.sag_frame, text="Kontrast İşlemleri", padx=5, pady=5)
        self.kontrast_frame.pack(fill='x', padx=5, pady=5)
        
        # Otomatik kontrast germe butonu
        self.otomatik_kontrast_buton = tk.Button(
            self.kontrast_frame,
            text="Otomatik Kontrast Germe",
            command=self.otomatik_kontrast_germe
        )
        self.otomatik_kontrast_buton.pack(padx=5, pady=2)
        
        # Manuel kontrast germe için değerler
        self.manuel_min_label = tk.Label(self.kontrast_frame, text="Min Değer (0-255):")
        self.manuel_min_label.pack()
        self.manuel_min_entry = tk.Entry(self.kontrast_frame)
        self.manuel_min_entry.pack()
        self.manuel_min_entry.insert(0, "50")
        
        self.manuel_max_label = tk.Label(self.kontrast_frame, text="Max Değer (0-255):")
        self.manuel_max_label.pack()
        self.manuel_max_entry = tk.Entry(self.kontrast_frame)
        self.manuel_max_entry.pack()
        self.manuel_max_entry.insert(0, "200")
        
        # Manuel kontrast germe butonu
        self.manuel_kontrast_buton = tk.Button(
            self.kontrast_frame,
            text="Manuel Kontrast Germe",
            command=self.manuel_kontrast_germe
        )
        self.manuel_kontrast_buton.pack(padx=5, pady=2)
        
        # Çoklu kontrast germe butonu
        self.coklu_kontrast_buton = tk.Button(
            self.kontrast_frame,
            text="Çoklu Kontrast Germe",
            command=self.coklu_kontrast_germe
        )
        self.coklu_kontrast_buton.pack(padx=5, pady=2)
        
        # Taşıma işlemleri için LabelFrame
        self.tasima_frame = tk.LabelFrame(self.sag_frame, text="Görüntü Taşıma", padx=5, pady=5)
        self.tasima_frame.pack(fill='x', padx=5, pady=5)
        
        # X ekseni için giriş
        self.x_label = tk.Label(self.tasima_frame, text="X ekseni (piksel):")
        self.x_label.pack()
        self.x_entry = tk.Entry(self.tasima_frame)
        self.x_entry.pack()
        self.x_entry.insert(0, "100")  # Varsayılan değer
        
        # Y ekseni için giriş
        self.y_label = tk.Label(self.tasima_frame, text="Y ekseni (piksel):")
        self.y_label.pack()
        self.y_entry = tk.Entry(self.tasima_frame)
        self.y_entry.pack()
        self.y_entry.insert(0, "50")  # Varsayılan değer
        
        # Manuel taşıma butonu
        self.manuel_tasima_buton = tk.Button(
            self.tasima_frame,
            text="Manuel Taşıma",
            command=self.manuel_tasima
        )
        self.manuel_tasima_buton.pack(padx=5, pady=2)
        
        # Fonksiyon ile taşıma butonu
        self.fonksiyon_tasima_buton = tk.Button(
            self.tasima_frame,
            text="Fonksiyon ile Taşıma",
            command=self.fonksiyon_tasima
        )
        self.fonksiyon_tasima_buton.pack(padx=5, pady=2)
        
        # Aynalama işlemleri için LabelFrame
        self.aynalama_frame = tk.LabelFrame(self.sag_frame, text="Görüntü Aynalama", padx=5, pady=5)
        self.aynalama_frame.pack(fill='x', padx=5, pady=5)
        
        # Dikey aynalama için X koordinatı
        self.x_ayna_label = tk.Label(self.aynalama_frame, text="X koordinatı:")
        self.x_ayna_label.pack()
        self.x_ayna_entry = tk.Entry(self.aynalama_frame)
        self.x_ayna_entry.pack()
        
        # Yatay aynalama için Y koordinatı
        self.y_ayna_label = tk.Label(self.aynalama_frame, text="Y koordinatı:")
        self.y_ayna_label.pack()
        self.y_ayna_entry = tk.Entry(self.aynalama_frame)
        self.y_ayna_entry.pack()
        
        # Açısal aynalama için açı
        self.aci_label = tk.Label(self.aynalama_frame, text="Açı (derece):")
        self.aci_label.pack()
        self.aci_entry = tk.Entry(self.aynalama_frame)
        self.aci_entry.pack()
        self.aci_entry.insert(0, "30")  # Varsayılan değer
        
        # Aynalama butonları
        self.dikey_aynalama_buton = tk.Button(
            self.aynalama_frame,
            text="Dikey Aynalama",
            command=self.dikey_aynalama
        )
        self.dikey_aynalama_buton.pack(padx=5, pady=2)
        
        self.yatay_aynalama_buton = tk.Button(
            self.aynalama_frame,
            text="Yatay Aynalama",
            command=self.yatay_aynalama
        )
        self.yatay_aynalama_buton.pack(padx=5, pady=2)
        
        self.acisal_aynalama_buton = tk.Button(
            self.aynalama_frame,
            text="Açısal Aynalama",
            command=self.acisal_aynalama
        )
        self.acisal_aynalama_buton.pack(padx=5, pady=2)
        
        # Eğme (Shearing) işlemleri için LabelFrame
        self.egme_frame = tk.LabelFrame(self.sol_frame, text="Görüntü Eğme (Shearing)", padx=5, pady=5)
        self.egme_frame.pack(fill='x', padx=5, pady=5)
        
        # X ekseni için eğme katsayısı
        self.shx_label = tk.Label(self.egme_frame, text="X Ekseni Eğme Katsayısı (-1 ile 1 arası):")
        self.shx_label.pack()
        self.shx_entry = tk.Entry(self.egme_frame)
        self.shx_entry.pack()
        self.shx_entry.insert(0, "0.5")  # Varsayılan değer
        
        # Y ekseni için eğme katsayısı
        self.shy_label = tk.Label(self.egme_frame, text="Y Ekseni Eğme Katsayısı (-1 ile 1 arası):")
        self.shy_label.pack()
        self.shy_entry = tk.Entry(self.egme_frame)
        self.shy_entry.pack()
        self.shy_entry.insert(0, "0.5")  # Varsayılan değer
        
        # Eğme butonları
        self.x_egme_buton = tk.Button(
            self.egme_frame,
            text="X Ekseni Eğme",
            command=self.x_egme_uygula
        )
        self.x_egme_buton.pack(padx=5, pady=2)
        
        self.y_egme_buton = tk.Button(
            self.egme_frame,
            text="Y Ekseni Eğme",
            command=self.y_egme_uygula
        )
        self.y_egme_buton.pack(padx=5, pady=2)
        
        # Manuel eğme butonları
        self.manuel_x_egme_buton = tk.Button(
            self.egme_frame,
            text="Manuel X Ekseni Eğme",
            command=self.manuel_x_egme_uygula
        )
        self.manuel_x_egme_buton.pack(padx=5, pady=2)
        
        self.manuel_y_egme_buton = tk.Button(
            self.egme_frame,
            text="Manuel Y Ekseni Eğme",
            command=self.manuel_y_egme_uygula
        )
        self.manuel_y_egme_buton.pack(padx=5, pady=2)
        
        # Alt frame'den ölçekleme frame'ini kaldır ve sol frame'e taşı
        self.olcekleme_frame = tk.LabelFrame(self.sag_frame, text="Görüntü Ölçekleme", padx=5, pady=5)
        self.olcekleme_frame.pack(fill='x', padx=5, pady=5)
        
        # Ölçek faktörü için giriş
        self.olcek_label = tk.Label(self.olcekleme_frame, text="Ölçek Faktörü (0.5-4):")
        self.olcek_label.pack()
        self.olcek_entry = tk.Entry(self.olcekleme_frame)
        self.olcek_entry.pack()
        self.olcek_entry.insert(0, "2")  # Varsayılan değer
        
        # İnterpolasyon yöntemi seçimi için radio butonlar
        self.interpolasyon_label = tk.Label(self.olcekleme_frame, text="İnterpolasyon Yöntemi:")
        self.interpolasyon_label.pack()
        
        self.interpolasyon_secimi = tk.StringVar()
        self.interpolasyon_secimi.set('bilinear')  # Varsayılan değer
        
        self.bilinear_radio = tk.Radiobutton(
            self.olcekleme_frame,
            text="Bilinear",
            variable=self.interpolasyon_secimi,
            value='bilinear'
        )
        self.bilinear_radio.pack()
        
        self.bicubic_radio = tk.Radiobutton(
            self.olcekleme_frame,
            text="Bicubic",
            variable=self.interpolasyon_secimi,
            value='bicubic'
        )
        self.bicubic_radio.pack()
        
        self.lanczos_radio = tk.Radiobutton(
            self.olcekleme_frame,
            text="Lanczos",
            variable=self.interpolasyon_secimi,
            value='lanczos'
        )
        self.lanczos_radio.pack()
        
        # Ölçekleme butonları
        self.buyut_piksel_buton = tk.Button(
            self.olcekleme_frame,
            text="Piksel Değiştirme ile Büyüt",
            command=self.piksel_buyut
        )
        self.buyut_piksel_buton.pack(padx=5, pady=2)
        
        self.kucult_piksel_buton = tk.Button(
            self.olcekleme_frame,
            text="Piksel Değiştirme ile Küçült",
            command=self.piksel_kucult
        )
        self.kucult_piksel_buton.pack(padx=5, pady=2)
        
        self.olcekle_buton = tk.Button(
            self.olcekleme_frame,
            text="İnterpolasyon ile Ölçekle",
            command=self.interpolasyon_olcekle
        )
        self.olcekle_buton.pack(padx=5, pady=2)
        
        # Döndürme işlemleri için LabelFrame
        self.dondurme_frame = tk.LabelFrame(self.sol_frame, text="Görüntü Döndürme", padx=5, pady=5)
        self.dondurme_frame.pack(fill='x', padx=5, pady=5)
        
        # Sobel Filtresi Ayarları için LabelFrame
        self.sobel_frame = tk.LabelFrame(self.sol_frame, text="Sobel Kenar Algılama", padx=5, pady=5)
        self.sobel_frame.pack(fill='x', padx=5, pady=5)
        
        # Sobel için kernel boyutu seçimi
        self.sobel_ksize_frame = tk.Frame(self.sobel_frame)
        self.sobel_ksize_frame.pack(fill='x', padx=5, pady=2)
        
        self.sobel_ksize_label = tk.Label(self.sobel_ksize_frame, text="Kernel Boyutu (ksize):")
        self.sobel_ksize_label.pack(side='left', padx=5)
        
        self.sobel_ksize_var = tk.StringVar()
        self.sobel_ksize_combobox = ttk.Combobox(self.sobel_ksize_frame, 
                                            textvariable=self.sobel_ksize_var,
                                            values=('1', '3', '5', '7'),
                                            width=5,
                                            state='readonly')
        self.sobel_ksize_combobox.current(1)  # Varsayılan 3
        self.sobel_ksize_combobox.pack(side='left', padx=5)
        
        # Sobel için derinlik seçimi
        self.sobel_depth_frame = tk.Frame(self.sobel_frame)
        self.sobel_depth_frame.pack(fill='x', padx=5, pady=2)
        
        self.sobel_depth_label = tk.Label(self.sobel_depth_frame, text="Derinlik:")
        self.sobel_depth_label.pack(side='left', padx=5)
        
        self.sobel_depth_var = tk.StringVar()
        self.sobel_depth_combobox = ttk.Combobox(self.sobel_depth_frame, 
                                            textvariable=self.sobel_depth_var,
                                            values=('CV_8U', 'CV_32F', 'CV_64F'),
                                            width=8,
                                            state='readonly')
        self.sobel_depth_combobox.current(2)  # Varsayılan CV_64F
        self.sobel_depth_combobox.pack(side='left', padx=5)
        
        # Sobel yön seçimi
        self.sobel_direction_frame = tk.Frame(self.sobel_frame)
        self.sobel_direction_frame.pack(fill='x', padx=5, pady=2)
        
        self.sobel_x_var = tk.IntVar(value=1)
        self.sobel_x_check = tk.Checkbutton(self.sobel_direction_frame, text="X Yönü", variable=self.sobel_x_var)
        self.sobel_x_check.pack(side='left', padx=5)
        
        self.sobel_y_var = tk.IntVar(value=1)
        self.sobel_y_check = tk.Checkbutton(self.sobel_direction_frame, text="Y Yönü", variable=self.sobel_y_var)
        self.sobel_y_check.pack(side='left', padx=5)
        
        # Sobel Filtresi uygula butonu
        self.sobel_buton = tk.Button(
            self.sobel_frame,
            text="Sobel Filtresi Uygula",
            command=self.sobel_filtresi_uygula
        )
        self.sobel_buton.pack(padx=5, pady=5)
        
        # Prewitt Filtresi Ayarları için LabelFrame
        self.prewitt_frame = tk.LabelFrame(self.sol_frame, text="Prewitt Kenar Algılama", padx=5, pady=5)
        self.prewitt_frame.pack(fill='x', padx=5, pady=5)
        
        # Prewitt için derinlik seçimi
        self.prewitt_depth_frame = tk.Frame(self.prewitt_frame)
        self.prewitt_depth_frame.pack(fill='x', padx=5, pady=2)
        
        self.prewitt_depth_label = tk.Label(self.prewitt_depth_frame, text="Derinlik:")
        self.prewitt_depth_label.pack(side='left', padx=5)
        
        self.prewitt_depth_var = tk.StringVar()
        self.prewitt_depth_combobox = ttk.Combobox(self.prewitt_depth_frame, 
                                            textvariable=self.prewitt_depth_var,
                                            values=('CV_8U', 'CV_32F', 'CV_64F'),
                                            width=8,
                                            state='readonly')
        self.prewitt_depth_combobox.current(2)  # Varsayılan CV_64F
        self.prewitt_depth_combobox.pack(side='left', padx=5)
        
        # Prewitt yön seçimi
        self.prewitt_direction_frame = tk.Frame(self.prewitt_frame)
        self.prewitt_direction_frame.pack(fill='x', padx=5, pady=2)
        
        self.prewitt_x_var = tk.IntVar(value=1)
        self.prewitt_x_check = tk.Checkbutton(self.prewitt_direction_frame, text="X Yönü", variable=self.prewitt_x_var)
        self.prewitt_x_check.pack(side='left', padx=5)
        
        self.prewitt_y_var = tk.IntVar(value=1)
        self.prewitt_y_check = tk.Checkbutton(self.prewitt_direction_frame, text="Y Yönü", variable=self.prewitt_y_var)
        self.prewitt_y_check.pack(side='left', padx=5)
        
        # Prewitt Filtresi uygula butonu
        self.prewitt_buton = tk.Button(
            self.prewitt_frame,
            text="Prewitt Filtresi Uygula",
            command=self.prewitt_filtresi_uygula
        )
        self.prewitt_buton.pack(padx=5, pady=5)
        
        # Roberts Cross Filtresi Ayarları için LabelFrame
        self.roberts_frame = tk.LabelFrame(self.sol_frame, text="Roberts Cross Kenar Algılama", padx=5, pady=5)
        self.roberts_frame.pack(fill='x', padx=5, pady=5)
        
        # Roberts Cross için derinlik seçimi
        self.roberts_depth_frame = tk.Frame(self.roberts_frame)
        self.roberts_depth_frame.pack(fill='x', padx=5, pady=2)
        
        self.roberts_depth_label = tk.Label(self.roberts_depth_frame, text="Derinlik:")
        self.roberts_depth_label.pack(side='left', padx=5)
        
        self.roberts_depth_var = tk.StringVar()
        self.roberts_depth_combobox = ttk.Combobox(self.roberts_depth_frame, 
                                            textvariable=self.roberts_depth_var,
                                            values=('CV_8U', 'CV_32F', 'CV_64F'),
                                            width=8,
                                            state='readonly')
        self.roberts_depth_combobox.current(2)  # Varsayılan CV_64F
        self.roberts_depth_combobox.pack(side='left', padx=5)
        
        # Roberts Cross yön seçimi
        self.roberts_direction_frame = tk.Frame(self.roberts_frame)
        self.roberts_direction_frame.pack(fill='x', padx=5, pady=2)
        
        self.roberts_x_var = tk.IntVar(value=1)
        self.roberts_x_check = tk.Checkbutton(self.roberts_direction_frame, text="X Yönü", variable=self.roberts_x_var)
        self.roberts_x_check.pack(side='left', padx=5)
        
        self.roberts_y_var = tk.IntVar(value=1)
        self.roberts_y_check = tk.Checkbutton(self.roberts_direction_frame, text="Y Yönü", variable=self.roberts_y_var)
        self.roberts_y_check.pack(side='left', padx=5)
        
        # Roberts Cross Filtresi uygula butonu
        self.roberts_buton = tk.Button(
            self.roberts_frame,
            text="Roberts Cross Filtresi Uygula",
            command=self.roberts_filtresi_uygula
        )
        self.roberts_buton.pack(padx=5, pady=5)
        
        # Compass Filtresi Ayarları için LabelFrame
        self.compass_frame = tk.LabelFrame(self.sol_frame, text="Compass Kenar Algılama", padx=5, pady=5)
        self.compass_frame.pack(fill='x', padx=5, pady=5)
        
        # Compass için derinlik seçimi
        self.compass_depth_frame = tk.Frame(self.compass_frame)
        self.compass_depth_frame.pack(fill='x', padx=5, pady=2)
        
        self.compass_depth_label = tk.Label(self.compass_depth_frame, text="Derinlik:")
        self.compass_depth_label.pack(side='left', padx=5)
        
        self.compass_depth_var = tk.StringVar()
        self.compass_depth_combobox = ttk.Combobox(self.compass_depth_frame, 
                                            textvariable=self.compass_depth_var,
                                            values=('CV_8U', 'CV_32F', 'CV_64F'),
                                            width=8,
                                            state='readonly')
        self.compass_depth_combobox.current(2)  # Varsayılan CV_64F
        self.compass_depth_combobox.pack(side='left', padx=5)
        
        # Compass yön seçimi
        self.compass_direction_frame = tk.Frame(self.compass_frame)
        self.compass_direction_frame.pack(fill='x', padx=5, pady=2)
        
        self.compass_east_var = tk.IntVar(value=1)
        self.compass_east_check = tk.Checkbutton(self.compass_direction_frame, text="Doğu", variable=self.compass_east_var)
        self.compass_east_check.pack(side='left', padx=2)
        
        self.compass_west_var = tk.IntVar(value=1)
        self.compass_west_check = tk.Checkbutton(self.compass_direction_frame, text="Batı", variable=self.compass_west_var)
        self.compass_west_check.pack(side='left', padx=2)
        
        self.compass_north_var = tk.IntVar(value=1)
        self.compass_north_check = tk.Checkbutton(self.compass_direction_frame, text="Kuzey", variable=self.compass_north_var)
        self.compass_north_check.pack(side='left', padx=2)
        
        self.compass_south_var = tk.IntVar(value=1)
        self.compass_south_check = tk.Checkbutton(self.compass_direction_frame, text="Güney", variable=self.compass_south_var)
        self.compass_south_check.pack(side='left', padx=2)
        
        # Compass Filtresi uygula butonu
        self.compass_buton = tk.Button(
            self.compass_frame,
            text="Compass Filtresi Uygula",
            command=self.compass_filtresi_uygula
        )
        self.compass_buton.pack(padx=5, pady=5)
        
        # Canny Kenar Algılama Ayarları için LabelFrame
        self.canny_frame = tk.LabelFrame(self.sol_frame, text="Canny Kenar Algılama", padx=5, pady=5)
        self.canny_frame.pack(fill='x', padx=5, pady=5)
        
        # Canny alt eşik değeri için giriş
        self.canny_low_threshold_frame = tk.Frame(self.canny_frame)
        self.canny_low_threshold_frame.pack(fill='x', padx=5, pady=2)
        
        self.canny_low_threshold_label = tk.Label(self.canny_low_threshold_frame, text="Alt Eşik Değeri:")
        self.canny_low_threshold_label.pack(side='left', padx=5)
        
        self.canny_low_threshold_var = tk.StringVar(value="50")
        self.canny_low_threshold_entry = tk.Entry(self.canny_low_threshold_frame, textvariable=self.canny_low_threshold_var, width=5)
        self.canny_low_threshold_entry.pack(side='left', padx=5)
        
        # Canny üst eşik değeri için giriş
        self.canny_high_threshold_frame = tk.Frame(self.canny_frame)
        self.canny_high_threshold_frame.pack(fill='x', padx=5, pady=2)
        
        self.canny_high_threshold_label = tk.Label(self.canny_high_threshold_frame, text="Üst Eşik Değeri:")
        self.canny_high_threshold_label.pack(side='left', padx=5)
        
        self.canny_high_threshold_var = tk.StringVar(value="150")
        self.canny_high_threshold_entry = tk.Entry(self.canny_high_threshold_frame, textvariable=self.canny_high_threshold_var, width=5)
        self.canny_high_threshold_entry.pack(side='left', padx=5)
        
        # Canny aperture boyutu için seçim
        self.canny_aperture_frame = tk.Frame(self.canny_frame)
        self.canny_aperture_frame.pack(fill='x', padx=5, pady=2)
        
        self.canny_aperture_label = tk.Label(self.canny_aperture_frame, text="Aperture Boyutu:")
        self.canny_aperture_label.pack(side='left', padx=5)
        
        self.canny_aperture_var = tk.StringVar()
        self.canny_aperture_combobox = ttk.Combobox(self.canny_aperture_frame, 
                                             textvariable=self.canny_aperture_var,
                                             values=('3', '5', '7'),
                                             width=5,
                                             state='readonly')
        self.canny_aperture_combobox.current(0)  # Varsayılan 3
        self.canny_aperture_combobox.pack(side='left', padx=5)
        
        # Canny L2Gradient seçeneği
        self.canny_l2_var = tk.IntVar(value=0)
        self.canny_l2_check = tk.Checkbutton(self.canny_frame, text="L2Gradient Kullan", variable=self.canny_l2_var)
        self.canny_l2_check.pack(padx=5, pady=2, anchor='w')
        
        # Canny Filtresi uygula butonu
        self.canny_buton = tk.Button(
            self.canny_frame,
            text="Canny Filtresi Uygula",
            command=self.canny_filtresi_uygula
        )
        self.canny_buton.pack(padx=5, pady=5)
        
        # Laplace Kenar Algılama Ayarları için LabelFrame
        self.laplace_frame = tk.LabelFrame(self.sol_frame, text="Laplace Kenar Algılama", padx=5, pady=5)
        self.laplace_frame.pack(fill='x', padx=5, pady=5)
        
        # Laplace için kernel boyutu seçimi
        self.laplace_ksize_frame = tk.Frame(self.laplace_frame)
        self.laplace_ksize_frame.pack(fill='x', padx=5, pady=2)
        
        self.laplace_ksize_label = tk.Label(self.laplace_ksize_frame, text="Kernel Boyutu (ksize):")
        self.laplace_ksize_label.pack(side='left', padx=5)
        
        self.laplace_ksize_var = tk.StringVar()
        self.laplace_ksize_combobox = ttk.Combobox(self.laplace_ksize_frame, 
                                             textvariable=self.laplace_ksize_var,
                                             values=('1', '3', '5', '7'),
                                             width=5,
                                             state='readonly')
        self.laplace_ksize_combobox.current(1)  # Varsayılan 3
        self.laplace_ksize_combobox.pack(side='left', padx=5)
        
        # Laplace için derinlik seçimi
        self.laplace_depth_frame = tk.Frame(self.laplace_frame)
        self.laplace_depth_frame.pack(fill='x', padx=5, pady=2)
        
        self.laplace_depth_label = tk.Label(self.laplace_depth_frame, text="Derinlik:")
        self.laplace_depth_label.pack(side='left', padx=5)
        
        self.laplace_depth_var = tk.StringVar()
        self.laplace_depth_combobox = ttk.Combobox(self.laplace_depth_frame, 
                                             textvariable=self.laplace_depth_var,
                                             values=('CV_8U', 'CV_32F', 'CV_64F'),
                                             width=8,
                                             state='readonly')
        self.laplace_depth_combobox.current(2)  # Varsayılan CV_64F
        self.laplace_depth_combobox.pack(side='left', padx=5)
        
        # Laplace Filtresi uygula butonu
        self.laplace_buton = tk.Button(
            self.laplace_frame,
            text="Laplace Filtresi Uygula",
            command=self.laplace_filtresi_uygula
        )
        self.laplace_buton.pack(padx=5, pady=5)
        
        # Gabor Filtre Ayarları için LabelFrame
        self.gabor_frame = tk.LabelFrame(self.sol_frame, text="Gabor Filtresi", padx=5, pady=5)
        self.gabor_frame.pack(fill='x', padx=5, pady=5)
        
        # Gabor için kernel boyutu girişi
        self.gabor_ksize_frame = tk.Frame(self.gabor_frame)
        self.gabor_ksize_frame.pack(fill='x', padx=5, pady=2)
        
        self.gabor_ksize_label = tk.Label(self.gabor_ksize_frame, text="Kernel Boyutu:")
        self.gabor_ksize_label.pack(side='left', padx=5)
        
        self.gabor_ksize_var = tk.StringVar(value="21")
        self.gabor_ksize_entry = tk.Entry(self.gabor_ksize_frame, textvariable=self.gabor_ksize_var, width=5)
        self.gabor_ksize_entry.pack(side='left', padx=5)
        
        # Gabor için sigma girişi
        self.gabor_sigma_frame = tk.Frame(self.gabor_frame)
        self.gabor_sigma_frame.pack(fill='x', padx=5, pady=2)
        
        self.gabor_sigma_label = tk.Label(self.gabor_sigma_frame, text="Sigma:")
        self.gabor_sigma_label.pack(side='left', padx=5)
        
        self.gabor_sigma_var = tk.StringVar(value="5")
        self.gabor_sigma_entry = tk.Entry(self.gabor_sigma_frame, textvariable=self.gabor_sigma_var, width=5)
        self.gabor_sigma_entry.pack(side='left', padx=5)
        
        # Gabor için theta (açı) girişi
        self.gabor_theta_frame = tk.Frame(self.gabor_frame)
        self.gabor_theta_frame.pack(fill='x', padx=5, pady=2)
        
        self.gabor_theta_label = tk.Label(self.gabor_theta_frame, text="Theta (açı):")
        self.gabor_theta_label.pack(side='left', padx=5)
        
        self.gabor_theta_var = tk.StringVar(value="45")
        self.gabor_theta_entry = tk.Entry(self.gabor_theta_frame, textvariable=self.gabor_theta_var, width=5)
        self.gabor_theta_entry.pack(side='left', padx=5)
        
        # Gabor için lambda (dalga boyu) girişi
        self.gabor_lambda_frame = tk.Frame(self.gabor_frame)
        self.gabor_lambda_frame.pack(fill='x', padx=5, pady=2)
        
        self.gabor_lambda_label = tk.Label(self.gabor_lambda_frame, text="Lambda (dalga boyu):")
        self.gabor_lambda_label.pack(side='left', padx=5)
        
        self.gabor_lambda_var = tk.StringVar(value="10")
        self.gabor_lambda_entry = tk.Entry(self.gabor_lambda_frame, textvariable=self.gabor_lambda_var, width=5)
        self.gabor_lambda_entry.pack(side='left', padx=5)
        
        # Gabor için gamma girişi
        self.gabor_gamma_frame = tk.Frame(self.gabor_frame)
        self.gabor_gamma_frame.pack(fill='x', padx=5, pady=2)
        
        self.gabor_gamma_label = tk.Label(self.gabor_gamma_frame, text="Gamma:")
        self.gabor_gamma_label.pack(side='left', padx=5)
        
        self.gabor_gamma_var = tk.StringVar(value="0.5")
        self.gabor_gamma_entry = tk.Entry(self.gabor_gamma_frame, textvariable=self.gabor_gamma_var, width=5)
        self.gabor_gamma_entry.pack(side='left', padx=5)
        
        # Gabor için psi girişi
        self.gabor_psi_frame = tk.Frame(self.gabor_frame)
        self.gabor_psi_frame.pack(fill='x', padx=5, pady=2)
        
        self.gabor_psi_label = tk.Label(self.gabor_psi_frame, text="Psi (faz):")
        self.gabor_psi_label.pack(side='left', padx=5)
        
        self.gabor_psi_var = tk.StringVar(value="0")
        self.gabor_psi_entry = tk.Entry(self.gabor_psi_frame, textvariable=self.gabor_psi_var, width=5)
        self.gabor_psi_entry.pack(side='left', padx=5)
        
        # Gabor için derinlik seçimi
        self.gabor_depth_frame = tk.Frame(self.gabor_frame)
        self.gabor_depth_frame.pack(fill='x', padx=5, pady=2)
        
        self.gabor_depth_label = tk.Label(self.gabor_depth_frame, text="Derinlik:")
        self.gabor_depth_label.pack(side='left', padx=5)
        
        self.gabor_depth_var = tk.StringVar()
        self.gabor_depth_combobox = ttk.Combobox(self.gabor_depth_frame, 
                                             textvariable=self.gabor_depth_var,
                                             values=('CV_8U', 'CV_32F', 'CV_64F'),
                                             width=8,
                                             state='readonly')
        self.gabor_depth_combobox.current(1)  # Varsayılan CV_32F
        self.gabor_depth_combobox.pack(side='left', padx=5)
        
        # Gabor Filtresi uygula butonu
        self.gabor_buton = tk.Button(
            self.gabor_frame,
            text="Gabor Filtresi Uygula",
            command=self.gabor_filtresi_uygula
        )
        self.gabor_buton.pack(padx=5, pady=5)
        
        # Hough Dönüşümü Ayarları için LabelFrame
        self.hough_frame = tk.LabelFrame(self.sol_frame, text="Hough Dönüşümü", padx=5, pady=5)
        self.hough_frame.pack(fill='x', padx=5, pady=5)
        
        # Hough Dönüşümü için notebook oluştur (sekme görünümü)
        self.hough_notebook = ttk.Notebook(self.hough_frame)
        self.hough_notebook.configure(width=180)

        self.hough_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Hough Doğru Dönüşümü sekmesi
        self.hough_lines_frame = ttk.Frame(self.hough_notebook)
        self.hough_notebook.add(self.hough_lines_frame, text="Doğru Algılama")
        
        # Kenar algılama için Canny eşik değerleri
        self.hough_lines_canny_frame = tk.Frame(self.hough_lines_frame)
        self.hough_lines_canny_frame.pack(fill='x', padx=5, pady=2)
        
        self.hough_lines_canny_low_label = tk.Label(self.hough_lines_canny_frame, text="Canny Alt Eşik:")
        self.hough_lines_canny_low_label.pack(side='left', padx=5)
        
        self.hough_lines_canny_low_var = tk.StringVar(value="50")
        self.hough_lines_canny_low_entry = tk.Entry(self.hough_lines_canny_frame, 
                                                 textvariable=self.hough_lines_canny_low_var, width=5)
        self.hough_lines_canny_low_entry.pack(side='left', padx=5)
        
        self.hough_lines_canny_high_label = tk.Label(self.hough_lines_canny_frame, text="Üst Eşik:")
        self.hough_lines_canny_high_label.pack(side='left', padx=5)
        
        self.hough_lines_canny_high_var = tk.StringVar(value="150")
        self.hough_lines_canny_high_entry = tk.Entry(self.hough_lines_canny_frame, 
                                                  textvariable=self.hough_lines_canny_high_var, width=5)
        self.hough_lines_canny_high_entry.pack(side='left', padx=5)
        
        # Hough Doğru parametreleri
        self.hough_lines_params_frame = tk.Frame(self.hough_lines_frame)
        self.hough_lines_params_frame.pack(fill='x', padx=5, pady=2)
        
        self.hough_lines_rho_label = tk.Label(self.hough_lines_params_frame, text="Rho:")
        self.hough_lines_rho_label.pack(side='left', padx=5)
        
        self.hough_lines_rho_var = tk.StringVar(value="1")
        self.hough_lines_rho_entry = tk.Entry(self.hough_lines_params_frame, 
                                           textvariable=self.hough_lines_rho_var, width=5)
        self.hough_lines_rho_entry.pack(side='left', padx=5)
        
        self.hough_lines_theta_label = tk.Label(self.hough_lines_params_frame, text="Theta (derece):")
        self.hough_lines_theta_label.pack(side='left', padx=5)
        
        self.hough_lines_theta_var = tk.StringVar(value="1")
        self.hough_lines_theta_entry = tk.Entry(self.hough_lines_params_frame, 
                                             textvariable=self.hough_lines_theta_var, width=5)
        self.hough_lines_theta_entry.pack(side='left', padx=5)
        
        # Eşik değeri
        self.hough_lines_threshold_frame = tk.Frame(self.hough_lines_frame)
        self.hough_lines_threshold_frame.pack(fill='x', padx=5, pady=2)
        
        self.hough_lines_threshold_label = tk.Label(self.hough_lines_threshold_frame, text="Eşik Değeri:")
        self.hough_lines_threshold_label.pack(side='left', padx=5)
        
        self.hough_lines_threshold_var = tk.StringVar(value="100")
        self.hough_lines_threshold_entry = tk.Entry(self.hough_lines_threshold_frame, 
                                                 textvariable=self.hough_lines_threshold_var, width=5)
        self.hough_lines_threshold_entry.pack(side='left', padx=5)
        
        # Buton
        self.hough_lines_apply_button = tk.Button(
            self.hough_lines_frame,
            text="Doğruları Algıla",
            command=self.hough_dogrulari_algıla
        )
        self.hough_lines_apply_button.pack(padx=5, pady=5)
        
        # Hough Çember Dönüşümü sekmesi
        self.hough_circles_frame = ttk.Frame(self.hough_notebook)
        self.hough_notebook.add(self.hough_circles_frame, text="Çember Algılama")
        
        # K-Means Segmentasyon Ayarları için LabelFrame
        self.kmeans_frame = tk.LabelFrame(self.sol_frame, text="K-Means Segmentasyon", padx=5, pady=5)
        self.kmeans_frame.pack(fill='x', padx=5, pady=5)
        
        # Morfolojik İşlemler için ana frame
        self.morphology_frame = tk.LabelFrame(self.sol_frame, text="Morfolojik İşlemler", padx=5, pady=5)
        self.morphology_frame.pack(fill='x', padx=5, pady=5)
        
        # Morfolojik İşlemler için Notebook widget
        self.morphology_notebook = ttk.Notebook(self.morphology_frame)
        self.morphology_notebook.pack(fill='x', padx=5, pady=5)
        
        # Aşındırma (Erode) sekmesi
        self.erode_frame = ttk.Frame(self.morphology_notebook)
        self.morphology_notebook.add(self.erode_frame, text="Aşındırma (Erode)")
        
        # Genişletme (Dilate) sekmesi
        self.dilate_frame = ttk.Frame(self.morphology_notebook)
        self.morphology_notebook.add(self.dilate_frame, text="Genişletme (Dilate)")
        
        # Genişletme için kernel boyutu seçimi
        self.dilate_kernel_frame = tk.Frame(self.dilate_frame)
        self.dilate_kernel_frame.pack(fill='x', padx=5, pady=2)
        
        self.dilate_kernel_label = tk.Label(self.dilate_kernel_frame, text="Kernel Boyutu:")
        self.dilate_kernel_label.pack(side='left', padx=5)
        
        self.dilate_kernel_var = tk.StringVar(value="3")
        self.dilate_kernel_combobox = ttk.Combobox(self.dilate_kernel_frame, 
                                              textvariable=self.dilate_kernel_var,
                                              values=('3', '5', '7', '9', '11'),
                                              width=5,
                                              state='readonly')
        self.dilate_kernel_combobox.pack(side='left', padx=5)
        
        # Genişletme için kernel şekli seçimi
        self.dilate_shape_frame = tk.Frame(self.dilate_frame)
        self.dilate_shape_frame.pack(fill='x', padx=5, pady=2)
        
        self.dilate_shape_label = tk.Label(self.dilate_shape_frame, text="Kernel Şekli:")
        self.dilate_shape_label.pack(side='left', padx=5)
        
        self.dilate_shape_var = tk.StringVar(value="Kare")
        self.dilate_shape_combobox = ttk.Combobox(self.dilate_shape_frame, 
                                              textvariable=self.dilate_shape_var,
                                              values=('Kare', 'Disk', 'Çapraz', 'Elips'),
                                              width=8,
                                              state='readonly')
        self.dilate_shape_combobox.pack(side='left', padx=5)
        
        # Genişletme için iterasyon sayısı
        self.dilate_iter_frame = tk.Frame(self.dilate_frame)
        self.dilate_iter_frame.pack(fill='x', padx=5, pady=2)
        
        self.dilate_iter_label = tk.Label(self.dilate_iter_frame, text="İterasyon Sayısı:")
        self.dilate_iter_label.pack(side='left', padx=5)
        
        self.dilate_iter_var = tk.StringVar(value="1")
        self.dilate_iter_combobox = ttk.Combobox(self.dilate_iter_frame, 
                                             textvariable=self.dilate_iter_var,
                                             values=('1', '2', '3', '4', '5', '10'),
                                             width=5,
                                             state='readonly')
        self.dilate_iter_combobox.pack(side='left', padx=5)
        
        # Genişletme butonları
        self.dilate_buttons_frame = tk.Frame(self.dilate_frame)
        self.dilate_buttons_frame.pack(fill='x', padx=5, pady=5)
        
        self.dilate_apply_button = tk.Button(
            self.dilate_buttons_frame,
            text="Genişletme Uygula",
            command=self.genisletme_uygula
        )
        self.dilate_apply_button.pack(side='left', padx=5)
        
        # Aşındırma için kernel boyutu seçimi
        self.erode_kernel_frame = tk.Frame(self.erode_frame)
        self.erode_kernel_frame.pack(fill='x', padx=5, pady=2)
        
        self.erode_kernel_label = tk.Label(self.erode_kernel_frame, text="Kernel Boyutu:")
        self.erode_kernel_label.pack(side='left', padx=5)
        
        self.erode_kernel_var = tk.StringVar(value="3")
        self.erode_kernel_combobox = ttk.Combobox(self.erode_kernel_frame, 
                                              textvariable=self.erode_kernel_var,
                                              values=('3', '5', '7', '9', '11'),
                                              width=5,
                                              state='readonly')
        self.erode_kernel_combobox.pack(side='left', padx=5)
        
        # Aşındırma için kernel şekli seçimi
        self.erode_shape_frame = tk.Frame(self.erode_frame)
        self.erode_shape_frame.pack(fill='x', padx=5, pady=2)
        
        self.erode_shape_label = tk.Label(self.erode_shape_frame, text="Kernel Şekli:")
        self.erode_shape_label.pack(side='left', padx=5)
        
        self.erode_shape_var = tk.StringVar(value="Kare")
        self.erode_shape_combobox = ttk.Combobox(self.erode_shape_frame, 
                                              textvariable=self.erode_shape_var,
                                              values=('Kare', 'Disk', 'Çapraz', 'Elips'),
                                              width=8,
                                              state='readonly')
        self.erode_shape_combobox.pack(side='left', padx=5)
        
        # Aşındırma için iterasyon sayısı
        self.erode_iter_frame = tk.Frame(self.erode_frame)
        self.erode_iter_frame.pack(fill='x', padx=5, pady=2)
        
        self.erode_iter_label = tk.Label(self.erode_iter_frame, text="İterasyon Sayısı:")
        self.erode_iter_label.pack(side='left', padx=5)
        
        self.erode_iter_var = tk.StringVar(value="1")
        self.erode_iter_combobox = ttk.Combobox(self.erode_iter_frame, 
                                             textvariable=self.erode_iter_var,
                                             values=('1', '2', '3', '4', '5', '10'),
                                             width=5,
                                             state='readonly')
        self.erode_iter_combobox.pack(side='left', padx=5)
        
        # Aşındırma butonları
        self.erode_buttons_frame = tk.Frame(self.erode_frame)
        self.erode_buttons_frame.pack(fill='x', padx=5, pady=5)
        
        self.erode_apply_button = tk.Button(
            self.erode_buttons_frame,
            text="Aşındırma Uygula",
            command=self.asindirma_uygula
        )
        self.erode_apply_button.pack(side='left', padx=5)
        
        # Küme (cluster) sayısı ayarı
        self.kmeans_k_frame = tk.Frame(self.kmeans_frame)
        self.kmeans_k_frame.pack(fill='x', padx=5, pady=2)
        
        self.kmeans_k_label = tk.Label(self.kmeans_k_frame, text="Küme Sayısı (K):")
        self.kmeans_k_label.pack(side='left', padx=5)
        
        self.kmeans_k_var = tk.StringVar(value="3")
        self.kmeans_k_combobox = ttk.Combobox(self.kmeans_k_frame, 
                                            textvariable=self.kmeans_k_var,
                                            values=('2', '3', '4', '5', '6', '7', '8', '10', '12', '15'),
                                            width=5,
                                            state='readonly')
        self.kmeans_k_combobox.pack(side='left', padx=5)
        
        # Maksimum iterasyon sayısı
        self.kmeans_iter_frame = tk.Frame(self.kmeans_frame)
        self.kmeans_iter_frame.pack(fill='x', padx=5, pady=2)
        
        self.kmeans_iter_label = tk.Label(self.kmeans_iter_frame, text="Maksimum İterasyon:")
        self.kmeans_iter_label.pack(side='left', padx=5)
        
        self.kmeans_iter_var = tk.StringVar(value="100")
        self.kmeans_iter_entry = tk.Entry(self.kmeans_iter_frame, textvariable=self.kmeans_iter_var, width=5)
        self.kmeans_iter_entry.pack(side='left', padx=5)
        
        # Epsilon (yaklaşım hassasiyeti)
        self.kmeans_epsilon_frame = tk.Frame(self.kmeans_frame)
        self.kmeans_epsilon_frame.pack(fill='x', padx=5, pady=2)
        
        self.kmeans_epsilon_label = tk.Label(self.kmeans_epsilon_frame, text="Epsilon:")
        self.kmeans_epsilon_label.pack(side='left', padx=5)
        
        self.kmeans_epsilon_var = tk.StringVar(value="0.2")
        self.kmeans_epsilon_entry = tk.Entry(self.kmeans_epsilon_frame, textvariable=self.kmeans_epsilon_var, width=5)
        self.kmeans_epsilon_entry.pack(side='left', padx=5)
        
        # Başlangıç merkezi ayarı
        self.kmeans_attempts_frame = tk.Frame(self.kmeans_frame)
        self.kmeans_attempts_frame.pack(fill='x', padx=5, pady=2)
        
        self.kmeans_attempts_label = tk.Label(self.kmeans_attempts_frame, text="Deneme Sayısı:")
        self.kmeans_attempts_label.pack(side='left', padx=5)
        
        self.kmeans_attempts_var = tk.StringVar(value="10")
        self.kmeans_attempts_entry = tk.Entry(self.kmeans_attempts_frame, textvariable=self.kmeans_attempts_var, width=5)
        self.kmeans_attempts_entry.pack(side='left', padx=5)
        
        # Merkez belirleme yöntemi
        self.kmeans_method_frame = tk.Frame(self.kmeans_frame)
        self.kmeans_method_frame.pack(fill='x', padx=5, pady=2)
        
        self.kmeans_method_label = tk.Label(self.kmeans_method_frame, text="Başlangıç Yöntemi:")
        self.kmeans_method_label.pack(side='left', padx=5)
        
        self.kmeans_method_var = tk.StringVar(value="Rastgele")
        self.kmeans_method_combobox = ttk.Combobox(self.kmeans_method_frame, 
                                               textvariable=self.kmeans_method_var,
                                               values=('Rastgele', 'PP'),
                                               width=8,
                                               state='readonly')
        self.kmeans_method_combobox.pack(side='left', padx=5)
        
        # Renk uzayı seçimi
        self.kmeans_colorspace_frame = tk.Frame(self.kmeans_frame)
        self.kmeans_colorspace_frame.pack(fill='x', padx=5, pady=2)
        
        self.kmeans_colorspace_label = tk.Label(self.kmeans_colorspace_frame, text="Renk Uzayı:")
        self.kmeans_colorspace_label.pack(side='left', padx=5)
        
        self.kmeans_colorspace_var = tk.StringVar(value="RGB")
        self.kmeans_colorspace_combobox = ttk.Combobox(self.kmeans_colorspace_frame, 
                                                   textvariable=self.kmeans_colorspace_var,
                                                   values=('RGB', 'HSV', 'LAB'),
                                                   width=5,
                                                   state='readonly')
        self.kmeans_colorspace_combobox.pack(side='left', padx=5)
        
        # Buton
        self.kmeans_apply_button = tk.Button(
            self.kmeans_frame,
            text="K-Means Segmentasyonu Uygula",
            command=self.kmeans_segmentasyonu_uygula
        )
        self.kmeans_apply_button.pack(padx=5, pady=5)
        
        # Ön işleme parametreleri
        self.hough_circles_preprocess_frame = tk.Frame(self.hough_circles_frame)
        self.hough_circles_preprocess_frame.pack(fill='x', padx=5, pady=2)
        
        self.hough_circles_blur_label = tk.Label(self.hough_circles_preprocess_frame, text="Bulanıklaştırma Boyutu:")
        self.hough_circles_blur_label.pack(side='left', padx=5)
        
        self.hough_circles_blur_var = tk.StringVar(value="9")
        self.hough_circles_blur_combobox = ttk.Combobox(self.hough_circles_preprocess_frame, 
                                                    textvariable=self.hough_circles_blur_var,
                                                    values=('3', '5', '7', '9', '11', '13'),
                                                    width=5,
                                                    state='readonly')
        self.hough_circles_blur_combobox.pack(side='left', padx=5)
        
        # Hough Çember parametreleri
        self.hough_circles_param1_frame = tk.Frame(self.hough_circles_frame)
        self.hough_circles_param1_frame.pack(fill='x', padx=5, pady=2)
        
        self.hough_circles_param1_label = tk.Label(self.hough_circles_param1_frame, text="Param1 (Kenar Eşiği):")
        self.hough_circles_param1_label.pack(side='left', padx=5)
        
        self.hough_circles_param1_var = tk.StringVar(value="50")
        self.hough_circles_param1_entry = tk.Entry(self.hough_circles_param1_frame, 
                                                textvariable=self.hough_circles_param1_var, width=5)
        self.hough_circles_param1_entry.pack(side='left', padx=5)
        
        self.hough_circles_param2_label = tk.Label(self.hough_circles_param1_frame, text="Param2 (Merkez Eşiği):")
        self.hough_circles_param2_label.pack(side='left', padx=5)
        
        self.hough_circles_param2_var = tk.StringVar(value="30")
        self.hough_circles_param2_entry = tk.Entry(self.hough_circles_param1_frame, 
                                                textvariable=self.hough_circles_param2_var, width=5)
        self.hough_circles_param2_entry.pack(side='left', padx=5)
        
        # Min/max yarıçap ve min mesafe
        self.hough_circles_radius_frame = tk.Frame(self.hough_circles_frame)
        self.hough_circles_radius_frame.pack(fill='x', padx=5, pady=2)
        
        self.hough_circles_min_radius_label = tk.Label(self.hough_circles_radius_frame, text="Min Yarıçap:")
        self.hough_circles_min_radius_label.pack(side='left', padx=5)
        
        self.hough_circles_min_radius_var = tk.StringVar(value="10")
        self.hough_circles_min_radius_entry = tk.Entry(self.hough_circles_radius_frame, 
                                                    textvariable=self.hough_circles_min_radius_var, width=5)
        self.hough_circles_min_radius_entry.pack(side='left', padx=5)
        
        self.hough_circles_max_radius_label = tk.Label(self.hough_circles_radius_frame, text="Max Yarıçap:")
        self.hough_circles_max_radius_label.pack(side='left', padx=5)
        
        self.hough_circles_max_radius_var = tk.StringVar(value="100")
        self.hough_circles_max_radius_entry = tk.Entry(self.hough_circles_radius_frame, 
                                                    textvariable=self.hough_circles_max_radius_var, width=5)
        self.hough_circles_max_radius_entry.pack(side='left', padx=5)
        
        # Merkezler arası minimum mesafe
        self.hough_circles_min_dist_frame = tk.Frame(self.hough_circles_frame)
        self.hough_circles_min_dist_frame.pack(fill='x', padx=5, pady=2)
        
        self.hough_circles_min_dist_label = tk.Label(self.hough_circles_min_dist_frame, text="Min. Merkez Mesafesi:")
        self.hough_circles_min_dist_label.pack(side='left', padx=5)
        
        self.hough_circles_min_dist_var = tk.StringVar(value="30")
        self.hough_circles_min_dist_entry = tk.Entry(self.hough_circles_min_dist_frame, 
                                                  textvariable=self.hough_circles_min_dist_var, width=5)
        self.hough_circles_min_dist_entry.pack(side='left', padx=5)
        
        # Çember Rengi
        self.hough_circles_color_frame = tk.Frame(self.hough_circles_frame)
        self.hough_circles_color_frame.pack(fill='x', padx=5, pady=2)
        
        self.hough_circles_color_label = tk.Label(self.hough_circles_color_frame, text="Çember Rengi:")
        self.hough_circles_color_label.pack(side='left', padx=5)
        
        self.hough_circles_color_var = tk.StringVar(value="Yeşil")
        self.hough_circles_color_combobox = ttk.Combobox(self.hough_circles_color_frame, 
                                                      textvariable=self.hough_circles_color_var,
                                                      values=('Yeşil', 'Kırmızı', 'Mavi', 'Sarı', 'Mor'),
                                                      width=8,
                                                      state='readonly')
        self.hough_circles_color_combobox.pack(side='left', padx=5)
        
        # Buton
        self.hough_circles_apply_button = tk.Button(
            self.hough_circles_frame,
            text="Çemberleri Algıla",
            command=self.hough_cemberleri_algıla
        )
        self.hough_circles_apply_button.pack(padx=5, pady=5)
        
        # Döndürme açısı için giriş
        self.aci_dondurme_label = tk.Label(self.dondurme_frame, text="Döndürme Açısı (derece):")
        self.aci_dondurme_label.pack()
        self.aci_dondurme_entry = tk.Entry(self.dondurme_frame)
        self.aci_dondurme_entry.pack()
        self.aci_dondurme_entry.insert(0, "30")  # Varsayılan değer
        
        # İnterpolasyon yöntemi seçimi için radio butonlar
        self.dondurme_interpolasyon_label = tk.Label(self.dondurme_frame, text="İnterpolasyon Yöntemi:")
        self.dondurme_interpolasyon_label.pack()
        
        self.dondurme_interpolasyon = tk.StringVar()
        self.dondurme_interpolasyon.set('nearest')  # Varsayılan değer
        
        self.nearest_radio = tk.Radiobutton(
            self.dondurme_frame,
            text="En Yakın Komşu (Alias)",
            variable=self.dondurme_interpolasyon,
            value='nearest'
        )
        self.nearest_radio.pack()
        
        self.bilinear_rotate_radio = tk.Radiobutton(
            self.dondurme_frame,
            text="Bilinear (Anti-alias)",
            variable=self.dondurme_interpolasyon,
            value='bilinear'
        )
        self.bilinear_rotate_radio.pack()
        
        self.bicubic_rotate_radio = tk.Radiobutton(
            self.dondurme_frame,
            text="Bicubic (Anti-alias)",
            variable=self.dondurme_interpolasyon,
            value='bicubic'
        )
        self.bicubic_rotate_radio.pack()
        
        self.lanczos_rotate_radio = tk.Radiobutton(
            self.dondurme_frame,
            text="Lanczos (Anti-alias)",
            variable=self.dondurme_interpolasyon,
            value='lanczos'
        )
        self.lanczos_rotate_radio.pack()
        
        # Döndürme butonu
        self.dondur_buton = tk.Button(
            self.dondurme_frame,
            text="Görüntüyü Döndür",
            command=self.goruntu_dondur
        )
        self.dondur_buton.pack(padx=5, pady=2)
        
        # Kırpma işlemleri için LabelFrame
        self.kirpma_frame = tk.LabelFrame(self.sol_frame, text="Görüntü Kırpma", padx=5, pady=5)
        self.kirpma_frame.pack(fill='x', padx=5, pady=5)
        
        # Başlangıç X koordinatı
        self.baslangic_x_label = tk.Label(self.kirpma_frame, text="Başlangıç X koordinatı:")
        self.baslangic_x_label.pack()
        self.baslangic_x_entry = tk.Entry(self.kirpma_frame)
        self.baslangic_x_entry.pack()
        self.baslangic_x_entry.insert(0, "100")  # Varsayılan değer
        
        # Bitiş X koordinatı
        self.bitis_x_label = tk.Label(self.kirpma_frame, text="Bitiş X koordinatı:")
        self.bitis_x_label.pack()
        self.bitis_x_entry = tk.Entry(self.kirpma_frame)
        self.bitis_x_entry.pack()
        self.bitis_x_entry.insert(0, "300")  # Varsayılan değer
        
        # Başlangıç Y koordinatı
        self.baslangic_y_label = tk.Label(self.kirpma_frame, text="Başlangıç Y koordinatı:")
        self.baslangic_y_label.pack()
        self.baslangic_y_entry = tk.Entry(self.kirpma_frame)
        self.baslangic_y_entry.pack()
        self.baslangic_y_entry.insert(0, "50")  # Varsayılan değer
        
        # Bitiş Y koordinatı
        self.bitis_y_label = tk.Label(self.kirpma_frame, text="Bitiş Y koordinatı:")
        self.bitis_y_label.pack()
        self.bitis_y_entry = tk.Entry(self.kirpma_frame)
        self.bitis_y_entry.pack()
        self.bitis_y_entry.insert(0, "200")  # Varsayılan değer
        
        # Kırpma butonu
        self.kirp_buton = tk.Button(
            self.kirpma_frame,
            text="Görüntüyü Kırp",
            command=self.goruntu_kirp
        )
        self.kirp_buton.pack(padx=5, pady=2)
    
    def goruntu_yukle(self):
        try:
            dosya_yolu = filedialog.askopenfilename(
                filetypes=[
                    ("Görüntü Dosyaları", "*.jpg *.jpeg *.png *.bmp"),
                    ("Tüm Dosyalar", "*.*")
                ]
            )
            
            if dosya_yolu:
                print(f"Seçilen dosya: {dosya_yolu}")  # Hata ayıklama için
                
                # Görüntüyü oku
                self.goruntu = cv2.imread(dosya_yolu)
                # Orijinal görüntüyü sakla
                self.orijinal_goruntu = self.goruntu.copy()
                
                if self.goruntu is not None:
                    # Görüntü boyutlarını al
                    yukseklik, genislik, kanal = self.goruntu.shape
                    
                    # Bilgi etiketini güncelle
                    boyut_bilgisi = f"Görüntü boyutları: {yukseklik}x{genislik}, Kanal sayısı: {kanal}"
                    self.bilgi_label.config(text=boyut_bilgisi)
                    
                    # Görüntüyü göster
                    self.goruntu_goster()
                    
                    messagebox.showinfo("Başarılı", "Görüntü yüklendi!")
                else:
                    messagebox.showerror("Hata", f"Görüntü yüklenemedi!\nDosya yolu: {dosya_yolu}")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu:\n{str(e)}")
    
    def goruntu_kaydet(self):
        if self.goruntu is not None:
            dosya_yolu = filedialog.asksaveasfilename(defaultextension=".jpg")
            if dosya_yolu:
                cv2.imwrite(dosya_yolu, self.goruntu)
                messagebox.showinfo("Başarılı", "Görüntü kaydedildi!")
        else:
            messagebox.showerror("Hata", "Kaydedilecek görüntü bulunamadı!")
    
    def goruntu_goster(self):
        if self.goruntu is not None:
            # Görüntü boyutlarını al
            h, w = self.goruntu.shape[:2]
            
            # Görüntü çok küçük mü kontrol et ve gerekirse yeniden boyutlandır
            MIN_DISPLAY_SIZE = 400  # Minimum görüntüleme boyutu
            scale_factor = 1.0
            
            # Küçük görüntüler için ölçeklendirme faktörü hesapla
            if max(h, w) < MIN_DISPLAY_SIZE:
                scale_factor = MIN_DISPLAY_SIZE / max(h, w)
                # Görüntüyü yeniden boyutlandır (sadece görüntüleme için, gerçek görüntü değişmez)
                display_img = cv2.resize(self.goruntu.copy(), 
                                       (int(w * scale_factor), int(h * scale_factor)), 
                                       interpolation=cv2.INTER_LINEAR)
            else:
                display_img = self.goruntu.copy()
            
            # Görüntüyü PIL formatına dönüştür
            if len(display_img.shape) == 2:  # Gri tonlamalı görüntü
                pil_goruntu = Image.fromarray(display_img)
            else:  # Renkli görüntü
                # OpenCV BGR, PIL RGB kullanır
                pil_goruntu = Image.fromarray(cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB))
            
            # Tkinter PhotoImage formatına dönüştür
            self.tk_goruntu = ImageTk.PhotoImage(image=pil_goruntu)
            
            # Canvas boyutunu belirle
            display_width, display_height = pil_goruntu.width, pil_goruntu.height
            canvas_width = max(display_width, 400)  # Canvas en az 400 piksel genişliğinde
            canvas_height = max(display_height, 300)  # Canvas en az 300 piksel yüksekliğinde
            
            # Canvas'ı temizle
            self.canvas.delete("all")
            
            # Canvas'ı günculle
            self.canvas.config(width=canvas_width, height=canvas_height)
            self.canvas.create_image(canvas_width//2, canvas_height//2, anchor='center', image=self.tk_goruntu)
            
            # Görüntü boyutu bilgisini göster
            if scale_factor > 1.0:
                boyut_str = f"Görüntü boyutları: {h}x{w} (Görüntüleme boyutu: {int(h*scale_factor)}x{int(w*scale_factor)})"
            else:
                boyut_str = f"Görüntü boyutları: {h}x{w}"
            self.bilgi_label.config(text=boyut_str)
    
    def gri_tonla(self):
        if self.goruntu is not None:
            # Görüntüyü gri tonlamaya çevir
            self.goruntu = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            # Gri görüntüyü 3 kanallı yap (görüntüleme için)
            self.goruntu = cv2.cvtColor(self.goruntu, cv2.COLOR_GRAY2BGR)
            
            # Görüntü boyutlarını günculle
            yukseklik, genislik = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {yukseklik}x{genislik}, Gri Seviye"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            # Görüntüyü göster
            self.goruntu_goster()
            messagebox.showinfo("Başarılı", "Resim griye çevrildi!")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def grayscale_donusum(self):
        if self.goruntu is not None:
            # BGR → Grayscale dönüşümü
            self.goruntu = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            # Gri görüntüyü 3 kanallı yap (görüntüleme için)
            self.goruntu = cv2.cvtColor(self.goruntu, cv2.COLOR_GRAY2BGR)
            
            # Görüntü boyutlarını günculle
            yukseklik, genislik = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {yukseklik}x{genislik}, Grayscale"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            # Görüntüyü göster
            self.goruntu_goster()
            messagebox.showinfo("Başarılı", "Grayscale dönüşümü tamamlandı!")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def orijinale_don(self):
        if self.orijinal_goruntu is not None:
            # Orijinal görüntüyü geri yükle
            self.goruntu = self.orijinal_goruntu.copy()
            
            # Görüntü boyutlarını günculle
            yukseklik, genislik, kanal = self.goruntu.shape
            boyut_bilgisi = f"Görüntü boyutları: {yukseklik}x{genislik}, Kanal sayısı: {kanal}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            # Görüntüyü göster
            self.goruntu_goster()
            messagebox.showinfo("Başarılı", "Orijinal görüntüye dönüldü!")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def kanal_sec(self):
        if self.goruntu is not None:
            secim = self.kanal_secimi.get()
            
            # Görüntüyü orijinalden kopyala
            #self.goruntu = self.orijinal_goruntu.copy()
            
            if secim == 'kirmizi':
                # Yeşil ve mavi kanalları sıfırla
                self.goruntu[:,:,1:3] = 0
                mesaj = "Mavi kanal görüntüleniyor!"
                kanal_bilgisi = "Kırmızı Kanal"
            elif secim == 'yesil':
                # Kırmızı ve mavi kanalları sıfırla
                self.goruntu[:,:,0] = 0
                self.goruntu[:,:,2] = 0
                mesaj = "Yeşil kanal görüntüleniyor!"
                kanal_bilgisi = "Yeşil Kanal"
            elif secim == 'mavi':
                # Kırmızı ve yeşil kanalları sıfırla
                self.goruntu[:,:,0:2] = 0
                mesaj = "Kırmızı kanal görüntüleniyor!"
                kanal_bilgisi = "Mavi Kanal"
            else:  # orijinal
                mesaj = "Orijinal görüntü görüntüleniyor!"
                kanal_bilgisi = f"Kanal sayısı: {self.goruntu.shape[2]}"
            
            # Bilgi etiketini günculle
            yukseklik, genislik = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {yukseklik}x{genislik}, {kanal_bilgisi}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            # Görüntüyü göster
            self.goruntu_goster()
            messagebox.showinfo("Başarılı", mesaj)
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def negatif_al(self):
        if self.goruntu is not None:
            # Görüntünün negatifini al
            self.goruntu = cv2.bitwise_not(self.goruntu)
            
            # Görüntü boyutlarını günculle
            yukseklik, genislik = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {yukseklik}x{genislik}, Negatif Görüntü"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            # Görüntüyü göster
            self.goruntu_goster()
            messagebox.showinfo("Başarılı", "Görüntünün negatifi alındı!")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def parlaklik_ayarla(self):
        if self.goruntu is not None:
            # Parlaklık değerini al
            parlaklik = self.parlaklik_slider.get()
            
            # Görüntüyü orijinalden kopyala
            #self.goruntu = self.orijinal_goruntu.copy()
            
            # Görüntü boyutlarını al
            x, y, z = self.goruntu.shape
            
            # Her piksel için parlaklık ekle
            for i in range(x):
                for j in range(y):
                    for k in range(z):
                        # Parlaklık değerini ekle ve 255'i aşmamasını sağla
                        yeni_deger = self.goruntu[i,j,k] + parlaklik
                        self.goruntu[i,j,k] = min(255, yeni_deger)
            
            # Görüntü boyutlarını günculle
            yukseklik, genislik = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {yukseklik}x{genislik}, Parlaklık: +{parlaklik}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            # Görüntüyü göster
            self.goruntu_goster()
            messagebox.showinfo("Başarılı", f"Parlaklık değeri {parlaklik} uygulandı!")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def esikleme_uygula(self):
        if self.goruntu is not None:
            # Eşik değerini al
            esik = self.esik_slider.get()
            
            # Görüntüyü orijinalden kopyala
            #self.goruntu = self.orijinal_goruntu.copy()
            
            # Görüntü boyutlarını al
            if len(self.goruntu.shape) == 3:  # Renkli görüntü
                x, y, z = self.goruntu.shape
                # Her piksel için eşikleme uygula
                for i in range(x):
                    for j in range(y):
                        for k in range(z):
                            if self.goruntu[i,j,k] >= esik:
                                self.goruntu[i,j,k] = 255
                            else:
                                self.goruntu[i,j,k] = 0
                kanal_bilgisi = "Renkli Eşikleme"
            else:  # Gri tonlamalı görüntü
                x, y = self.goruntu.shape
                # Her piksel için eşikleme uygula
                for i in range(x):
                    for j in range(y):
                        if self.goruntu[i,j] >= esik:
                            self.goruntu[i,j] = 255
                        else:
                            self.goruntu[i,j] = 0
                kanal_bilgisi = "Gri Eşikleme"
            
            # Bilgi etiketini günculle
            boyut_bilgisi = f"Görüntü boyutları: {x}x{y}, {kanal_bilgisi}, Eşik: {esik}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            # Görüntüyü göster
            self.goruntu_goster()
            messagebox.showinfo("Başarılı", f"Eşikleme uygulandı! (Eşik değeri: {esik})")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def histogram_goster(self):
        if self.goruntu is not None:
            plt.figure(figsize=(12, 4))
            
            # Görüntü renkli mi kontrol et
            if len(self.goruntu.shape) == 3:  # Renkli görüntü
                colors = ('b', 'g', 'r')
                plt.subplot(1, 2, 1)
                plt.title("Renkli Görüntü")
                plt.imshow(cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2RGB))
                plt.axis('off')
                
                plt.subplot(1, 2, 2)
                plt.title("RGB Histogram")
                for i, color in enumerate(colors):
                    hist = cv2.calcHist([self.goruntu], [i], None, [256], [0, 256])
                    plt.plot(hist, color=color)
                plt.xlabel("Piksel Değeri")
                plt.ylabel("Frekans")
                plt.xlim([0, 256])
            else:  # Gri seviye görüntü
                plt.subplot(1, 2, 1)
                plt.title("Gri Seviye Görüntü")
                plt.imshow(self.goruntu, cmap='gray')
                plt.axis('off')
                
                plt.subplot(1, 2, 2)
                plt.title("Gri Seviye Histogram")
                hist = cv2.calcHist([self.goruntu], [0], None, [256], [0, 256])
                plt.plot(hist, color='black')
                plt.xlabel("Piksel Değeri")
                plt.ylabel("Frekans")
                plt.xlim([0, 256])
            
            plt.tight_layout()
            plt.show()
            messagebox.showinfo("Başarılı", "Histogram gösteriliyor!")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def histogram_esitle(self):
        if self.goruntu is not None:
            try:
                if len(self.goruntu.shape) == 3:  # Renkli görüntü
                    # Renkli görüntüyü LAB renk uzayına çevir
                    lab = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2LAB)
                    # L kanalını ayır ve eşitle
                    l, a, b = cv2.split(lab)
                    l_esitlenmis = cv2.equalizeHist(l)
                    # Kanalları birleştir
                    lab_esitlenmis = cv2.merge((l_esitlenmis, a, b))
                    # BGR'ye geri çevir
                    self.goruntu = cv2.cvtColor(lab_esitlenmis, cv2.COLOR_LAB2BGR)
                else:  # Gri seviye görüntü
                    self.goruntu = cv2.equalizeHist(self.goruntu)
                
                # Görüntüyü günculle
                self.goruntu_goster()
                
                # Bilgi etiketini günculle
                yukseklik, genislik = self.goruntu.shape[:2]
                kanal_bilgisi = "Histogram Eşitlenmiş"
                boyut_bilgisi = f"Görüntü boyutları: {yukseklik}x{genislik}, {kanal_bilgisi}"
                self.bilgi_label.config(text=boyut_bilgisi)
                
                messagebox.showinfo("Başarılı", "Histogram eşitleme işlemi tamamlandı!")
            except Exception as e:
                messagebox.showerror("Hata", f"Histogram eşitleme sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def otomatik_kontrast_germe(self):
        if self.goruntu is not None:
            try:
                # Görüntüyü gri tonlamaya çevir
                if len(self.goruntu.shape) == 3:
                    gri_goruntu = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
                else:
                    gri_goruntu = self.goruntu.copy()
                
                # Minimum ve maksimum değerleri bul
                I_min = np.min(gri_goruntu)
                I_max = np.max(gri_goruntu)
                
                # Kontrast germe işlemi
                stretched = ((gri_goruntu - I_min) / (I_max - I_min) * 255).astype(np.uint8)
                
                # Görüntüyü 3 kanallı yap
                self.goruntu = cv2.cvtColor(stretched, cv2.COLOR_GRAY2BGR)
                
                # Görüntüyü günculle
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", "Otomatik kontrast germe uygulandı!")
            except Exception as e:
                messagebox.showerror("Hata", f"Kontrast germe sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def manuel_kontrast_germe(self):
        if self.goruntu is not None:
            try:
                # Kullanıcının girdiği değerleri al
                in_min = int(self.manuel_min_entry.get())
                in_max = int(self.manuel_max_entry.get())
                
                # Değerlerin geçerliliğini kontrol et
                if not (0 <= in_min < in_max <= 255):
                    messagebox.showerror("Hata", "Geçersiz min/max değerleri!")
                    return
                
                # Görüntüyü gri tonlamaya çevir
                if len(self.goruntu.shape) == 3:
                    gri_goruntu = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
                else:
                    gri_goruntu = self.goruntu.copy()
                
                # Kontrast germe işlemi
                stretched = np.clip((gri_goruntu - in_min) / (in_max - in_min) * 255, 0, 255).astype(np.uint8)
                
                # Görüntüyü 3 kanallı yap
                self.goruntu = cv2.cvtColor(stretched, cv2.COLOR_GRAY2BGR)
                
                # Görüntüyü günculle
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", f"Manuel kontrast germe uygulandı! (min={in_min}, max={in_max})")
            except ValueError:
                messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
            except Exception as e:
                messagebox.showerror("Hata", f"Kontrast germe sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def coklu_kontrast_germe(self):
        if self.goruntu is not None:
            try:
                # Görüntüyü gri tonlamaya çevir
                if len(self.goruntu.shape) == 3:
                    gri_goruntu = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
                else:
                    gri_goruntu = self.goruntu.copy()
                
                # Çoklu kontrast bölgeleri
                ranges = [
                    (0, 80, 0, 100),     # Karanlık bölgeler
                    (81, 160, 50, 200),   # Orta tonlar
                    (161, 255, 150, 255)  # Açık tonlar
                ]
                
                # Yeni görüntü oluştur
                stretched = np.zeros_like(gri_goruntu, dtype=np.uint8)
                
                # Her bölge için kontrast germe uygula
                for in_min, in_max, out_min, out_max in ranges:
                    mask = (gri_goruntu >= in_min) & (gri_goruntu <= in_max)
                    stretched[mask] = np.clip(
                        (gri_goruntu[mask] - in_min) / (in_max - in_min) * (out_max - out_min) + out_min,
                        out_min, out_max
                    )
                
                # Görüntüyü 3 kanallı yap
                self.goruntu = cv2.cvtColor(stretched, cv2.COLOR_GRAY2BGR)
                
                # Görüntüyü günculle
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", "Çoklu kontrast germe uygulandı!")
            except Exception as e:
                messagebox.showerror("Hata", f"Kontrast germe sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def manuel_tasima(self):
        if self.goruntu is not None:
            try:
                # Taşıma değerlerini al
                dx = int(self.x_entry.get())
                dy = int(self.y_entry.get())
                
                # Görüntü boyutlarını al
                h, w = self.goruntu.shape[:2]
                
                # Yeni görüntü oluştur
                tasimis_goruntu = np.zeros_like(self.goruntu)
                
                # Manuel taşıma işlemi
                for y in range(h - dy):
                    for x in range(w - dx):
                        tasimis_goruntu[y + dy, x + dx] = self.goruntu[y, x]
                
                # Görüntüyü günculle
                self.goruntu = tasimis_goruntu
                
                # Bilgi etiketini günculle
                yukseklik, genislik = self.goruntu.shape[:2]
                boyut_bilgisi = f"Görüntü boyutları: {yukseklik}x{genislik}, Taşıma: dx={dx}, dy={dy}"
                self.bilgi_label.config(text=boyut_bilgisi)
                
                # Görüntüyü göster
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", f"Görüntü manuel olarak taşındı! (dx={dx}, dy={dy})")
            except ValueError:
                messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
            except Exception as e:
                messagebox.showerror("Hata", f"Taşıma işlemi sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def fonksiyon_tasima(self):
        if self.goruntu is not None:
            try:
                # Taşıma değerlerini al
                dx = int(self.x_entry.get())
                dy = int(self.y_entry.get())
                
                # Taşıma matrisi oluştur
                T = np.float32([[1, 0, dx], [0, 1, dy]])
                
                # Görüntüyü taşı (warpAffine kullanarak)
                tasimis_goruntu = cv2.warpAffine(
                    self.goruntu, 
                    T, 
                    (self.goruntu.shape[1], self.goruntu.shape[0])
                )
                
                # Görüntüyü günculle
                self.goruntu = tasimis_goruntu
                
                # Bilgi etiketini günculle
                yukseklik, genislik = self.goruntu.shape[:2]
                boyut_bilgisi = f"Görüntü boyutları: {yukseklik}x{genislik}, Taşıma: dx={dx}, dy={dy}"
                self.bilgi_label.config(text=boyut_bilgisi)
                
                # Görüntüyü göster
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", f"Görüntü fonksiyon ile taşındı! (dx={dx}, dy={dy})")
            except ValueError:
                messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
            except Exception as e:
                messagebox.showerror("Hata", f"Taşıma işlemi sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def dikey_aynalama(self):
        if self.goruntu is not None:
            try:
                # Görüntü boyutlarını al
                h, w = self.goruntu.shape[:2]
                
                # X koordinatını al veya varsayılan olarak ortayı kullan
                x0 = int(self.x_ayna_entry.get()) if self.x_ayna_entry.get() else w // 2
                
                # Yeni görüntü oluştur
                aynali_goruntu = self.goruntu.copy()
                
                # Dikey aynalama işlemi
                for y1 in range(h):
                    for x1 in range(w):
                        x2 = -x1 + 2 * x0  # Aynalama formülü
                        if 0 <= x2 < w:
                            aynali_goruntu[y1, x2] = self.goruntu[y1, x1]
                
                # Görüntüyü günculle
                self.goruntu = aynali_goruntu
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", f"Dikey aynalama uygulandı! (x={x0})")
            except Exception as e:
                messagebox.showerror("Hata", f"Aynalama sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def yatay_aynalama(self):
        if self.goruntu is not None:
            try:
                # Görüntü boyutlarını al
                h, w = self.goruntu.shape[:2]
                
                # Y koordinatını al veya varsayılan olarak ortayı kullan
                y0 = int(self.y_ayna_entry.get()) if self.y_ayna_entry.get() else h // 2
                
                # Yeni görüntü oluştur
                aynali_goruntu = self.goruntu.copy()
                
                # Yatay aynalama işlemi
                for y1 in range(h):
                    y2 = -y1 + 2 * y0  # Aynalama formülü
                    if 0 <= y2 < h:
                        aynali_goruntu[y2, :] = self.goruntu[y1, :]
                
                # Görüntüyü günculle
                self.goruntu = aynali_goruntu
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", f"Yatay aynalama uygulandı! (y={y0})")
            except Exception as e:
                messagebox.showerror("Hata", f"Aynalama sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def acisal_aynalama(self):
        if self.goruntu is not None:
            try:
                # Görüntü boyutlarını al
                h, w = self.goruntu.shape[:2]
                
                # Merkez noktası ve açıyı al
                x0 = int(self.x_ayna_entry.get()) if self.x_ayna_entry.get() else w // 2
                y0 = int(self.y_ayna_entry.get()) if self.y_ayna_entry.get() else h // 2
                theta = np.radians(float(self.aci_entry.get()))
                
                # Yeni görüntü oluştur
                aynali_goruntu = np.zeros_like(self.goruntu)
                
                # Açısal aynalama işlemi
                for y1 in range(h):
                    for x1 in range(w):
                        delta = (x1 - x0) * np.sin(theta) - (y1 - y0) * np.cos(theta)
                        
                        x2 = int(x1 + 2 * delta * (-np.sin(theta)))
                        y2 = int(y1 + 2 * delta * (np.cos(theta)))
                        
                        if 0 <= x2 < w and 0 <= y2 < h:
                            aynali_goruntu[y2, x2] = self.goruntu[y1, x1]
                
                # Görüntüyü günculle
                self.goruntu = aynali_goruntu
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", f"Açısal aynalama uygulandı! (x={x0}, y={y0}, açı={theta}°)")
            except Exception as e:
                messagebox.showerror("Hata", f"Aynalama sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def x_egme_uygula(self):
        if self.goruntu is not None:
            try:
                # Eğme katsayısını al
                sh_x = float(self.shx_entry.get())
                
                # Görüntü boyutlarını al
                h, w = self.goruntu.shape[:2]
                
                # Shearing dönüşüm matrisi
                S = np.float32([[1, sh_x, 0], [0, 1, 0]])
                
                # Yeni genişlik hesaplama
                new_w = w + int(abs(sh_x * h))
                
                # Shearing işlemi
                self.goruntu = cv2.warpAffine(self.goruntu, S, (new_w, h))
                
                # Görüntüyü günculle
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", f"X ekseni üzerinde eğme uygulandı! (katsayı={sh_x})")
            except Exception as e:
                messagebox.showerror("Hata", f"Eğme işlemi sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def y_egme_uygula(self):
        if self.goruntu is not None:
            try:
                # Eğme katsayısını al
                sh_y = float(self.shy_entry.get())
                
                # Görüntü boyutlarını al
                h, w = self.goruntu.shape[:2]
                
                # Shearing dönüşüm matrisi
                S = np.float32([[1, 0, 0], [sh_y, 1, 0]])
                
                # Yeni yükseklik hesaplama
                new_h = h + int(abs(sh_y * w))
                
                # Shearing işlemi
                self.goruntu = cv2.warpAffine(self.goruntu, S, (w, new_h))
                
                # Görüntüyü günculle
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", f"Y ekseni üzerinde eğme uygulandı! (katsayı={sh_y})")
            except Exception as e:
                messagebox.showerror("Hata", f"Eğme işlemi sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def manuel_x_egme_uygula(self):
        if self.goruntu is not None:
            try:
                # Eğme katsayısını al
                sh_x = float(self.shx_entry.get())
                
                # Görüntü boyutlarını al
                h, w = self.goruntu.shape[:2]
                
                # Yeni genişlik hesaplama
                new_w = w + int(abs(sh_x * h))
                
                # Yeni görüntü oluştur
                egik_goruntu = np.zeros((h, new_w, 3), dtype=np.uint8)
                
                # Manuel eğme işlemi
                for y in range(h):
                    for x in range(w):
                        x2 = int(x + sh_x * y)  # X koordinatını kaydırma
                        if 0 <= x2 < new_w:
                            egik_goruntu[y, x2] = self.goruntu[y, x]
                
                # Görüntüyü günculle
                self.goruntu = egik_goruntu
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", f"Manuel X ekseni üzerinde eğme uygulandı! (katsayı={sh_x})")
            except Exception as e:
                messagebox.showerror("Hata", f"Eğme işlemi sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def manuel_y_egme_uygula(self):
        if self.goruntu is not None:
            try:
                # Eğme katsayısını al
                sh_y = float(self.shy_entry.get())
                
                # Görüntü boyutlarını al
                h, w = self.goruntu.shape[:2]
                
                # Yeni yükseklik hesaplama
                new_h = h + int(abs(sh_y * w))
                
                # Yeni görüntü oluştur
                egik_goruntu = np.zeros((new_h, w, 3), dtype=np.uint8)
                
                # Manuel eğme işlemi
                for y in range(h):
                    for x in range(w):
                        y2 = int(y + sh_y * x)  # Y koordinatını kaydırma
                        if 0 <= y2 < new_h:
                            egik_goruntu[y2, x] = self.goruntu[y, x]
                
                # Görüntüyü günculle
                self.goruntu = egik_goruntu
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", f"Manuel Y ekseni üzerinde eğme uygulandı! (katsayı={sh_y})")
            except Exception as e:
                messagebox.showerror("Hata", f"Eğme işlemi sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def piksel_buyut(self):
        if self.goruntu is not None:
            try:
                # Ölçek faktörünü al
                scale_factor = float(self.olcek_entry.get())
                if scale_factor <= 1:
                    raise ValueError("Büyütme için ölçek faktörü 1'den büyük olmalıdır!")
                
                # Görüntü boyutlarını al
                h, w = self.goruntu.shape[:2]
                
                # Yeni boyutları hesapla
                new_h, new_w = int(h * scale_factor), int(w * scale_factor)
                
                # Yeni görüntü oluştur
                zoomed_image = np.zeros((new_h, new_w, 3), dtype=np.uint8)
                
                # Piksel değiştirme ile büyütme (5_1.py'den alındı)
                for y in range(h):
                    for x in range(w):
                        zoomed_image[y * int(scale_factor): (y + 1) * int(scale_factor),
                                   x * int(scale_factor): (x + 1) * int(scale_factor)] = self.goruntu[y, x]
                
                # Görüntüyü günculle
                self.goruntu = zoomed_image
                
                # Bilgi etiketini günculle
                boyut_bilgisi = f"Görüntü boyutları: {new_h}x{new_w}, Piksel Değiştirme ile Büyütme: {scale_factor}x"
                self.bilgi_label.config(text=boyut_bilgisi)
                
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", f"Görüntü piksel değiştirme ile {scale_factor}x büyütüldü!")
            except Exception as e:
                messagebox.showerror("Hata", f"Ölçekleme sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def piksel_kucult(self):
        if self.goruntu is not None:
            try:
                # Ölçek faktörünü al
                scale_factor = float(self.olcek_entry.get())
                if scale_factor >= 1:
                    raise ValueError("Küçültme için ölçek faktörü 1'den küçük olmalıdır!")
                
                # Görüntü boyutlarını al
                h, w = self.goruntu.shape[:2]
                
                # Yeni boyutları hesapla (4_1.py'den alındı)
                new_h, new_w = int(h * scale_factor), int(w * scale_factor)
                
                # Yeni görüntü oluştur
                downsampled_image = np.zeros((new_h, new_w, 3), dtype=np.uint8)
                
                # Piksel değiştirme ile küçültme
                for y in range(new_h):
                    for x in range(new_w):
                        downsampled_image[y, x] = self.goruntu[int(y / scale_factor), int(x / scale_factor)]
                
                # Görüntüyü günculle
                self.goruntu = downsampled_image
                
                # Bilgi etiketini günculle
                boyut_bilgisi = f"Görüntü boyutları: {new_h}x{new_w}, Piksel Değiştirme ile Küçültme: {scale_factor}x"
                self.bilgi_label.config(text=boyut_bilgisi)
                
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", f"Görüntü piksel değiştirme ile {scale_factor}x küçültüldü!")
            except Exception as e:
                messagebox.showerror("Hata", f"Ölçekleme sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def interpolasyon_olcekle(self):
        if self.goruntu is not None:
            try:
                # Ölçek faktörünü al
                scale_factor = float(self.olcek_entry.get())
                if scale_factor <= 0:
                    raise ValueError("Ölçek faktörü pozitif olmalıdır!")
                
                # Görüntü boyutlarını al
                h, w = self.goruntu.shape[:2]
                
                # Yeni boyutları hesapla
                new_h, new_w = int(h * scale_factor), int(w * scale_factor)
                
                # İnterpolasyon yöntemini belirle (4_2.py ve 5_2.py'den alındı)
                interpolasyon = self.interpolasyon_secimi.get()
                if interpolasyon == 'bilinear':
                    method = cv2.INTER_LINEAR
                elif interpolasyon == 'bicubic':
                    method = cv2.INTER_CUBIC
                else:  # lanczos
                    method = cv2.INTER_LANCZOS4
                
                # Görüntüyü yeniden boyutlandır
                self.goruntu = cv2.resize(self.goruntu, (new_w, new_h), interpolation=method)
                
                # Bilgi etiketini günculle
                islem = "büyütüldü" if scale_factor > 1 else "küçültüldü"
                boyut_bilgisi = f"Görüntü boyutları: {new_h}x{new_w}, {interpolasyon.capitalize()} interpolasyon ile {islem}: {scale_factor}x"
                self.bilgi_label.config(text=boyut_bilgisi)
                
                # Görüntüyü günculle
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", f"Görüntü {interpolasyon} interpolasyon ile {scale_factor}x {islem}!")
            except Exception as e:
                messagebox.showerror("Hata", f"Ölçekleme sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def goruntu_dondur(self):
        if self.goruntu is not None:
            try:
                # Döndürme açısını al
                angle = float(self.aci_dondurme_entry.get())
                
                # Görüntü boyutlarını al
                h, w = self.goruntu.shape[:2]
                
                # Merkez noktasını hesapla
                center = (w // 2, h // 2)
                
                # Döndürme matrisini oluştur
                rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                
                # İnterpolasyon yöntemini belirle
                interpolasyon = self.dondurme_interpolasyon.get()
                if interpolasyon == 'nearest':
                    method = cv2.INTER_NEAREST
                elif interpolasyon == 'bilinear':
                    method = cv2.INTER_LINEAR
                elif interpolasyon == 'bicubic':
                    method = cv2.INTER_CUBIC
                else:  # lanczos
                    method = cv2.INTER_LANCZOS4
                
                # Görüntüyü döndür
                self.goruntu = cv2.warpAffine(self.goruntu, rotation_matrix, (w, h), flags=method)
                
                # Bilgi etiketini günculle
                boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Döndürme: {angle}°, Yöntem: {interpolasyon}"
                self.bilgi_label.config(text=boyut_bilgisi)
                
                # Görüntüyü göster
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", f"Görüntü {angle}° döndürüldü! (Yöntem: {interpolasyon})")
            except Exception as e:
                messagebox.showerror("Hata", f"Döndürme işlemi sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def goruntu_kirp(self):
        if self.goruntu is not None:
            try:
                # Kırpma koordinatlarını al
                baslangic_x = int(self.baslangic_x_entry.get())
                bitis_x = int(self.bitis_x_entry.get())
                baslangic_y = int(self.baslangic_y_entry.get())
                bitis_y = int(self.bitis_y_entry.get())
                
                # Görüntü boyutlarını al
                h, w = self.goruntu.shape[:2]
                
                # Koordinatların geçerliliğini kontrol et
                if not (0 <= baslangic_x < bitis_x <= w and 0 <= baslangic_y < bitis_y <= h):
                    messagebox.showerror("Hata", "Geçersiz kırpma koordinatları!")
                    return
                
                # Görüntüyü kırp
                self.goruntu = self.goruntu[baslangic_y:bitis_y, baslangic_x:bitis_x]
                
                # Bilgi etiketini günculle
                yeni_h, yeni_w = self.goruntu.shape[:2]
                boyut_bilgisi = f"Görüntü boyutları: {yeni_h}x{yeni_w}, Kırpma: ({baslangic_x},{baslangic_y}) - ({bitis_x},{bitis_y})"
                self.bilgi_label.config(text=boyut_bilgisi)
                
                # Görüntüyü göster
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", "Görüntü kırpıldı!")
            except ValueError:
                messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
            except Exception as e:
                messagebox.showerror("Hata", f"Kırpma işlemi sırasında bir hata oluştu:\n{str(e)}")
        else:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
    
    def baslat(self):
        # Frame'in boyutunu günculle ve scroll bölgesini ayarla
        def configure_scroll_region(event):
            self.canvas_container.configure(scrollregion=self.canvas_container.bbox('all'))
        
        # Frame boyutu değiştiğinde scroll bölgesini günculle
        self.ana_frame.bind('<Configure>', configure_scroll_region)
        
        # Mouse wheel ile scroll yapabilme
        def _on_mousewheel(event):
            self.canvas_container.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas_container.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Pencere yeniden boyutlandırıldığında içerikleri yeniden düzenle
        def on_resize(event):
            # Yatay kaydırmayı devre dışı bırakmak için, canvas_container genişliğini pencere genişliğine ayarla
            width = event.width
            height = event.height
            self.canvas_container.configure(width=width, height=height)
            
        self.pencere.bind("<Configure>", on_resize)
        
        self.pencere.mainloop()

    # Perspektif düzeltme için kullanılacak metodlar
    def perspektif_duzeltme(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
            
        if not self.perspektif_duzeltme_aktif:
            # Perspektif düzeltmeyi başlat
            self.perspektif_duzeltme_aktif = True
            self.perspektif_noktalar = []
            self.perspektif_buton.config(text="Perspektif İptal")
            
            # Kullanıcıya talimat ver
            messagebox.showinfo("Perspektif Düzeltme", 
                                "Lütfen görüntü üzerinde düzeltmek istediğiniz dörtgenin 4 köşesini sırayla seçin:\n" +
                                "1. Sol üst\n2. Sağ üst\n3. Sol alt\n4. Sağ alt")
        else:
            # Perspektif düzeltmeyi iptal et
            self.perspektif_duzeltme_aktif = False
            self.perspektif_noktalar = []
            self.perspektif_buton.config(text="Perspektif Düzeltme")
    
    def canvas_click(self, event):
        if not self.perspektif_duzeltme_aktif or self.goruntu is None:
            return
            
        # Canvas koordinatlarını görüntü koordinatlarına dönüştür
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_height, img_width = self.goruntu.shape[:2]
        
        # Canvas içindeki görüntünün merkezden başladığını varsayalım
        x_offset = (canvas_width - img_width) // 2
        y_offset = (canvas_height - img_height) // 2
        
        # Tıklanan noktanın görüntü üzerindeki koordinatlarını hesapla
        x = event.x - x_offset
        y = event.y - y_offset
        
        # Görüntü sınırları içinde mi kontrol et
        if 0 <= x < img_width and 0 <= y < img_height:
            self.perspektif_noktalar.append((x, y))
            
            # Noktayı görsel olarak işaretle
            self.canvas.create_oval(event.x-5, event.y-5, event.x+5, event.y+5, 
                                  fill="red", outline="white", width=2, tags="point")
            self.canvas.create_text(event.x+10, event.y-10, text=str(len(self.perspektif_noktalar)), 
                                  fill="red", font=("Arial", 12, "bold"))
            
            # 4 nokta seçildiğinde perspektif düzeltmeyi uygula
            if len(self.perspektif_noktalar) == 4:
                # Kullanıcının seçtiği noktaları numpy array'e çevir
                pts1 = np.float32(self.perspektif_noktalar)
                
                # Düzeltme sonrası boyutu belirle
                rect_width = max(np.linalg.norm(pts1[1] - pts1[0]), np.linalg.norm(pts1[3] - pts1[2]))
                rect_height = max(np.linalg.norm(pts1[2] - pts1[0]), np.linalg.norm(pts1[3] - pts1[1]))
                width, height = int(rect_width), int(rect_height)
                
                # Düzeltme sonrası köşeleri belirle
                pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
                
                # Perspektif dönüşüm matrisini hesapla
                matrix = cv2.getPerspectiveTransform(pts1, pts2)
                
                # Perspektif dönüşümünü uygula
                self.goruntu = cv2.warpPerspective(self.goruntu, matrix, (width, height))
                
                # Perspektif düzeltmeyi devre dışı bırak
                self.perspektif_duzeltme_aktif = False
                self.perspektif_buton.config(text="Perspektif Düzeltme")
                
                # Sonucu göster
                self.goruntu_goster()
                messagebox.showinfo("Başarılı", "Perspektif düzeltme uygulandı!")

    # Median slider değeri değiştiğinde entry'yi güncelle
    def update_median_entry(self, value):
        self.median_boyut_entry.delete(0, tk.END)
        self.median_boyut_entry.insert(0, value)
    
    # Ortalama (Mean) Filtre işlemleri
    def ortalama_filtre_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Filtre boyutlarını al
            x_boyut = int(self.mean_x_entry.get())
            y_boyut = int(self.mean_y_entry.get())
            
            # Boyutların geçerliliğini kontrol et
            if x_boyut < 1 or y_boyut < 1:
                messagebox.showerror("Hata", "Filtre boyutları pozitif tam sayı olmalıdır!")
                return
            
            # Ortalama (Mean) filtresini uygula
            self.goruntu = cv2.blur(self.goruntu, (x_boyut, y_boyut))
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini günculle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Ortalama Filtre: {x_boyut}x{y_boyut}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Ortalama filtre uygulandı! ({x_boyut}x{y_boyut})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")
    
    def hizli_ortalama_filtre(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # 5x5 Ortalama (Mean) filtresini uygula
            self.goruntu = cv2.blur(self.goruntu, (5, 5))
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini günculle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Ortalama Filtre: 5x5"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", "5x5 Ortalama filtre uygulandı!")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")
    
    # Medyan (Median) Filtre işlemleri
    def medyan_filtre_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Filtre boyutunu al
            boyut = int(self.median_boyut_entry.get())
            
            # Boyutun tek sayı olduğunu kontrol et
            if boyut % 2 == 0:
                messagebox.showerror("Hata", "Medyan filtre boyutu tek sayı olmalıdır!")
                return
            
            # Medyan (Median) filtresini uygula
            self.goruntu = cv2.medianBlur(self.goruntu, boyut)
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini günculle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Medyan Filtre: {boyut}x{boyut}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Medyan filtre uygulandı! ({boyut}x{boyut})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")
    
    def hizli_medyan_filtre(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # 5x5 Medyan (Median) filtresini uygula
            self.goruntu = cv2.medianBlur(self.goruntu, 5)
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini günculle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Medyan Filtre: 5x5"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", "5x5 Medyan filtre uygulandı!")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")
            
    def konservatif_filtreleme(self, image):
        """Konservatif yumuşatma algoritması - 4-konservatif_yumusatma.py'den alındı"""
        filtered_image = image.copy()
        shape = image.shape
        
        if len(shape) == 2:  # Gri tonlamalı görüntü
            rows, cols = shape
            channels = 1
        else:  # Renkli görüntü
            rows, cols, channels = shape

        for i in range(1, rows-1):
            for j in range(1, cols-1):
                if channels == 1:  # Gri tonlamalı görüntü
                    region = image[i-1:i+2, j-1:j+2]
                    min_val = np.min(region)
                    max_val = np.max(region)
                    if image[i, j] < min_val:
                        filtered_image[i, j] = min_val
                    elif image[i, j] > max_val:
                        filtered_image[i, j] = max_val
                else:  # Renkli görüntü (BGR)
                    for c in range(channels):
                        region = image[i-1:i+2, j-1:j+2, c]
                        min_val = np.min(region)
                        max_val = np.max(region)
                        if image[i, j, c] < min_val:
                            filtered_image[i, j, c] = min_val
                        elif image[i, j, c] > max_val:
                            filtered_image[i, j, c] = max_val

        return filtered_image

    def konservatif_filtre_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Konservatif filtreleme uygula
            self.goruntu = self.konservatif_filtreleme(self.goruntu)
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Konservatif Filtre Uygulandı"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", "Konservatif filtreleme başarıyla uygulandı!")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")
            
    def hizli_konservatif_filtre(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Konservatif filtreleme uygula
            self.goruntu = self.konservatif_filtreleme(self.goruntu)
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Konservatif Filtre Uygulandı"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", "Konservatif filtreleme başarıyla uygulandı!")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")
            
    def crimmins_speckle_removal(self, image):
        """Crimmins Speckle giderme algoritması - 5-crimmins_speckle.py'den alındı"""
        filtered_image = image.copy()
        shape = image.shape
        
        if len(shape) == 2:  # Gri tonlamalı görüntü
            rows, cols = shape
            channels = 1
        else:  # Renkli görüntü
            rows, cols, channels = shape

        for i in range(1, rows-1):
            for j in range(1, cols-1):
                if channels == 1:  # Gri tonlamalı görüntü
                    center_pixel = image[i, j]
                    neighbors = [image[i-1, j], image[i+1, j], image[i, j-1], image[i, j+1]]
                    avg_neighbors = np.mean(neighbors)

                    if center_pixel > avg_neighbors + 20:
                        filtered_image[i, j] = avg_neighbors
                    elif center_pixel < avg_neighbors - 20:
                        filtered_image[i, j] = avg_neighbors
                else:  # Renkli görüntü (BGR)
                    for c in range(channels):
                        center_pixel = image[i, j, c]
                        neighbors = [image[i-1, j, c], image[i+1, j, c], image[i, j-1, c], image[i, j+1, c]]
                        avg_neighbors = np.mean(neighbors)

                        if center_pixel > avg_neighbors + 20:
                            filtered_image[i, j, c] = avg_neighbors
                        elif center_pixel < avg_neighbors - 20:
                            filtered_image[i, j, c] = avg_neighbors

        return filtered_image

    def crimmins_filtre_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Crimmins Speckle giderme algoritmasını uygula
            self.goruntu = self.crimmins_speckle_removal(self.goruntu)
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Crimmins Speckle Giderme Uygulandı"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", "Crimmins Speckle giderme başarıyla uygulandı!")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")
            
    def hizli_crimmins_filtre(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Crimmins Speckle giderme algoritmasını uygula
            self.goruntu = self.crimmins_speckle_removal(self.goruntu)
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Crimmins Speckle Giderme Uygulandı"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", "Crimmins Speckle giderme başarıyla uygulandı!")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")
    
    def fft_lowpass_filtre(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Görüntüyü gri tonlamalı hale getir
            if len(self.goruntu.shape) > 2:
                gray_image = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                gray_image = self.goruntu.copy()
                
            # Fourier dönüşümü uygula
            f_transform = np.fft.fft2(gray_image)
            f_transform_shifted = np.fft.fftshift(f_transform)  # Düşük frekansları merkeze getir
            
            # Filtre boyutu
            rows, cols = gray_image.shape
            mask = np.zeros((rows, cols), np.uint8)
            
            # Merkez noktasına yakın düşük frekansları bırak, yüksek frekansları sıfır yap
            r = 30  # Filtrenin kesme çapı
            center = (cols//2, rows//2)
            cv2.circle(mask, center, r, 1, -1)
            
            # Filtreyi uygula
            filtered = f_transform_shifted * mask
            filtered_image = np.fft.ifft2(np.fft.ifftshift(filtered)).real
            
            # Sonucu 0-255 aralığına normalize et
            filtered_image = cv2.normalize(filtered_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = filtered_image
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, FFT Low-Pass Filter Uygulandı (r={r})"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", "FFT Low-Pass Filter başarıyla uygulandı!")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")
    
    def fft_highpass_filtre(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Görüntüyü gri tonlamalı hale getir
            if len(self.goruntu.shape) > 2:
                gray_image = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                gray_image = self.goruntu.copy()
                
            # Fourier dönüşümü uygula
            f_transform = np.fft.fft2(gray_image)
            f_transform_shifted = np.fft.fftshift(f_transform)  # Düşük frekansları merkeze getir
            
            # Filtre boyutu
            rows, cols = gray_image.shape
            
            # High-pass filter maskesi
            mask = np.ones((rows, cols), np.uint8)
            r = 30  # Filtrenin kesme çapı
            center = (cols//2, rows//2)
            cv2.circle(mask, center, r, 0, -1)  # Düşük frekansları sıfırla
            
            # Filtreyi uygula
            filtered = f_transform_shifted * mask
            filtered_image = np.fft.ifft2(np.fft.ifftshift(filtered)).real
            
            # Sonucu 0-255 aralığına normalize et
            filtered_image = cv2.normalize(filtered_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = filtered_image
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, FFT High-Pass Filter Uygulandı (r={r})"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", "FFT High-Pass Filter başarıyla uygulandı!")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")

    # Gauss Filtresi işlemleri
    def update_gauss_sigma_entry(self, value):
        self.gauss_sigma_entry.delete(0, tk.END)
        self.gauss_sigma_entry.insert(0, value)

    def gauss_filtre_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Filtre boyutunu ve sigma değerini al
            boyut = int(self.gauss_boyut_var.get())
            sigma = float(self.gauss_sigma_entry.get())
            
            # Boyutun geçerliliğini kontrol et
            if boyut < 1 or boyut % 2 == 0:
                messagebox.showerror("Hata", "Gauss filtre boyutu pozitif tek sayı olmalıdır!")
                return
            
            # Sigma değerinin geçerliliğini kontrol et
            if sigma <= 0:
                messagebox.showerror("Hata", "Sigma değeri pozitif olmalıdır!")
                return
            
            # Gauss filtresini uygula
            self.goruntu = cv2.GaussianBlur(self.goruntu, (boyut, boyut), sigma)
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini günculle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Gauss Filtre: {boyut}x{boyut}, σ={sigma:.1f}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Gauss filtre uygulandı! ({boyut}x{boyut}, σ={sigma:.1f})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")

    def hizli_gauss_filtre(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # 5x5 Gauss filtresini uygula, sigma=1.0
            self.goruntu = cv2.GaussianBlur(self.goruntu, (5, 5), 1.0)
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini günculle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Gauss Filtre: 5x5, σ=1.0"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", "5x5 Gauss filtre uygulandı! (σ=1.0)")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")

    # Band geçiren filtre (Band-Pass Filter) fonksiyonu
    def band_geciren_filtre(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Gri tonlama kontrolü yap
            if len(self.goruntu.shape) > 2:
                # Renkli görüntüyü gri tonlamaya çevir
                img_gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                # Zaten gri tonlamalı
                img_gray = self.goruntu.copy()
            
            # Filtre parametrelerini al
            D1 = int(self.band_d1_entry.get())  # Alt sınır
            D2 = int(self.band_d2_entry.get())  # Üst sınır
            
            # Parametrelerin geçerliliğini kontrol et
            if D1 < 0 or D2 < 0 or D1 >= D2:
                messagebox.showerror("Hata", "Geçerli band değerleri girin! D1 < D2 olmalıdır.")
                return
            
            # Fourier dönüşümünü uygula
            f_transform = np.fft.fft2(img_gray)
            f_transform_shifted = np.fft.fftshift(f_transform)  # Düşük frekansları merkeze al
            
            # Band geçiren filtre maskesi oluştur
            rows, cols = img_gray.shape
            mask = np.zeros((rows, cols), np.uint8)
            center = (cols//2, rows//2)
            
            # Maske oluştur (D1 <= D <= D2 aralığındaki frekansları geçir)
            for u in range(rows):
                for v in range(cols):
                    D = np.sqrt((u - center[1])**2 + (v - center[0])**2)
                    if D1 <= D <= D2:
                        mask[u, v] = 1  # Sadece belirli aralıktaki frekansları geçir
            
            # Filtreyi uygula
            filtered = f_transform_shifted * mask
            filtered_image = np.fft.ifft2(np.fft.ifftshift(filtered)).real
            
            # Sonucu 0-255 aralığına normalize et
            filtered_image = cv2.normalize(filtered_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = filtered_image
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Band Geçiren Filtre: D1={D1}, D2={D2}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Band geçiren filtre uygulandı! (D1={D1}, D2={D2})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")
    
    # Band durduran filtre (Band-Stop Filter) fonksiyonu
    def band_durduran_filtre(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Gri tonlama kontrolü yap
            if len(self.goruntu.shape) > 2:
                # Renkli görüntüyü gri tonlamaya çevir
                img_gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                # Zaten gri tonlamalı
                img_gray = self.goruntu.copy()
            
            # Filtre parametrelerini al
            D1 = int(self.band_d1_entry.get())  # Alt sınır
            D2 = int(self.band_d2_entry.get())  # Üst sınır
            
            # Parametrelerin geçerliliğini kontrol et
            if D1 < 0 or D2 < 0 or D1 >= D2:
                messagebox.showerror("Hata", "Geçerli band değerleri girin! D1 < D2 olmalıdır.")
                return
            
            # Fourier dönüşümünü uygula
            f_transform = np.fft.fft2(img_gray)
            f_transform_shifted = np.fft.fftshift(f_transform)  # Düşük frekansları merkeze al
            
            # Band durduran filtre maskesi oluştur
            rows, cols = img_gray.shape
            mask = np.ones((rows, cols), np.uint8)  # Tüm frekansları geçir başlangıçta
            center = (cols//2, rows//2)
            
            # Maske oluştur (D1 <= D <= D2 aralığındaki frekansları durdur)
            for u in range(rows):
                for v in range(cols):
                    D = np.sqrt((u - center[1])**2 + (v - center[0])**2)
                    if D1 <= D <= D2:
                        mask[u, v] = 0  # Belirli aralıktaki frekansları durdur
            
            # Filtreyi uygula
            filtered = f_transform_shifted * mask
            filtered_image = np.fft.ifft2(np.fft.ifftshift(filtered)).real
            
            # Sonucu 0-255 aralığına normalize et
            filtered_image = cv2.normalize(filtered_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = filtered_image
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Band Durduran Filtre: D1={D1}, D2={D2}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Band durduran filtre uygulandı! (D1={D1}, D2={D2})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")
    


    # Butterworth filtre fonksiyonu
    def butterworth_filter(self, shape, D0, n, highpass=False):
        rows, cols = shape
        mask = np.zeros((rows, cols), np.float32)
        center = (cols//2, rows//2)
        
        for u in range(rows):
            for v in range(cols):
                D = np.sqrt((u - center[1])**2 + (v - center[0])**2)
                H = 1 / (1 + (D/D0)**(2*n)) if not highpass else 1 - (1 / (1 + (D/D0)**(2*n)))
                mask[u, v] = H
        
        return mask
    
    # Butterworth alçak geçiren filtre (Low-Pass Filter)
    def butterworth_alcak_geciren_filtre(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Filtre parametrelerini al
            D0 = int(self.butterworth_d0_entry.get())  # Kesim frekansı
            n = int(self.butterworth_n_entry.get())  # Filtre derecesi
            
            # Parametrelerin geçerliliğini kontrol et
            if D0 < 1 or n < 1:
                messagebox.showerror("Hata", "D0 ve n değerleri en az 1 olmalıdır.")
                return
            
            # Gri tonlama kontrolü yap
            if len(self.goruntu.shape) > 2:
                # Renkli görüntüyü gri tonlamaya çevir
                img_gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                # Zaten gri tonlamalı
                img_gray = self.goruntu.copy()
            
            # Fourier dönüşümünü uygula
            f_transform = np.fft.fft2(img_gray)
            f_transform_shifted = np.fft.fftshift(f_transform)  # Düşük frekansları merkeze al
            
            # Butterworth alçak geçiren filtre maskesi oluştur
            mask = self.butterworth_filter(img_gray.shape, D0, n, highpass=False)
            
            # Filtreyi uygula
            filtered = f_transform_shifted * mask
            filtered_image = np.fft.ifft2(np.fft.ifftshift(filtered)).real
            
            # Sonucu 0-255 aralığına normalize et
            filtered_image = cv2.normalize(filtered_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = filtered_image
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Butterworth Alçak Geçiren Filtre: D0={D0}, n={n}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Butterworth alçak geçiren filtre uygulandı! (D0={D0}, n={n})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")
    
    # Butterworth yüksek geçiren filtre (High-Pass Filter)
    def butterworth_yuksek_geciren_filtre(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Filtre parametrelerini al
            D0 = int(self.butterworth_d0_entry.get())  # Kesim frekansı
            n = int(self.butterworth_n_entry.get())  # Filtre derecesi
            
            # Parametrelerin geçerliliğini kontrol et
            if D0 < 1 or n < 1:
                messagebox.showerror("Hata", "D0 ve n değerleri en az 1 olmalıdır.")
                return
            
            # Gri tonlama kontrolü yap
            if len(self.goruntu.shape) > 2:
                # Renkli görüntüyü gri tonlamaya çevir
                img_gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                # Zaten gri tonlamalı
                img_gray = self.goruntu.copy()
            
            # Fourier dönüşümünü uygula
            f_transform = np.fft.fft2(img_gray)
            f_transform_shifted = np.fft.fftshift(f_transform)  # Düşük frekansları merkeze al
            
            # Butterworth yüksek geçiren filtre maskesi oluştur
            mask = self.butterworth_filter(img_gray.shape, D0, n, highpass=True)
            
            # Filtreyi uygula
            filtered = f_transform_shifted * mask
            filtered_image = np.fft.ifft2(np.fft.ifftshift(filtered)).real
            
            # Sonucu 0-255 aralığına normalize et
            filtered_image = cv2.normalize(filtered_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = filtered_image
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Butterworth Yüksek Geçiren Filtre: D0={D0}, n={n}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Butterworth yüksek geçiren filtre uygulandı! (D0={D0}, n={n})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")

    # Gaussian filtre fonksiyonu
    def gaussian_filter(self, shape, D0, highpass=False):
        rows, cols = shape
        mask = np.zeros((rows, cols), np.float32)
        center = (cols//2, rows//2)
        
        for u in range(rows):
            for v in range(cols):
                D = np.sqrt((u - center[1])**2 + (v - center[0])**2)
                H = np.exp(-(D**2) / (2 * (D0**2))) if not highpass else 1 - np.exp(-(D**2) / (2 * (D0**2)))
                mask[u, v] = H
        
        return mask
    
    # Gaussian alçak geçiren filtre (Low-Pass Filter)
    def gaussian_alcak_geciren_filtre(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Filtre parametrelerini al
            D0 = int(self.gaussian_d0_entry.get())  # Standart sapma
            
            # Parametrelerin geçerliliğini kontrol et
            if D0 < 1:
                messagebox.showerror("Hata", "D0 değeri en az 1 olmalıdır.")
                return
            
            # Gri tonlama kontrolü yap
            if len(self.goruntu.shape) > 2:
                # Renkli görüntüyü gri tonlamaya çevir
                img_gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                # Zaten gri tonlamalı
                img_gray = self.goruntu.copy()
            
            # Fourier dönüşümünü uygula
            f_transform = np.fft.fft2(img_gray)
            f_transform_shifted = np.fft.fftshift(f_transform)  # Düşük frekansları merkeze al
            
            # Gaussian alçak geçiren filtre maskesi oluştur
            mask = self.gaussian_filter(img_gray.shape, D0, highpass=False)
            
            # Filtreyi uygula
            filtered = f_transform_shifted * mask
            filtered_image = np.fft.ifft2(np.fft.ifftshift(filtered)).real
            
            # Sonucu 0-255 aralığına normalize et
            filtered_image = cv2.normalize(filtered_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = filtered_image
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Gaussian Alçak Geçiren Filtre: D0={D0}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Gaussian alçak geçiren filtre uygulandı! (D0={D0})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")
    
    # Gaussian yüksek geçiren filtre (High-Pass Filter)
    def gaussian_yuksek_geciren_filtre(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Filtre parametrelerini al
            D0 = int(self.gaussian_d0_entry.get())  # Standart sapma
            
            # Parametrelerin geçerliliğini kontrol et
            if D0 < 1:
                messagebox.showerror("Hata", "D0 değeri en az 1 olmalıdır.")
                return
            
            # Gri tonlama kontrolü yap
            if len(self.goruntu.shape) > 2:
                # Renkli görüntüyü gri tonlamaya çevir
                img_gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                # Zaten gri tonlamalı
                img_gray = self.goruntu.copy()
            
            # Fourier dönüşümünü uygula
            f_transform = np.fft.fft2(img_gray)
            f_transform_shifted = np.fft.fftshift(f_transform)  # Düşük frekansları merkeze al
            
            # Gaussian yüksek geçiren filtre maskesi oluştur
            mask = self.gaussian_filter(img_gray.shape, D0, highpass=True)
            
            # Filtreyi uygula
            filtered = f_transform_shifted * mask
            filtered_image = np.fft.ifft2(np.fft.ifftshift(filtered)).real
            
            # Sonucu 0-255 aralığına normalize et
            filtered_image = cv2.normalize(filtered_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = filtered_image
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Gaussian Yüksek Geçiren Filtre: D0={D0}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Gaussian yüksek geçiren filtre uygulandı! (D0={D0})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")

    # Homomorfik filtre fonksiyonu
    def homomorfik_filtre_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Filtre parametrelerini al
            d0 = int(self.homomorfik_d0_entry.get())  # Kesim frekansı
            h_l = float(self.homomorfik_hl_entry.get())  # Alçak frekans kazancı
            h_h = float(self.homomorfik_hh_entry.get())  # Yüksek frekans kazancı
            c = float(self.homomorfik_c_entry.get())  # Keskinlik kontrolü
            
            # Parametrelerin geçerliliğini kontrol et
            if d0 < 1 or h_l < 0 or h_h < 0 or c < 0:
                messagebox.showerror("Hata", "Tüm değerler pozitif olmalıdır!")
                return
            
            # Görüntüyü gri tona çevir
            if len(self.goruntu.shape) > 2:
                gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                gray = self.goruntu.copy()
            
            # Logaritmik dönüşüm
            log_image = np.log1p(np.float32(gray))
            
            # Fourier dönüşümü
            f_transform = np.fft.fft2(log_image)
            f_transform_shifted = np.fft.fftshift(f_transform)
            
            # Homomorfik filtre oluştur
            rows, cols = gray.shape
            center = (cols//2, rows//2)
            H = np.zeros((rows, cols), np.float32)
            
            for u in range(rows):
                for v in range(cols):
                    D = np.sqrt((u - center[1])**2 + (v - center[0])**2)
                    H[u, v] = (h_h - h_l) * (1 - np.exp(-c * (D**2 / d0**2))) + h_l
            
            # Filtreyi uygula
            filtered = f_transform_shifted * H
            filtered_image = np.fft.ifft2(np.fft.ifftshift(filtered)).real
            
            # Üssel dönüşüm
            final_image = np.expm1(filtered_image)
            final_image = np.clip(final_image, 0, 255)
            
            # Sonucu görüntüye aktar
            filtered_result = np.uint8(final_image)
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(filtered_result, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = filtered_result
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Homomorfik Filtre: D0={d0}, H_L={h_l}, H_H={h_h}, C={c}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Homomorfik filtre uygulandı! (D0={d0}, H_L={h_l}, H_H={h_h}, C={c})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")

    # Sobel filtresi fonksiyonu
    def sobel_filtresi_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Filtre parametrelerini al
            ksize = int(self.sobel_ksize_var.get())  # Kernel boyutu
            
            # Seçilen derinliği belirle
            depth_str = self.sobel_depth_var.get()
            if depth_str == "CV_8U":
                depth = cv2.CV_8U
            elif depth_str == "CV_32F":
                depth = cv2.CV_32F
            else:  # CV_64F
                depth = cv2.CV_64F
            
            # Yönleri kontrol et
            x_direction = self.sobel_x_var.get()
            y_direction = self.sobel_y_var.get()
            
            if not x_direction and not y_direction:
                messagebox.showerror("Hata", "En az bir yön seçmelisiniz (X veya Y)!")
                return
            
            # Görüntüyü gri tona çevir
            if len(self.goruntu.shape) > 2:
                gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                gray = self.goruntu.copy()
            
            # Sobel filtresini uygula
            if x_direction:
                sobel_x = cv2.Sobel(gray, depth, 1, 0, ksize=ksize)
            else:
                sobel_x = np.zeros_like(gray, dtype=np.float64)
                
            if y_direction:
                sobel_y = cv2.Sobel(gray, depth, 0, 1, ksize=ksize)
            else:
                sobel_y = np.zeros_like(gray, dtype=np.float64)
            
            # Kenar büyüklüğünü hesapla (Gradient Magnitude)
            sobel_magnitude = cv2.magnitude(sobel_x, sobel_y)
            
            # Eğer derinlik CV_8U değilse, görüntüde göstermek için dönüştür
            if depth != cv2.CV_8U:
                sobel_magnitude = cv2.normalize(sobel_magnitude, None, 0, 255, cv2.NORM_MINMAX)
            
            # Sonucu görüntüye aktar
            result = np.uint8(sobel_magnitude)
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = result
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            yonler = ""
            if x_direction:
                yonler += "X "
            if y_direction:
                yonler += "Y"
                
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Sobel Filtresi: ksize={ksize}, depth={depth_str}, yön={yonler}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Sobel filtresi uygulandı! (ksize={ksize}, depth={depth_str}, yön={yonler})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli parametreler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")

    # Prewitt filtresi fonksiyonu
    def prewitt_filtresi_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Seçilen derinliği belirle
            depth_str = self.prewitt_depth_var.get()
            if depth_str == "CV_8U":
                depth = cv2.CV_8U
            elif depth_str == "CV_32F":
                depth = cv2.CV_32F
            else:  # CV_64F
                depth = cv2.CV_64F
            
            # Yönleri kontrol et
            x_direction = self.prewitt_x_var.get()
            y_direction = self.prewitt_y_var.get()
            
            if not x_direction and not y_direction:
                messagebox.showerror("Hata", "En az bir yön seçmelisiniz (X veya Y)!")
                return
            
            # Görüntüyü gri tona çevir
            if len(self.goruntu.shape) > 2:
                gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                gray = self.goruntu.copy()
            
            # Prewitt kernelleri tanımla
            kernel_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
            kernel_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])
            
            # Prewitt filtresini uygula
            if x_direction:
                # X yönü için filtre uygula
                prewitt_x = cv2.filter2D(gray, depth, kernel_x)
            else:
                prewitt_x = np.zeros_like(gray, dtype=np.float64)
                
            if y_direction:
                # Y yönü için filtre uygula
                prewitt_y = cv2.filter2D(gray, depth, kernel_y)
            else:
                prewitt_y = np.zeros_like(gray, dtype=np.float64)
            
            # Kenar büyüklüğünü hesapla (Gradient Magnitude)
            prewitt_magnitude = cv2.magnitude(prewitt_x.astype(np.float32), prewitt_y.astype(np.float32))
            
            # Eğer derinlik CV_8U değilse, görüntüde göstermek için dönüştür
            if depth != cv2.CV_8U:
                prewitt_magnitude = cv2.normalize(prewitt_magnitude, None, 0, 255, cv2.NORM_MINMAX)
            
            # Sonucu görüntüye aktar
            result = np.uint8(prewitt_magnitude)
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = result
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            yonler = ""
            if x_direction:
                yonler += "X "
            if y_direction:
                yonler += "Y"
                
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Prewitt Filtresi: depth={depth_str}, yön={yonler}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Prewitt filtresi uygulandı! (depth={depth_str}, yön={yonler})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli parametreler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")

    # Roberts Cross filtresi fonksiyonu
    def roberts_filtresi_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Seçilen derinliği belirle
            depth_str = self.roberts_depth_var.get()
            if depth_str == "CV_8U":
                depth = cv2.CV_8U
            elif depth_str == "CV_32F":
                depth = cv2.CV_32F
            else:  # CV_64F
                depth = cv2.CV_64F
            
            # Yönleri kontrol et
            x_direction = self.roberts_x_var.get()
            y_direction = self.roberts_y_var.get()
            
            if not x_direction and not y_direction:
                messagebox.showerror("Hata", "En az bir yön seçmelisiniz (X veya Y)!")
                return
            
            # Görüntüyü gri tona çevir
            if len(self.goruntu.shape) > 2:
                gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                gray = self.goruntu.copy()
            
            # Roberts Cross kernelleri tanımla
            kernel_x = np.array([[1, 0], [0, -1]], dtype=np.float32)
            kernel_y = np.array([[0, 1], [-1, 0]], dtype=np.float32)
            
            # Roberts Cross filtresini uygula
            if x_direction:
                # X yönü için filtre uygula
                roberts_x_result = cv2.filter2D(gray, depth, kernel_x)
            else:
                roberts_x_result = np.zeros_like(gray, dtype=np.float32)
                
            if y_direction:
                # Y yönü için filtre uygula
                roberts_y_result = cv2.filter2D(gray, depth, kernel_y)
            else:
                roberts_y_result = np.zeros_like(gray, dtype=np.float32)
            
            # Kenar büyüklüğünü hesapla (Gradient Magnitude)
            roberts_magnitude = cv2.magnitude(roberts_x_result.astype(np.float32), roberts_y_result.astype(np.float32))
            
            # Roberts Cross genellikle daha ince kenarlar verir, bu yüzden görüntüyü biraz iyileştirelim
            # Gamma düzeltmesi uygula - kenarları biraz daha belirginleştirir
            gamma = 0.7
            roberts_magnitude = np.power(roberts_magnitude, gamma)
            
            # Eğer derinlik CV_8U değilse, görüntüde göstermek için dönüştür
            if depth != cv2.CV_8U:
                roberts_magnitude = cv2.normalize(roberts_magnitude, None, 0, 255, cv2.NORM_MINMAX)
            
            # Sonucu görüntüye aktar
            result = np.uint8(roberts_magnitude)
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = result
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            yonler = ""
            if x_direction:
                yonler += "X "
            if y_direction:
                yonler += "Y"
                
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Roberts Cross Filtresi: depth={depth_str}, yön={yonler}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Roberts Cross filtresi uygulandı! (depth={depth_str}, yön={yonler})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli parametreler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")

    # Compass filtresi fonksiyonu
    def compass_filtresi_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Seçilen derinliği belirle
            depth_str = self.compass_depth_var.get()
            if depth_str == "CV_8U":
                depth = cv2.CV_8U
            elif depth_str == "CV_32F":
                depth = cv2.CV_32F
            else:  # CV_64F
                depth = cv2.CV_64F
            
            # Seçilen yönleri kontrol et
            east = self.compass_east_var.get()
            west = self.compass_west_var.get()
            north = self.compass_north_var.get()
            south = self.compass_south_var.get()
            
            if not (east or west or north or south):
                messagebox.showerror("Hata", "En az bir yön seçmelisiniz!")
                return
            
            # Görüntüyü gri tona çevir
            if len(self.goruntu.shape) > 2:
                gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                gray = self.goruntu.copy()
            
            # Compass filtre matrislerini tanımla
            compass_kernels = []
            if east:
                compass_kernels.append(np.array([[-1,-1,-1], [1,1,1], [1,1,1]]))  # Doğu (E)
            if west:
                compass_kernels.append(np.array([[1,1,1], [1,1,1], [-1,-1,-1]]))  # Batı (W)
            if north:
                compass_kernels.append(np.array([[-1,1,1], [-1,1,1], [-1,1,1]]))  # Kuzey (N)
            if south:
                compass_kernels.append(np.array([[1,1,-1], [1,1,-1], [1,1,-1]]))  # Güney (S)
            
            # Tüm seçilen yönlerde filtreleri uygula ve maksimum değeri al
            compass_edges = np.zeros_like(gray, dtype=np.float32)
            for kernel in compass_kernels:
                # Belirtilen derinlikte filtre uygula
                edge = cv2.filter2D(gray, depth, kernel)
                # Maksimum değerleri al
                compass_edges = np.maximum(compass_edges, edge)
            
            # Eğer derinlik CV_8U değilse, görüntüde göstermek için dönüştür
            if depth != cv2.CV_8U:
                compass_edges = cv2.normalize(compass_edges, None, 0, 255, cv2.NORM_MINMAX)
            
            # Sonucu görüntüye aktar
            result = np.uint8(compass_edges)
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = result
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            yonler = []
            if east:
                yonler.append("Doğu")
            if west:
                yonler.append("Batı")
            if north:
                yonler.append("Kuzey")
            if south:
                yonler.append("Güney")
            yon_str = ", ".join(yonler)
                
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Compass Filtresi: depth={depth_str}, yönler={yon_str}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Compass filtresi uygulandı! (depth={depth_str}, yönler={yon_str})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli parametreler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")

    # Canny filtresi fonksiyonu
    def canny_filtresi_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Parametreleri al
            low_threshold = int(self.canny_low_threshold_var.get())
            high_threshold = int(self.canny_high_threshold_var.get())
            aperture_size = int(self.canny_aperture_var.get())
            l2gradient = bool(self.canny_l2_var.get())
            
            # Eşik değerlerini kontrol et
            if low_threshold >= high_threshold:
                messagebox.showerror("Hata", "Alt eşik değeri üst eşik değerinden küçük olmalıdır!")
                return
            
            # Görüntüyü gri tona çevir
            if len(self.goruntu.shape) > 2:
                gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                gray = self.goruntu.copy()
            
            # Canny kenar algılama algoritmasını uygula
            canny_edges = cv2.Canny(gray, low_threshold, high_threshold, 
                                   apertureSize=aperture_size, L2gradient=l2gradient)
            
            # Sonucu görüntüye aktar
            result = canny_edges.copy()
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = result
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            l2_text = "Evet" if l2gradient else "Hayır"
                
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Canny Filtresi: alt={low_threshold}, üst={high_threshold}, aperture={aperture_size}, L2gradient={l2_text}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Canny filtresi uygulandı! (alt={low_threshold}, üst={high_threshold})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal parametreler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")

    # Laplace filtresi fonksiyonu
    def laplace_filtresi_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Parametreleri al
            ksize = int(self.laplace_ksize_var.get())
            
            # Seçilen derinliği belirle
            depth_str = self.laplace_depth_var.get()
            if depth_str == "CV_8U":
                depth = cv2.CV_8U
            elif depth_str == "CV_32F":
                depth = cv2.CV_32F
            else:  # CV_64F
                depth = cv2.CV_64F
            
            # Görüntüyü gri tona çevir
            if len(self.goruntu.shape) > 2:
                gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                gray = self.goruntu.copy()
            
            # Laplace filtresini uygula
            laplacian = cv2.Laplacian(gray, depth, ksize=ksize)
            
            # Laplace sonucu negatif değerler içerebileceği için mutlak değeri al
            laplacian_abs = np.abs(laplacian)
            
            # Eğer derinlik CV_8U değilse, görüntüde göstermek için dönüştür
            if depth != cv2.CV_8U:
                laplacian_abs = cv2.normalize(laplacian_abs, None, 0, 255, cv2.NORM_MINMAX)
            
            # Sonucu görüntüye aktar
            result = np.uint8(laplacian_abs)
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = result
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Laplace Filtresi: ksize={ksize}, depth={depth_str}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Laplace filtresi uygulandı! (ksize={ksize}, depth={depth_str})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli parametreler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")

    # Gabor filtresi fonksiyonu
    def gabor_filtresi_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Parametreleri al
            kernel_size = int(self.gabor_ksize_var.get())
            # Tek sayı olmalı
            if kernel_size % 2 == 0:
                kernel_size += 1
                
            sigma = float(self.gabor_sigma_var.get())
            theta_degree = float(self.gabor_theta_var.get())
            # Dereceyi radyana çevir
            theta = theta_degree * np.pi / 180.0
            
            lambd = float(self.gabor_lambda_var.get())  # Lambda kelimesi Python'da rezerve edilmiş olduğu için lambd kullanılıyor
            gamma = float(self.gabor_gamma_var.get())
            psi = float(self.gabor_psi_var.get())
            
            # Seçilen derinliği belirle
            depth_str = self.gabor_depth_var.get()
            if depth_str == "CV_8U":
                depth = cv2.CV_8U
            elif depth_str == "CV_32F":
                depth = cv2.CV_32F
            else:  # CV_64F
                depth = cv2.CV_64F
            
            # Görüntüyü gri tona çevir
            if len(self.goruntu.shape) > 2:
                gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                gray = self.goruntu.copy()
            
            # Gabor kernel oluştur
            gabor_kernel = cv2.getGaborKernel((kernel_size, kernel_size), sigma, theta, lambd, gamma, psi, ktype=depth)
            
            # Gabor filtresini uygula
            gabor_result = cv2.filter2D(gray, depth, gabor_kernel)
            
            # Eğer derinlik CV_8U değilse, görüntüde göstermek için dönüştür
            if depth != cv2.CV_8U:
                gabor_result = cv2.normalize(gabor_result, None, 0, 255, cv2.NORM_MINMAX)
            
            # Sonucu görüntüye aktar
            result = np.uint8(gabor_result)
            
            # Eğer orijinal görüntü renkliyse, filtrelenmiş görüntüyü BGR formatına çevir
            if len(self.goruntu.shape) > 2:
                self.goruntu = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
            else:
                self.goruntu = result
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Gabor Filtresi: ksize={kernel_size}, sigma={sigma}, theta={theta_degree}°, lambda={lambd}, gamma={gamma}, psi={psi}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Gabor filtresi uygulandı! (theta={theta_degree}°, sigma={sigma})")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli parametreler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulama sırasında bir hata oluştu:\n{str(e)}")

    # Hough doğru algılama fonksiyonu
    def hough_dogrulari_algıla(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Parametreleri al
            canny_low = int(self.hough_lines_canny_low_var.get())
            canny_high = int(self.hough_lines_canny_high_var.get())
            rho = float(self.hough_lines_rho_var.get())
            theta_degree = float(self.hough_lines_theta_var.get())
            theta_rad = theta_degree * np.pi / 180.0  # Dereceyi radyana çevir
            threshold = int(self.hough_lines_threshold_var.get())
            
            # Canny kenar tespiti için görüntüyü gri tonlamaya çevir
            if len(self.goruntu.shape) > 2:
                gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                gray = self.goruntu.copy()
            
            # Canny kenar tespiti uygula
            edges = cv2.Canny(gray, canny_low, canny_high)
            
            # Hough Dönüşümü ile doğruları tespit et
            lines = cv2.HoughLines(edges, rho, theta_rad, threshold)
            
            # Orijinal görüntüyü renkliye çevir (eğer gri tonlamadaysa)
            if len(self.goruntu.shape) <= 2:
                output = cv2.cvtColor(self.goruntu, cv2.COLOR_GRAY2BGR)
            else:
                output = self.goruntu.copy()
            
            # Doğruları görüntüye çiz
            if lines is not None:
                for line in lines:
                    rho_val, theta_val = line[0]
                    a = np.cos(theta_val)
                    b = np.sin(theta_val)
                    x0 = a * rho_val
                    y0 = b * rho_val
                    x1 = int(x0 + 1000 * (-b))
                    y1 = int(y0 + 1000 * (a))
                    x2 = int(x0 - 1000 * (-b))
                    y2 = int(y0 - 1000 * (a))
                    cv2.line(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Sonuç görüntüsünü güncelle
            self.goruntu = output
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Tespit edilen doğru sayısını hesapla
            line_count = 0 if lines is None else len(lines)
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Hough Doğru Algılama: {line_count} doğru tespit edildi"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Hough doğru algılama tamamlandı! {line_count} doğru tespit edildi.")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli parametreler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Algılama sırasında bir hata oluştu:\n{str(e)}")
    
    # Genişletme (Dilate) fonksiyonu
    def genisletme_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Parametreleri al
            kernel_size = int(self.dilate_kernel_var.get())
            iterations = int(self.dilate_iter_var.get())
            shape = self.dilate_shape_var.get()
            
            # Kernel şeklini belirle
            if shape == "Kare":
                kernel = np.ones((kernel_size, kernel_size), np.uint8)
            elif shape == "Disk":
                # Disk (dairesel) şekilli kernel oluştur
                radius = kernel_size // 2
                kernel = np.zeros((kernel_size, kernel_size), np.uint8)
                y, x = np.ogrid[-radius:radius+1, -radius:radius+1]
                mask = x**2 + y**2 <= radius**2
                kernel[mask] = 1
            elif shape == "Çapraz":
                # Çapraz şekilli kernel oluştur
                kernel = np.zeros((kernel_size, kernel_size), np.uint8)
                for i in range(kernel_size):
                    kernel[i, i] = 1
                    kernel[i, kernel_size - i - 1] = 1
            elif shape == "Elips":
                # Elips şekilli kernel oluştur
                radius_x = kernel_size // 2
                radius_y = kernel_size // 3 if kernel_size > 3 else 1
                kernel = np.zeros((kernel_size, kernel_size), np.uint8)
                y, x = np.ogrid[-radius_y:radius_y+1, -radius_x:radius_x+1]
                mask = (x**2)/(radius_x**2) + (y**2)/(radius_y**2) <= 1
                kernel[mask] = 1
            
            # Görüntü renkli mi kontrol et
            if len(self.goruntu.shape) > 2 and self.goruntu.shape[2] == 3:
                # Renkli görüntü, her kanalı ayrı ayrı işle
                b, g, r = cv2.split(self.goruntu)
                b_dilated = cv2.dilate(b, kernel, iterations=iterations)
                g_dilated = cv2.dilate(g, kernel, iterations=iterations)
                r_dilated = cv2.dilate(r, kernel, iterations=iterations)
                result = cv2.merge([b_dilated, g_dilated, r_dilated])
            else:
                # Gri tonlamalı görüntü
                result = cv2.dilate(self.goruntu, kernel, iterations=iterations)
            
            # Sonuç görüntüsünü güncelle
            self.goruntu = result
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Genişletme: {shape} kernel, boyut: {kernel_size}, iterasyon: {iterations}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Genişletme işlemi tamamlandı! {shape} kernel, boyut: {kernel_size}, iterasyon: {iterations}")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli parametreler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Genişletme sırasında bir hata oluştu:\n{str(e)}")
            
    # Aşındırma (Erode) fonksiyonu
    def asindirma_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Parametreleri al
            kernel_size = int(self.erode_kernel_var.get())
            iterations = int(self.erode_iter_var.get())
            shape = self.erode_shape_var.get()
            
            # Kernel şeklini belirle
            if shape == "Kare":
                kernel = np.ones((kernel_size, kernel_size), np.uint8)
            elif shape == "Disk":
                # Disk (dairesel) şekilli kernel oluştur
                radius = kernel_size // 2
                kernel = np.zeros((kernel_size, kernel_size), np.uint8)
                y, x = np.ogrid[-radius:radius+1, -radius:radius+1]
                mask = x**2 + y**2 <= radius**2
                kernel[mask] = 1
            elif shape == "Çapraz":
                # Çapraz şekilli kernel oluştur
                kernel = np.zeros((kernel_size, kernel_size), np.uint8)
                for i in range(kernel_size):
                    kernel[i, i] = 1
                    kernel[i, kernel_size - i - 1] = 1
            elif shape == "Elips":
                # Elips şekilli kernel oluştur
                radius_x = kernel_size // 2
                radius_y = kernel_size // 3 if kernel_size > 3 else 1
                kernel = np.zeros((kernel_size, kernel_size), np.uint8)
                y, x = np.ogrid[-radius_y:radius_y+1, -radius_x:radius_x+1]
                mask = (x**2)/(radius_x**2) + (y**2)/(radius_y**2) <= 1
                kernel[mask] = 1
            
            # Görüntü renkli mi kontrol et
            if len(self.goruntu.shape) > 2 and self.goruntu.shape[2] == 3:
                # Renkli görüntü, her kanalı ayrı ayrı işle
                b, g, r = cv2.split(self.goruntu)
                b_eroded = cv2.erode(b, kernel, iterations=iterations)
                g_eroded = cv2.erode(g, kernel, iterations=iterations)
                r_eroded = cv2.erode(r, kernel, iterations=iterations)
                result = cv2.merge([b_eroded, g_eroded, r_eroded])
            else:
                # Gri tonlamalı görüntü
                result = cv2.erode(self.goruntu, kernel, iterations=iterations)
            
            # Sonuç görüntüsünü güncelle
            self.goruntu = result
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Aşındırma: {shape} kernel, boyut: {kernel_size}, iterasyon: {iterations}"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Aşındırma işlemi tamamlandı! {shape} kernel, boyut: {kernel_size}, iterasyon: {iterations}")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli parametreler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Aşındırma sırasında bir hata oluştu:\n{str(e)}")
            
    # K-Means segmentasyon fonksiyonu
    def kmeans_segmentasyonu_uygula(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Parametreleri al
            k = int(self.kmeans_k_var.get())
            max_iter = int(self.kmeans_iter_var.get())
            epsilon = float(self.kmeans_epsilon_var.get())
            attempts = int(self.kmeans_attempts_var.get())
            
            # Merkez başlangıç yöntemini belirle
            method = self.kmeans_method_var.get()
            if method == "Rastgele":
                flags = cv2.KMEANS_RANDOM_CENTERS
            else:  # PP (k-means++)
                flags = cv2.KMEANS_PP_CENTERS
            
            # Renk uzayı dönüşümü
            colorspace = self.kmeans_colorspace_var.get()
            if colorspace == "RGB":
                if len(self.goruntu.shape) > 2 and self.goruntu.shape[2] == 3:
                    if self.goruntu.dtype == np.uint8:
                        # BGR'dan RGB'ye çevir (OpenCV BGR kullanır)
                        img = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2RGB)
                    else:
                        img = self.goruntu.copy()
                else:
                    # Gri tonlamalı görüntüyü RGB'ye çevir
                    img = cv2.cvtColor(self.goruntu, cv2.COLOR_GRAY2RGB)
            elif colorspace == "HSV":
                if len(self.goruntu.shape) > 2 and self.goruntu.shape[2] == 3:
                    img = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2HSV)
                else:
                    # Gri tonlamalı görüntüyü RGB'ye, sonra HSV'ye çevir
                    rgb = cv2.cvtColor(self.goruntu, cv2.COLOR_GRAY2RGB)
                    img = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
            else:  # LAB
                if len(self.goruntu.shape) > 2 and self.goruntu.shape[2] == 3:
                    img = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2LAB)
                else:
                    # Gri tonlamalı görüntüyü RGB'ye, sonra LAB'a çevir
                    rgb = cv2.cvtColor(self.goruntu, cv2.COLOR_GRAY2RGB)
                    img = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
            
            # Görüntüyü 2D diziye dönüştür
            h, w = img.shape[:2]
            pixel_values = img.reshape((-1, 3))
            pixel_values = np.float32(pixel_values)
            
            # K-Means durma kriterlerini ayarla
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, max_iter, epsilon)
            
            # K-Means algoritmasını uygula
            _, labels, centers = cv2.kmeans(pixel_values, k, None, criteria, attempts, flags)
            
            # Küme merkezlerini uint8'e dönüştür
            centers = np.uint8(centers)
            
            # Etiketlere göre piksel değerlerini belirle
            segmented_data = centers[labels.flatten()]
            
            # 2D görüntü haline geri çevir
            segmented_image = segmented_data.reshape((h, w, 3))
            
            # Renk uzayını BGR'a çevir (GUI'de göstermek için)
            if colorspace == "RGB":
                segmented_image = cv2.cvtColor(segmented_image, cv2.COLOR_RGB2BGR)
            elif colorspace == "HSV":
                segmented_image = cv2.cvtColor(segmented_image, cv2.COLOR_HSV2BGR)
            elif colorspace == "LAB":
                segmented_image = cv2.cvtColor(segmented_image, cv2.COLOR_LAB2BGR)
            
            # Sonuç görüntüsünü güncelle
            self.goruntu = segmented_image
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, K-Means Segmentasyon: {k} küme kullanıldı"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"K-Means segmentasyon işlemi tamamlandı! {k} küme kullanıldı.")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli parametreler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Segmentasyon sırasında bir hata oluştu:\n{str(e)}")
            
    # Hough çember algılama fonksiyonu
    def hough_cemberleri_algıla(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
        
        try:
            # Parametreleri al
            blur_size = int(self.hough_circles_blur_var.get())
            # Blur size tek sayı olmalı
            if blur_size % 2 == 0:
                blur_size += 1
                
            param1 = int(self.hough_circles_param1_var.get())
            param2 = int(self.hough_circles_param2_var.get())
            min_radius = int(self.hough_circles_min_radius_var.get())
            max_radius = int(self.hough_circles_max_radius_var.get())
            min_dist = int(self.hough_circles_min_dist_var.get())
            
            # Çember rengi seç
            color_name = self.hough_circles_color_var.get()
            if color_name == "Yeşil":
                color = (0, 255, 0)
            elif color_name == "Kırmızı":
                color = (0, 0, 255)
            elif color_name == "Mavi":
                color = (255, 0, 0)
            elif color_name == "Sarı":
                color = (0, 255, 255)
            else:  # Mor
                color = (255, 0, 255)
            
            # Görüntüyü gri tonlamaya çevir
            if len(self.goruntu.shape) > 2:
                gray = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            else:
                gray = self.goruntu.copy()
            
            # Gaussian bulanıklaştırma uygula (gürültüyü azaltmak için)
            blurred = cv2.GaussianBlur(gray, (blur_size, blur_size), 2)
            
            # Hough Çember Algoritması
            circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, min_dist,
                                      param1=param1, param2=param2, 
                                      minRadius=min_radius, maxRadius=max_radius)
            
            # Orijinal görüntüyü renkliye çevir (eğer gri tonlamadaysa)
            if len(self.goruntu.shape) <= 2:
                output = cv2.cvtColor(self.goruntu, cv2.COLOR_GRAY2BGR)
            else:
                output = self.goruntu.copy()
            
            # Çemberleri çiz
            circle_count = 0
            if circles is not None:
                circles = np.uint16(np.around(circles))
                circle_count = len(circles[0])
                for i in circles[0, :]:
                    # Çember çevresini çiz
                    cv2.circle(output, (i[0], i[1]), i[2], color, 2)
                    # Çember merkezini çiz
                    cv2.circle(output, (i[0], i[1]), 2, (0, 0, 255), 3)
            
            # Sonuç görüntüsünü güncelle
            self.goruntu = output
            
            # Görüntüyü göster
            self.goruntu_goster()
            
            # Bilgi etiketini güncelle
            h, w = self.goruntu.shape[:2]
            boyut_bilgisi = f"Görüntü boyutları: {h}x{w}, Hough Çember Algılama: {circle_count} çember tespit edildi"
            self.bilgi_label.config(text=boyut_bilgisi)
            
            messagebox.showinfo("Başarılı", f"Hough çember algılama tamamlandı! {circle_count} çember tespit edildi.")
        
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli parametreler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Algılama sırasında bir hata oluştu:\n{str(e)}")

    # El hareketi ile parlaklık ayarı penceresi açma fonksiyonu
    def el_parlaklik_penceresi_ac(self):
        if self.goruntu is None:
            messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
            return
            
        # Yeni pencere oluştur
        self.el_pencere = tk.Toplevel(self.pencere)
        self.el_pencere.title("El Hareketi ile Parlaklık Kontrolü")
        self.el_pencere.geometry("1000x600")
        
        # Ana frame
        ana_frame = tk.Frame(self.el_pencere)
        ana_frame.pack(expand=True, fill='both')
        
        # Sol panel (görüntü için)
        sol_panel = tk.Frame(ana_frame, width=500)
        sol_panel.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Sağ panel (kamera için)
        sag_panel = tk.Frame(ana_frame, width=500, bg='#e0e0e0')
        sag_panel.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Görüntü için label
        self.el_goruntu_label = tk.Label(sol_panel)
        self.el_goruntu_label.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Bilgi etiketi
        self.el_bilgi_label = tk.Label(
            sol_panel, 
            text="Parlaklık: 1.0", 
            font=("Arial", 12)
        )
        self.el_bilgi_label.pack(pady=10)
        
        # Kamera görüntüsü için label
        self.kamera_label = tk.Label(sag_panel, bg='black')
        self.kamera_label.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Kamera aç/kapat butonu
        self.kamera_buton = tk.Button(
            sag_panel,
            text="Kamerayı Aç",
            command=self.toggle_camera,
            bg="#FF9800",
            fg="white",
            font=("Arial", 12),
            padx=10,
            pady=5
        )
        self.kamera_buton.pack(pady=10)
        
        # İncelenen görüntüyü göster
        self.guncel_goruntu_goster()
        
        # Kamera değişkenleri
        self.cap = None
        self.kamera_aktif = False
        
        # MediaPipe el tanıma modülü
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Kamera güncelleme fonksiyonunu başlat
        self.update_kamera()
        
    def guncel_goruntu_goster(self):
        if self.goruntu is not None:
            # OpenCV görüntüsünü PIL formatına dönüştür
            if len(self.goruntu.shape) == 3:
                img_rgb = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2RGB)
            else:
                img_rgb = cv2.cvtColor(self.goruntu, cv2.COLOR_GRAY2RGB)
                
            img_pil = Image.fromarray(img_rgb)
            
            # Görüntüyü ekrana sığacak şekilde yeniden boyutlandır
            max_width, max_height = 400, 400
            img_width, img_height = img_pil.size
            ratio = min(max_width/img_width, max_height/img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            img_resized = img_pil.resize((new_width, new_height), Image.LANCZOS)
            self.photo_img = ImageTk.PhotoImage(img_resized)
            
            # Görüntüyü label'a yerleştir
            self.el_goruntu_label.config(image=self.photo_img)
            self.el_goruntu_label.image = self.photo_img
            
    def toggle_camera(self):
        if self.kamera_aktif:
            self.stop_camera()
        else:
            self.start_camera()
    
    def start_camera(self):
        self.cap = cv2.VideoCapture(0)  # Varsayılan kamera
        if self.cap.isOpened():
            self.kamera_aktif = True
            self.kamera_buton.config(text="Kamerayı Kapat", bg="#F44336")
        else:
            messagebox.showerror("Hata", "Kamera açılamadı!")
    
    def stop_camera(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.kamera_aktif = False
        self.kamera_label.config(image="")
        self.kamera_buton.config(text="Kamerayı Aç", bg="#FF9800")
    
    def update_kamera(self):
        if self.kamera_aktif and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Yatay çevirme (ayna görüntüsü)
                frame = cv2.flip(frame, 1)
                
                # Frame'i RGB'ye dönüştür (MediaPipe için)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # El tespiti yap
                results = self.hands.process(rgb_frame)
                
                # El hareketi algılandıysa
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # El işaretlerini çiz
                        self.mp_drawing.draw_landmarks(
                            frame, 
                            hand_landmarks, 
                            self.mp_hands.HAND_CONNECTIONS
                        )
                        
                        # Başparmak ve işaret parmağı noktalarını al
                        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                        
                        # Piksel koordinatlarına dönüştür
                        h, w, c = frame.shape
                        thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                        index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
                        
                        # İki parmak arasındaki mesafeyi hesapla
                        distance = math.sqrt((thumb_x - index_x)**2 + (thumb_y - index_y)**2)
                        
                        # Parmaklar arasına çizgi çiz
                        cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (0, 255, 0), 2)
                        
                        # Mesafeyi ekranda göster
                        cv2.putText(frame, f"Mesafe: {int(distance)}", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        
                        # Parlaklık ayarını güncelle (mesafeyi 0.1-2.0 arasında bir değere normalize et)
                        # Mesafe 20-200 piksel arasında olabilir
                        normalized_distance = max(0.1, min(2.0, distance / 100))
                        
                        # Görüntü parlaklığını ayarla
                        self.parlaklik_el_ile_ayarla(normalized_distance)
                        
                        # Bilgi etiketini güncelle
                        self.el_bilgi_label.config(text=f"Parlaklık: {normalized_distance:.1f}")
                
                # Frame'i Tkinter'da göstermek için dönüştür
                camera_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                camera_image = Image.fromarray(camera_image)
                camera_image = ImageTk.PhotoImage(image=camera_image)
                
                # Kamera görüntüsünü güncelle
                self.kamera_label.config(image=camera_image)
                self.kamera_label.image = camera_image  # Referansı sakla
        
        # Fonksiyonu tekrar çağır (her 10ms'de bir)
        if hasattr(self, 'el_pencere') and self.el_pencere.winfo_exists():
            self.el_pencere.after(10, self.update_kamera)
            
    def parlaklik_el_ile_ayarla(self, factor):
        if self.goruntu is not None:
            try:
                # Geçici olarak bir kopya oluştur
                if len(self.goruntu.shape) == 3:
                    img = cv2.cvtColor(self.goruntu.copy(), cv2.COLOR_BGR2RGB)
                else:
                    img = cv2.cvtColor(self.goruntu.copy(), cv2.COLOR_GRAY2RGB)
                    
                pil_img = Image.fromarray(img)
                
                # Parlaklık ayarını uygula
                enhancer = ImageEnhance.Brightness(pil_img)
                enhanced_img = enhancer.enhance(factor)
                
                # Geçici görüntü oluştur (orijinali değiştirmeyeceğiz)
                temp_goruntu = cv2.cvtColor(np.array(enhanced_img), cv2.COLOR_RGB2BGR)
                
                # Geçici görüntüyü göster
                if len(temp_goruntu.shape) == 3:
                    temp_rgb = cv2.cvtColor(temp_goruntu, cv2.COLOR_BGR2RGB)
                else:
                    temp_rgb = cv2.cvtColor(temp_goruntu, cv2.COLOR_GRAY2RGB)
                    
                temp_pil = Image.fromarray(temp_rgb)
                
                # Görüntüyü ekrana sığacak şekilde yeniden boyutlandır
                max_width, max_height = 400, 400
                img_width, img_height = temp_pil.size
                ratio = min(max_width/img_width, max_height/img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                
                img_resized = temp_pil.resize((new_width, new_height), Image.LANCZOS)
                self.photo_img = ImageTk.PhotoImage(img_resized)
                
                # Görüntüyü label'a yerleştir
                self.el_goruntu_label.config(image=self.photo_img)
                self.el_goruntu_label.image = self.photo_img
                
            except Exception as e:
                print(f"Hata: {str(e)}")

if __name__ == "__main__":
    uygulama = GoruntuIsleme()
    uygulama.baslat()
