# Görüntü İşleme Arayüzü

Bu proje, Tkinter kullanarak geliştirilmiş bir görüntü işleme uygulamasıdır. Kullanıcılar, görüntülerini yükleyerek çeşitli dönüşümler ve analizler yapabilir.

## Özellikler
- **Görüntü Yükleme**: Kullanıcılar bilgisayarlarından görüntü dosyaları seçerek yükleyebilir.
- **Gri Tonlama**: Seçilen görüntüyü gri tonlamaya çevirir.
- **Negatif Dönüşüm**: Görüntünün negatifini alarak yeni bir versiyonunu oluşturur.
- **Histogram Gösterme**: Görüntünün histogram analizini yapar.
- **Histogram Eşitleme**: Histogram dengeleme işlemi uygular.
- **RGB Kanallarını Ayırma**: Görüntüyü kırmızı, yeşil ve mavi kanallarına ayırarak gösterebilir.
- **Parlaklık ve Kontrast Ayarlama**: Görüntü üzerinde parlaklık ve kontrast değişiklikleri yapılabilir.
- **Eşikleme**: Belirli bir eşik değeri belirlenerek görüntünün siyah-beyaz hale getirilmesi sağlanabilir.
- **Filtreleme**: Gaussian ve Median filtreleme işlemleri uygulanabilir.
- **Kenar Tespiti**: Sobel ve Canny algoritmaları kullanılarak görüntüdeki kenarlar belirlenebilir.
- **Kaydetme**: Düzenlenen görüntüler kaydedilebilir.
- **Taşıma**: Görüntü farklı konumlara taşınabilir.
- **Aynalama**: Görüntü yatay veya dikey olarak aynalanabilir.
- **Eğme (Shearing)**: Görüntü belirli bir açıyla eğilebilir.
- **Ölçekleme (Zoom In/Out)**: Görüntü yakınlaştırılabilir veya uzaklaştırılabilir.
- **Döndürme (Rotate)**: Görüntü belirli açılarla döndürülebilir.
- **Kırpma**: İstenen bölge seçilerek görüntü kırpılabilir.
- **Dışarıdan Görsel Okuma**: Kullanıcı dışarıdan görsel dosyaları okuyabilir.
- **Görseli Kaydetme**: Düzenlenmiş görseller kaydedilebilir.
- **Resmi Griye Çevirme veya Gri Tonda Okuma**: Kullanıcı görüntüyü gri tonlu olarak açabilir veya sonradan griye çevirebilir.

## Gereksinimler
Bu projenin çalışabilmesi için aşağıdaki kütüphaneler yüklenmelidir:
```bash
pip install opencv-python numpy pillow matplotlib
```

## Kullanım
1. **Uygulamayı Başlatma:**
    ```bash
    python Goruntu_Isleme.py
    ```
2. **Görüntüyü Yükleyin:** "Görüntü Yükle" butonuna tıklayarak bir resim seçin.
3. **Dönüşümleri Uygulayın:** Uygun butonlara basarak gri tonlama, negatif alma, histogram eşitleme gibi işlemleri gerçekleştirin.
4. **Filtreleme ve Kenar Tespiti:** Gaussian, Median, Sobel veya Canny işlemlerini uygulayabilirsiniz.
5. **Dönüştürülmüş Görüntüyü Kaydedin:** "Görüntü Kaydet" butonu ile yeni görüntüyü bilgisayarınıza kaydedebilirsiniz.

## Katkıda Bulunma
Projeye katkıda bulunmak için:
1. Bu repoyu forklayın.
2. Yeni özellik ekleyin veya hata düzeltin.
3. Pull request gönderin.





