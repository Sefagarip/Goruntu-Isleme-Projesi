import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt

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
        
        # Pencere boyutunu ayarla
        self.pencere.geometry("1200x800")
        
        # Ana container frame oluştur (3x3 grid için)
        self.ana_frame = tk.Frame(self.ana_frame)
        self.ana_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Sol frame
        self.sol_frame = tk.Frame(self.ana_frame)
        self.sol_frame.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        
        # Sağ frame
        self.sag_frame = tk.Frame(self.ana_frame)
        self.sag_frame.grid(row=1, column=2, padx=5, pady=5, sticky='nsew')
        
        # Üst frame
        self.ust_frame = tk.Frame(self.ana_frame)
        self.ust_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        
        # Alt frame
        self.alt_frame = tk.Frame(self.ana_frame)
        self.alt_frame.grid(row=2, column=1, padx=5, pady=5, sticky='nsew')
        
        # Orta frame (Canvas için)
        self.orta_frame = tk.Frame(self.ana_frame)
        self.orta_frame.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')
        
        # Canvas'ı orta frame'e ekle
        self.canvas = tk.Canvas(self.orta_frame)
        self.canvas.pack(expand=True)
        
        # Grid ağırlıklarını ayarla
        self.ana_frame.grid_rowconfigure(1, weight=1)
        self.ana_frame.grid_columnconfigure(1, weight=1)
        
        # Görüntü değişkeni
        self.goruntu = None
        
        # Orijinal görüntüyü saklamak için yeni değişken
        self.orijinal_goruntu = None
        
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
        
        self.gri_buton = tk.Button(
            self.buton_frame,
            text="Resmi Griye Çevir",
            command=self.gri_tonla
        )
        self.gri_buton.pack(side='left', padx=5)
        
        self.grayscale_buton = tk.Button(
            self.buton_frame,
            text="Grayscale Dönüşüm",
            command=self.grayscale_donusum
        )
        self.grayscale_buton.pack(side='left', padx=5)
        
        self.negatif_buton = tk.Button(
            self.buton_frame,
            text="Negatif Görüntü",
            command=self.negatif_al
        )
        self.negatif_buton.pack(side='left', padx=5)
        
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
            value='kirmizi',
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
            value='mavi',
            command=self.kanal_sec
        )
        self.b_radio.pack(padx=5)
        
        # Parlaklık ayarı için LabelFrame
        self.parlaklik_frame = tk.LabelFrame(self.sag_frame, text="Parlaklık Ayarı", padx=5, pady=5)
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
        self.esikleme_frame = tk.LabelFrame(self.sol_frame, text="Eşikleme Ayarı", padx=5, pady=5)
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
        self.tasima_frame = tk.LabelFrame(self.sol_frame, text="Görüntü Taşıma", padx=5, pady=5)
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
        self.aynalama_frame = tk.LabelFrame(self.sol_frame, text="Görüntü Aynalama", padx=5, pady=5)
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
        self.egme_frame = tk.LabelFrame(self.sag_frame, text="Görüntü Eğme (Shearing)", padx=5, pady=5)
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
        self.olcekleme_frame = tk.LabelFrame(self.sol_frame, text="Görüntü Ölçekleme", padx=5, pady=5)
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
        self.dondurme_frame = tk.LabelFrame(self.sag_frame, text="Görüntü Döndürme", padx=5, pady=5)
        self.dondurme_frame.pack(fill='x', padx=5, pady=5)
        
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
            # BGR'den RGB'ye dönüştür
            rgb_goruntu = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2RGB)
            # PIL Image'e dönüştür
            pil_goruntu = Image.fromarray(rgb_goruntu)
            
            # Pencereye sığacak şekilde yeniden boyutlandır
            max_boyut = 500
            oran = min(max_boyut/pil_goruntu.width, max_boyut/pil_goruntu.height)
            yeni_genislik = int(pil_goruntu.width * oran)
            yeni_yukseklik = int(pil_goruntu.height * oran)
            pil_goruntu = pil_goruntu.resize((yeni_genislik, yeni_yukseklik))
            
            # Tkinter'da gösterilebilir formata dönüştür
            self.tk_goruntu = ImageTk.PhotoImage(pil_goruntu)
            
            # Canvas'ı görüntü boyutuna ayarla
            self.canvas.config(width=yeni_genislik, height=yeni_yukseklik)
            # Görüntüyü canvas'a yerleştir
            self.canvas.create_image(0, 0, anchor='nw', image=self.tk_goruntu)
    
    def gri_tonla(self):
        if self.goruntu is not None:
            # Görüntüyü gri tonlamaya çevir
            self.goruntu = cv2.cvtColor(self.goruntu, cv2.COLOR_BGR2GRAY)
            # Gri görüntüyü 3 kanallı yap (görüntüleme için)
            self.goruntu = cv2.cvtColor(self.goruntu, cv2.COLOR_GRAY2BGR)
            
            # Görüntü boyutlarını güncelle
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
            
            # Görüntü boyutlarını güncelle
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
            
            # Görüntü boyutlarını güncelle
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
            self.goruntu = self.orijinal_goruntu.copy()
            
            if secim == 'kirmizi':
                # Yeşil ve mavi kanalları sıfırla
                self.goruntu[:,:,1:3] = 0
                mesaj = "Kırmızı kanal görüntüleniyor!"
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
                mesaj = "Mavi kanal görüntüleniyor!"
                kanal_bilgisi = "Mavi Kanal"
            else:  # orijinal
                mesaj = "Orijinal görüntü görüntüleniyor!"
                kanal_bilgisi = f"Kanal sayısı: {self.goruntu.shape[2]}"
            
            # Bilgi etiketini güncelle
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
            
            # Görüntü boyutlarını güncelle
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
            self.goruntu = self.orijinal_goruntu.copy()
            
            # Görüntü boyutlarını al
            x, y, z = self.goruntu.shape
            
            # Her piksel için parlaklık ekle
            for i in range(x):
                for j in range(y):
                    for k in range(z):
                        # Parlaklık değerini ekle ve 255'i aşmamasını sağla
                        yeni_deger = self.goruntu[i,j,k] + parlaklik
                        self.goruntu[i,j,k] = min(255, yeni_deger)
            
            # Görüntü boyutlarını güncelle
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
            self.goruntu = self.orijinal_goruntu.copy()
            
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
            
            # Bilgi etiketini güncelle
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
                
                # Görüntüyü güncelle
                self.goruntu_goster()
                
                # Bilgi etiketini güncelle
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
                
                # Görüntüyü güncelle
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
                
                # Görüntüyü güncelle
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
                
                # Görüntüyü güncelle
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
                
                # Görüntüyü güncelle
                self.goruntu = tasimis_goruntu
                
                # Bilgi etiketini güncelle
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
                
                # Görüntüyü güncelle
                self.goruntu = tasimis_goruntu
                
                # Bilgi etiketini güncelle
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
                
                # Görüntüyü güncelle
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
                
                # Görüntüyü güncelle
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
                
                # Görüntüyü güncelle
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
                
                # Görüntüyü güncelle
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
                
                # Görüntüyü güncelle
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
                
                # Görüntüyü güncelle
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
                
                # Görüntüyü güncelle
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
                
                # Görüntüyü güncelle
                self.goruntu = zoomed_image
                
                # Bilgi etiketini güncelle
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
                
                # Görüntüyü güncelle
                self.goruntu = downsampled_image
                
                # Bilgi etiketini güncelle
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
                
                # Bilgi etiketini güncelle
                islem = "büyütüldü" if scale_factor > 1 else "küçültüldü"
                boyut_bilgisi = f"Görüntü boyutları: {new_h}x{new_w}, {interpolasyon.capitalize()} interpolasyon ile {islem}: {scale_factor}x"
                self.bilgi_label.config(text=boyut_bilgisi)
                
                # Görüntüyü güncelle
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
                
                # Bilgi etiketini güncelle
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
                
                # Bilgi etiketini güncelle
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
        # Frame'in boyutunu güncelle ve scroll bölgesini ayarla
        def configure_scroll_region(event):
            self.canvas_container.configure(scrollregion=self.canvas_container.bbox('all'))
        
        # Frame boyutu değiştiğinde scroll bölgesini güncelle
        self.ana_frame.bind('<Configure>', configure_scroll_region)
        
        # Mouse wheel ile scroll yapabilme
        def _on_mousewheel(event):
            self.canvas_container.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas_container.bind_all("<MouseWheel>", _on_mousewheel)
        
        self.pencere.mainloop()

if __name__ == "__main__":
    uygulama = GoruntuIsleme()
    uygulama.baslat()
