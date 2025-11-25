#!/usr/bin/env python3
"""
Verification script to check project completeness
"""
import json
import os
from pathlib import Path

def check_files():
    """Check if all required files exist"""
    print("="*70)
    print("🔍 VERIFICACIÓN DEL PROYECTO MORPHOLOGY ATLAS")
    print("="*70)
    print()
    
    required_files = {
        'Documentación': [
            'README.md',
            'INICIO_RAPIDO.md',
            'RESUMEN_FINAL.md',
            'README_EXTRACTION.md',
        ],
        'Aplicación Web': [
            'index.html',
        ],
        'Scripts': [
            'extract_pdfs.py',
            'extract_terms.py',
            'organize_content.py',
            'create_sample.py',
        ],
        'Datos Organizados': [
            'data/organized/morphology_terms.json',
            'data/organized/terms_by_category.json',
            'data/organized/terms_index.json',
            'data/organized/summary.json',
            'data/organized/content_by_category.json',
            'data/organized/images_catalog.json',
        ]
    }
    
    all_ok = True
    
    for category, files in required_files.items():
        print(f"📂 {category}:")
        for file in files:
            exists = os.path.exists(file)
            status = "✅" if exists else "❌"
            print(f"   {status} {file}")
            if not exists:
                all_ok = False
        print()
    
    return all_ok

def check_data_integrity():
    """Check data files integrity"""
    print("="*70)
    print("📊 VERIFICACIÓN DE INTEGRIDAD DE DATOS")
    print("="*70)
    print()
    
    try:
        # Load terms
        with open('data/organized/morphology_terms.json', 'r') as f:
            terms = json.load(f)
        
        print(f"✅ morphology_terms.json:")
        print(f"   • Total términos: {len(terms)}")
        print(f"   • Primer término: {terms[0]['term']}")
        print(f"   • Último término: {terms[-1]['term']}")
        print()
        
        # Load terms by category
        with open('data/organized/terms_by_category.json', 'r') as f:
            categories = json.load(f)
        
        print(f"✅ terms_by_category.json:")
        print(f"   • Total categorías: {len(categories)}")
        for cat, cat_terms in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
            emoji = {'ear': '👂', 'head_face': '👤', 'nose_philtrum': '👃', 
                     'lips_mouth': '👄', 'hands_feet': '✋', 'teeth': '🦷',
                     'periorbital': '👁️', 'genitalia': '🔬', 'general': '📚',
                     'phenotypic_variations': '🧬', 'introduction': '📖'}.get(cat, '📝')
            print(f"   • {emoji} {cat:25} : {len(cat_terms):3} términos")
        print()
        
        # Load index
        with open('data/organized/terms_index.json', 'r') as f:
            index = json.load(f)
        
        print(f"✅ terms_index.json:")
        print(f"   • Total términos indexados: {index['total_terms']}")
        print()
        
        # Load summary
        with open('data/organized/summary.json', 'r') as f:
            summary = json.load(f)
        
        print(f"✅ summary.json:")
        print(f"   • Total documentos: {summary['total_documents']}")
        print(f"   • Total imágenes: {summary['total_images']}")
        print()
        
        # Load images catalog
        with open('data/organized/images_catalog.json', 'r') as f:
            images = json.load(f)
        
        print(f"✅ images_catalog.json:")
        print(f"   • Total imágenes catalogadas: {len(images)}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar integridad: {e}")
        return False

def check_images():
    """Check images directory"""
    print("="*70)
    print("🖼️  VERIFICACIÓN DE IMÁGENES")
    print("="*70)
    print()
    
    if os.path.exists('images'):
        images = [f for f in os.listdir('images') if f.endswith('.png')]
        print(f"✅ Directorio de imágenes existe")
        print(f"   • Total archivos PNG: {len(images)}")
        print(f"   • Primera imagen: {images[0] if images else 'N/A'}")
        print(f"   • Última imagen: {images[-1] if images else 'N/A'}")
    else:
        print(f"❌ Directorio de imágenes no existe")
        return False
    
    print()
    return True

def check_pdfs():
    """Check PDFs directory"""
    print("="*70)
    print("📄 VERIFICACIÓN DE PDFs")
    print("="*70)
    print()
    
    if os.path.exists('pdfs'):
        pdfs = [f for f in os.listdir('pdfs') if f.endswith('.pdf')]
        print(f"✅ Directorio de PDFs existe")
        print(f"   • Total archivos PDF: {len(pdfs)}")
    else:
        print(f"⚠️  Directorio de PDFs no existe")
    
    print()
    return True

def main():
    """Run all checks"""
    print()
    
    files_ok = check_files()
    data_ok = check_data_integrity()
    images_ok = check_images()
    pdfs_ok = check_pdfs()
    
    print("="*70)
    print("📋 RESUMEN FINAL")
    print("="*70)
    print()
    
    if files_ok and data_ok and images_ok:
        print("✅ ¡PROYECTO COMPLETAMENTE VERIFICADO!")
        print()
        print("🎉 El proyecto Morphology Atlas está listo para usar.")
        print()
        print("📝 Próximos pasos:")
        print("   1. Abre index.html en tu navegador")
        print("   2. O ejecuta: python3 -m http.server 8000")
        print("   3. Luego abre: http://localhost:8000")
        print()
        return 0
    else:
        print("⚠️  ALGUNOS ELEMENTOS NECESITAN ATENCIÓN")
        print()
        if not files_ok:
            print("   • Faltan algunos archivos requeridos")
        if not data_ok:
            print("   • Problemas con la integridad de datos")
        if not images_ok:
            print("   • Problemas con las imágenes")
        print()
        return 1

if __name__ == '__main__':
    exit(main())
