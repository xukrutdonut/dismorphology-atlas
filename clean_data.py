#!/usr/bin/env python3
"""
Clean and improve morphology terms data
"""
import json
import re
from collections import defaultdict

OUTPUT_DIR = "data/organized"

def clean_definition(definition):
    """Clean definition text from garbage"""
    
    # Remove common garbage patterns
    garbage_patterns = [
        r'15524833.*?(?=\s|$)',  # Document IDs
        r'Downloaded from.*?(?=\.|$)',
        r'https?://\S+',
        r'www\.\S+',
        r'DOI:?\s*\S+',
        r'\[[\d\s,]+\]',  # Citations like [2010]
        r'Wiley Online Library.*?(?=\.|$)',
        r'See the Terms and Conditions.*?(?=\.|$)',
        r'Spanish Cochrane.*?(?=\.|$)',
        r'Ministerio de.*?(?=\.|$)',
        r'on Wiley Online Library.*?(?=\.|$)',
        r'for rules of use.*?(?=\.|$)',
        r'OA articles are governed.*?(?=\.|$)',
        r'Creative Commons License.*?(?=\.|$)',
        r'HUNTER ET AL\..*?(?=\.|$)',
        r'AMERICAN JOURNAL.*?(?=\.|$)',
        r'Courtesy of Dr\..*?(?=\.|$)',
        r'Reprinted with permission.*?(?=\.|$)',
        r'Panel [A-Z] reprinted.*?(?=\.|$)',
        r'FIG\.\s+\d+\..*?(?=FIG\.|$)',  # Remove figure references from definitions
    ]
    
    cleaned = definition
    for pattern in garbage_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    cleaned = ' '.join(cleaned.split())
    
    # Remove trailing punctuation artifacts
    cleaned = re.sub(r'\s+[,;:]\s*$', '', cleaned)
    
    return cleaned.strip()

def detect_see_reference(definition):
    """Detect if definition is a 'see' reference to another term"""
    # Pattern: "see Term Name" or "See Term Name"
    # More strict pattern to capture the term correctly
    see_match = re.match(r'^[Ss]ee\s+([A-Z][A-Za-z,\s\-()\']+?)(?:\s+[A-Z][a-z]+:|$|\s+\()', definition, re.IGNORECASE)
    if see_match:
        referenced_term = see_match.group(1).strip()
        # Clean up the referenced term
        referenced_term = re.sub(r'[,;:\s]+$', '', referenced_term)
        # Remove trailing articles or prepositions
        referenced_term = re.sub(r'\s+(and|or|of|the|a|an)$', '', referenced_term, flags=re.IGNORECASE)
        return referenced_term
    
    # Try alternative patterns
    alt_match = re.match(r'^[Ss]ee:\s*([A-Z][A-Za-z,\s\-()\']+?)(?:\.|$)', definition)
    if alt_match:
        referenced_term = alt_match.group(1).strip()
        referenced_term = re.sub(r'[,;:\s]+$', '', referenced_term)
        return referenced_term
    
    return None

def remove_duplicate_images(images_data):
    """Remove duplicate images (same figure number from same document base)"""
    seen = {}
    unique_images = []
    
    for img_data in images_data:
        # Create key: base filename + figure number
        img_file = img_data['image']
        fig_num = img_data['figure']
        
        # Extract base name (remove -XXX.png suffix and variations)
        base = re.sub(r'(_standard_terminology_for_t-|-\d{3}\.png$)', '', img_file)
        
        key = (base, fig_num)
        
        if key not in seen:
            seen[key] = img_data
            unique_images.append(img_data)
        else:
            # Keep the one with better caption (longer, more informative)
            existing = seen[key]
            if len(img_data['caption']) > len(existing['caption']) and 'Fig.' not in img_data['caption']:
                seen[key] = img_data
                # Replace in unique_images
                idx = unique_images.index(existing)
                unique_images[idx] = img_data
    
    return unique_images

def clean_caption(caption):
    """Clean caption text"""
    # Same garbage patterns as definitions
    cleaned = clean_definition(caption)
    
    # If caption is just "Fig. X", it's not informative
    if re.match(r'^Fig\.\s*\d+\s*$', cleaned, re.IGNORECASE):
        return None
    
    return cleaned if cleaned else None

