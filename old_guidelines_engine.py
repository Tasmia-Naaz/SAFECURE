"""
Guideline-Based Treatment Analysis Engine with Simplified Explanations
Rule-based system using oncology guidelines
"""

from oncology_guidelines import ONCOLOGY_GUIDELINES, CANCER_STAGES, TREATMENT_RISKS, GUIDELINE_REFERENCES

class GuidelineEngine:
    """Analyzes treatments against oncology guidelines with simplified explanations"""
    
    # Valid cancer-related keywords
    CANCER_KEYWORDS = [
        'cancer', 'tumor', 'tumour', 'carcinoma', 'sarcoma', 'melanoma', 'leukemia', 
        'lymphoma', 'myeloma', 'metastatic', 'malignant', 'neoplasm', 'oncology',
        'breast', 'lung', 'colon', 'rectal', 'colorectal', 'prostate', 'pancreatic',
        'liver', 'kidney', 'bladder', 'ovarian', 'cervical', 'uterine', 'testicular',
        'thyroid', 'brain', 'glioma', 'meningioma', 'nsclc', 'sclc', 'adenocarcinoma',
        'squamous cell', 'basal cell', 'dcis', 'invasive', 'her2', 'triple negative',
        'stage', 'grade', 'biopsy', 'metastasis'
    ]
    
    # Valid treatment keywords
    TREATMENT_KEYWORDS = [
        'chemotherapy', 'chemo', 'radiation', 'radiotherapy', 'surgery', 'surgical',
        'resection', 'mastectomy', 'lumpectomy', 'lobectomy', 'colectomy', 'prostatectomy',
        'immunotherapy', 'targeted therapy', 'hormonal therapy', 'hormone therapy',
        'adjuvant', 'neoadjuvant', 'palliative', 'pembrolizumab', 'nivolumab',
        'trastuzumab', 'bevacizumab', 'osimertinib',
        # NEWLY ADDED TREATMENTS
        'cryotherapy', 'cryo therapy', 'freezing therapy',
        'active surveillance', 'watchful waiting', 'observation',
        'photodynamic therapy', 'pdt', 'light therapy',
        'stem cell transplant', 'bone marrow transplant', 'hematopoietic transplant',
        'radiofrequency ablation', 'rfa', 'ablation therapy'
    ]
    
    def __init__(self):
        self.guidelines = ONCOLOGY_GUIDELINES
    
    def format_stage_display(self, stage):
        
        stage_mappings = {
            'stage_0': 'Stage 0',
            'stage_i': 'Stage I',
            'stage_ii': 'Stage II',
            'stage_iii': 'Stage III',
            'stage_iv': 'Stage IV',
            'low_risk': 'Low Risk',
            'intermediate_risk': 'Intermediate Risk',
            'high_risk': 'High Risk',
            'metastatic': 'Metastatic'
        }
        return stage_mappings.get(stage, stage.replace('_', ' ').title())
    
    def simplify_treatment_text(self, technical_text, cancer_type, stage):
        """Convert medical jargon to plain language"""
        
        # Common simplification mappings
        simplifications = {
            # Breast Cancer
            'Neoadjuvant chemotherapy → Surgery → Adjuvant therapy': 
                'First, you receive chemotherapy to shrink the tumor. Then surgery to remove it. Finally, additional treatment to prevent cancer from coming back.',
            
            'Surgery + Radiation':
                'The tumor is removed through surgery, followed by radiation therapy to kill any remaining cancer cells in the area.',
            
            'Neoadjuvant chemotherapy → Surgery → Radiation + Adjuvant therapy':
                'Treatment starts with chemotherapy to shrink the tumor, then surgery to remove it, radiation to target the area, and follow-up treatment to reduce recurrence risk.',
            
            'Surgery (lumpectomy) + Radiation':
                'A small surgery removes just the tumor (not the whole breast), followed by radiation to the breast area.',
            
            # Lung Cancer
            'Surgical resection (lobectomy)':
                'Surgery to remove the part of the lung containing the tumor.',
            
            'Surgery + Adjuvant chemotherapy':
                'Surgery removes the tumor, followed by chemotherapy to kill any remaining cancer cells.',
            
            'Concurrent chemoradiation → Durvalumab (if PD-L1+)':
                'Chemotherapy and radiation given together, followed by immunotherapy drug (Durvalumab) if tests show your cancer is likely to respond.',
            
            # Colorectal Cancer
            'Surgical resection only':
                'Surgery to remove the tumor is the only treatment needed at this stage.',
            
            'Surgery + Adjuvant FOLFOX/CAPOX (6 months)':
                'Surgery removes the tumor, followed by 6 months of chemotherapy using drug combinations (FOLFOX or CAPOX).',
            
            'Chemotherapy → Surgery':
                'Chemotherapy first to shrink the tumor, then surgery to remove it.',
            
            # Prostate Cancer
            'Active surveillance (preferred)':
                'Closely monitoring the cancer with regular tests instead of immediate treatment, because the cancer is slow-growing.',
            
            'Radical prostatectomy OR Radiation + ADT (4-6 months)':
                'Either complete removal of the prostate through surgery, OR radiation therapy combined with hormone therapy for 4-6 months.',
            
            'Radiation + ADT (18-36 months)':
                'Radiation therapy to the prostate area, combined with hormone therapy for 18-36 months to shrink the cancer.',
        }
        
        # Try exact match first
        if technical_text in simplifications:
            return simplifications[technical_text]
        
        # General simplifications for common terms
        simplified = technical_text
        
        # Replace common medical terms
        replacements = {
            'adjuvant': 'follow-up',
            'neoadjuvant': 'pre-surgery',
            'resection': 'surgical removal',
            'lobectomy': 'lung surgery',
            'lumpectomy': 'tumor removal surgery',
            'mastectomy': 'breast removal surgery',
            'prostatectomy': 'prostate removal surgery',
            '→': ', then',
            '+': ' combined with',
            'CDK4/6 inhibitor': 'cancer growth blocker',
            'hormonal therapy': 'hormone treatment',
            'immunotherapy': 'immune system treatment',
            'palliative': 'symptom management',
        }
        
        for medical, simple in replacements.items():
            simplified = simplified.replace(medical, simple)
        
        return simplified
    
    def simplify_evidence_level(self, evidence_level):
        """Explain what evidence level means"""
        explanations = {
            'Category 1': 'Highest confidence - Based on extensive research and expert agreement. This is the standard treatment that doctors worldwide recommend.',
            'Category 2A': 'High confidence - Strong evidence supports this approach. Most doctors would recommend this.',
            'Category 2B': 'Moderate confidence - Some evidence supports this, but there may be other good options too.',
            'Category 3': 'Lower confidence - Limited research available. Doctors may disagree on this approach.',
        }
        
        return explanations.get(evidence_level, 'This treatment is supported by medical research and clinical experience.')
    
    def _has_keyboard_mashing(self, word):
        """Detect keyboard mashing patterns (e.g., 'asdfgh', 'qwerty')"""
        keyboard_rows = [
            'qwertyuiop',
            'asdfghjkl',
            'zxcvbnm'
        ]
        
        word_lower = word.lower()
        
        # Check for consecutive keyboard sequences
        for row in keyboard_rows:
            for i in range(len(row) - 3):
                sequence = row[i:i+4]
                if sequence in word_lower or sequence[::-1] in word_lower:
                    return True
        
        return False
    
    def is_valid_cancer_input(self, symptoms):
        """Validate if symptoms contain cancer-related information"""
        symptoms_lower = symptoms.lower().strip()
        
        # Check 1: Minimum length requirement
        if len(symptoms_lower) < 5:
            return False
        
        # Check 2: Check for gibberish (repeated characters, random strings)
        words = symptoms_lower.split()
        
        # Filter out very short words
        meaningful_words = [word for word in words if len(word) > 2 and word.isalpha()]
        
        if len(meaningful_words) < 2:
            return False
        
        # Check 3: Detect gibberish by checking character diversity
        gibberish_count = 0
        for word in meaningful_words:
            if len(word) > 4:
                unique_chars = len(set(word))
                char_diversity = unique_chars / len(word)
                
                # If less than 40% unique characters, likely gibberish
                if char_diversity < 0.4:
                    gibberish_count += 1
                
                # Check for keyboard mashing patterns (consecutive keys)
                consecutive_pattern = self._has_keyboard_mashing(word)
                if consecutive_pattern:
                    gibberish_count += 1
        
        # If more than 50% of words are gibberish, reject
        if len(meaningful_words) > 0 and gibberish_count / len(meaningful_words) > 0.5:
            return False
        
        # Check 4: Must contain at least ONE cancer-related keyword
        has_cancer_keyword = any(keyword in symptoms_lower for keyword in self.CANCER_KEYWORDS)
        
        if not has_cancer_keyword:
            return False
        
        # Check 5: Verify it's not just the keyword with gibberish
        # Count how many real medical/cancer words vs total words
        medical_word_count = sum(1 for keyword in self.CANCER_KEYWORDS if keyword in symptoms_lower)
        
        # Need at least 1 cancer keyword and reasonable word ratio
        if medical_word_count == 0:
            return False
        
        return True
    
    def is_valid_treatment(self, treatment):
        """Validate if treatment is cancer-related"""
        treatment_lower = treatment.lower().strip()
        
        # Check 1: Minimum length
        if len(treatment_lower) < 4:
            return False
        
        # Check 2: Check for gibberish
        words = treatment_lower.split()
        
        if len(words) == 0:
            return False
        
        gibberish_count = 0
        for word in words:
            if len(word) > 4:
                unique_chars = len(set(word))
                char_diversity = unique_chars / len(word)
                
                if char_diversity < 0.4:
                    gibberish_count += 1
                
                if self._has_keyboard_mashing(word):
                    gibberish_count += 1
        
        # If more than 50% gibberish, reject
        if len(words) > 0 and gibberish_count / len(words) > 0.5:
            return False
        
        # Check 3: Must contain at least ONE treatment keyword
        has_treatment_keyword = any(keyword in treatment_lower for keyword in self.TREATMENT_KEYWORDS)
        
        return has_treatment_keyword
    
    def normalize_cancer_type(self, symptoms):
        """Extract cancer type from symptoms"""
        symptoms_lower = symptoms.lower()
        
        cancer_mapping = {
            'breast': 'breast_cancer',
            'lung': 'lung_cancer',
            'nsclc': 'lung_cancer',
            'sclc': 'lung_cancer',
            'colon': 'colorectal_cancer',
            'rectal': 'colorectal_cancer',
            'colorectal': 'colorectal_cancer',
            'prostate': 'prostate_cancer'
        }
        
        for keyword, cancer_type in cancer_mapping.items():
            if keyword in symptoms_lower:
                return cancer_type
        
        return None
    
    def normalize_stage(self, symptoms):
        """Extract staging information from symptoms"""
        symptoms_lower = symptoms.lower()
        
        # Look for stage indicators
        if 'stage iv' in symptoms_lower or 'stage 4' in symptoms_lower or 'metastatic' in symptoms_lower:
            return 'stage_iv'
        elif 'stage iii' in symptoms_lower or 'stage 3' in symptoms_lower:
            return 'stage_iii'
        elif 'stage ii' in symptoms_lower or 'stage 2' in symptoms_lower:
            return 'stage_ii'
        elif 'stage i' in symptoms_lower or 'stage 1' in symptoms_lower:
            return 'stage_i'
        elif 'stage 0' in symptoms_lower or 'in situ' in symptoms_lower or 'dcis' in symptoms_lower:
            return 'stage_0'
        
        # For prostate cancer, check risk levels
        if 'low risk' in symptoms_lower:
            return 'low_risk'
        elif 'intermediate' in symptoms_lower:
            return 'intermediate_risk'
        elif 'high risk' in symptoms_lower:
            return 'high_risk'
        
        return None
    
    def analyze_treatment(self, symptoms, recommended_treatment):
        """Main analysis function with comprehensive validation"""
        
        # STEP 1: Validate symptoms contain cancer-related information
        if not self.is_valid_cancer_input(symptoms):
            return {
                'status': 'incomplete',
                'message': 'Please provide valid cancer-related symptoms or diagnosis information.',
                'validation_error': True,
                'suggestion': '''Please provide meaningful information that includes:

• Cancer type (breast, lung, colorectal, or prostate cancer)
• Stage information (Stage 0, I, II, III, or IV) 
• Relevant symptoms or diagnosis details

Examples of valid input:
✓ "Stage II breast cancer, HER2 positive"
✓ "Lung cancer stage III, EGFR positive"  
✓ "Colorectal cancer stage IV with liver metastases"
✗ Random characters or unrelated text'''
            }
        
        # STEP 2: Validate treatment is cancer-related
        if not self.is_valid_treatment(recommended_treatment):
            return {
                'status': 'incomplete',
                'message': 'Please provide a valid cancer treatment.',
                'validation_error': True,
                'suggestion': '''Valid cancer treatments include:

• Chemotherapy / Chemo
• Radiation therapy / Radiotherapy
• Surgery / Surgical resection
• Immunotherapy (e.g., Pembrolizumab, Nivolumab)
• Targeted therapy (e.g., Trastuzumab, Osimertinib)
• Hormonal therapy / Hormone therapy

Examples:
✓ "Chemotherapy"
✓ "Surgery followed by radiation"
✓ "Targeted therapy with Trastuzumab"
✗ Random characters or unrelated treatments'''
            }
        
        # STEP 3: Identify cancer type
        cancer_type = self.normalize_cancer_type(symptoms)
        
        if not cancer_type:
            return {
                'status': 'incomplete',
                'message': 'Unable to identify specific cancer type. Please specify (breast, lung, colorectal, or prostate cancer).',
                'validation_error': True,
                'suggestion': 'Currently supported cancer types:\n• Breast Cancer\n• Lung Cancer (NSCLC)\n• Colorectal Cancer\n• Prostate Cancer'
            }
        
        # STEP 4: Get guideline data
        guideline_data = self.guidelines.get(cancer_type)
        
        if not guideline_data:
            return {
                'status': 'not_found',
                'message': 'Guidelines not available for this cancer type.',
                'validation_error': True
            }
        
        # STEP 5: Extract staging
        stage = self.normalize_stage(symptoms)
        
        if not stage:
            return {
                'status': 'incomplete',
                'message': 'Cancer stage not specified. Please include staging information (Stage 0, I, II, III, or IV).',
                'cancer_type': guideline_data['cancer_type'],
                'guideline_source': guideline_data['guideline_source'],
                'biomarker_tests_required': guideline_data.get('biomarker_tests', []),
                'validation_error': True,
                'suggestion': 'Please specify the cancer stage:\n• Stage 0 (in situ)\n• Stage I (early)\n• Stage II (local spread)\n• Stage III (regional)\n• Stage IV (metastatic)'
            }
        
        # STEP 6: Get stage-specific guideline
        stage_guideline = guideline_data.get(stage)
        
        if not stage_guideline:
            return {
                'status': 'not_found',
                'message': f'Guidelines not available for {self.format_stage_display(stage)}.',
                'validation_error': True
            }
        
        # STEP 7: Analyze recommended treatment against guideline
        treatment_lower = recommended_treatment.lower()
        
        # Check if treatment aligns with guidelines
        is_aligned = self._check_treatment_alignment(treatment_lower, stage_guideline)
        
        # STEP 8: Get technical and simplified treatment text
        technical_treatment = stage_guideline.get('standard_treatment', 'N/A')
        simplified_treatment = self.simplify_treatment_text(
            technical_treatment, 
            guideline_data['cancer_type'], 
            stage
        )
        
        # Simplify evidence level
        evidence_level = stage_guideline.get('evidence_level', 'N/A')
        evidence_explanation = self.simplify_evidence_level(evidence_level)
        
        # STEP 9: Prepare comprehensive result with PROPERLY FORMATTED STAGE
        result = {
            'status': 'found',
            'validation_error': False,
            'cancer_type': guideline_data['cancer_type'],
            'stage': self.format_stage_display(stage),
            'stage_description': CANCER_STAGES.get(stage, 'N/A'),
            'recommended_treatment': recommended_treatment,
            'guideline_source': guideline_data['guideline_source'],
            'guideline_url': guideline_data.get('guideline_url'),
            'biomarker_tests_required': guideline_data.get('biomarker_tests', []),
            
            # Treatment alignment
            'alignment': 'Aligned with Guidelines' if is_aligned else 'Requires Verification',
            'alignment_details': self._get_alignment_details(treatment_lower, stage_guideline),
            
            # Stage-specific information (BOTH VERSIONS)
            'standard_treatment': technical_treatment,
            'standard_treatment_simple': simplified_treatment,
            'standard_treatment_technical': technical_treatment,
            
            'alternative_treatments': stage_guideline.get('alternatives', []),
            'survival_rate': stage_guideline.get('survival_rate', 'N/A'),
            'recovery_time': stage_guideline.get('recovery', 'N/A'),
            'estimated_cost': stage_guideline.get('cost_inr', 'N/A'),
            'evidence_level': evidence_level,
            'evidence_explanation': evidence_explanation,
            
            # Additional considerations
            'adjuvant_therapy': stage_guideline.get('adjuvant_therapy', {}),
            'contraindications': stage_guideline.get('contraindications', []),
            'special_notes': stage_guideline.get('biomarker_requirement', ''),
            
            # Risks
            'potential_risks': self._get_treatment_risks(treatment_lower),
            
            # References
            'official_guidelines': GUIDELINE_REFERENCES
        }
        
        return result
    
    def _check_treatment_alignment(self, treatment, stage_guideline):
        """Check if treatment aligns with guideline"""
        standard = str(stage_guideline.get('standard_treatment', '')).lower()
        alternatives = [str(alt).lower() for alt in stage_guideline.get('alternatives', [])]
        adjuvant = str(stage_guideline.get('adjuvant_therapy', '')).lower()
        
        # Check if treatment appears in any guideline recommendation
        for guideline_text in [standard, adjuvant] + alternatives:
            if any(keyword in guideline_text for keyword in treatment.split()):
                return True
        
        return False
    
    def _get_alignment_details(self, treatment, stage_guideline):
        """Get detailed alignment information"""
        standard = stage_guideline.get('standard_treatment', 'N/A')
        
        # Simple keyword matching
        if any(word in standard.lower() for word in treatment.split()):
            return "✓ Your recommended treatment matches the standard guideline approach"
        else:
            return "⚠ Your recommended treatment differs from the standard guideline"
    
    def _get_treatment_risks(self, treatment):
        """Get risks for treatment modality"""
        risks = []
        
        for modality, modality_risks in TREATMENT_RISKS.items():
            if modality in treatment:
                risks.extend(modality_risks)
        
        return risks if risks else ['Consult oncologist for specific risks']

# Global instance
guideline_engine = GuidelineEngine()