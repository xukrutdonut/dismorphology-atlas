#!/usr/bin/env python3
"""
Mejora el algoritmo de asociación términos-imágenes para términos compuestos
"""
import json
import re
from collections import defaultdict

def normalize_text(text):
    """Normaliza texto para búsqueda"""
    text = text.lower().strip()
    # Mantener guiones y espacios importantes
    text = re.sub(r'[^\w\s\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_compound_components(term):
    """Extrae componentes de términos compuestos"""
    # Normalizar el término
    normalized = normalize_text(term)
    
    # Dividir por comas primero (términos múltiples)
    main_parts = [p.strip() for p in term.split(',')]
    
    components = []
    for part in main_parts:
        part = normalize_text(part)
        
        # Dividir por espacios y guiones
        words = re.split(r'[\s\-]+', part)
        words = [w.strip() for w in words if w.strip() and len(w) > 2]
        
        # Filtrar palabras muy comunes
        stop_words = {'of', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with', 'by'}
        words = [w for w in words if w not in stop_words]
        
        components.extend(words)
        
        # También incluir la parte completa
        if len(words) > 1:
            components.append(part.replace(' ', '').replace('-', ''))
    
    # Remover duplicados manteniendo orden
    seen = set()
    unique_components = []
    for comp in components:
        if comp not in seen and len(comp) > 2:
            seen.add(comp)
            unique_components.append(comp)
    
    return unique_components

def find_best_image_matches(term, term_mappings):
    """Encuentra las mejores asociaciones de imágenes para un término"""
    components = extract_compound_components(term)
    
    best_matches = []
    
    for mapping in term_mappings:
        caption = mapping.get('caption', '')
        normalized_caption = normalize_text(caption)
        
        # Calcular score de coincidencia
        score = 0
        matches = []
        
        for component in components:
            if component in normalized_caption:
                score += len(component)  # Palabras más largas tienen más peso
                matches.append(component)
        
        # Bonus por múltiples coincidencias
        if len(matches) > 1:
            score *= 1.5
        
        # Bonus por coincidencia exacta del término completo
        if normalize_text(term).replace(' ', '') in normalized_caption.replace(' ', ''):
            score *= 2
        
        if score > 0:
            mapping['match_score'] = score
            mapping['matched_components'] = matches
            best_matches.append(mapping)
    
    # Ordenar por score descendente
    best_matches.sort(key=lambda x: x['match_score'], reverse=True)
    
    return best_matches[:6]  # Máximo 6 imágenes

def improve_term_image_mapping():
    """Mejora el mapeo de términos-imágenes con algoritmo mejorado"""
    
    # Cargar mapeo existente
    with open('data/organized/term_image_mapping.json', 'r', encoding='utf-8') as f:
        existing_mapping = json.load(f)
    
    # Cargar términos
    with open('data/organized/morphology_terms.json', 'r', encoding='utf-8') as f:
        terms = json.load(f)
    
    print(f"Mejorando mapeo para {len(existing_mapping)} términos...")
    
    improved_mapping = {}
    terms_with_images = []
    stats = {
        'improved': 0,
        'compound_terms': 0,
        'total_with_images': 0
    }
    
    for term_obj in terms:
        term_name = term_obj['term']
        
        # Verificar si es término compuesto
        components = extract_compound_components(term_name)
        is_compound = len(components) > 2
        
        if is_compound:
            stats['compound_terms'] += 1
        
        if term_name in existing_mapping:
            original_mappings = existing_mapping[term_name]
            
            # Aplicar algoritmo mejorado
            improved_matches = find_best_image_matches(term_name, original_mappings)
            
            if improved_matches:
                improved_mapping[term_name] = improved_matches
                terms_with_images.append(term_name)
                stats['total_with_images'] += 1
                
                if len(improved_matches) != len(original_mappings):
                    stats['improved'] += 1
                    print(f"✓ Mejorado: {term_name} ({len(original_mappings)} -> {len(improved_matches)} imágenes)")
    
    print(f"\nEstadísticas:")
    print(f"  Términos compuestos: {stats['compound_terms']}")
    print(f"  Términos con imágenes: {stats['total_with_images']}")
    print(f"  Mapeos mejorados: {stats['improved']}")
    
    # Guardar mapeo mejorado
    with open('data/organized/term_image_mapping_improved.json', 'w', encoding='utf-8') as f:
        json.dump(improved_mapping, f, indent=2, ensure_ascii=False)
    
    # Guardar formato simple para la web
    simple_mapping = {}
    for term, mappings in improved_mapping.items():
        simple_mapping[term] = []
        for mapping in mappings:
            if mapping.get('images'):
                for img in mapping['images']:
                    simple_mapping[term].append({
                        'image': img,
                        'figure': mapping.get('figure', 1),
                        'caption': mapping.get('caption', f"Fig. {mapping.get('figure', 1)}"),
                        'match_score': mapping.get('match_score', 1.0)
                    })
    
    with open('data/organized/term_images_with_captions.json', 'w', encoding='utf-8') as f:
        json.dump(simple_mapping, f, indent=2, ensure_ascii=False)
    
    # Guardar lista de términos con imágenes
    with open('data/organized/terms_with_images.json', 'w', encoding='utf-8') as f:
        json.dump(terms_with_images, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Mapeo mejorado guardado")
    print(f"✓ {len(terms_with_images)} términos tienen imágenes asociadas")
    
    return improved_mapping, terms_with_images

if __name__ == "__main__":
    improve_term_image_mapping()