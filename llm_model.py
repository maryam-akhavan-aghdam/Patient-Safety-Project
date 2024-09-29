
# pip install transformers datasets torch

# pip install scikit-learn

# pip install transformers[torch] accelerate -U

import argparse

parser = argparse.ArgumentParser(description="LLM Backend")
parser.add_argument('--input', type=str, help="the input prompt", required=True)
args = parser.parse_args()


import torch
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification

# Fine-tuning the ClinicalBERT LLM Model

model_name = "emilyalsentzer/Bio_ClinicalBERT"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")


prompt = args.input

entities = nlp(prompt)


diagnosis_mapping = {
    'hypertension': 'Cardiology',
    'chest pain': 'Cardiology',
    'shortness of breath': 'Pulmonology',
    'cough': 'Pulmonology',
    'asthma': 'Pulmonology',
    'diabetes': 'Endocrinology',
    'fever': 'Infectious Diseases',
    'fatigue': 'General Medicine',
    'back pain': 'Orthopedics',
    'nausea': 'Gastroenterology',
    'headache': 'Neurology',
    'dizziness': 'Neurology',
    'joint pain': 'Rheumatology',
}

treatment_mapping = {
    'Cardiology': ['ACE inhibitors', 'Beta-blockers', 'Calcium channel blockers', 'Statins', 'Diuretics'],
    'Pulmonology': ['Inhaled corticosteroids', 'Bronchodilators', 'Oxygen therapy', 'Leukotriene modifiers'],
    'Endocrinology': ['Insulin', 'Metformin', 'Sulfonylureas', 'Thiazolidinediones'],
    'Infectious Diseases': ['Antibiotics', 'Antivirals', 'Antifungals', 'Supportive care'],
    'General Medicine': ['Rest', 'Hydration', 'Pain relievers', 'Vitamin supplements'],
    'Orthopedics': ['Physical therapy', 'Nonsteroidal anti-inflammatory drugs (NSAIDs)', 'Corticosteroid injections'],
    'Gastroenterology': ['Antacids', 'Proton pump inhibitors (PPIs)', 'Antiemetics'],
    'Neurology': ['Pain relievers', 'Triptans', 'Beta-blockers for migraine prevention', 'Anticonvulsants'],
    'Rheumatology': ['Nonsteroidal anti-inflammatory drugs (NSAIDs)', 'Corticosteroids', 'Disease-modifying antirheumatic drugs (DMARDs)'],
}

# Score is between 0 (no error) and 1 (high risk of error)
medication_error_rules = {
    ('hypertension', 'Beta-blockers'): 0.2,  # Low risk
    ('Cardiology', 'ACE inhibitors'): 0.15,  # Moderate risk
    ('Pulmonology', 'Inhaled corticosteroids'): 0.3,  # Moderate risk of overuse
    ('Pulmonology', 'Bronchodilators'): 0.1,  # Low risk
    ('Endocrinology', 'Metformin'): 0.15,  # Very low risk
    ('Infectious Diseases', 'Antibiotics'): 0.05,  # Minimal risk
    ('Orthopedics', 'NSAIDs'): 0.27,  # Low risk of gastrointestinal side effects
    ('Gastroenterology', 'Antacids'): 0.19,  # Very low risk
    ('Neurology', 'Triptans'): 0.32,  # Possible risk of interaction
    ('Rheumatology', 'DMARDs'): 0.43,  # Moderate risk of immunosuppression
}

def group_entities(entities):
    grouped_entities = []
    current_entity = {
        'entity': entities[0]['entity_group'],
        'word': entities[0]['word']
    }
    
    for i in range(1, len(entities)):
        if entities[i]['entity_group'] == current_entity['entity']:
            current_entity['word'] += entities[i]['word'].replace("##", "")  # Merge subwords
        else:
            grouped_entities.append(current_entity)
            current_entity = {
                'entity': entities[i]['entity_group'],
                'word': entities[i]['word']
            }
    
    grouped_entities.append(current_entity)
    return grouped_entities

grouped_entities = group_entities(entities)


diagnoses = []
for entity in grouped_entities:
    word = entity['word'].lower()
    for diagnosis, category in diagnosis_mapping.items():
        if diagnosis in word:
            diagnoses.append({
                'diagnosis': diagnosis,
                'category': category
            })


output_results = []

if diagnoses:
    for diag in diagnoses:
        category = diag['category']
        treatments = treatment_mapping.get(category, [])[:2]  # Limit to exactly 2 treatments
        treatments_info = []
        
        for treatment in treatments:
            error_score = medication_error_rules.get((diag['diagnosis'], treatment), 0.0)
            treatments_info.append({
                'description': treatment,
                'score': f"{error_score:.2f}"  
            })
        
        output_results.append({
            'Category': category,
            'Treatments': treatments_info
        })


print(output_results)

