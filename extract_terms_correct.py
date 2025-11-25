#!/usr/bin/env python3
"""
Correct extraction of morphological terms with proper definitions
"""
import json
import os
import re
from pathlib import Path
from collections import defaultdict

DATA_DIR = "data"
OUTPUT_DIR = "data/organized"

def extract_terms_with_definitions(text_content, filename):
    """Extract terms with their actual definitions"""
    terms = []
    
    # Pattern to match:
    # Term Name
    # Definition: Definition text. [objective/subjective]
    #   Comment: Comment text (optional)
    
    # First, let's find all term blocks
    # A term block starts with a capitalized term name and contains "Definition:"
    pattern = r'^([A-Z][A-Za-z,\s\-()\']+?)\s*\n+Definition:\s+(.+?)(?=\n\s*(?:[A-Z][A-Za-z,\s\-()\']+?\s*\n+Definition:|\Z))'
    
    matches = re.finditer(pattern, text_content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        term_name = match.group(1).strip()
        definition_block = match.group(2).strip()
        
        # Clean term name
        term_name = ' '.join(term_name.split())
        
        # Extract the actual definition (before "Comment:" if present)
        if 'Comment:' in definition_block:
            parts = definition_block.split('Comment:', 1)
            definition = parts[0].strip()
            comment = parts[1].strip()
        else:
            definition = definition_block
            comment = None
        
        # Clean definition
        definition = ' '.join(definition.split())
        
        # Remove objective/subjective markers from end
        definition = re.sub(r'\s+(objective|subjective)\s*$', '', definition, flags=re.IGNORECASE)
        
        # Validation
        if (term_name and definition and 
            len(term_name) < 100 and 
            len(term_name.split()) <= 15 and
            len(definition) > 10 and
            not term_name.startswith('http') and
            not term_name.startswith('www') and
            not term_name.startswith('DOI') and
            not term_name.startswith('Fig') and
            not term_name.startswith('Table') and
            'Copyright' not in term_name and
            'Received' not in term_name and
            '@' not in term_name and
            term_name != 'Definition' and
            term_name != 'Comment' and
            term_name != 'Synonym'):
            
            term_dict = {
                'term': term_name,
                'definition': definition[:1500],  # Limit length
                'source': os.path.basename(filename)
            }
            
            if comment and len(comment) > 10:
                term_dict['comment'] = comment[:500]
            
            terms.append(term_dict)
    
    return terms

def categorize_by_topic(filename):
    """Determine the anatomical topic from filename"""
    name_lower = filename.lower()
    
    topics = {
        'ear': ['ear', 'auricul'],
        'head_face': ['head', 'face', 'facial', 'cranium'],
        'nose_philtrum': ['nose', 'philtrum', 'nasal'],
        'lips_mouth': ['lip', 'mouth', 'oral'],
        'periorbital': ['periorbital', 'eye', 'eyelid'],
        'hands_feet': ['hand', 'feet', 'finger', 'toe', 'nail'],
        'genitalia': ['genital'],
        'teeth': ['teeth', 'dental', 'tooth', 'dent'],
        'introduction': ['introduction'],
        'phenotypic_variations': ['phenotypic', 'variation'],
    }
    
    for topic, keywords in topics.items():
        for keyword in keywords:
            if keyword in name_lower:
                return topic
    
    return 'general'

def main():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    # Load metadata
    with open(f"{DATA_DIR}/extraction_metadata.json", 'r') as f:
        metadata = json.load(f)
    
    all_terms = []
    terms_by_category = defaultdict(list)
    
    print("="*70)
    print("🔍 EXTRACCIÓN CORRECTA DE TÉRMINOS Y DEFINICIONES")
    print("="*70)
    print()
    
    for item in metadata:
        text_file = item['text_file']
        
        if not os.path.exists(text_file):
            continue
        
        filename = os.path.basename(text_file)
        print(f"📄 {filename[:65]}")
        
        # Read text
        with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
            text_content = f.read()
        
        # Extract terms
        terms = extract_terms_with_definitions(text_content, text_file)
        
        if terms:
            category = categorize_by_topic(item['original_filename'])
            
            for term in terms:
                term['category'] = category
                term['document'] = item['original_filename'].replace('.pdf', '')
                all_terms.append(term)
                terms_by_category[category].append(term)
            
            print(f"   ✅ {len(terms)} términos extraídos")
            # Show sample
            if terms:
                sample = terms[0]
                print(f"   📝 Ejemplo: {sample['term']}")
                print(f"      Def: {sample['definition'][:80]}...")
        else:
            print(f"   ⚠️  No se encontraron términos")
        print()
    
    # Remove duplicates
    seen = set()
    unique_terms = []
    for term in all_terms:
        key = (term['term'].lower().strip(), term['category'])
        if key not in seen:
            seen.add(key)
            unique_terms.append(term)
    
    # Sort
    unique_terms.sort(key=lambda x: (x['category'], x['term'].lower()))
    
    # Save all terms
    terms_file = f"{OUTPUT_DIR}/morphology_terms_corrected.json"
    with open(terms_file, 'w', encoding='utf-8') as f:
        json.dump(unique_terms, f, indent=2, ensure_ascii=False)
    
    # Save by category
    categories_dict = {}
    for cat in set(t['category'] for t in unique_terms):
        cat_terms = [t for t in unique_terms if t['category'] == cat]
        categories_dict[cat] = sorted(cat_terms, key=lambda x: x['term'].lower())
    
    categories_file = f"{OUTPUT_DIR}/terms_by_category_corrected.json"
    with open(categories_file, 'w', encoding='utf-8') as f:
        json.dump(categories_dict, f, indent=2, ensure_ascii=False)
    
    # Create index
    index = {
        'total_terms': len(unique_terms),
        'categories': {cat: len(terms) for cat, terms in categories_dict.items()},
        'sample_terms': [t['term'] for t in unique_terms[:30]]
    }
    
    index_file = f"{OUTPUT_DIR}/terms_index_corrected.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print("="*70)
    print("✅ EXTRACCIÓN COMPLETADA")
    print("="*70)
    print()
    print(f"📊 Estadísticas:")
    print(f"   • Total términos únicos: {len(unique_terms)}")
    print(f"   • Categorías: {len(categories_dict)}")
    print()
    print(f"📂 Términos por categoría:")
    for cat, terms in sorted(categories_dict.items(), key=lambda x: len(x[1]), reverse=True):
        emoji = {'ear': '👂', 'head_face': '👤', 'nose_philtrum': '👃', 
                 'lips_mouth': '👄', 'hands_feet': '✋', 'teeth': '🦷',
                 'periorbital': '👁️', 'genitalia': '🔬', 'general': '📚',
                 'phenotypic_variations': '🧬', 'introduction': '📖'}.get(cat, '📝')
        print(f"   {emoji} {cat:25} : {len(terms):4} términos")
    print()
    print(f"💾 Archivos generados:")
    print(f"   • {terms_file}")
    print(f"   • {categories_file}")
    print(f"   • {index_file}")
    print()
    print(f"🔍 Ejemplos de términos extraídos:")
    for i, term in enumerate(unique_terms[:5], 1):
        print(f"   {i}. {term['term']}")
        print(f"      → {term['definition'][:100]}...")
        print()

if __name__ == '__main__':
    main()
