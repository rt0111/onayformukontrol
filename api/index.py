#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel Serverless Function için Flask App
"""

import sys
import os
import tempfile

# Ana dizini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Vercel için geçici dosya dizini ayarla
if not os.path.exists('/tmp'):
    os.makedirs('/tmp', exist_ok=True)

# Upload klasörünü /tmp altında oluştur
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from app import app

# Vercel için upload klasörünü güncelle
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Vercel için app export
application = app

if __name__ == "__main__":
    app.run()