# Satınalma Süreci Analiz Asistanı

PDF onay formlarını analiz ederek satınalma kararlarını çıkaran, risk analizi yapan ve onay mercii belirleyen Python uygulaması.

## 🎯 Özellikler

### 1. PDF Analizi
- PDF'den "Satınalma Kararı" bölümünü otomatik çıkarma
- Türkçe ve İngilizce metin desteği
- Çoklu PDF okuma kütüphanesi desteği (PyPDF2 + pdfplumber)

### 2. Risk Analizi
Otomatik risk kategorileri tespiti:
- **Ticari Riskler**: Ambargo, kartel, fiyat manipülasyonu, tek tedarikçiye bağımlılık
- **Etik Riskler**: Rüşvet, çıkar çatışması, kayırmacılık, şeffaflık eksikliği
- **Yasal Riskler**: Yasadışı işlemler, rekabet ihlali, dolandırıcılık, mevzuata aykırılık

### 3. Onay Kurgusu Kontrolü
Toplam alım değerine göre otomatik onay mercii belirleme:
- 0 – 1.000 USD → Satınalmacı
- 1.001 – 5.000 USD → Şef / Kategori Yöneticisi
- 5.001 – 75.000 USD → Müdür / Bölge Müdürü
- 75.001 – 150.000 USD → Direktör
- 150.001 – 400.000 USD → Kıdemli Direktör
- 400.001 – 600.000 USD → Genel Müdür Yardımcısı
- 600.001 USD ve üzeri → Genel Müdür

### 4. Satınalma Kararı Özeti
Otomatik özet çıkarma:
- Tedarikçi bilgileri
- Kabul edilen teklif detayları
- Toplam alım değeri ve para birimi
- Teslimat/vade/ödeme koşulları
- Önemli tarihler
- Sözleşme bilgileri
- Risk potansiyeli olan ifadeler

## 🚀 Kurulum

### Gereksinimler
- Python 3.7+
- Windows/Linux/macOS

### Adım 1: Depoyu İndirin
```bash
git clone <repository-url>
cd onayformukontrol
```

### Adım 2: Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### Adım 3: Test Edin
```bash
python satinalma_analiz.py
```

## 💻 Kullanım

### GUI Arayüzü (Önerilen)
```bash
python gui_arayuz.py
```

**Özellikler:**
- Dosya seçme dialogu
- İlerleme çubuğu
- Sonuçları görüntüleme
- Rapor kaydetme
- Kullanıcı dostu arayüz

### Komut Satırı Arayüzü

#### Temel Kullanım
```bash
python cli_arayuz.py onay_formu.pdf
```

#### Gelişmiş Seçenekler
```bash
# Raporu dosyaya kaydet
python cli_arayuz.py -o rapor.txt onay_formu.pdf

# Sadece risk tespitlerini göster
python cli_arayuz.py --only-risks onay_formu.pdf

# JSON formatında çıktı
python cli_arayuz.py --json onay_formu.pdf

# Detaylı çıktı
python cli_arayuz.py -v onay_formu.pdf
```

#### Etkileşimli Mod
```bash
python cli_arayuz.py
```

### Python Kodu İçinde Kullanım
```python
from satinalma_analiz import SatinalmaAnalizAsistani

# Asistanı başlat
asistan = SatinalmaAnalizAsistani()

# PDF'i analiz et
sonuc = asistan.pdf_analiz_et('onay_formu.pdf')

# Rapor oluştur
rapor = asistan.rapor_olustur(sonuc)
print(rapor)

# Sonuç verilerine erişim
print(f"Risk sayısı: {len(sonuc.risk_tespitleri)}")
print(f"Onay mercii: {sonuc.onay_mercii}")
print(f"Toplam değer: {sonuc.toplam_alim_degeri} {sonuc.para_birimi}")
```

## 📊 Çıktı Formatı

### Standart Rapor
```
============================================================
                SATINALMA SÜRECİ ANALİZ RAPORU
============================================================
Analiz Tarihi: 15.01.2024 14:30

1. SATINALMA KARARI (Çıkarılan Metin)
----------------------------------------
[Çıkarılan satınalma kararı metni]

2. RİSK TESPİTLERİ
----------------------------------------
1. Ticari Risk
   İfade: [Risk içeren cümle]
   Açıklama: [Risk açıklaması]
   Satır: 15

3. ONAY MERCİİ
----------------------------------------
Toplam Alım Değeri: 25,000.00 USD
Bu ihalenin onay mercii: Müdür / Bölge Müdürü

4. SATINALMA KARARI ÖZETİ
----------------------------------------
• Tedarikçi Bilgileri: [Özet]
• Kabul Edilen Teklif: [Özet]
• Toplam Deger: [Özet]
```

### JSON Çıktısı
```json
{
  "analiz_tarihi": "2024-01-15T14:30:00",
  "satinalma_karari": "[Metin]",
  "risk_tespitleri": [
    {
      "kategori": "Ticari Risk",
      "ifade": "[Cümle]",
      "aciklama": "[Açıklama]",
      "satir_no": 15
    }
  ],
  "onay_mercii": "Müdür / Bölge Müdürü",
  "toplam_alim_degeri": 25000.0,
  "para_birimi": "USD",
  "ozet": {
    "tedarikci_bilgileri": "[Özet]",
    "kabul_edilen_teklif": "[Özet]"
  }
}
```

## 🔧 Yapılandırma

### Risk Kelimelerini Özelleştirme
`satinalma_analiz.py` dosyasında risk kategorilerini düzenleyebilirsiniz:

```python
self.ticari_riskler = [
    'ambargo', 'kartel', 'fiyat manipülasyonu',
    # Yeni kelimeler ekleyin
]
```

### Onay Limitlerini Değiştirme
```python
self.onay_limitleri = [
    (0, 1000, "Satınalmacı"),
    # Yeni limitler ekleyin
]
```

## 🐛 Sorun Giderme

### PDF Okuma Sorunları
- PDF'nin metin tabanlı olduğundan emin olun (taranmış görüntü değil)
- Farklı PDF kütüphaneleri denenecektir (PyPDF2 → pdfplumber)
- PDF şifreli ise şifreyi kaldırın

### Encoding Sorunları
- Türkçe karakterler için UTF-8 encoding kullanılır
- Windows'ta terminal encoding sorunları için `chcp 65001` komutunu çalıştırın

### Bağımlılık Sorunları
```bash
# Tüm bağımlılıkları yeniden yükle
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## 📞 Destek

Sorularınız için issue açabilir veya iletişime geçebilirsiniz.

---

**Not**: Bu sistem denetim ve uyumluluk amaçlı geliştirilmiştir. Sonuçlar insan denetiminden geçirilmelidir.