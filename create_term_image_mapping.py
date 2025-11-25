#!/usr/bin/env python3
"""
Create a mapping between terms and their associated images based on figure references
"""
import json
import os
import re
from pathlib import Path
from collections import defaultdict

DATA_DIR = "data"
OUTPUT_DIR = "data/organized"

def extract_figure_references(text):
    """Extract figure references from text (Fig. X, Figure X, etc.)"""
    # Patterns for figure references
    patterns = [
        r'\(Fig\.?\s*(\d+[a-z]?(?:-\d+)?)\)',  # (Fig. 3), (Fig. 3a), (Fig. 3-5)
        r'\(Figs\.?\s*([\d,\s\-]+)\)',          # (Figs. 3, 4, 5)
        r'Figure\s+(\d+[a-z]?)',                # Figure 3, Figure 3a
        r'FIG\.?\s+(\d+[a-z]?)',                # FIG. 3, FIG 3a
    ]
    
    figures = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            fig_ref = match.group(1)
            # Handle ranges like "3-5" or lists like "3, 4, 5"
            if '-' in fig_ref:
                # Range: 3-5
                parts = fig_ref.split('-')
                try:
                    start = int(re.search(r'\d+', parts[0]).group())
                    end = int(re.search(r'\d+', parts[1]).group())
                    figures.extend(range(start, end + 1))
                except:
                    pass
            elif ',' in fig_ref:
                # List: 3, 4, 5
                for num in fig_ref.split(','):
                    try:
                        figures.append(int(re.search(r'\d+', num).group()))
                    except:
                        pass
            else:
                # Single figure
                try:
                    figures.append(int(re.search(r'\d+', fig_ref).group()))
                except:
                    pass
    
    return sorted(list(set(figures)))

def create_term_image_mapping():
    """Create mapping between terms and images"""
    
    # Load terms
    with open(f"{OUTPUT_DIR}/morphology_terms.json", 'r') as f:
        terms = json.load(f)
    
    # Load images catalog
    with open(f"{OUTPUT_DIR}/images_catalog.json", 'r') as f:
        images_catalog = json.load(f)
    
    term_image_map = {}
    
    print("Creating term-image mapping...")
    print()
    
    for term in terms:
        # Get the definition text
        definition = term['definition']
        term_name = term['term']
        source = term['source']
        
        # Extract figure references from definition
        figure_nums = extract_figure_references(definition)
        
        if figure_nums:
            # Find matching images based on source file
            base_name = source.replace('.txt', '').replace('data/', '')
            
            # Look for images in catalog
            matching_images = []
            
            if images_catalog.get('by_category'):
                for cat_key, cat_data in images_catalog['by_category'].items():
                    # Match by source file name
                    if base_name in cat_key or cat_key in base_name:
                        all_imgs = cat_data.get('all_images', [])
                        
                        # Map figure numbers to image indices
                        for fig_num in figure_nums:
                            # Figures usually map to image indices (Fig. 1 -> image-000.png, etc.)
                            # Try exact match first
                            img_index = f"-{fig_num:03d}.png"
                            for img in all_imgs:
                                if img_index in img or f"-{fig_num:02d}.png" in img:
                                    matching_images.append(img)
            
            if matching_images:
                term_image_map[term_name] = {
                    'term': term_name,
                    'category': term['category'],
                    'document': term['document'],
                    'source': source,
                    'figure_references': figure_nums,
                    'images': list(set(matching_images))
                }
                print(f"✓ {term_name[:50]:50} -> Figs: {figure_nums} ({len(matching_images)} images)")
    
    print()
    print(f"Total terms with image mappings: {len(term_image_map)}")
    
    # Save mapping
    mapping_file = f"{OUTPUT_DIR}/term_image_mapping.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(term_image_map, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Mapping saved to: {mapping_file}")
    
    # Create a simpler lookup by term name
    simple_map = {term_name: data['images'] for term_name, data in term_image_map.items()}
    simple_file = f"{OUTPUT_DIR}/term_images_simple.json"
    with open(simple_file, 'w', encoding='utf-8') as f:
        json.dump(simple_map, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Simple mapping saved to: {simple_file}")
    
    # Statistics
    print(f"\nStatistics:")
    print(f"  Terms with images: {len(term_image_map)}")
    total_imgs = sum(len(data['images']) for data in term_image_map.values())
    print(f"  Total image associations: {total_imgs}")
    avg_imgs = total_imgs / len(term_image_map) if term_image_map else 0
    print(f"  Average images per term: {avg_imgs:.2f}")

if __name__ == '__main__':
    create_term_image_mapping()
