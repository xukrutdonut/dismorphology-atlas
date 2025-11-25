#!/usr/bin/env python3
"""
Organize extracted morphology content by anatomical regions
"""
import json
import os
import re
from pathlib import Path
from collections import defaultdict

DATA_DIR = "data"
IMAGES_DIR = "images"
OUTPUT_DIR = "data/organized"

# Define anatomical categories based on filenames
CATEGORIES = {
    'introduction': ['introduction'],
    'head_face': ['head_and_face', 'head and face'],
    'ear': ['ear', 'ear_an_initial'],
    'periorbital': ['periorbital'],
    'nose_philtrum': ['nose_and_philtrum', 'nose and philtrum'],
    'lips_mouth': ['lips_mouth_and_oral', 'lips, mouth'],
    'teeth': ['teeth', 'dental'],
    'hands_feet': ['hands_and_feet', 'hands and feet'],
    'genitalia': ['genitalia', 'external_genitalia'],
    'phenotypic_variations': ['phenotypic_variations', 'phenotypic abnormalities'],
    'general': ['standard_terminology_for_t']
}

def categorize_content(safe_name, original_filename):
    """Determine the category for a given file"""
    name_lower = safe_name.lower()
    original_lower = original_filename.lower()
    
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in name_lower or keyword in original_lower:
                return category
    
    return 'other'

def extract_terms_from_text(text_content):
    """Extract morphological terms and definitions from text"""
    terms = []
    
    # Look for term definitions (patterns like "Term: Definition" or bold terms)
    lines = text_content.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Look for definition patterns
        if ':' in line and len(line) < 200:
            parts = line.split(':', 1)
            if len(parts) == 2 and len(parts[0]) < 100:
                term = parts[0].strip()
                definition = parts[1].strip()
                
                # Filter out common non-term patterns
                if term and definition and not term.startswith('http') and not term.isdigit():
                    terms.append({
                        'term': term,
                        'definition': definition
                    })
    
    return terms

def main():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    # Load metadata
    with open(f"{DATA_DIR}/extraction_metadata.json", 'r') as f:
        metadata = json.load(f)
    
    # Organize by category
    organized = defaultdict(list)
    
    for item in metadata:
        category = categorize_content(item['safe_name'], item['original_filename'])
        
        # Read text content
        text_content = ""
        if os.path.exists(item['text_file']):
            with open(item['text_file'], 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
        
        # Find associated images
        image_prefix = item['image_prefix']
        images = []
        if os.path.exists(IMAGES_DIR):
            for img_file in sorted(os.listdir(IMAGES_DIR)):
                if img_file.startswith(os.path.basename(image_prefix)):
                    images.append(os.path.join(IMAGES_DIR, img_file))
        
        # Extract terms from text
        terms = extract_terms_from_text(text_content)
        
        organized[category].append({
            'title': item['original_filename'].replace('.pdf', ''),
            'safe_name': item['safe_name'],
            'text_file': item['text_file'],
            'text_preview': text_content[:500] if text_content else "",
            'text_length': len(text_content),
            'images': images,
            'image_count': len(images),
            'terms_found': len(terms),
            'sample_terms': terms[:5] if terms else []
        })
    
    # Save organized data
    output_file = f"{OUTPUT_DIR}/content_by_category.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dict(organized), f, indent=2, ensure_ascii=False)
    
    # Create summary
    summary = {
        'total_documents': len(metadata),
        'total_images': sum(len(cat_items[0]['images']) for cat_items in organized.values() if cat_items),
        'categories': {}
    }
    
    for category, items in organized.items():
        summary['categories'][category] = {
            'document_count': len(items),
            'image_count': sum(item['image_count'] for item in items),
            'total_text_length': sum(item['text_length'] for item in items),
            'titles': [item['title'] for item in items]
        }
    
    summary_file = f"{OUTPUT_DIR}/summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Content organized!")
    print(f"  Categories: {len(organized)}")
    print(f"  Total documents: {summary['total_documents']}")
    print(f"  Total images: {summary['total_images']}")
    print(f"\nOutput files:")
    print(f"  - {output_file}")
    print(f"  - {summary_file}")
    
    print("\nCategories breakdown:")
    for category, info in summary['categories'].items():
        print(f"  {category}: {info['document_count']} docs, {info['image_count']} images")

if __name__ == '__main__':
    main()
