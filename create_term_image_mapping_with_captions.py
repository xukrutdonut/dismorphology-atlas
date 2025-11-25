#!/usr/bin/env python3
"""
Extract image captions from text and create enhanced term-image mapping
"""
import json
import os
import re
from pathlib import Path
from collections import defaultdict

DATA_DIR = "data"
OUTPUT_DIR = "data/organized"

def extract_figure_captions(text):
    """Extract figure captions from text"""
    captions = {}
    
    # Pattern for figure captions: "FIG. X. Caption text"
    # This captures multi-line captions too
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
    """Extract figure references from text (Fig. X, Figure X, etc.)"""
    patterns = [
        r'\(Fig\.?\s*(\d+[a-z]?(?:-\d+)?)\)',
        r'\(Figs\.?\s*([\d,\s\-]+)\)',
        r'Figure\s+(\d+[a-z]?)',
        r'see Fig\.?\s*(\d+[a-z]?)',
    ]
    
    figures = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            fig_ref = match.group(1).strip()
            if '-' in fig_ref:
                parts = fig_ref.split('-')
                try:
                    start = int(re.search(r'\d+', parts[0]).group())
                    end = int(re.search(r'\d+', parts[1]).group())
                    figures.extend(range(start, end + 1))
                except:
                    pass
            elif ',' in fig_ref:
                for num in fig_ref.split(','):
                    try:
                        clean_num = re.search(r'\d+', num.strip())
                        if clean_num:
                            figures.append(int(clean_num.group()))
                    except:
                        pass
            else:
                try:
                    clean_num = re.search(r'\d+', fig_ref)
                    if clean_num:
                        figures.append(int(clean_num.group()))
                except:
                    pass
    
    return sorted(list(set(figures)))

def create_term_image_mapping_with_captions():
    """Create enhanced mapping with captions"""
    
    # Load terms
    with open(f"{OUTPUT_DIR}/morphology_terms.json", 'r') as f:
        terms = json.load(f)
    
    # Load images catalog
    with open(f"{OUTPUT_DIR}/images_catalog.json", 'r') as f:
        images_catalog = json.load(f)
    
    term_image_map = {}
    
    # Extract captions from all text files
    print("Extracting figure captions from documents...")
    print()
    
    all_captions = {}
    for txt_file in Path(DATA_DIR).glob('*.txt'):
        with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
            captions = extract_figure_captions(text)
            if captions:
                base_name = txt_file.stem
                all_captions[base_name] = captions
                print(f"✓ {txt_file.name[:60]:60} - {len(captions)} captions")
    
    print()
    print("Creating term-image-caption mapping...")
    print()
    
    for term in terms:
        definition = term['definition']
        term_name = term['term']
        source = term['source']
        
        # Extract figure references from definition
        figure_nums = extract_figure_references(definition)
        
        if figure_nums:
            base_name = source.replace('.txt', '').replace('data/', '')
            
            # Find matching images and captions
            matching_data = []
            
            if images_catalog.get('by_category'):
                for cat_key, cat_data in images_catalog['by_category'].items():
                    if base_name in cat_key or cat_key in base_name:
                        all_imgs = cat_data.get('all_images', [])
                        
                        # Get captions for this document
                        doc_captions = all_captions.get(base_name, {})
                        
                        for fig_num in figure_nums:
                            # Find corresponding image
                            img_index = f"-{fig_num:03d}.png"
                            for img in all_imgs:
                                if img_index in img or f"-{fig_num:02d}.png" in img:
                                    caption = doc_captions.get(fig_num, f"Fig. {fig_num}")
                                    matching_data.append({
                                        'image': img,
                                        'figure': fig_num,
                                        'caption': caption
                                    })
            
            if matching_data:
                term_image_map[term_name] = {
                    'term': term_name,
                    'category': term['category'],
                    'document': term['document'],
                    'source': source,
                    'figure_references': figure_nums,
                    'images': matching_data
                }
                
                captions_preview = ', '.join([d['caption'][:30] for d in matching_data[:2]])
                print(f"✓ {term_name[:45]:45} -> {len(matching_data)} imgs: {captions_preview}...")
    
    print()
    print(f"Total terms with enhanced mappings: {len(term_image_map)}")
    
    # Save enhanced mapping
    mapping_file = f"{OUTPUT_DIR}/term_image_mapping_with_captions.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(term_image_map, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Enhanced mapping saved to: {mapping_file}")
    
    # Create simple lookup for web app
    simple_map = {}
    for term_name, data in term_image_map.items():
        simple_map[term_name] = data['images']
    
    simple_file = f"{OUTPUT_DIR}/term_images_with_captions.json"
    with open(simple_file, 'w', encoding='utf-8') as f:
        json.dump(simple_map, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Web-ready mapping saved to: {simple_file}")
    
    # Save just captions by document
    captions_file = f"{OUTPUT_DIR}/figure_captions.json"
    with open(captions_file, 'w', encoding='utf-8') as f:
        json.dump(all_captions, f, indent=2, ensure_ascii=False)
    
    print(f"✓ All captions saved to: {captions_file}")
    
    # Statistics
    print(f"\nStatistics:")
    print(f"  Documents with captions: {len(all_captions)}")
    total_captions = sum(len(caps) for caps in all_captions.values())
    print(f"  Total captions extracted: {total_captions}")
    print(f"  Terms with enhanced mappings: {len(term_image_map)}")
    total_imgs = sum(len(data['images']) for data in term_image_map.values())
    print(f"  Total image-caption associations: {total_imgs}")
    avg_imgs = total_imgs / len(term_image_map) if term_image_map else 0
    print(f"  Average images per term: {avg_imgs:.2f}")

if __name__ == '__main__':
    create_term_image_mapping_with_captions()
