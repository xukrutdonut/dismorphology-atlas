#!/usr/bin/env python3
"""
Extract text and images from Elements of Morphology PDFs
"""
import os
import subprocess
import json
import re
from pathlib import Path

# Directories
PDF_DIR = "pdfs"
DATA_DIR = "data"
IMAGES_DIR = "images"

# Ensure output directories exist
Path(DATA_DIR).mkdir(exist_ok=True)
Path(IMAGES_DIR).mkdir(exist_ok=True)

def sanitize_filename(filename):
    """Create a safe filename from PDF name"""
    # Remove .pdf extension
    name = filename.replace('.pdf', '')
    # Remove common prefixes and clean up
    name = re.sub(r'^.*?(\d{4})\s*-\s*', '', name)
    # Replace spaces and special chars with underscores
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '_', name)
    return name.lower().strip('_')

def extract_text(pdf_path, output_path):
    """Extract text from PDF using pdftotext"""
    try:
        subprocess.run(['pdftotext', '-layout', pdf_path, output_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return False

def extract_images(pdf_path, output_prefix):
    """Extract images from PDF using pdfimages"""
    try:
        # Extract as PNG format
        subprocess.run(['pdfimages', '-png', pdf_path, output_prefix], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting images from {pdf_path}: {e}")
        return False

def main():
    pdf_files = sorted([f for f in os.listdir(PDF_DIR) if f.endswith('.pdf') and not f.startswith('download')])
    
    extracted_data = []
    
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file}")
        
        pdf_path = os.path.join(PDF_DIR, pdf_file)
        safe_name = sanitize_filename(pdf_file)
        
        # Extract text
        text_output = os.path.join(DATA_DIR, f"{safe_name}.txt")
        print(f"  Extracting text to: {text_output}")
        extract_text(pdf_path, text_output)
        
        # Extract images
        image_prefix = os.path.join(IMAGES_DIR, safe_name)
        print(f"  Extracting images with prefix: {image_prefix}")
        extract_images(pdf_path, image_prefix)
        
        # Store metadata
        extracted_data.append({
            'original_filename': pdf_file,
            'safe_name': safe_name,
            'text_file': text_output,
            'image_prefix': image_prefix
        })
    
    # Save metadata
    metadata_path = os.path.join(DATA_DIR, 'extraction_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(extracted_data, f, indent=2)
    
    print(f"\n✓ Extraction complete! Metadata saved to {metadata_path}")
    print(f"  Text files: {DATA_DIR}/")
    print(f"  Images: {IMAGES_DIR}/")

if __name__ == '__main__':
    main()
