#!/usr/bin/env python3
"""
Create a sample JSON file with well-formatted anatomical terms
"""
import json

# Example of well-extracted terms from the documents
sample_terms = [
    {
        "term": "Antihelix",
        "definition": "A Y-shaped curved cartilaginous ridge arising from the antitragus and separating the concha, triangular fossa, and scapha. The antihelix represents a folding of the conchal cartilage and it usually has similar prominence to a well-developed helix.",
        "category": "ear",
        "document": "Elements of morphology - Standard terminology for the ear",
        "related_images": ["images/elements_of_morphology_standard_terminology_for_the_ear-003.png"]
    },
    {
        "term": "Tragus",
        "definition": "A posterior, slightly inferior, protrusion of skin-covered cartilage, anterior to the auditory meatus. The inferoposterior margin of the tragus forms the anterior wall of the incisura.",
        "category": "ear",
        "document": "Elements of morphology - Standard terminology for the ear",
        "related_images": ["images/elements_of_morphology_standard_terminology_for_the_ear-068.png"]
    },
    {
        "term": "Philtrum",
        "definition": "The vertical groove in the medial portion of the upper lip, extending from the nasal septum to the vermilion border.",
        "category": "nose_philtrum",
        "document": "Elements of morphology - Standard terminology for the nose and philtrum",
        "related_images": []
    },
    {
        "term": "Palpebral fissure",
        "definition": "The distance between the inner and outer canthi of the eye. The palpebral fissure length can be measured in several ways.",
        "category": "periorbital",
        "document": "Elements of morphology - Standard terminology for the periorbital region",
        "related_images": []
    },
    {
        "term": "Clinodactyly",
        "definition": "A congenital curvature of a finger or toe in the radio-ulnar or lateral plane.",
        "category": "hands_feet",
        "document": "Elements of morphology - Standard terminology for the hands and feet",
        "related_images": []
    }
]

# Save sample
with open('data/organized/SAMPLE_TERMS.json', 'w', encoding='utf-8') as f:
    json.dump(sample_terms, f, indent=2, ensure_ascii=False)

print("✓ Sample terms file created: data/organized/SAMPLE_TERMS.json")
print(f"\nExample format:")
for term in sample_terms[:2]:
    print(f"\n{term['term']} ({term['category']})")
    print(f"  {term['definition'][:80]}...")
