#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Satınalma Süreci Analiz Asistanı - Komut Satırı Arayüzü
Terminal tabanlı kullanım için
"""

import sys
import os
import argparse
from datetime import datetime
from satinalma_analiz import SatinalmaAnalizAsistani

def format_number_tr(number):
    """Sayıyı Türk formatına çevirir (binlik nokta, ondalık virgül)"""
    if number is None:
        return "0,00"
    
    # Sayıyı string'e çevir
    formatted = f"{number:,.2f}"
    
    # İngilizce formatı (1,234.56) -> Türk formatına (1.234,56) çevir
    # Önce ondalık kısmı ayır
    if '.' in formatted:
        integer_part, decimal_part = formatted.rsplit('.', 1)
        # Binlik ayırıcıları değiştir: virgül -> nokta
        integer_part = integer_part.replace(',', '.')
        # Türk formatında birleştir: nokta binlik, virgül ondalık
        return f"{integer_part},{decimal_part}"
    else:
        # Ondalık kısım yok, sadece binlik ayırıcıları değiştir
        return formatted.replace(',', '.') + ",00"

def print_banner():
    """Program başlık banner'ını yazdırır"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║              SATINALMA SÜRECİ ANALİZ ASİSTANI              ║
║                     Versiyon 1.0                            ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_help():
    """Yardım bilgilerini yazdırır"""
    help_text = """
KULLANIM:
    python cli_arayuz.py [SEÇENEKLER] <PDF_DOSYASI>

SEÇENEKLER:
    -h, --help              Bu yardım mesajını göster
    -o, --output FILE       Raporu belirtilen dosyaya kaydet
    -v, --verbose           Detaylı çıktı
    --only-risks           Sadece risk tespitlerini göster
    --only-summary         Sadece özeti göster
    --json                 JSON formatında çıktı

ÖRNEKLER:
    python cli_arayuz.py onay_formu.pdf
    python cli_arayuz.py -o rapor.txt onay_formu.pdf
    python cli_arayuz.py --only-risks onay_formu.pdf
    python cli_arayuz.py --json onay_formu.pdf
"""
    print(help_text)

def format_json_output(sonuc):
    """Sonucu JSON formatında döndürür"""
    import json
    
    # Risk tespitlerini dict'e çevir
    riskler = []
    for risk in sonuc.risk_tespitleri:
        riskler.append({
            "kategori": risk.kategori,
            "ifade": risk.ifade,
            "aciklama": risk.aciklama,
            "satir_no": risk.satir_no
        })
    
    json_data = {
        "analiz_tarihi": datetime.now().isoformat(),
        "satinalma_karari": sonuc.satinalma_karari,
        "risk_tespitleri": riskler,
        "onay_mercii": sonuc.onay_mercii,
        "toplam_alim_degeri": sonuc.toplam_alim_degeri,
        "para_birimi": sonuc.para_birimi,
        "ozet": sonuc.ozet
    }
    
    return json.dumps(json_data, ensure_ascii=False, indent=2)

def format_risks_only(sonuc):
    """Sadece risk tespitlerini formatlar"""
    output = []
    output.append("RİSK TESPİTLERİ")
    output.append("=" * 50)
    
    if sonuc.risk_tespitleri:
        for i, risk in enumerate(sonuc.risk_tespitleri, 1):
            output.append(f"{i}. {risk.kategori}")
            output.append(f"   İfade: {risk.ifade}")
            output.append(f"   Açıklama: {risk.aciklama}")
            output.append(f"   Satır: {risk.satir_no}")
            output.append("")
    else:
        output.append("Risk tespit edilmedi.")
    
    return "\n".join(output)

def format_summary_only(sonuc):
    """Sadece özeti formatlar"""
    output = []
    output.append("SATINALMA KARARI ÖZETİ")
    output.append("=" * 50)
    
    output.append(f"Toplam Alım Değeri: {format_number_tr(sonuc.toplam_alim_degeri)} {sonuc.para_birimi}")
    output.append(f"Onay Mercii: {sonuc.onay_mercii}")
    output.append("")
    
    for baslik, icerik in sonuc.ozet.items():
        if icerik.strip():
            output.append(f"• {baslik.replace('_', ' ').title()}: {icerik.strip()}")
    
    return "\n".join(output)

