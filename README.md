# 🚗 Python Tkinter Araç Kiralama Sistemi

Bu proje, Python ve **Tkinter** arayüz kütüphanesi kullanılarak geliştirilmiş, küçük ve orta ölçekli işletmeler için tasarlanmış bir masaüstü araç kiralama otomasyonudur.

Veritabanı gereksinimi olmadan, tüm verileri yerel bir **JSON** dosyasında (`araclar.json`) tutarak hafif ve taşınabilir bir çözüm sunar. Ayrıca **Matplotlib** kütüphanesi yüklüyse görsel raporlar sunabilir.

---

## 🚀 Özellikler

* **✅ Araç Yönetimi (CRUD):** Yeni araç ekleme, mevcut araçları silme ve bilgilerini güncelleme.
* **📅 Kiralama ve İade Süreçleri:**
    * Müşteri adı ve tarih aralığı ile araç kiralama.
    * Gün sayısına göre otomatik toplam ücret hesaplama.
    * Kiradaki aracı tek tuşla iade alma.
* **🛠️ Durum Takibi:** Araçları "Müsait", "Kirada" veya "Bakımda" olarak işaretleme ve filtreleme.
* **📝 Not Sistemi:** Her araç için özel notlar ekleme ve kaydetme.
* **📊 Raporlama ve Grafikler:**
    * Genel durum özeti ve beklenen ciro raporu.
    * Araç durum dağılımı (Pasta Grafiği - Matplotlib gerektirir).
    * Marka dağılımı analizi (Sütun Grafiği - Matplotlib gerektirir).
* **💾 Veri Kalıcılığı:** Program kapatıldığında veriler otomatik olarak JSON formatında kaydedilir.

---

## 📷 Ekran Görüntüleri

<img width="2879" height="1919" alt="image" src="https://github.com/user-attachments/assets/927ddc97-4f10-4545-b3df-e2dcd59c7f27" />
<img width="789" height="914" alt="image" src="https://github.com/user-attachments/assets/ff4ad7f3-f80d-456b-868c-d08800a2d5e4" />
<img width="567" height="432" alt="image" src="https://github.com/user-attachments/assets/02cc87ea-581d-4066-9a09-fcdf9be75a92" />
<img width="1193" height="1206" alt="image" src="https://github.com/user-attachments/assets/dc488a39-f3ef-4d0a-be15-073e7f9a78b8" />
<img width="1594" height="994" alt="image" src="https://github.com/user-attachments/assets/145ed5a4-707c-4e27-8a06-857be6d37eac" />

---

## 🛠️ Kullanılan Teknolojiler

* **Python 3**
* **Tkinter:** Grafiksel Kullanıcı Arayüzü (GUI) tasarımı için.
* **JSON:** Verilerin yerel olarak saklanması için.
* **Datetime:** Tarih hesaplamaları ve kiralama süresi belirleme için.
* **Matplotlib (Opsiyonel):** Verileri grafiksel olarak görselleştirmek için.

---

## 💻 Kurulum ve Çalıştırma / Installation

1.  Projeyi bilgisayarınıza klonlayın:
    ```bash
    git clone [https://github.com/AhmetEmreOzumagi/Tkinter-Car-Rental-Management.git](https://github.com/AhmetEmreOzumagi/Tkinter-Car-Rental-Management.git)
    ```
2.  Proje dizinine gidin.
3.  **(Opsiyonel)** Grafik özelliklerini kullanabilmek için `matplotlib` kütüphanesini yükleyin:
    ```bash
    pip install matplotlib
    ```
4.  Uygulamayı çalıştırın:
    ```bash
    python main.py
    ```

---

## 📞 İletişim

* **Geliştirici:** Ahmet Emre Özümağı/ Elif Büşra Çaylan
* **LinkedIn:** https://www.linkedin.com/in/ahmet-emre-%C3%B6z%C3%BCma%C4%9F%C4%B1-46067431b/
