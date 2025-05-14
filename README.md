# Advanced Image Processing Suite - Gelişmiş Görüntü İşleme Paketi

# 🇹🇷 | 🇬🇧 Choose Your Language / Dil Seçin
📌 [English](#english) | [Türkçe](#turkish)

<div id="english"></div>

```
****************************************************************************
*             _                               _                            *
*    /\      | |                             | |                           *
*   /  \   __| |_   ____ _ _ __   ___ ___  __| |                           *
*  / /\ \ / _` \ \ / / _` | '_ \ / __/ _ \/ _` |                           *
* / ____ \ (_| |\ V / (_| | | | | (_|  __/ (_| |                           *
*/_/___ \_\__,_| \_/ \__,_|_| |_|\___\___|\__,_|                           *
*|_   _|                                                                   *
*  | |  _ __ ___   __ _  __ _  ___                                         *
*  | | | '_ ` _ \ / _` |/ _` |/ _ \                                        *
* _| |_| | | | | | (_| | (_| |  __/                                        *
*|_____|_| |_| |_|\__,_|\__, |\___| _                _____       _ _       *
*|  __ \                 __/ |     (_)              / ____|     (_) |      *
*| |__) | __ ___   ___ _|___/__ ___ _ _ __   __ _  | (___  _   _ _| |_ ___ *
*|  ___/ '__/ _ \ / __/ _ \/ __/ __| | '_ \ / _` |  \___ \| | | | | __/ _ \*
*| |   | | | (_) | (_|  __/\__ \__ \ | | | | (_| |  ____) | |_| | | ||  __/*
*|_|   |_|  \___/ \___\___||___/___/_|_| |_|\__, | |_____/ \__,_|_|\__\___|*
*                                            __/ |                         *
*                                           |___/                          *
****************************************************************************
```

## Description

This comprehensive image processing application provides a user-friendly interface built with Tkinter for performing a wide range of image processing operations. From basic transformations to advanced frequency domain processing, edge detection, and morphological operations, this tool offers a complete suite for image analysis and manipulation. The application also features an innovative hand gesture control system that utilizes computer vision to adjust image brightness through natural hand movements.

## Features

### Basic Operations
- **Image Loading & Saving**: Load images from your computer and save processed results
- **Original Image Recovery**: Easily revert to the original image at any point in your workflow
- **Grayscale Conversion**: Convert color images to grayscale using standard or weighted methods
- **Negative Transformation**: Create negative versions of images by inverting pixel values
- **Brightness & Contrast**: Adjust brightness and contrast with intuitive sliders
- **Histogram Visualization**: Analyze image statistics with detailed histograms
- **Histogram Equalization**: Enhance contrast using histogram equalization
- **Automatic Contrast Stretching**: Optimize image contrast automatically
- **Manual Contrast Stretching**: Fine-tune contrast with manual parameter settings
- **Multi-point Contrast Stretching**: Apply contrast stretching with multiple control points
- **Channel Separation**: View and manipulate individual RGB color channels
- **Thresholding Operations**: Convert images to binary using various thresholding methods

### Geometric Transformations
- **Translation**: 
  - Manual Translation: Move images by specified pixel amounts
  - Function-based Translation: Apply mathematical transformations
- **Mirroring**: 
  - Horizontal Mirroring: Flip images along the horizontal axis
  - Vertical Mirroring: Flip images along the vertical axis
  - Angular Mirroring: Mirror images at custom angles
- **Shearing**: 
  - X-axis Shearing: Automatic and manual implementation
  - Y-axis Shearing: Automatic and manual implementation
- **Scaling**: 
  - Pixel Enlargement: Increase image size pixel by pixel
  - Pixel Reduction: Decrease image size with pixel-based methods
  - Interpolation-based Scaling: Resize using various interpolation algorithms
- **Rotation**: Rotate images at precise angles with border handling
- **Cropping**: Interactive region selection for precise cropping
- **Perspective Correction**: Four-point perspective transformation with interactive point selection

### Spatial Filtering
- **Mean (Average) Filter**: 
  - Standard Implementation: Reduce noise by averaging neighboring pixels
  - Fast Implementation: Optimized algorithm for better performance
- **Median Filter**: 
  - Standard Implementation: Effective for salt-and-pepper noise removal
  - Fast Implementation: Performance-optimized implementation
- **Gaussian Filter**: 
  - Standard Implementation: Smooth images with adjustable sigma parameter
  - Fast Implementation: Optimized Gaussian filtering
- **Conservative Smoothing**: Edge-preserving noise reduction technique
- **Crimmins Speckle Removal**: Advanced algorithm for specialized noise reduction

### Frequency Domain Processing
- **Fast Fourier Transform (FFT) Based Filters**:
  - **Low-pass Filter**: Remove high-frequency components (noise)
  - **High-pass Filter**: Enhance edges by removing low frequencies
  - **Band-pass Filter**: Retain frequencies within specific ranges
  - **Band-stop Filter**: Remove frequencies within specific ranges
- **Butterworth Filters**:
  - **Low-pass**: Smooth transition filtering with adjustable cutoff and order
  - **High-pass**: Edge enhancement with smooth transition
- **Gaussian Frequency Filters**:
  - **Low-pass**: Gaussian-based smoothing in frequency domain
  - **High-pass**: Gaussian-based edge enhancement
- **Homomorphic Filtering**: Simultaneously normalize brightness and enhance contrast

### Edge & Feature Detection
- **First-order Gradient Operators**:
  - **Sobel**: Direction-sensitive edge detection with magnitude and direction visualization
  - **Prewitt**: Alternative first-order edge detection
  - **Roberts Cross**: Diagonal edge detection
  - **Compass**: Multi-directional edge detection with 8 directions
- **Second-order Operators**:
  - **Laplacian**: Highlight rapid intensity changes in all directions
- **Advanced Edge Detectors**:
  - **Canny**: Multi-stage edge detection with hysteresis thresholding
- **Texture Analysis**:
  - **Gabor Filter**: Analyze texture with orientation and frequency sensitivity

### Feature Detection & Analysis
- **Hough Transforms**:
  - **Line Detection**: Find straight lines with parameter visualization
  - **Circle Detection**: Identify circles with adjustable parameters
- **Morphological Operations**:
  - **Dilation**: Expand bright regions for feature enhancement
  - **Erosion**: Shrink bright regions and remove small details
- **Segmentation**:
  - **K-means Clustering**: Segment images into K regions based on color similarity

### Interactive & Advanced Features
- **Hand Gesture Control**: 
  - Control brightness by pinching gestures captured via webcam
  - Uses MediaPipe hand tracking technology
- **Camera Integration**: Capture and process live video feed
- **User-friendly Interface**: Intuitive layout with organized tool panels
- **Scrollable Interface**: Support for large images with automatic scrollbars

## Requirements

This project requires the following Python libraries:

```bash
pip install opencv-python==4.8.0.76 numpy==1.24.3 pillow==10.0.0 matplotlib==3.7.2 mediapipe==0.10.3 tk==0.1.0
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YourUsername/Goruntu-Isleme-Projesi.git
   cd Goruntu-Isleme-Projesi
   ```

2. **Install required libraries:**
   ```bash
   pip install -r requirements.txt
   ```
   Or install them individually using the command above.

## Usage

1. **Launch the application:**
   ```bash
   python Goruntu_Isleme.py
   ```

2. **Basic Workflow:**
   - Click the "Görüntü Yükle" (Load Image) button to select an image file
   - Use the various buttons and sliders in the interface to apply different image processing operations
   - Save your processed image using the "Görüntü Kaydet" (Save Image) button

3. **Keyboard Shortcuts:**
   - Use the mouse wheel to scroll through the interface
   - For perspective correction, click four points on the image to define the corners
   - For cropping, click and drag to select the crop region

4. **Using Advanced Features:**
   - **Hand Gesture Control:** Click the "El Parlaklık" button to open the hand gesture control window. Move your thumb and index finger closer or farther apart to adjust brightness.
   - **Frequency Domain Filters:** Apply FFT filters to work with the image in the frequency domain, which is useful for removing specific types of noise.
   - **K-means Segmentation:** Use this to automatically segment your image into distinct regions based on color similarity.

## Project Structure

- `Goruntu_Isleme.py`: Main application file containing the complete implementation
- `requirements.txt`: List of required Python packages and their versions
- `README.md`: This documentation file
- `example_images/`: Directory containing sample images to test the application (if included)

## Contributing

Contributions are welcome! To contribute to the project:

1. Fork this repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request


<div id="turkish"></div>

```
*****************************************************************************
*  _____      _ _           _        _____ _   _      _   _       _   _   _ *
* / ____|    | (_)         (_)      / ____(_) (_)    (_) (_)     | | (_) (_)*
*| |  __  ___| |_ _ __ ___  _ ___  | |  __  ___  _ __ _   _ _ __ | |_ _   _ *
*| | |_ |/ _ \ | | '_ ` _ \| / __| | | |_ |/ _ \| '__| | | | '_ \| __| | | |*
*| |__| |  __/ | | | | | | | \__ \ | |__| | (_) | |  | |_| | | | | |_| |_| |*
* \_____|\___|_|_|_| |_| |_|_|___/  \_____|\___/|_|   \__,_|_| |_|\__|\__,_|*
*|_   _|   | |                     |  __ \    | |      | | (_)              *
*  | |  ___| | ___ _ __ ___   ___  | |__) |_ _| | _____| |_ _               *
*  | | / __| |/ _ \ '_ ` _ \ / _ \ |  ___/ _` | |/ / _ \ __| |              *
* _| |_\__ \ |  __/ | | | | |  __/ | |  | (_| |   <  __/ |_| |              *
*|_____|___/_|\___|_| |_| |_|\___| |_|   \__,_|_|\_\___|\__|_|              *
*****************************************************************************
```

## Genel Bakış

Bu kapsamlı görüntü işleme uygulaması, Tkinter ile geliştirilmiş kullanıcı dostu bir arayüz sunarak geniş bir yelpazede görüntü işleme işlemlerini gerçekleştirmenize olanak tanır. Temel dönüşümlerden gelişmiş frekans alanı işlemlerine, kenar tespitine ve morfolojik işlemlere kadar uzanan bu araç, görüntü analizi ve manipülasyonu için eksiksiz bir paket sunar. Uygulama ayrıca, doğal el hareketleri aracılığıyla görüntü parlaklığını ayarlamak için bilgisayarlı görme kullanan yenilikçi bir el hareket kontrol sistemi içerir.

## Özellikler

### Temel İşlemler
- **Görüntü Yükleme ve Kaydetme**: Bilgisayarınızdan görüntü yükleyin ve işlenmiş sonuçları kaydedin
- **Orijinal Görüntüyü Geri Yükleme**: Çalışma akışınızda herhangi bir noktada orijinal görüntüye kolayca geri dönün
- **Gri Tonlama Dönüşümü**: Renkli görüntüleri standart veya ağırlıklı yöntemlerle gri tonlamaya dönüştürün
- **Negatif Dönüşüm**: Piksel değerlerini tersine çevirerek görüntülerin negatif versiyonlarını oluşturun
- **Parlaklık ve Kontrast**: Sezgisel kaydırıcılarla parlaklık ve kontrastı ayarlayın
- **Histogram Görüntüleme**: Ayrıntılı histogramlarla görüntü istatistiklerini analiz edin
- **Histogram Eşitleme**: Histogram eşitleme kullanarak kontrastı geliştirin
- **Otomatik Kontrast Germe**: Görüntü kontrastını otomatik olarak optimize edin
- **Manuel Kontrast Germe**: Manuel parametre ayarlarıyla kontrastı hassas bir şekilde ayarlayın
- **Çoklu Nokta Kontrast Germe**: Birden çok kontrol noktasıyla kontrast germe uygulama
- **Kanal Ayırma**: Tek tek RGB renk kanallarını görüntüleyin ve manipüle edin
- **Eşikleme İşlemleri**: Çeşitli eşikleme yöntemleri kullanarak görüntüleri ikili görüntüye dönüştürün

### Geometrik Dönüşümler
- **Taşıma**: 
  - Manuel Taşıma: Görüntüleri belirtilen piksel miktarlarınca taşıyın
  - Fonksiyon Tabanlı Taşıma: Matematiksel dönüşümler uygulayın
- **Aynalama**: 
  - Yatay Aynalama: Görüntüleri yatay eksen boyunca çevirin
  - Dikey Aynalama: Görüntüleri dikey eksen boyunca çevirin
  - Açısal Aynalama: Görüntüleri özel açılarda aynalama
- **Eğme (Shearing)**: 
  - X-ekseni Eğme: Otomatik ve manuel uygulama
  - Y-ekseni Eğme: Otomatik ve manuel uygulama
- **Ölçekleme**: 
  - Piksel Büyütme: Görüntü boyutunu piksel piksel artırın
  - Piksel Küçültme: Piksel tabanlı yöntemlerle görüntü boyutunu azaltın
  - İnterpolasyon Tabanlı Ölçekleme: Çeşitli interpolasyon algoritmaları kullanarak yeniden boyutlandırın
- **Döndürme**: Görüntüleri kenar işlemeyle hassas açılarda döndürün
- **Kırpma**: Hassas kırpma için etkileşimli bölge seçimi
- **Perspektif Düzeltme**: Etkileşimli nokta seçimiyle dört noktalı perspektif dönüşümü
### Uzamsal Filtreleme
- **Ortalama (Average) Filtresi**: 
  - Standart Uygulama: Komşu pikselleri ortalayarak gürültü azaltma
  - Hızlı Uygulama: Daha iyi performans için optimize edilmiş algoritma
- **Medyan Filtresi**: 
  - Standart Uygulama: Tuz-biber gürültüsü giderme için etkili
  - Hızlı Uygulama: Performans-optimize edilmiş implementasyon
- **Gauss Filtresi**: 
  - Standart Uygulama: Ayarlanabilir sigma parametresi ile görüntüleri yumuşatma
  - Hızlı Uygulama: Optimize edilmiş Gauss filtreleme
- **Konservatif Yumuşatma**: Kenar korumalı gürültü azaltma tekniği
- **Crimmins Benek Giderme**: Özelleşmiş gürültü azaltma için gelişmiş algoritma

### Frekans Alanı İşleme
- **Hızlı Fourier Dönüşümü (FFT) Tabanlı Filtreler**:
  - **Alçak Geçiren Filtre**: Yüksek frekans bileşenlerini (gürültü) kaldırır
  - **Yüksek Geçiren Filtre**: Düşük frekansları kaldırarak kenarları geliştirir
  - **Bant Geçiren Filtre**: Belirli aralıklardaki frekansları korur
  - **Bant Durduran Filtre**: Belirli aralıklardaki frekansları kaldırır
- **Butterworth Filtreleri**:
  - **Alçak Geçiren**: Ayarlanabilir kesim ve derece ile yumuşak geçişli filtreleme
  - **Yüksek Geçiren**: Yumuşak geçişli kenar geliştirme
- **Gauss Frekans Filtreleri**:
  - **Alçak Geçiren**: Frekans alanında Gauss tabanlı yumuşatma
  - **Yüksek Geçiren**: Gauss tabanlı kenar geliştirme
- **Homomorfik Filtreleme**: Aynı anda parlaklığı normalize etme ve kontrastı geliştirme

### Kenar ve Özellik Tespiti
- **Birinci Derece Gradyan Operatörleri**:
  - **Sobel**: Yöne duyarlı kenar tespiti, büyüklük ve yön görselleştirme ile
  - **Prewitt**: Alternatif birinci derece kenar tespiti
  - **Roberts Cross**: Çapraz kenar tespiti
  - **Pusula (Compass)**: 8 farklı yönde çok yönlü kenar tespiti
- **İkinci Derece Operatörler**:
  - **Laplace**: Tüm yönlerde hızlı yoğunluk değişimlerini vurgulama
- **Gelişmiş Kenar Dedektörleri**:
  - **Canny**: Histerezis eşikleme ile çok aşamalı kenar tespiti
- **Doku Analizi**:
  - **Gabor Filtresi**: Yön ve frekans hassasiyeti ile doku analizi

### Özellik Tespiti ve Analiz
- **Hough Dönüşümleri**:
  - **Doğru Tespiti**: Parametre görselleştirme ile düz çizgilerin bulunması
  - **Çember Tespiti**: Ayarlanabilir parametrelerle çemberlerin tanımlanması
- **Morfolojik İşlemler**:
  - **Genişletme (Dilation)**: Özellik geliştirme için parlak bölgelerin genişletilmesi
  - **Aşındırma (Erosion)**: Parlak bölgelerin daraltılması ve küçük detayların kaldırılması
- **Segmentasyon**:
  - **K-ortalamalar Kümeleme**: Görüntü piksellerini renk benzerliğine göre K bölgeye ayırma

### Etkileşimli ve Gelişmiş Özellikler
- **El Hareketi Kontrolü**: 
  - Webcam aracılığıyla yakalanan tutma hareketleriyle parlaklığı kontrol etme
  - MediaPipe el takip teknolojisini kullanır
- **Kamera Entegrasyonu**: Canlı video akışını yakalama ve işleme
- **Kullanıcı Dostu Arayüz**: Düzenli araç panelleri ile sezgisel düzen
- **Kaydırılabilir Arayüz**: Otomatik kaydırma çubukları ile büyük görüntüler için destek

## Gereksinimler

Bu projenin çalışabilmesi için aşağıdaki Python kütüphaneleri gereklidir:

```bash
pip install opencv-python==4.8.0.76 numpy==1.24.3 pillow==10.0.0 matplotlib==3.7.2 mediapipe==0.10.3 tk==0.1.0
```

## Kurulum

1. **Repoyu klonlayın:**
   ```bash
   git clone https://github.com/KullaniciAdiniz/Goruntu-Isleme-Projesi.git
   cd Goruntu-Isleme-Projesi
   ```

2. **Gerekli kütüphaneleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```
   Veya yukarıdaki komutu kullanarak tek tek yükleyebilirsiniz.

## Kullanım

1. **Uygulamayı başlatın:**
   ```bash
   python Goruntu_Isleme.py
   ```

2. **Temel İş Akışı:**
   - "Görüntü Yükle" butonuna tıklayarak bir görüntü dosyası seçin
   - Arayüzdeki çeşitli butonları ve kaydırıcıları kullanarak farklı görüntü işleme operasyonlarını uygulayın
   - İşlenmiş görüntünüzü "Görüntü Kaydet" butonu ile kaydedin

3. **Klavye Kısayolları ve Fare Kullanımı:**
   - Arayüz içinde gezinmek için fare tekerleğini kullanın
   - Perspektif düzeltme için, köşeleri tanımlamak üzere görüntüde dört noktaya tıklayın
   - Kırpmak için tıklayıp sürükleyerek kırpma bölgesini seçin

4. **Gelişmiş Özelliklerin Kullanımı:**
   - **El Hareketi Kontrolü:** "El Parlaklık" butonuna tıklayarak el hareket kontrol penceresini açın. Başparmak ve işaret parmağınızı birbirine yaklaştırıp uzaklaştırarak parlaklığı ayarlayın.
   - **Frekans Alanı Filtreleri:** FFT filtrelerini uygulayarak görüntüyü frekans alanında işleyin, bu belirli türdeki gürültüleri gidermek için faydalıdır.
   - **K-ortalamalar Segmentasyonu:** Görüntünüzü renk benzerliğine göre belirgin bölgelere otomatik olarak ayırmak için kullanın.

## Proje Yapısı

- `Goruntu_Isleme.py`: Tam uygulamayı içeren ana uygulama dosyası
- `requirements.txt`: Gerekli Python paketlerinin ve sürümlerinin listesi
- `README.md`: Bu dokümantasyon dosyası
- `example_images/`: Uygulamayı test etmek için örnek görüntüleri içeren dizin (eğer varsa)

## Katkıda Bulunma

Katkılarınızı bekliyoruz! Projeye katkıda bulunmak için:

1. Bu repoyu forklayın
2. Yeni bir dal oluşturun (`git checkout -b feature/harika-ozellik`)
3. Değişikliklerinizi yapın
4. Değişikliklerinizi kaydedin (`git commit -m 'Harika bir özellik ekle'`)
5. Dala itelemede bulunun (`git push origin feature/harika-ozellik`)
6. Bir Pull Request açın