def main():
    print("="*70)
    print("🧹 LIMPIEZA Y MEJORA DE DATOS")
    print("="*70)
    print()
    
    # Load terms
    print("📂 Cargando términos...")
    with open(f"{OUTPUT_DIR}/morphology_terms.json", 'r') as f:
        terms = json.load(f)
    
    # Load images with captions
    print("📂 Cargando mapeo de imágenes...")
    with open(f"{OUTPUT_DIR}/term_images_with_captions.json", 'r') as f:
        term_images = json.load(f)
    
    # Clean terms
    print()
    print("🧹 Limpiando definiciones...")
    cleaned_terms = []
    see_references = {}
    
    for term in terms:
        # Clean definition
        original_def = term['definition']
        cleaned_def = clean_definition(original_def)
        
        # Check if it's a "see" reference
        see_ref = detect_see_reference(cleaned_def)
        
        if see_ref:
            term['definition'] = f"See: {see_ref}"
            term['reference_to'] = see_ref
            see_references[term['term']] = see_ref
            print(f"  🔗 {term['term'][:50]:50} → {see_ref}")
        else:
            term['definition'] = cleaned_def
        
        cleaned_terms.append(term)
    
    # Clean images and remove duplicates
    print()
    print("🖼️  Limpiando imágenes y eliminando duplicados...")
    cleaned_images = {}
    
    for term_name, images_data in term_images.items():
        # Remove duplicates
        unique_imgs = remove_duplicate_images(images_data)
        
        # Clean captions
        cleaned_imgs = []
        for img_data in unique_imgs:
            cleaned_caption = clean_caption(img_data['caption'])
            if cleaned_caption:
                img_data['caption'] = cleaned_caption
                cleaned_imgs.append(img_data)
        
        if cleaned_imgs:
            cleaned_images[term_name] = cleaned_imgs
            if len(images_data) != len(cleaned_imgs):
                print(f"  ✂️  {term_name[:45]:45}: {len(images_data)} → {len(cleaned_imgs)} imágenes")
    
    # Save cleaned data
    print()
    print("💾 Guardando datos limpios...")
    
    # Save cleaned terms
    with open(f"{OUTPUT_DIR}/morphology_terms.json", 'w', encoding='utf-8') as f:
        json.dump(cleaned_terms, f, indent=2, ensure_ascii=False)
    print(f"  ✅ morphology_terms.json actualizado")
    
    # Update terms by category
    terms_by_cat = defaultdict(list)
    for term in cleaned_terms:
        terms_by_cat[term['category']].append(term)
    
    with open(f"{OUTPUT_DIR}/terms_by_category.json", 'w', encoding='utf-8') as f:
        json.dump(dict(terms_by_cat), f, indent=2, ensure_ascii=False)
    print(f"  ✅ terms_by_category.json actualizado")
    
    # Save cleaned images
    with open(f"{OUTPUT_DIR}/term_images_with_captions.json", 'w', encoding='utf-8') as f:
        json.dump(cleaned_images, f, indent=2, ensure_ascii=False)
    print(f"  ✅ term_images_with_captions.json actualizado")
    
    # Save see references index
    with open(f"{OUTPUT_DIR}/term_references.json", 'w', encoding='utf-8') as f:
        json.dump(see_references, f, indent=2, ensure_ascii=False)
    print(f"  ✅ term_references.json creado")
    
    # Statistics
    print()
    print("="*70)
    print("📊 ESTADÍSTICAS")
    print("="*70)
    print(f"  Términos totales:              {len(cleaned_terms)}")
    print(f"  Términos con referencia 'see': {len(see_references)}")
    print(f"  Términos con imágenes:         {len(cleaned_images)}")
    
    # Calculate total images before and after
    total_before = sum(len(imgs) for imgs in term_images.values())
    total_after = sum(len(imgs) for imgs in cleaned_images.values())
    print(f"  Imágenes antes de limpieza:    {total_before}")
    print(f"  Imágenes después de limpieza:  {total_after}")
    print(f"  Duplicados eliminados:         {total_before - total_after}")
    
    print()
    print("✅ Limpieza completada!")

if __name__ == '__main__':
    main()
