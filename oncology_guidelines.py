"""
Oncology Guidelines Database
Based on NCCN, ASCO, and ESMO Guidelines (2025)
"""

# Cancer Staging System
CANCER_STAGES = {
    'stage_0': 'Carcinoma in situ',
    'stage_i': 'Small, localized tumor',
    'stage_ii': 'Larger tumor or limited lymph node spread',
    'stage_iii': 'Regional lymph node involvement',
    'stage_iv': 'Metastatic disease'
}

# Comprehensive Guideline Database
ONCOLOGY_GUIDELINES = {
    'breast_cancer': {
        'cancer_type': 'Breast Cancer',
        'guideline_source': 'NCCN Guidelines v5.2025',
        'guideline_url': 'https://www.nccn.org/guidelines/category_1',
        'biomarker_tests': ['ER/PR', 'HER2', 'Ki-67', 'Oncotype DX'],
        
        'stage_0': {
            'standard_treatment': 'Surgery (lumpectomy) + Radiation',
            'alternatives': ['Mastectomy', 'Hormonal therapy (if ER+)'],
            'survival_rate': '98-99% 5-year',
            'recovery': '4-6 weeks',
            'evidence_level': 'Category 1',
            'cost_inr': '₹2,00,000-₹4,00,000',
            'contraindications': ['Pregnancy (for radiation)']
        },
        
        'stage_i': {
            'standard_treatment': 'Surgery + Radiation',
            'adjuvant_therapy': {
                'HR+/HER2-': 'Hormonal therapy 5-10 years',
                'HER2+': 'Trastuzumab + Chemotherapy',
                'Triple_negative': 'Chemotherapy'
            },
            'survival_rate': '95-100% 5-year',
            'recovery': '6-12 months',
            'evidence_level': 'Category 1',
            'cost_inr': '₹5,00,000-₹10,00,000',
            'biomarker_requirement': 'ER/PR/HER2 testing mandatory'
        },
        
        'stage_ii': {
            'standard_treatment': 'Neoadjuvant chemotherapy → Surgery → Adjuvant therapy',
            'chemotherapy_regimens': ['AC-T', 'TC', 'TCH (if HER2+)'],
            'survival_rate': '85-93% 5-year',
            'recovery': '9-18 months',
            'evidence_level': 'Category 1',
            'cost_inr': '₹8,00,000-₹15,00,000'
        },
        
        'stage_iii': {
            'standard_treatment': 'Neoadjuvant chemotherapy → Surgery → Radiation + Adjuvant therapy',
            'clinical_trial_recommendation': 'Consider enrollment',
            'survival_rate': '72-84% 5-year',
            'recovery': '12-24 months',
            'cost_inr': '₹10,00,000-₹18,00,000'
        },
        
        'stage_iv': {
            'treatment_goal': 'Palliation and life extension',
            'first_line_by_subtype': {
                'HR+/HER2-': 'CDK4/6 inhibitor + Hormonal therapy',
                'HER2+': 'Trastuzumab + Pertuzumab + Chemotherapy',
                'Triple_negative': 'Chemotherapy ± Immunotherapy (if PD-L1+)'
            },
            'median_survival': '2-5 years',
            'cost_inr': '₹15,00,000-₹30,00,000/year',
            'palliative_care': 'Strongly recommended alongside treatment'
        }
    },
    
    'lung_cancer': {
        'cancer_type': 'Non-Small Cell Lung Cancer (NSCLC)',
        'guideline_source': 'NCCN NSCLC v2.2026',
        'guideline_url': 'https://www.nccn.org/guidelines/category_1',
        'biomarker_tests': ['EGFR', 'ALK', 'ROS1', 'BRAF', 'PD-L1', 'KRAS G12C'],
        
        'stage_i': {
            'standard_treatment': 'Surgical resection (lobectomy)',
            'adjuvant_therapy': 'Osimertinib (if EGFR+), Chemotherapy (if ≥4cm)',
            'non_surgical_option': 'SBRT (stereotactic radiotherapy)',
            'survival_rate': '73-92% 5-year',
            'recovery': '6-12 weeks',
            'evidence_level': 'Category 1',
            'cost_inr': '₹4,00,000-₹8,00,000'
        },
        
        'stage_ii': {
            'standard_treatment': 'Surgery + Adjuvant chemotherapy',
            'biomarker_directed': 'Osimertinib (if EGFR+)',
            'survival_rate': '60-75% 5-year',
            'recovery': '9-18 months',
            'cost_inr': '₹6,00,000-₹12,00,000'
        },
        
        'stage_iii': {
            'resectable': 'Surgery + Adjuvant therapy',
            'unresectable': 'Concurrent chemoradiation → Durvalumab (if PD-L1+)',
            'survival_rate': '26-36% 5-year',
            'recovery': '12-24 months',
            'cost_inr': '₹8,00,000-₹15,00,000'
        },
        
        'stage_iv': {
            'treatment_approach': 'Based on driver mutations',
            'driver_positive': {
                'EGFR': 'Osimertinib (first-line)',
                'ALK': 'Alectinib or Brigatinib',
                'KRAS_G12C': 'Sotorasib or Adagrasib',
                'BRAF_V600E': 'Dabrafenib + Trametinib'
            },
            'driver_negative': 'Immunotherapy ± Chemotherapy (based on PD-L1)',
            'median_survival': '12-24 months',
            'cost_inr': '₹10,00,000-₹25,00,000/year',
            'biomarker_requirement': 'Comprehensive molecular testing mandatory'
        }
    },
    
    'colorectal_cancer': {
        'cancer_type': 'Colorectal Cancer',
        'guideline_source': 'NCCN Colon v5.2025',
        'guideline_url': 'https://www.nccn.org/guidelines/category_1',
        'biomarker_tests': ['MSI/MMR', 'KRAS/NRAS', 'BRAF', 'HER2'],
        
        'stage_i': {
            'standard_treatment': 'Surgical resection only',
            'adjuvant_therapy': 'Not recommended',
            'survival_rate': '90-95% 5-year',
            'recovery': '6-8 weeks',
            'cost_inr': '₹3,50,000-₹6,00,000'
        },
        
        'stage_ii': {
            'standard_treatment': 'Surgery',
            'adjuvant_therapy': 'Consider if high-risk features',
            'msi_high_note': 'Adjuvant chemo NOT recommended for MSI-H',
            'survival_rate': '80-87% 5-year',
            'cost_inr': '₹4,00,000-₹8,00,000'
        },
        
        'stage_iii': {
            'standard_treatment': 'Surgery + Adjuvant FOLFOX/CAPOX (6 months)',
            'survival_rate': '64-84% 5-year',
            'recovery': '9-18 months',
            'evidence_level': 'Category 1',
            'cost_inr': '₹6,00,000-₹12,00,000'
        },
        
        'stage_iv': {
            'potentially_resectable': 'Chemotherapy → Surgery',
            'unresectable': {
                'MSI_high': 'Pembrolizumab (immunotherapy)',
                'MSI_stable': 'FOLFOX/FOLFIRI + Bevacizumab ± anti-EGFR'
            },
            'median_survival': '24-30 months',
            'cost_inr': '₹10,00,000-₹20,00,000/year',
            'biomarker_requirement': 'MSI and RAS testing mandatory'
        }
    },
    
    'prostate_cancer': {
        'cancer_type': 'Prostate Cancer',
        'guideline_source': 'NCCN Prostate v4.2026',
        'guideline_url': 'https://www.nccn.org/guidelines/category_1',
        'biomarker_tests': ['PSA', 'Gleason score', 'BRCA testing'],
        
        'low_risk': {
            'standard_treatment': 'Active surveillance (preferred)',
            'alternatives': ['Surgery', 'Radiation therapy'],
            'survival_rate': '>95% 15-year',
            'monitoring': 'PSA every 6 months, biopsy every 2-5 years',
            'cost_inr': '₹50,000-₹1,00,000/year (surveillance)'
        },
        
        'intermediate_risk': {
            'standard_treatment': 'Radical prostatectomy OR Radiation + ADT (4-6 months)',
            'survival_rate': '85-95% 10-year',
            'recovery': '8-16 weeks',
            'cost_inr': '₹4,00,000-₹8,00,000'
        },
        
        'high_risk': {
            'standard_treatment': 'Radiation + ADT (18-36 months)',
            'alternative': 'Radical prostatectomy + extended lymph node dissection',
            'survival_rate': '70-85% 10-year',
            'cost_inr': '₹6,00,000-₹12,00,000'
        },
        
        'metastatic': {
            'castration_sensitive': 'ADT + Novel hormonal agent OR docetaxel',
            'castration_resistant': 'Abiraterone/Enzalutamide/Docetaxel',
            'median_survival': '3-5 years',
            'cost_inr': '₹8,00,000-₹15,00,000/year'
        }
    }
}

# Treatment Risks Database
TREATMENT_RISKS = {
    'chemotherapy': ['Nausea', 'Hair loss', 'Fatigue', 'Infection risk', 'Neuropathy'],
    'radiation': ['Skin changes', 'Fatigue', 'Local tissue damage'],
    'surgery': ['Infection', 'Bleeding', 'Anesthesia risks'],
    'immunotherapy': ['Immune-related side effects', 'Fatigue', 'Rash'],
    'targeted_therapy': ['Diarrhea', 'Liver toxicity', 'Skin issues', 'Hypertension'],
    'hormonal_therapy': ['Hot flashes', 'Bone loss', 'Cardiovascular effects']
}

# Guideline URLs (Official Sources)
GUIDELINE_REFERENCES = {
    'nccn': 'https://www.nccn.org/guidelines/category_1',
    'asco': 'https://www.asco.org/research-guidelines/quality-guidelines/guidelines',
    'esmo': 'https://www.esmo.org/guidelines/guidelines-by-topic',
    'cancer_care_ontario': 'https://www.cancercareontario.ca/en/guidelines-advice'
}