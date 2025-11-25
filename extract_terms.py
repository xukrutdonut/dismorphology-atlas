#!/usr/bin/env python3
"""
Smart extraction handling two-column PDFs
"""
import json
import os
import re
from pathlib import Path
from collections import defaultdict

DATA_DIR = "data"
OUTPUT_DIR = "data/organized"

def split_multicolumn_term(text):
    """Split terms that come from two-column PDFs"""
    # Pattern: "Term1 ... spaces ... Term2"  with "Definition: text"
    # Terms usually have capital letters and may contain commas
    pattern = r'^([A-Z][A-Za-z,\s\-()\']+?)\s{2,}([A-Z][A-Za-z,\s\-()\']+?)$'
    match = re.match(pattern, text)
    if match:
        term1 = match.group(1).strip()
        term2 = match.group(2).strip()
        # Both terms should be reasonable length
        if 3 < len(term1) < 100 and 3 < len(term2) < 100:
            return [term1, term2]
    return [text]

def clean_term(term):
    """Clean and normalize term text"""
    term = ' '.join(term.split())
    term = term.rstrip('.,;:')
    # Remove "Definition" suffix if present
    term = re.sub(r'\s+Definition\s*$', '', term, flags=re.IGNORECASE)
    return term

def clean_definition(definition):
    """Clean and normalize definition text"""
    definition = ' '.join(definition.split())
    # Remove leading "Definition:" or "Definition."
    definition = re.sub(r'^Definition[:\.]?\s*', '', definition, flags=re.IGNORECASE)
    if len(definition) > 800:
        definition = definition[:797] + '...'
    return definition

def is_valid_term(term):
    """Check if term is a valid morphological term"""
    term_lower = term.lower()
    
    # Must start with capital letter
    if not term[0].isupper():
        return False
    
    # Invalid patterns
    invalid_patterns = [
        r'^anatomical?\s+variation',
        r'^all\s+the\s+',
        r'fig\.',
        r'table\s+\d',
        r'http',
        r'www\.',
        r'\.com',
        r'@',
        r'copyright',
        r'received\s+\d',
        r'doi\s*:',
        r'^\d+\.',
        r'\n{2,}',
    ]
    
    for pattern in invalid_patterns:
        if re.search(pattern, term_lower):
            return False
    
    # Length checks
    if len(term) < 3 or len(term) > 80:
        return False
    
    # Word count check
    word_count = len(term.split())
    if word_count > 10:
        return False
    
    return True

