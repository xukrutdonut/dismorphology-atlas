#!/usr/bin/env python3
"""
Create term-image mapping by analyzing image captions for term matches
"""
import json
import os
import re
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

DATA_DIR = "data"
OUTPUT_DIR = "data/organized"

def normalize_term(term):
    """Normalize term for better matching"""
    # Convert to lowercase and remove punctuation
    normalized = term.lower()
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    normalized = ' '.join(normalized.split())
    return normalized

def similarity(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a, b).ratio()

def extract_terms_from_caption(caption, term_list, min_similarity=0.8):
    """Extract terms that appear in a caption"""
    caption_normalized = normalize_term(caption)
    found_terms = []
    
    for term in term_list:
        term_normalized = normalize_term(term)
        
        # Exact match
        if term_normalized in caption_normalized:
            found_terms.append({
                'term': term,
                'match_type': 'exact',
                'confidence': 1.0
            })
            continue
        
        # Partial word match
        term_words = term_normalized.split()
        caption_words = caption_normalized.split()
        
        # Check if all words of the term appear in the caption
        if len(term_words) > 1:
            matches = 0
            for word in term_words:
                if len(word) > 2 and word in caption_words:
                    matches += 1
            
            if matches >= len(term_words) * 0.7:  # 70% of words match
                confidence = matches / len(term_words)
                found_terms.append({
                    'term': term,
                    'match_type': 'partial',
                    'confidence': confidence
                })
                continue
        
        # Fuzzy match for longer terms
        if len(term_normalized) > 8:
            sim = similarity(term_normalized, caption_normalized)
            if sim >= min_similarity:
                found_terms.append({
                    'term': term,
                    'match_type': 'fuzzy',
                    'confidence': sim
                })
    
    return found_terms

def create_term_image_mapping():
    """Create mapping between terms and images based on captions"""
    
    # Load terms
    terms_file = os.path.join(OUTPUT_DIR, 'morphology_terms.json')
    with open(terms_file, 'r', encoding='utf-8') as f:
        terms_data = json.load(f)
    
    # Extract term names
    term_names = [term['term'] for term in terms_data]
    
    # Load captions
    captions_file = os.path.join(OUTPUT_DIR, 'figure_captions.json')
    with open(captions_file, 'r', encoding='utf-8') as f:
        captions_data = json.load(f)
    
    term_image_mapping = defaultdict(list)
    image_term_mapping = defaultdict(list)
    
    total_matches = 0
    document_stats = {}
    
    print("🔍 Analyzing captions for term matches...\n")
    
    for doc_name, doc_captions in captions_data.items():
        print(f"📄 {doc_name}")
        doc_matches = 0
        
        for fig_num, caption in doc_captions.items():
            # Find terms in this caption
            found_terms = extract_terms_from_caption(caption, term_names)
            
            if found_terms:
                # Determine image file names based on document and figure number
                doc_clean = doc_name.replace('.txt', '')
                
                # Look for actual image files
                image_candidates = []
                
                # Try different naming patterns
                patterns = [
                    f"images/{doc_clean}-{fig_num.zfill(3)}.png",
                    f"images/{doc_clean}-{fig_num.zfill(2)}.png", 
                    f"images/{doc_clean}_{fig_num.zfill(3)}.png",
                    f"images/{doc_clean}_{fig_num.zfill(2)}.png",
                    f"images/{doc_clean}-{fig_num}.png",
                    f"images/{doc_clean}_{fig_num}.png"
                ]
                
                # Find existing images
                for pattern in patterns:
                    if os.path.exists(pattern):
                        image_candidates.append(os.path.basename(pattern))
                
                # If no exact match, try to find similar files
                if not image_candidates:
                    try:
                        images_dir = Path("images")
                        for img_file in images_dir.glob(f"{doc_clean}*"):
                            if fig_num in str(img_file):
                                image_candidates.append(img_file.name)
                    except:
                        pass
                
                for term_match in found_terms:
                    term = term_match['term']
                    confidence = term_match['confidence']
                    match_type = term_match['match_type']
                    
                    # Add to mappings
                    mapping_entry = {
                        'figure': int(fig_num) if fig_num.isdigit() else fig_num,
                        'caption': caption,
                        'confidence': confidence,
                        'match_type': match_type,
                        'document': doc_name,
                        'images': image_candidates
                    }
                    
                    term_image_mapping[term].append(mapping_entry)
                    
                    for img in image_candidates:
                        image_term_mapping[img].append({
                            'term': term,
                            'confidence': confidence,
                            'match_type': match_type,
                            'figure': int(fig_num) if fig_num.isdigit() else fig_num,
                            'caption': caption
                        })
                    
                    doc_matches += 1
                    total_matches += 1
                    
                    print(f"   ✓ Fig.{fig_num}: {term} ({match_type}, {confidence:.2f})")
        
        document_stats[doc_name] = doc_matches
        if doc_matches == 0:
            print("   ⚠️  No term matches found")
        print()
    
    # Save mappings
    term_mapping_file = os.path.join(OUTPUT_DIR, 'term_image_mapping.json')
    with open(term_mapping_file, 'w', encoding='utf-8') as f:
        json.dump(dict(term_image_mapping), f, indent=2, ensure_ascii=False)
    
    image_mapping_file = os.path.join(OUTPUT_DIR, 'image_term_mapping.json')
    with open(image_mapping_file, 'w', encoding='utf-8') as f:
        json.dump(dict(image_term_mapping), f, indent=2, ensure_ascii=False)
    
    # Create web-ready format for the application
    web_mapping = {}
    for term, mappings in term_image_mapping.items():
        web_mapping[term] = []
        for mapping in mappings:
            for img in mapping['images']:
                web_mapping[term].append({
                    'image': img,
                    'figure': mapping['figure'],
                    'caption': mapping['caption'][:200] + '...' if len(mapping['caption']) > 200 else mapping['caption'],
                    'confidence': mapping['confidence']
                })
    
    web_file = os.path.join(OUTPUT_DIR, 'term_images_with_captions.json')
    with open(web_file, 'w', encoding='utf-8') as f:
        json.dump(web_mapping, f, indent=2, ensure_ascii=False)
    
    # Print statistics
    print("=" * 70)
    print("✅ TERM-IMAGE MAPPING COMPLETED")
    print("=" * 70)
    print(f"📊 Statistics:")
    print(f"   • Total term-image matches: {total_matches}")
    print(f"   • Terms with images: {len(term_image_mapping)}")
    print(f"   • Images with terms: {len(image_term_mapping)}")
    print(f"   • Documents processed: {len(document_stats)}")
    print()
    
    print("📂 Files generated:")
    print(f"   • {term_mapping_file}")
    print(f"   • {image_mapping_file}")
    print(f"   • {web_file}")
    print()
    
    # Show top matches
    if term_image_mapping:
        print("🔍 Top term-image associations:")
        sorted_terms = sorted(term_image_mapping.items(), 
                            key=lambda x: len(x[1]), reverse=True)[:10]
        
        for i, (term, mappings) in enumerate(sorted_terms[:5], 1):
            print(f"   {i}. {term}")
            print(f"      → {len(mappings)} image(s), avg confidence: {sum(m['confidence'] for m in mappings)/len(mappings):.2f}")
        print()
    
    return dict(term_image_mapping), dict(image_term_mapping)

if __name__ == '__main__':
    create_term_image_mapping()