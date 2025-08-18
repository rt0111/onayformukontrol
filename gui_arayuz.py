#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Satınalma Süreci Analiz Asistanı - GUI Arayüzü
Tkinter tabanlı kullanıcı dostu arayüz
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
from satinalma_analiz import SatinalmaAnalizAsistani

class SatinalmaAnalizGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Satınalma Süreci Analiz Asistanı")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Analiz asistanını başlat
        self.asistan = SatinalmaAnalizAsistani()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Kullanıcı arayüzünü oluşturur"""
        # Ana başlık
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', padx=10, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="Satınalma Süreci Analiz Asistanı",
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(expand=True)
        
        # Dosya seçim bölümü
        file_frame = tk.LabelFrame(self.root, text="PDF Dosya Seçimi", font=('Arial', 12, 'bold'))
        file_frame.pack(fill='x', padx=10, pady=5)
        
        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.file_path_var, font=('Arial', 10), width=70)
        file_entry.pack(side='left', padx=10, pady=10, fill='x', expand=True)
        
        browse_btn = tk.Button(
            file_frame, 
            text="Dosya Seç", 
            command=self.browse_file,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=12
        )
        browse_btn.pack(side='right', padx=10, pady=10)
        
        # Analiz butonu
        analyze_btn = tk.Button(
            self.root,
            text="ANALİZ BAŞLAT",
            command=self.start_analysis,
            bg='#27ae60',
            fg='white',
            font=('Arial', 14, 'bold'),
            height=2
        )
        analyze_btn.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.root, 
            mode='indeterminate',
            length=400
        )
        self.progress.pack(pady=5)
        
        # Sonuç alanı
        result_frame = tk.LabelFrame(self.root, text="Analiz Sonuçları", font=('Arial', 12, 'bold'))
        result_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Sonuç metni için scrolled text
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            font=('Courier New', 10),
            bg='#ffffff',
            fg='#2c3e50'
        )
        self.result_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Alt butonlar
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        save_btn = tk.Button(
            button_frame,
            text="Raporu Kaydet",
            command=self.save_report,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 10, 'bold')
        )
        save_btn.pack(side='left', padx=5)
        
        clear_btn = tk.Button(
            button_frame,
            text="Temizle",
            command=self.clear_results,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 10, 'bold')
        )
        clear_btn.pack(side='left', padx=5)
        
        # Durum çubuğu
        self.status_var = tk.StringVar()
        self.status_var.set("Hazır - PDF dosyası seçin ve analiz başlatın")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=('Arial', 9)
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_file(self):
        """PDF dosyası seçme dialogu"""
        file_path = filedialog.askopenfilename(
            title="PDF Dosyası Seçin",
            filetypes=[("PDF Dosyaları", "*.pdf"), ("Tüm Dosyalar", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.status_var.set(f"Dosya seçildi: {os.path.basename(file_path)}")
    
    def start_analysis(self):
        """Analizi başlatır"""
        file_path = self.file_path_var.get()
        
        if not file_path:
            messagebox.showerror("Hata", "Lütfen önce bir PDF dosyası seçin!")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("Hata", "Seçilen dosya bulunamadı!")
            return
        
        # Analizi ayrı thread'de çalıştır
        self.progress.start()
        self.status_var.set("Analiz yapılıyor...")
        
        analysis_thread = threading.Thread(target=self.run_analysis, args=(file_path,))
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def run_analysis(self, file_path):
        """Analizi çalıştırır (thread içinde)"""
        try:
            # Analizi yap
            sonuc = self.asistan.pdf_analiz_et(file_path)
            rapor = self.asistan.rapor_olustur(sonuc)
            
            # UI'yi güncelle (main thread'de)
            self.root.after(0, self.update_results, rapor)
            
        except Exception as e:
            error_msg = f"Analiz sırasında hata oluştu:\n{str(e)}"
            self.root.after(0, self.show_error, error_msg)
    
    def update_results(self, rapor):
        """Sonuçları günceller"""
        self.progress.stop()
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, rapor)
        self.status_var.set("Analiz tamamlandı")
    
    def show_error(self, error_msg):
        """Hata mesajını gösterir"""
        self.progress.stop()
        self.status_var.set("Analiz hatası")
        messagebox.showerror("Analiz Hatası", error_msg)
    
    def save_report(self):
        """Raporu dosyaya kaydeder"""
        content = self.result_text.get(1.0, tk.END).strip()
        
        if not content:
            messagebox.showwarning("Uyarı", "Kaydedilecek rapor bulunamadı!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Raporu Kaydet",
            defaultextension=".txt",
            filetypes=[("Metin Dosyaları", "*.txt"), ("Tüm Dosyalar", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Başarılı", f"Rapor kaydedildi:\n{file_path}")
                self.status_var.set(f"Rapor kaydedildi: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Hata", f"Rapor kaydedilemedi:\n{str(e)}")
    
    def clear_results(self):
        """Sonuçları temizler"""
        self.result_text.delete(1.0, tk.END)
        self.file_path_var.set("")
        self.status_var.set("Hazır - PDF dosyası seçin ve analiz başlatın")

def main():
    """Ana fonksiyon"""
    root = tk.Tk()
    app = SatinalmaAnalizGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()