def extract_morphology_terms(text_content, filename):
    """Extract morphological terms handling multi-column format"""
    terms = []
    
    # Main pattern: "Term: Definition"
    # This captures terms followed by their definitions
    pattern = r'^([\s]*[A-Z][A-Za-z,\s\-()\'\/]+?):\s+(.+?)(?=\n\s*[A-Z][A-Za-z,\s\-()\'\/]+?:\s+|\Z)'
    matches = re.finditer(pattern, text_content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        term_line = match.group(1).strip()
        definition_text = match.group(2).strip()
        
        # Split if this is a two-column term
        term_names = split_multicolumn_term(term_line)
        
        # If we have two terms from columns, try to split definition too
        if len(term_names) == 2:
            # Try to split definition at "Definition:" that appears in the middle
            def_parts = re.split(r'\s+Definition[:\.]?\s+', definition_text)
            if len(def_parts) == 2:
                # We have matching definitions for both terms
                for i, term_name in enumerate(term_names):
                    term = clean_term(term_name)
                    definition = clean_definition(def_parts[i])
                    
                    if is_valid_term(term) and len(definition) > 20:
                        terms.append({
                            'term': term,
                            'definition': definition,
                            'source': os.path.basename(filename)
                        })
            else:
                # Couldn't split definition, use for first term only
                term = clean_term(term_names[0])
                definition = clean_definition(definition_text)
                
                if is_valid_term(term) and len(definition) > 20:
                    terms.append({
                        'term': term,
                        'definition': definition,
                        'source': os.path.basename(filename)
                    })
        else:
            # Single term
            term = clean_term(term_line)
            definition = clean_definition(definition_text)
            
            if is_valid_term(term) and len(definition) > 20:
                terms.append({
                    'term': term,
                    'definition': definition,
                    'source': os.path.basename(filename)
                })
    
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
    print("🔬 SMART MORPHOLOGICAL TERM EXTRACTION")
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
        terms = extract_morphology_terms(text_content, text_file)
        
        if terms:
            category = categorize_by_topic(item['original_filename'])
            
            for term in terms:
                term['category'] = category
                term['document'] = item['original_filename'].replace('.pdf', '')
                all_terms.append(term)
                terms_by_category[category].append(term)
            
            print(f"   ✅ {len(terms)} terms")
        else:
            print(f"   ⚠️  No terms")
    
    # Remove duplicates - keep first occurrence
    seen = set()
    unique_terms = []
    for term in all_terms:
        key = (term['term'].lower().strip(), term['category'])
        if key not in seen:
            seen.add(key)
            unique_terms.append(term)
    
    # Sort terms alphabetically by category then term name
    unique_terms.sort(key=lambda x: (x['category'], x['term'].lower()))
    
    # Save all terms
    terms_file = f"{OUTPUT_DIR}/morphology_terms.json"
    with open(terms_file, 'w', encoding='utf-8') as f:
        json.dump(unique_terms, f, indent=2, ensure_ascii=False)
    
    # Save terms by category
    categories_dict = {}
    for cat in set(t['category'] for t in unique_terms):
        cat_terms = [t for t in unique_terms if t['category'] == cat]
        categories_dict[cat] = sorted(cat_terms, key=lambda x: x['term'].lower())
    
    categories_file = f"{OUTPUT_DIR}/terms_by_category.json"
    with open(categories_file, 'w', encoding='utf-8') as f:
        json.dump(categories_dict, f, indent=2, ensure_ascii=False)
    
    # Create index
    index = {
        'total_terms': len(unique_terms),
        'categories': {cat: len(terms) for cat, terms in categories_dict.items()},
        'sample_terms': [t['term'] for t in unique_terms[:30]]
    }
    
    index_file = f"{OUTPUT_DIR}/terms_index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print()
    print("="*70)
    print("✅ EXTRACTION COMPLETE!")
    print("="*70)
    print()
    print(f"📊 Statistics:")
    print(f"   • Total unique terms: {len(unique_terms)}")
    print(f"   • Categories: {len(categories_dict)}")
    print()
    print(f"📂 Terms by category:")
    for cat, terms in sorted(categories_dict.items(), key=lambda x: len(x[1]), reverse=True):
        emoji = {'ear': '👂', 'head_face': '👤', 'nose_philtrum': '👃', 
                 'lips_mouth': '👄', 'hands_feet': '✋', 'teeth': '🦷',
                 'periorbital': '👁️', 'genitalia': '🔬', 'general': '📚',
                 'phenotypic_variations': '🧬'}.get(cat, '📝')
        print(f"   {emoji} {cat:25} : {len(terms):4} terms")
    print()
    print(f"💾 Files created:")
    print(f"   • {terms_file}")
    print(f"   • {categories_file}")
    print(f"   • {index_file}")
    print()
    print(f"🔍 Sample terms (first 10):")
    for i, term in enumerate(unique_terms[:10], 1):
        cat_emoji = {'ear': '👂', 'head_face': '👤', 'nose_philtrum': '👃', 
                     'lips_mouth': '👄', 'hands_feet': '✋', 'teeth': '🦷',
                     'periorbital': '👁️', 'genitalia': '🔬'}.get(term['category'], '📝')
        print(f"   {i:2}. {cat_emoji} {term['term']}")

if __name__ == '__main__':
    main()
