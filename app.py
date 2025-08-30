#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Satınalma Süreci Analiz Asistanı - Web Uygulaması
Flask tabanlı modern web arayüzü
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, flash, redirect, url_for
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from satinalma_analiz import SatinalmaAnalizAsistani
import uuid
import threading
import time

app = Flask(__name__)
app.secret_key = 'satinalma_analiz_secret_key_2024'

# Konfigürasyon
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Upload klasörünü oluştur
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global değişkenler
analiz_asistani = SatinalmaAnalizAsistani()
analiz_sonuclari = {}  # Analiz sonuçlarını saklamak için

def allowed_file(filename):
    """Dosya uzantısı kontrolü"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

def format_currency(amount, currency='USD'):
    """Para formatı - Türk sayı formatında"""
    return f"{format_number_tr(amount)} {currency}"

def get_risk_color(kategori):
    """Risk kategorisine göre renk döndürür"""
    colors = {
        'Ticari Risk': '#e74c3c',
        'Etik Risk': '#f39c12', 
        'Yasal Risk': '#c0392b'
    }
    return colors.get(kategori, '#95a5a6')

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """PDF dosyası yükleme"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Dosya seçilmedi'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Dosya seçilmedi'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Sadece PDF dosyaları kabul edilir'}), 400
        
        # Güvenli dosya adı oluştur
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{filename}")
        
        # Dosyayı kaydet
        file.save(file_path)
        
        # Analizi başlat (arka planda)
        thread = threading.Thread(
            target=analyze_pdf_background, 
            args=(file_path, unique_id, filename)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'file_id': unique_id,
            'filename': filename,
            'message': 'Dosya yüklendi, analiz başlatıldı'
        })
    
    except Exception as e:
        return jsonify({'error': f'Yükleme hatası: {str(e)}'}), 500

def analyze_pdf_background(file_path, file_id, filename):
    """PDF analizini arka planda yapar"""
    try:
        # Analiz durumunu güncelle
        analiz_sonuclari[file_id] = {
            'status': 'analyzing',
            'filename': filename,
            'start_time': datetime.now(),
            'progress': 0
        }
        
        # Analizi yap
        time.sleep(1)  # UI için kısa bekleme
        analiz_sonuclari[file_id]['progress'] = 25
        
        sonuc = analiz_asistani.pdf_analiz_et(file_path)
        analiz_sonuclari[file_id]['progress'] = 75
        
        # Sonuçları formatla
        formatted_result = {
            'status': 'completed',
            'filename': filename,
            'start_time': analiz_sonuclari[file_id]['start_time'],
            'end_time': datetime.now(),
            'progress': 100,
            'satinalma_karari': sonuc.satinalma_karari,
            'risk_sayisi': len(sonuc.risk_tespitleri),
            'risk_tespitleri': [
                {
                    'kategori': risk.kategori,
                    'ifade': risk.ifade,
                    'aciklama': risk.aciklama,
                    'satir_no': risk.satir_no,
                    'color': get_risk_color(risk.kategori)
                } for risk in sonuc.risk_tespitleri
            ],
            'onay_mercii': sonuc.onay_mercii,
            'toplam_alim_degeri': sonuc.toplam_alim_degeri,
            'para_birimi': sonuc.para_birimi,
            'formatted_amount': format_currency(sonuc.toplam_alim_degeri, sonuc.para_birimi),
            'alim_tipi': sonuc.alim_tipi,
            'sozlesme_suresi': sonuc.sozlesme_suresi,
            'onay_kurgusu': sonuc.onay_kurgusu,
            'ozet': sonuc.ozet,
            'rapor': analiz_asistani.rapor_olustur(sonuc)
        }
        
        analiz_sonuclari[file_id] = formatted_result
        
        # Dosyayı temizle
        try:
            os.remove(file_path)
        except:
            pass
            
    except Exception as e:
        analiz_sonuclari[file_id] = {
            'status': 'error',
            'filename': filename,
            'error': str(e),
            'end_time': datetime.now()
        }

@app.route('/status/<file_id>')
def get_analysis_status(file_id):
    """Analiz durumunu döndürür"""
    if file_id not in analiz_sonuclari:
        return jsonify({'error': 'Analiz bulunamadı'}), 404
    
    result = analiz_sonuclari[file_id].copy()
    
    # Datetime objelerini string'e çevir
    if 'start_time' in result:
        result['start_time'] = result['start_time'].strftime('%H:%M:%S')
    if 'end_time' in result:
        result['end_time'] = result['end_time'].strftime('%H:%M:%S')
    
    return jsonify(result)

@app.route('/result/<file_id>')
def show_result(file_id):
    """Analiz sonucunu gösterir"""
    if file_id not in analiz_sonuclari:
        flash('Analiz sonucu bulunamadı', 'error')
        return redirect(url_for('index'))
    
    result = analiz_sonuclari[file_id]
    
    if result['status'] != 'completed':
        flash('Analiz henüz tamamlanmadı', 'warning')
        return redirect(url_for('index'))
    
    return render_template('result.html', result=result, file_id=file_id)

@app.route('/download/<file_id>')
def download_report(file_id):
    """Raporu indir"""
    if file_id not in analiz_sonuclari:
        return jsonify({'error': 'Rapor bulunamadı'}), 404
    
    result = analiz_sonuclari[file_id]
    
    if result['status'] != 'completed':
        return jsonify({'error': 'Analiz tamamlanmadı'}), 400
    
    # Raporu dosyaya yaz
    report_filename = f"analiz_raporu_{file_id}.txt"
    report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(result['rapor'])
    
    return send_from_directory(
        app.config['UPLOAD_FOLDER'], 
        report_filename, 
        as_attachment=True,
        download_name=f"satinalma_analiz_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for analysis"""
    try:
        data = request.get_json()
        
        if 'file_id' not in data:
            return jsonify({'error': 'file_id gerekli'}), 400
        
        file_id = data['file_id']
        
        if file_id not in analiz_sonuclari:
            return jsonify({'error': 'Analiz bulunamadı'}), 404
        
        return jsonify(analiz_sonuclari[file_id])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Sağlık kontrolü"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Template filters
@app.template_filter('datetime')
def datetime_filter(dt):
    if isinstance(dt, str):
        return dt
    return dt.strftime('%d.%m.%Y %H:%M:%S')

@app.template_filter('currency')
def currency_filter(amount, currency='USD'):
    return format_currency(amount, currency)

@app.template_filter('number_tr')
def number_tr_filter(number):
    """Sayıyı Türk formatına çevirir (binlik nokta, ondalık virgül)"""
    return format_number_tr(number)

# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Dosya çok büyük (max 16MB)'}), 413

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Satınalma Analiz Web Uygulaması başlatılıyor...")
    print(f"📱 Port: {port}")
    app.run(debug=False, host='0.0.0.0', port=port)