def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(
        description="Satınalma Süreci Analiz Asistanı",
        add_help=False
    )
    
    parser.add_argument('pdf_file', nargs='?', help='Analiz edilecek PDF dosyası')
    parser.add_argument('-h', '--help', action='store_true', help='Yardım mesajını göster')
    parser.add_argument('-o', '--output', help='Çıktı dosyası')
    parser.add_argument('-v', '--verbose', action='store_true', help='Detaylı çıktı')
    parser.add_argument('--only-risks', action='store_true', help='Sadece risk tespitleri')
    parser.add_argument('--only-summary', action='store_true', help='Sadece özet')
    parser.add_argument('--json', action='store_true', help='JSON formatında çıktı')
    
    args = parser.parse_args()
    
    # Yardım göster
    if args.help or not args.pdf_file:
        print_banner()
        print_help()
        return
    
    # PDF dosyası kontrolü
    if not os.path.exists(args.pdf_file):
        print(f"❌ Hata: PDF dosyası bulunamadı: {args.pdf_file}")
        return 1
    
    if args.verbose:
        print_banner()
        print(f"📄 PDF Dosyası: {args.pdf_file}")
        print(f"⏰ Analiz Başlangıcı: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print("🔍 Analiz yapılıyor...\n")
    
    try:
        # Analiz asistanını başlat
        asistan = SatinalmaAnalizAsistani()
        
        # Analizi yap
        sonuc = asistan.pdf_analiz_et(args.pdf_file)
        
        # Çıktı formatını belirle
        if args.json:
            output = format_json_output(sonuc)
        elif args.only_risks:
            output = format_risks_only(sonuc)
        elif args.only_summary:
            output = format_summary_only(sonuc)
        else:
            output = asistan.rapor_olustur(sonuc)
        
        # Çıktıyı göster veya kaydet
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"✅ Rapor kaydedildi: {args.output}")
            except Exception as e:
                print(f"❌ Rapor kaydedilemedi: {e}")
                return 1
        else:
            print(output)
        
        if args.verbose:
            print(f"\n✅ Analiz tamamlandı: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
            print(f"📊 Risk Sayısı: {len(sonuc.risk_tespitleri)}")
            print(f"💰 Toplam Değer: {format_number_tr(sonuc.toplam_alim_degeri)} {sonuc.para_birimi}")
            print(f"👤 Onay Mercii: {sonuc.onay_mercii}")
    
    except Exception as e:
        print(f"❌ Analiz hatası: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

def interactive_mode():
    """Etkileşimli mod"""
    print_banner()
    print("🔄 Etkileşimli mod başlatıldı")
    print("Çıkmak için 'quit' veya 'exit' yazın\n")
    
    asistan = SatinalmaAnalizAsistani()
    
    while True:
        try:
            pdf_path = input("📄 PDF dosya yolu girin: ").strip()
            
            if pdf_path.lower() in ['quit', 'exit', 'q']:
                print("👋 Çıkılıyor...")
                break
            
            if not pdf_path:
                continue
            
            if not os.path.exists(pdf_path):
                print(f"❌ Dosya bulunamadı: {pdf_path}\n")
                continue
            
            print("🔍 Analiz yapılıyor...")
            sonuc = asistan.pdf_analiz_et(pdf_path)
            rapor = asistan.rapor_olustur(sonuc)
            
            print("\n" + "="*60)
            print(rapor)
            print("="*60 + "\n")
            
            # Rapor kaydetme seçeneği
            save_choice = input("💾 Raporu dosyaya kaydetmek ister misiniz? (e/h): ").strip().lower()
            if save_choice in ['e', 'evet', 'yes', 'y']:
                output_file = input("📁 Dosya adı girin (örn: rapor.txt): ").strip()
                if output_file:
                    try:
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(rapor)
                        print(f"✅ Rapor kaydedildi: {output_file}\n")
                    except Exception as e:
                        print(f"❌ Kaydetme hatası: {e}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Çıkılıyor...")
            break
        except Exception as e:
            print(f"❌ Hata: {e}\n")

if __name__ == "__main__":
    # Eğer argüman verilmemişse etkileşimli mod
    if len(sys.argv) == 1:
        interactive_mode()
    else:
        sys.exit(main())