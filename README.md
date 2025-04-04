# Image Processing Interface - Görüntü İşleme Arayüzü

📌 Read this in: [English](#description) | [Türkçe](#açıklama)

## Description

This project is an image processing application developed using Tkinter. Users can upload their images to perform various transformations and analyses.

## Features
- **Image Loading**: Users can select and upload image files from their computers.
- **Grayscale Conversion**: Converts the selected image to grayscale.
- **Negative Transformation**: Creates a new version by taking the negative of the image.
- **Histogram Display**: Performs histogram analysis of the image.
- **Histogram Equalization**: Applies histogram equalization process.
- **RGB Channel Separation**: Can display the image by separating it into red, green, and blue channels.
- **Brightness and Contrast Adjustment**: Brightness and contrast adjustments can be made on the image.
- **Thresholding**: The image can be converted to black and white by specifying a threshold value.
- **Filtering**: Gaussian and Median filtering operations can be applied.
- **Edge Detection**: Edges in the image can be detected using Sobel and Canny algorithms.
- **Saving**: Edited images can be saved.
- **Translation**: The image can be moved to different positions.
- **Mirroring**: The image can be mirrored horizontally or vertically.
- **Shearing**: The image can be sheared at a specific angle.
- **Scaling (Zoom In/Out)**: The image can be zoomed in or out.
- **Rotation**: The image can be rotated at specific angles.
- **Cropping**: The image can be cropped by selecting the desired region.
- **External Image Reading**: Users can read image files from external sources.
- **Image Saving**: Edited images can be saved.
- **Grayscale Conversion or Grayscale Reading**: Users can open the image in grayscale or convert it to grayscale later.

## Requirements
This project requires the following libraries to be installed:
```bash
pip install opencv-python numpy pillow matplotlib
```

## Usage
1. **Starting the Application:**
    ```bash
    python Image_Processing.py
    ```
2. **Load an Image:** Click on the "Load Image" button to select an image.
3. **Apply Transformations:** Press the appropriate buttons to perform grayscale conversion, negative transformation, histogram equalization, etc.
4. **Filtering and Edge Detection:** You can apply Gaussian, Median, Sobel, or Canny operations.
5. **Save the Transformed Image:** You can save the new image to your computer using the "Save Image" button.

## Contributing
To contribute to the project:
1. Fork this repository.
2. Add a new feature or fix a bug.
3. Submit a pull request.

## Açıklama

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


