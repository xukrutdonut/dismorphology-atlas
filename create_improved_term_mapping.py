#!/usr/bin/env python3
"""
Improved term-image mapping with better compound term matching
Handles terms with multiple components (noun + adjective)
"""
import json
import os
import re
from pathlib import Path
from collections import defaultdict
import unicodedata

DATA_DIR = "data"
OUTPUT_DIR = "data/organized"

def normalize_text(text):
    """Normalize text for better matching"""
    # Remove accents and convert to lowercase
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    text = text.lower().strip()
    
    # Remove common punctuation but keep hyphens
    text = re.sub(r'[^\w\s\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text

def extract_term_components(term):
    """Extract components from a term (handle compound terms)"""
    normalized = normalize_text(term)
    
    # Split by common separators
    components = re.split(r'[\s\-,;]+', normalized)
    components = [c.strip() for c in components if c.strip() and len(c) > 2]
    
    # Also include the full term
    full_term = re.sub(r'[\s\-]+', ' ', normalized).strip()
    if full_term not in components:
        components.append(full_term)
    
    return components

def extract_figure_captions(text):
    """Extract figure captions from text"""
    captions = {}
    
    # Pattern for figure captions: "FIG. X. Caption text"
    pattern = r'FIG\.?\s+(\d+[a-z]?)\.?\s+(.+?)(?=\n\s*FIG\.|\n\n|\Z)'
    
    matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
    
    for match in matches:
        fig_num_str = match.group(1)
        caption_text = match.group(2).strip()
        
        # Clean up caption
        caption_text = ' '.join(caption_text.split())
        caption_text = caption_text.replace('\n', ' ')
        
        # Extract just the number
        try:
            fig_num = int(re.search(r'\d+', fig_num_str).group())
            # Limit caption length
            if len(caption_text) > 200:
                caption_text = caption_text[:197] + '...'
            captions[fig_num] = caption_text
        except:
            pass
    
    return captions

def extract_figure_references(text):
    """Extract figure references from text"""
    patterns = [
        r'\(Fig\.?\s*(\d+[a-z]?(?:-\d+)?)\)',
        r'\(Figs\.?\s*([\d,\s\-]+)\)',
        r'Figure\s+(\d+[a-z]?)',
        r'see Fig\.?\s*(\d+[a-z]?)',
        r'Fig\.?\s*(\d+[a-z]?)',
    ]
    
    figure_nums = set()
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            nums_str = match.group(1)
            
            # Handle ranges and lists
            if ',' in nums_str or '-' in nums_str:
                # Extract individual numbers
                individual_nums = re.findall(r'\d+', nums_str)
                for num_str in individual_nums:
                    try:
                        figure_nums.add(int(num_str))
                    except:
                        pass
            else:
                try:
                    num = int(re.search(r'\d+', nums_str).group())
                    figure_nums.add(num)
                except:
                    pass
    
    return sorted(list(figure_nums))

def match_term_in_caption(term_components, caption_text):
    """Check if term components match in caption"""
    normalized_caption = normalize_text(caption_text)
    
    # For compound terms, all components should be present
    if len(term_components) > 1:
        # Check if all major components are present
        matches = 0
        for component in term_components:
            if len(component) > 2:  # Skip very short components
                if component in normalized_caption:
                    matches += 1
        
        # Require at least 70% of components to match for compound terms
        return matches >= len(term_components) * 0.7
    else:
        # Single component - check direct match
        return any(comp in normalized_caption for comp in term_components)

def create_enhanced_mapping():
    """Create enhanced term-image mapping with better compound term support"""
    
    # Load existing data
    print("Loading data files...")
    
    with open(f"{OUTPUT_DIR}/morphology_terms.json", 'r', encoding='utf-8') as f:
        terms = json.load(f)
    
    with open(f"{OUTPUT_DIR}/images_catalog.json", 'r', encoding='utf-8') as f:
        images_catalog = json.load(f)
    
    print(f"Loaded {len(terms)} terms")
    
    # Extract all captions
    print("\nExtracting captions from documents...")
    all_captions = {}
    for txt_file in Path(DATA_DIR).glob('*.txt'):
        with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
            captions = extract_figure_captions(text)
            if captions:
                base_name = txt_file.stem
                all_captions[base_name] = captions
                print(f"✓ {txt_file.name[:50]:50} - {len(captions)} captions")
    
    print(f"\nTotal documents with captions: {len(all_captions)}")
    
    # Create mappings
    term_image_map = {}
    terms_with_images = set()
    mapping_stats = {
        'direct_reference': 0,
        'caption_match': 0,
        'fallback': 0,
        'compound_terms': 0
    }
    
    print("\nCreating enhanced term-image mappings...")
    
    for i, term in enumerate(terms):
        if i % 100 == 0:
            print(f"Processing term {i+1}/{len(terms)}...")
        
        definition = term['definition']
        term_name = term['term']
        source = term['source']
        
        # Extract term components for better matching
        term_components = extract_term_components(term_name)
        is_compound = len(term_components) > 1
        
        if is_compound:
            mapping_stats['compound_terms'] += 1
        
        matching_data = []
        base_name = source.replace('.txt', '').replace('data/', '')
        
        # Method 1: Direct figure references in definition
        figure_nums = extract_figure_references(definition)
        
        if figure_nums:
            mapping_stats['direct_reference'] += 1
            
            # Find matching images
            if images_catalog.get('by_category'):
                for cat_key, cat_data in images_catalog['by_category'].items():
                    # More flexible matching for category keys
                    if any(part in cat_key for part in base_name.split('_')[:3]) or \
                       any(part in base_name for part in cat_key.split('_')[:3]):
                        all_imgs = cat_data.get('all_images', [])
                        doc_captions = all_captions.get(base_name, {})
                        
                        for fig_num in figure_nums:
                            # Find corresponding image with more flexible matching
                            img_patterns = [
                                f"-{fig_num:03d}.png",
                                f"-{fig_num:02d}.png", 
                                f"_{fig_num:03d}.png",
                                f"_{fig_num:02d}.png",
                                f"-{fig_num}.png"
                            ]
                            
                            for img in all_imgs:
                                for pattern in img_patterns:
                                    if pattern in img:
                                        caption = doc_captions.get(fig_num, f"Fig. {fig_num}")
                                        matching_data.append({
                                            'image': img,
                                            'figure': fig_num,
                                            'caption': caption,
                                            'match_type': 'direct_reference'
                                        })
                                        break
                                if matching_data:  # Found match, break outer loop
                                    break
        
        # Method 2: Search in captions for term matches
        if not matching_data:
            doc_captions = all_captions.get(base_name, {})
            
            for fig_num, caption in doc_captions.items():
                if match_term_in_caption(term_components, caption):
                    
                    # Find corresponding image
                    if images_catalog.get('by_category'):
                        for cat_key, cat_data in images_catalog['by_category'].items():
                            if any(part in cat_key for part in base_name.split('_')[:3]) or \
                               any(part in base_name for part in cat_key.split('_')[:3]):
                                all_imgs = cat_data.get('all_images', [])
                                
                                img_patterns = [
                                    f"-{fig_num:03d}.png",
                                    f"-{fig_num:02d}.png",
                                    f"_{fig_num:03d}.png", 
                                    f"_{fig_num:02d}.png",
                                    f"-{fig_num}.png"
                                ]
                                
                                for img in all_imgs:
                                    for pattern in img_patterns:
                                        if pattern in img:
                                            matching_data.append({
                                                'image': img,
                                                'figure': fig_num,
                                                'caption': caption,
                                                'match_type': 'caption_match'
                                            })
                                            mapping_stats['caption_match'] += 1
                                            break
                                    if matching_data:
                                        break
                                if matching_data:
                                    break
        
        # Method 3: Fallback - general document images (limited)
        if not matching_data:
            
            if images_catalog.get('by_category'):
                for cat_key, cat_data in images_catalog['by_category'].items():
                    if any(part in cat_key for part in base_name.split('_')[:3]) or \
                       any(part in base_name for part in cat_key.split('_')[:3]):
                        all_imgs = cat_data.get('all_images', [])
                        doc_captions = all_captions.get(base_name, {})
                        
                        # Take first few images as fallback
                        for i, img in enumerate(all_imgs[:2]):  # Limit to 2 images
                            try:
                                fig_match = re.search(r'[-_](\d+)\.png', img)
                                if fig_match:
                                    fig_num = int(fig_match.group(1))
                                    caption = doc_captions.get(fig_num, f"Imagen del documento (Fig. {fig_num})")
                                else:
                                    fig_num = i + 1
                                    caption = f"Imagen del documento ({i+1})"
                                
                                matching_data.append({
                                    'image': img,
                                    'figure': fig_num,
                                    'caption': caption,
                                    'match_type': 'fallback'
                                })
                            except:
                                pass
                        
                        if matching_data:
                            mapping_stats['fallback'] += 1
                            break
        
        # Store results
        if matching_data:
            term_image_map[term_name] = matching_data
            terms_with_images.add(term_name)
    
    print(f"\nMapping Statistics:")
    print(f"  Terms with direct figure references: {mapping_stats['direct_reference']}")
    print(f"  Terms matched by caption content: {mapping_stats['caption_match']}")
    print(f"  Terms with fallback images: {mapping_stats['fallback']}")
    print(f"  Compound terms processed: {mapping_stats['compound_terms']}")
    print(f"  Total terms with images: {len(terms_with_images)}")
    
    # Save enhanced mapping
    mapping_file = f"{OUTPUT_DIR}/term_images_enhanced.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(term_image_map, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Enhanced mapping saved to: {mapping_file}")
    
    # Save list of terms with images (for UI indicators)
    terms_with_images_file = f"{OUTPUT_DIR}/terms_with_images.json"
    with open(terms_with_images_file, 'w', encoding='utf-8') as f:
        json.dump(list(terms_with_images), f, indent=2, ensure_ascii=False)
    
    print(f"✓ Terms with images list saved to: {terms_with_images_file}")
    
    # Create legacy format for backward compatibility
    legacy_map = {}
    for term_name, images_data in term_image_map.items():
        legacy_map[term_name] = images_data
    
    legacy_file = f"{OUTPUT_DIR}/term_images_with_captions.json"
    with open(legacy_file, 'w', encoding='utf-8') as f:
        json.dump(legacy_map, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Legacy format saved to: {legacy_file}")
    
    return term_image_map, terms_with_images

if __name__ == "__main__":
    create_enhanced_mapping()