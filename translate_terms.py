#!/usr/bin/env python3
"""
Script para traducir términos médicos al español
"""
import json
import os
import time
from deep_translator import GoogleTranslator

def translate_text(text, max_retries=3):
    """Traduce texto al español con reintentos"""
    if not text or text.strip() == "":
        return text
    
    # Texto demasiado corto o ya en español
    if len(text) < 3:
        return text
    
    for attempt in range(max_retries):
        try:
            translator = GoogleTranslator(source='en', target='es')
            # Dividir textos largos en chunks
            if len(text) > 4500:
                chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
                translated_chunks = []
                for chunk in chunks:
                    translated_chunks.append(translator.translate(chunk))
                    time.sleep(0.5)
                return ' '.join(translated_chunks)
            else:
                result = translator.translate(text)
                time.sleep(0.3)  # Evitar rate limiting
                return result
        except Exception as e:
            print(f"Error en intento {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print(f"No se pudo traducir: {text[:50]}...")
                return text
    
    return text

def translate_term_entry(entry, index, total):
    """Traduce una entrada de término"""
    print(f"[{index}/{total}] Traduciendo: {entry.get('term', 'Unknown')}")
    
    translated = entry.copy()
    
    # Traducir definición
    if 'definition' in entry and entry['definition']:
        print(f"  - Traduciendo definición...")
        translated['definition'] = translate_text(entry['definition'])
    
    # Traducir comentario
    if 'comment' in entry and entry['comment']:
        print(f"  - Traduciendo comentario...")
        translated['comment'] = translate_text(entry['comment'])
    
    # Traducir categoría
    if 'category' in entry and entry['category']:
        category_map = {
            'periorbital': 'periorbital',
            'ear': 'oído',
            'nose': 'nariz',
            'mouth': 'boca',
            'lips': 'labios',
            'head': 'cabeza',
            'face': 'cara',
            'hands': 'manos',
            'feet': 'pies',
            'external_genitalia': 'genitales_externos',
            'teeth': 'dientes',
            'general': 'general'
        }
        translated['category'] = category_map.get(entry['category'], entry['category'])
    
    return translated

def translate_json_file(input_file, output_file):
    """Traduce un archivo JSON completo"""
    print(f"\n{'='*60}")
    print(f"Procesando: {input_file}")
    print(f"{'='*60}\n")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict):
        translated_data = {}
        for category, entries in data.items():
            print(f"\n--- Categoría: {category} ({len(entries)} términos) ---")
            translated_entries = []
            for i, entry in enumerate(entries, 1):
                translated_entry = translate_term_entry(entry, i, len(entries))
                translated_entries.append(translated_entry)
            translated_data[category] = translated_entries
    elif isinstance(data, list):
        print(f"Total de términos: {len(data)}")
        translated_data = []
        for i, entry in enumerate(data, 1):
            translated_entry = translate_term_entry(entry, i, len(data))
            translated_data.append(translated_entry)
    else:
        translated_data = data
    
    # Guardar resultado
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Guardado en: {output_file}\n")

def main():
    data_dir = '/home/arkantu/docker/morphology-atlas/data/organized'
    
    # Archivos a traducir
    files_to_translate = [
        'morphology_terms.json',
        'terms_by_category_corrected.json',
        'morphology_terms_corrected.json'
    ]
    
    for filename in files_to_translate:
        input_path = os.path.join(data_dir, filename)
        if os.path.exists(input_path):
            # Crear backup
            backup_path = input_path + '.backup_en'
            if not os.path.exists(backup_path):
                import shutil
                shutil.copy2(input_path, backup_path)
                print(f"Backup creado: {backup_path}")
            
            # Traducir
            translate_json_file(input_path, input_path)
        else:
            print(f"Archivo no encontrado: {input_path}")
    
    print("\n" + "="*60)
    print("✓ Traducción completada!")
    print("="*60)

if __name__ == "__main__":
    main()
