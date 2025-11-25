#!/usr/bin/env python3
"""
Extract morphological terms and definitions from the text files
"""
import json
import os
import re
from pathlib import Path
from collections import defaultdict

DATA_DIR = "data"
OUTPUT_DIR = "data/organized"

def extract_structured_terms(text_content, filename):
    """Extract terms with definitions using various patterns"""
    terms = []
    lines = text_content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and headers
        if not line or len(line) < 3:
            i += 1
            continue
        
        # Pattern 1: "Term: Definition" on same line
        if ':' in line and len(line) < 500:
            parts = line.split(':', 1)
            if len(parts) == 2:
                term = parts[0].strip()
                definition = parts[1].strip()
                
                # Filter valid terms
                if (term and definition and 
                    not term.startswith('http') and 
                    not term.isdigit() and
                    len(term) < 100 and
                    len(term.split()) <= 10):
                    
                    # Look ahead for continuation
                    j = i + 1
                    while j < len(lines) and j < i + 5:
                        next_line = lines[j].strip()
                        if next_line and not ':' in next_line and len(next_line) < 300:
                            definition += ' ' + next_line
                            j += 1
                        else:
                            break
                    
                    terms.append({
                        'term': term,
                        'definition': definition.strip(),
                        'source': os.path.basename(filename)
                    })
        
        # Pattern 2: Bold/capitalized term followed by definition
        elif line.isupper() and len(line) < 100 and len(line.split()) <= 8:
            term = line
            definition = ""
            j = i + 1
            while j < len(lines) and j < i + 10:
                next_line = lines[j].strip()
                if next_line and not next_line.isupper():
                    definition += ' ' + next_line
                    if next_line.endswith('.'):
                        break
                    j += 1
                else:
                    break
            
            if definition:
                terms.append({
                    'term': term.title(),
                    'definition': definition.strip(),
                    'source': os.path.basename(filename)
                })
        
        i += 1
    
    return terms

def categorize_by_topic(filename):
    """Determine the anatomical topic from filename"""
    name_lower = filename.lower()
    
    topics = {
        'ear': ['ear'],
        'head_face': ['head', 'face'],
        'nose_philtrum': ['nose', 'philtrum'],
        'lips_mouth': ['lip', 'mouth', 'oral'],
        'periorbital': ['periorbital', 'eye'],
        'hands_feet': ['hand', 'feet', 'finger', 'toe'],
        'genitalia': ['genital'],
        'teeth': ['teeth', 'dental'],
        'introduction': ['introduction'],
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
    
    print("Extracting terms from documents...\n")
    
    for item in metadata:
        text_file = item['text_file']
        
        if not os.path.exists(text_file):
            continue
        
        print(f"Processing: {os.path.basename(text_file)}")
        
        # Read text
        with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
            text_content = f.read()
        
        # Extract terms
        terms = extract_structured_terms(text_content, text_file)
        
        if terms:
            category = categorize_by_topic(item['original_filename'])
            
            for term in terms:
                term['category'] = category
                term['document'] = item['original_filename'].replace('.pdf', '')
                all_terms.append(term)
                terms_by_category[category].append(term)
            
            print(f"  Found {len(terms)} terms")
        else:
            print(f"  No terms found")
    
    # Remove duplicates (same term and definition)
    seen = set()
    unique_terms = []
    for term in all_terms:
        key = (term['term'].lower(), term['definition'][:100])
        if key not in seen:
            seen.add(key)
            unique_terms.append(term)
    
    # Save all terms
    terms_file = f"{OUTPUT_DIR}/morphology_terms.json"
    with open(terms_file, 'w', encoding='utf-8') as f:
        json.dump(unique_terms, f, indent=2, ensure_ascii=False)
    
    # Save terms by category
    categories_file = f"{OUTPUT_DIR}/terms_by_category.json"
    with open(categories_file, 'w', encoding='utf-8') as f:
        json.dump(dict(terms_by_category), f, indent=2, ensure_ascii=False)
    
    # Create index
    index = {
        'total_terms': len(unique_terms),
        'categories': {cat: len(terms) for cat, terms in terms_by_category.items()},
        'sample_terms': [t['term'] for t in unique_terms[:20]]
    }
    
    index_file = f"{OUTPUT_DIR}/terms_index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Extraction complete!")
    print(f"  Total unique terms: {len(unique_terms)}")
    print(f"  Categories: {len(terms_by_category)}")
    print(f"\nTerms by category:")
    for cat, terms in sorted(terms_by_category.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {cat}: {len(terms)} terms")
    
    print(f"\nOutput files:")
    print(f"  - {terms_file}")
    print(f"  - {categories_file}")
    print(f"  - {index_file}")

if __name__ == '__main__':
    main()
