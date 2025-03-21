#!/usr/bin/env python3
"""
PDF OCR Converterのセットアップスクリプト
"""
from setuptools import setup, find_packages

setup(
    name="pdf_ocr_converter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pdf2image>=1.16.0",
        "Pillow>=9.0.0",
        "pytesseract>=0.3.8",
        "PyMuPDF>=1.19.0",
        "tqdm>=4.62.0",
        "numpy>=1.20.0",
    ],
    entry_points={
        "console_scripts": [
            "pdf-ocr=pdf_ocr_converter.main:main",
            "pdf-ocr-config=pdf_ocr_converter.config_helper:main",
        ],
    },
    author="PDF OCR Converter Team",
    author_email="example@example.com",
    description="画像PDFからOCRでテキストを抽出し検索可能なPDFを生成するツール",
    keywords="pdf, ocr, text extraction, vertical text",
    python_requires=">=3.6",
)
