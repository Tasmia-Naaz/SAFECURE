"""
SafeCure - Smart Second Opinion System
Flask Web Application for Cancer Treatment Analysis
Dual System: Rule-Based + Guideline-Based Analysis
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from user_agents import parse
import ast

# Import guideline engine
from old_guidelines_engine import guideline_engine

# PDF Generation imports (optional)
try:
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    PDF_ENABLED = True
except ImportError:
    PDF_ENABLED = False
    print("⚠️  ReportLab not installed. PDF generation disabled.")

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///safecure.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Mail Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'safecure.care123@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'zweo fsyo lnxl xsle'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME') or 'safecure.care123@gmail.com'

    BASE_URL = 'http://localhost:5000'

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Extensions
db = SQLAlchemy(app)
mail = Mail(app)

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(db.Model):
    """User account model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    consultations = db.relationship('Consultation', backref='user', lazy=True, cascade='all, delete-orphan')
    login_history = db.relationship('LoginHistory', backref='user', lazy=True, cascade='all, delete-orphan')

class LoginHistory(db.Model):
    """Track login attempts and device information"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    device_info = db.Column(db.String(200))
    browser_info = db.Column(db.String(200))
    is_suspicious = db.Column(db.Boolean, default=False)
    success = db.Column(db.Boolean, default=True)

class Consultation(db.Model):
    """Store consultation records"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    recommended_treatment = db.Column(db.String(200), nullable=False)
    result = db.Column(db.Text, nullable=False)
    analysis_type = db.Column(db.String(50), default='combined')  # 'guideline', 'rule_based', or 'combined'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============================================================================
# EMAIL FUNCTIONS
# ============================================================================

def send_welcome_email(user):
    """Send welcome email after registration"""
    try:
        msg = Message(
            subject='Welcome to SafeCure! 🎉',
            recipients=[user.email]
        )
        
        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #667eea;">Welcome to SafeCure! 🎉</h2>
                <p>Hello <strong>{user.name}</strong>,</p>
                <p>Thank you for registering with SafeCure - Smart Second Opinion System.</p>

                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #667eea;">What You Can Do:</h3>
                    <ul>
                        <li>✅ Get second opinions on cancer treatments</li>
                        <li>✅ Verify treatment recommendations against NCCN guidelines</li>
                        <li>✅ Understand risks and recovery times</li>
                        <li>✅ Track your consultation history</li>
                    </ul>
                </div>

                <p style="margin-top: 30px;">
                    <a href="{app.config['BASE_URL']}/login" 
                       style="background-color: #667eea; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Login to Your Account
                    </a>
                </p>

                <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; 
                         color: #666; font-size: 12px;">
                    <strong>⚠️ Important:</strong> SafeCure provides informational support only. 
                    Always consult qualified healthcare professionals for medical decisions.
                </p>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        print(f"✓ Welcome email sent to {user.email}")
        return True
    except Exception as e:
        print(f"✗ Error sending welcome email: {e}")
        return False

def send_login_alert_email(user, device_info, browser_info, ip_address):
    """Send email alert for new device login"""
    try:
        msg = Message(
            subject='🔒 SafeCure: New Device Login Detected',
            recipients=[user.email]
        )
        
        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #667eea;">🔒 New Device Login Alert</h2>
                <p>Hello <strong>{user.name}</strong>,</p>
                <p>We detected a login to your SafeCure account from a new device:</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>🕐 Time:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>💻 Device:</strong> {device_info}</p>
                    <p><strong>🌐 Browser:</strong> {browser_info}</p>
                    <p><strong>📍 IP Address:</strong> {ip_address}</p>
                </div>
                
                <p>If this was you, no action is needed. Your account is secure.</p>
                
                <p><strong>⚠️ If this wasn't you:</strong></p>
                <ol>
                    <li>Change your password immediately</li>
                    <li>Review your account activity</li>
                    <li>Contact support if needed</li>
                </ol>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        print(f"✓ Login alert sent to {user.email}")
        return True
    except Exception as e:
        print(f"✗ Error sending login alert: {e}")
        return False

def send_suspicious_login_email(user, failed_attempts, ip_address):
    """Send email alert for suspicious login attempts"""
    try:
        msg = Message(
            subject='⚠️ SafeCure: Suspicious Login Activity Detected',
            recipients=[user.email]
        )
        
        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; 
                        border: 1px solid #ff6b6b; border-radius: 10px;">
                <h2 style="color: #ff6b6b;">⚠️ Suspicious Login Activity Alert</h2>
                <p>Hello <strong>{user.name}</strong>,</p>
                <p><strong>We detected suspicious activity on your SafeCure account.</strong></p>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; 
                            margin: 20px 0; border-left: 4px solid #ff6b6b;">
                    <p><strong>🚨 Alert Details:</strong></p>
                    <p><strong>Failed Login Attempts:</strong> {failed_attempts}</p>
                    <p><strong>Time:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>IP Address:</strong> {ip_address}</p>
                </div>
                
                <p><strong>🛡️ Recommended Actions:</strong></p>
                <ol>
                    <li><strong>Change your password immediately</strong></li>
                    <li>Review recent account activity</li>
                    <li>Contact support if you didn't make these attempts</li>
                </ol>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        print(f"✓ Suspicious activity alert sent to {user.email}")
        return True
    except Exception as e:
        print(f"✗ Error sending suspicious activity alert: {e}")
        return False

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_device_info(user_agent_string):
    """Extract device information from user agent"""
    user_agent = parse(user_agent_string)
    return f"{user_agent.device.family} ({user_agent.os.family} {user_agent.os.version_string})"

def get_browser_info(user_agent_string):
    """Extract browser information from user agent"""
    user_agent = parse(user_agent_string)
    return f"{user_agent.browser.family} {user_agent.browser.version_string}"

def is_new_device(user, device_info):
    """Check if login is from a new device"""
    previous_logins = LoginHistory.query.filter_by(
        user_id=user.id,
        device_info=device_info,
        success=True
    ).first()
    return previous_logins is None

def check_suspicious_activity(user, ip_address):
    """Check for suspicious login attempts (3+ failed attempts in 15 minutes)"""
    time_threshold = datetime.utcnow() - timedelta(minutes=15)
    failed_attempts = LoginHistory.query.filter(
        LoginHistory.user_id == user.id,
        LoginHistory.success == False,
        LoginHistory.login_time >= time_threshold
    ).count()
    
    return failed_attempts >= 3, failed_attempts

# ============================================================================
# RULE-BASED KNOWLEDGE BASE (Original System)
# ============================================================================

TREATMENT_DATABASE = {
    'chemotherapy': {
        'indications': ['breast cancer', 'lung cancer', 'leukemia', 'lymphoma', 'colon cancer'],
        'risks': ['Nausea and vomiting', 'Hair loss', 'Fatigue', 'Increased infection risk', 'Anemia'],
        'recovery_time': '6-12 months',
        'urgency': 'High - Start within 2-4 weeks of diagnosis',
        'survival_rate': '60-80%',
        'estimated_cost': '₹4,00,000 - ₹7,50,000',
        'cost_usd': '$5,000 - $9,000',
        'myths': {
            'myth1': 'Chemotherapy is always necessary for all cancers',
            'fact1': 'Treatment depends on cancer type, stage, and individual factors',
            'myth2': 'Chemotherapy always causes severe side effects',
            'fact2': 'Side effects vary; modern medications help manage them effectively'
        }
    },
    'radiation therapy': {
        'indications': ['localized tumors', 'brain cancer', 'prostate cancer', 'breast cancer'],
        'risks': ['Skin irritation', 'Fatigue', 'Localized pain', 'Long-term tissue changes'],
        'recovery_time': '3-6 months',
        'urgency': 'Moderate - Typically within 4-6 weeks',
        'survival_rate': '65-85%',
        'estimated_cost': '₹3,20,000 - ₹6,00,000',
        'cost_usd': '$4,000 - $7,500',
        'myths': {
            'myth1': 'Radiation makes you radioactive',
            'fact1': 'External radiation does not make you radioactive',
            'myth2': 'Radiation always burns the skin',
            'fact2': 'Modern techniques minimize skin damage significantly'
        }
    },
    'surgery': {
        'indications': ['solid tumors', 'localized cancer', 'early-stage cancer', 'tumor biopsy'],
        'risks': ['Infection', 'Bleeding', 'Anesthesia complications', 'Organ damage'],
        'recovery_time': '4-8 weeks',
        'urgency': 'High - Timing depends on cancer stage',
        'survival_rate': '70-90%',
        'estimated_cost': '₹4,80,000 - ₹9,00,000',
        'cost_usd': '$6,000 - $11,000',
        'myths': {
            'myth1': 'Surgery causes cancer to spread',
            'fact1': 'Proper surgical techniques prevent spread; surgery often cures localized cancer',
            'myth2': 'All tumors require immediate surgery',
            'fact2': 'Some cancers respond better to other treatments first'
        }
    },
    'immunotherapy': {
        'indications': ['melanoma', 'lung cancer', 'kidney cancer', 'bladder cancer'],
        'risks': ['Immune-related side effects', 'Fatigue', 'Skin reactions', 'Digestive issues'],
        'recovery_time': '3-6 months',
        'urgency': 'Moderate - Best results when started early',
        'survival_rate': '55-75%',
        'estimated_cost': '₹8,00,000 - ₹15,00,000',
        'cost_usd': '$10,000 - $18,000',
        'myths': {
            'myth1': 'Immunotherapy works for everyone',
            'fact1': 'Effectiveness varies; biomarker testing helps predict response',
            'myth2': 'Immunotherapy has no side effects',
            'fact2': 'Can cause immune system overactivity affecting various organs'
        }
    },
    'targeted therapy': {
        'indications': ['HER2+ breast cancer', 'EGFR+ lung cancer', 'BRAF mutated melanoma'],
        'risks': ['Diarrhea', 'Liver problems', 'Skin issues', 'High blood pressure'],
        'recovery_time': '2-4 months',
        'urgency': 'Moderate - Requires genetic testing first',
        'survival_rate': '65-85%',
        'estimated_cost': '₹9,60,000 - ₹18,00,000',
        'cost_usd': '$12,000 - $22,000',
        'myths': {
            'myth1': 'Targeted therapy is always better than chemotherapy',
            'fact1': 'Effective only for specific genetic mutations',
            'myth2': 'Targeted therapy is side-effect free',
            'fact2': 'Has different, sometimes serious side effects'
        }
    },
    'hormonal therapy': {
        'indications': ['breast cancer (ER/PR+)', 'prostate cancer', 'endometrial cancer', 'ovarian cancer'],
        'risks': ['Hot flashes', 'Bone loss (osteoporosis)', 'Cardiovascular effects', 'Mood changes', 'Sexual dysfunction'],
        'recovery_time': '5-10 years (often long-term maintenance)',
        'urgency': 'Moderate - Usually adjuvant therapy',
        'survival_rate': '70-90% (varies by cancer type and stage)',
        'estimated_cost': '₹2,00,000 - ₹8,00,000/year',
        'cost_usd': '$2,500 - $10,000/year',
        'myths': {
            'myth1': 'Hormonal therapy is only for women',
            'fact1': 'Used for both men (prostate cancer) and women (breast/endometrial cancer)',
            'myth2': 'Hormonal therapy always causes severe side effects',
            'fact2': 'Side effects vary; many patients tolerate it well with management'
        }
    },
    'radiofrequency ablation': {
        'indications': ['liver cancer', 'kidney cancer', 'lung cancer', 'bone metastases', 'small localized tumors'],
        'risks': ['Pain at treatment site', 'Infection', 'Bleeding', 'Organ damage', 'Nerve injury'],
        'recovery_time': '1-2 weeks',
        'urgency': 'Moderate - For localized tumors not suitable for surgery',
        'survival_rate': '60-80% (varies by tumor size and location)',
        'estimated_cost': '₹3,00,000 - ₹6,00,000',
        'cost_usd': '$3,750 - $7,500',
        'myths': {
            'myth1': 'Radiofrequency ablation is the same as radiation therapy',
            'fact1': 'RFA uses heat from radiofrequency waves, not ionizing radiation',
            'myth2': 'RFA can treat any size tumor',
            'fact2': 'Most effective for small tumors (usually <3-5 cm)'
        }
    },
    'stem cell transplant': {
        'indications': ['leukemia', 'lymphoma', 'multiple myeloma', 'aplastic anemia', 'some solid tumors'],
        'risks': ['Severe infections', 'Graft vs host disease', 'Organ damage', 'Secondary cancers', 'Infertility'],
        'recovery_time': '6-12 months',
        'urgency': 'High - Often required for cure in blood cancers',
        'survival_rate': '50-80% (varies by disease and donor match)',
        'estimated_cost': '₹20,00,000 - ₹40,00,000',
        'cost_usd': '$25,000 - $50,000',
        'myths': {
            'myth1': 'Stem cell transplant always cures the disease',
            'fact1': 'Success depends on disease type, stage, and patient condition',
            'myth2': 'Stem cell transplant is extremely painful',
            'fact2': 'Pain is managed with medications; procedure itself is not painful'
        }
    },
    'cryotherapy': {
        'indications': ['skin cancer', 'cervical cancer', 'prostate cancer', 'liver cancer', 'kidney cancer', 'retinoblastoma'],
        'risks': ['Pain and discomfort', 'Blistering', 'Infection', 'Scarring', 'Nerve damage', 'Organ perforation'],
        'recovery_time': '1-4 weeks',
        'urgency': 'Moderate - For localized early-stage cancers',
        'survival_rate': '70-95% (varies by cancer type and stage)',
        'estimated_cost': '₹50,000 - ₹3,00,000',
        'cost_usd': '$625 - $3,750',
        'myths': {
            'myth1': 'Cryotherapy is only for skin conditions',
            'fact1': 'Used for various cancers including prostate, liver, and cervical cancer',
            'myth2': 'Cryotherapy always causes severe pain',
            'fact2': 'Local anesthesia and pain management make it tolerable for most patients'
        }
    },
    'active surveillance': {
        'indications': ['low-risk prostate cancer', 'early-stage thyroid cancer', 'small renal masses', 'ductal carcinoma in situ (DCIS)'],
        'risks': ['Disease progression during monitoring', 'Anxiety and stress', 'Need for more frequent testing', 'Delayed treatment if progression occurs'],
        'recovery_time': 'Ongoing monitoring (no active treatment)',
        'urgency': 'Low - For very low-risk cancers where immediate treatment may not be necessary',
        'survival_rate': '95-100% (for appropriately selected low-risk cases)',
        'estimated_cost': '₹20,000 - ₹50,000/year',
        'cost_usd': '$250 - $625/year',
        'myths': {
            'myth1': 'Active surveillance means doing nothing',
            'fact1': 'Involves regular monitoring with PSA tests, biopsies, and imaging to detect changes early',
            'myth2': 'Active surveillance is riskier than immediate treatment',
            'fact2': 'For low-risk cancers, survival rates are excellent and avoids unnecessary treatment side effects'
        }
    },
    'photodynamic therapy': {
        'indications': ['skin cancer', 'esophageal cancer', 'lung cancer', 'bladder cancer', 'head and neck cancers', 'actinic keratosis'],
        'risks': ['Skin sensitivity to light', 'Burns and blisters', 'Pain during treatment', 'Infection', 'Scarring', 'Eye damage'],
        'recovery_time': '2-6 weeks',
        'urgency': 'Moderate - For superficial cancers and precancerous conditions',
        'survival_rate': '60-90% (varies by cancer type and stage)',
        'estimated_cost': '₹1,00,000 - ₹5,00,000',
        'cost_usd': '$1,250 - $6,250',
        'myths': {
            'myth1': 'PDT is only for skin problems',
            'fact1': 'Used for various cancers including lung, bladder, and esophageal cancer',
            'myth2': 'PDT requires prolonged light avoidance',
            'fact2': 'Light sensitivity typically resolves within 4-6 weeks with proper precautions'
        }
    }
}

# ============================================================================
# TREATMENT ANALYSIS FUNCTIONS (COMBINED SYSTEM)
# ============================================================================

def generate_safe_alternatives(current_treatment, symptoms):
    """Generate alternative treatment suggestions"""
    alternative_mappings = {
        'chemotherapy': ['radiation therapy', 'surgery', 'targeted therapy', 'hormonal therapy', 'immunotherapy'],
        'radiation therapy': ['chemotherapy', 'surgery', 'immunotherapy', 'radiofrequency ablation', 'cryotherapy'],
        'surgery': ['chemotherapy', 'radiation therapy', 'targeted therapy', 'radiofrequency ablation', 'cryotherapy'],
        'immunotherapy': ['chemotherapy', 'targeted therapy', 'radiation therapy', 'stem cell transplant'],
        'targeted therapy': ['chemotherapy', 'immunotherapy', 'surgery', 'hormonal therapy', 'stem cell transplant'],
        'hormonal therapy': ['chemotherapy', 'targeted therapy', 'surgery', 'active surveillance'],
        'radiofrequency ablation': ['surgery', 'radiation therapy', 'chemotherapy', 'cryotherapy'],
        'stem cell transplant': ['chemotherapy', 'targeted therapy', 'immunotherapy', 'radiation therapy'],
        'cryotherapy': ['surgery', 'radiation therapy', 'radiofrequency ablation', 'photodynamic therapy'],
        'active surveillance': ['hormonal therapy', 'cryotherapy', 'photodynamic therapy'],
        'photodynamic therapy': ['radiation therapy', 'cryotherapy', 'surgery', 'chemotherapy']
    }
    
    alternatives = []
    if current_treatment in alternative_mappings:
        for alt in alternative_mappings[current_treatment]:
            if alt in TREATMENT_DATABASE:
                data = TREATMENT_DATABASE[alt]
                alternatives.append({
                    'name': alt.title(),
                    'survival_rate': data['survival_rate'],
                    'recovery_time': data['recovery_time'],
                    'estimated_cost': data['estimated_cost']
                })

    return alternatives

def analyze_treatment_rule_based(symptoms, treatment):
    """Analyze treatment using rule-based system (Original) with validation"""
    
    # VALIDATION STEP 1: Check if symptoms are valid
    # Import validation from guideline engine
    from old_guidelines_engine import guideline_engine
    
    if not guideline_engine.is_valid_cancer_input(symptoms):
        return {
            'status': 'incomplete',
            'analysis_type': 'rule_based',
            'message': 'Please provide valid cancer-related symptoms or diagnosis information.',
            'suggestion': '''Please provide meaningful information that includes:

• Cancer type or symptoms (breast cancer, lung cancer, etc.)
• Any relevant medical details

Examples of valid input:
✓ "Breast cancer with tumor"
✓ "Lung cancer symptoms"
✓ "Leukemia diagnosis"
✗ Random characters or unrelated text'''
        }
    
    # VALIDATION STEP 2: Check if treatment is valid
    if not guideline_engine.is_valid_treatment(treatment):
        return {
            'status': 'incomplete',
            'analysis_type': 'rule_based',
            'message': 'Please provide a valid cancer treatment.',
            'suggestion': '''Valid cancer treatments include:

• Chemotherapy / Chemo
• Radiation therapy / Radiotherapy
• Surgery / Surgical resection
• Immunotherapy
• Targeted therapy
• Hormonal therapy

Examples:
✓ "Chemotherapy"
✓ "Surgery followed by radiation"
✗ Random characters or unrelated treatments'''
        }
    
    # ORIGINAL LOGIC (after validation passes)
    treatment_lower = treatment.lower()
    matched_treatment = None
    
    # Find matching treatment in database
    for key in TREATMENT_DATABASE:
        if key in treatment_lower:
            matched_treatment = key
            break
    
    if not matched_treatment:
        return {
            'status': 'not_found',
            'message': 'Treatment not found in our database.',
            'analysis_type': 'rule_based'
        }
    
    treatment_data = TREATMENT_DATABASE[matched_treatment]
    symptoms_lower = symptoms.lower()
    
    # Rule-based matching
    matching_indications = [ind for ind in treatment_data['indications'] 
                          if ind in symptoms_lower]
    
    # Determine appropriateness
    if matching_indications:
        appropriateness = 'Appropriate'
    else:
        appropriateness = 'Requires Verification'
    
    # Generate alternatives
    safe_alternatives = generate_safe_alternatives(matched_treatment, symptoms)
    
    return {
        'status': 'found',
        'analysis_type': 'rule_based',
        'treatment_name': matched_treatment.title(),
        'appropriateness': appropriateness,
        'matching_indications': matching_indications,
        'all_indications': treatment_data['indications'],
        'risks': treatment_data['risks'],
        'recovery_time': treatment_data['recovery_time'],
        'urgency': treatment_data['urgency'],
        'survival_rate': treatment_data['survival_rate'],
        'estimated_cost': treatment_data['estimated_cost'],
        'cost_usd': treatment_data['cost_usd'],
        'myths': treatment_data['myths'],
        'safe_alternatives': safe_alternatives
    }

def analyze_treatment_combined(symptoms, treatment):
    """
    Combined analysis using both guideline-based and rule-based systems
    Priority: Guideline-based (if applicable) + Rule-based (for additional context)
    """
    # Try guideline-based analysis first
    guideline_result = guideline_engine.analyze_treatment(symptoms, treatment)
    
    # Try rule-based analysis
    rule_based_result = analyze_treatment_rule_based(symptoms, treatment)
    
    # Combine results
    if guideline_result['status'] == 'found':
        # Guideline found - primary source
        combined_result = {
            'status': 'found',
            'analysis_type': 'combined',
            'primary_source': 'guideline',
            
            # Guideline data (primary)
            'cancer_type': guideline_result.get('cancer_type'),
            'stage': guideline_result.get('stage'),
            'stage_description': guideline_result.get('stage_description'),
            'guideline_source': guideline_result.get('guideline_source'),
            'guideline_url': guideline_result.get('guideline_url'),
            'alignment': guideline_result.get('alignment'),
            'alignment_details': guideline_result.get('alignment_details'),
            'standard_treatment': guideline_result.get('standard_treatment'),
            
            # SIMPLIFIED TREATMENT - KEY ADDITION
            'standard_treatment_simple': guideline_result.get('standard_treatment_simple'),
            'standard_treatment_technical': guideline_result.get('standard_treatment_technical', 
                                                                  guideline_result.get('standard_treatment')),
            
            'alternative_treatments': guideline_result.get('alternative_treatments'),
            'biomarker_tests_required': guideline_result.get('biomarker_tests_required'),
            'evidence_level': guideline_result.get('evidence_level'),
            'adjuvant_therapy': guideline_result.get('adjuvant_therapy'),
            'contraindications': guideline_result.get('contraindications'),
            'special_notes': guideline_result.get('special_notes'),
            'official_guidelines': guideline_result.get('official_guidelines'),
            
            # Guideline metrics
            'survival_rate': guideline_result.get('survival_rate'),
            'recovery_time': guideline_result.get('recovery', 'N/A'),
            'estimated_cost': guideline_result.get('estimated_cost'),
            
            # Rule-based data (supplementary)
            'risks': guideline_result.get('potential_risks', []),
            'treatment_name': rule_based_result.get('treatment_name', treatment.title()),
        }
        
        # Add rule-based myths if available
        if rule_based_result['status'] == 'found':
            combined_result['myths'] = rule_based_result.get('myths', {})
            combined_result['urgency'] = rule_based_result.get('urgency', 'Consult oncologist')
            
            # Merge risks (combine both sources)
            rule_risks = rule_based_result.get('risks', [])
            guideline_risks = guideline_result.get('potential_risks', [])
            combined_result['risks'] = list(set(rule_risks + guideline_risks))
        
        return combined_result
    
    elif guideline_result['status'] == 'incomplete':
        # Guideline incomplete - use rule-based with guideline info
        if rule_based_result['status'] == 'found':
            combined_result = rule_based_result.copy()
            combined_result['analysis_type'] = 'combined'
            combined_result['primary_source'] = 'rule_based'
            combined_result['guideline_note'] = guideline_result.get('message')
            combined_result['cancer_type'] = guideline_result.get('cancer_type')
            combined_result['guideline_source'] = guideline_result.get('guideline_source')
            combined_result['biomarker_tests_required'] = guideline_result.get('biomarker_tests_required', [])
            return combined_result
        else:
            # Return guideline incomplete status
            return guideline_result
    
    else:
        # Guideline not found - use rule-based only
        if rule_based_result['status'] == 'found':
            rule_based_result['analysis_type'] = 'combined'
            rule_based_result['primary_source'] = 'rule_based'
            rule_based_result['guideline_note'] = 'Guidelines not available for this cancer type'
            return rule_based_result
        else:
            # Both failed
            return {
                'status': 'not_found',
                'analysis_type': 'combined',
                'message': 'Treatment analysis not available. Please consult with a healthcare professional.'
            }

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
        
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Send welcome email
        send_welcome_email(new_user)
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with security monitoring"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        # Get client information
        ip_address = request.remote_addr
        user_agent_string = request.headers.get('User-Agent', '')
        device_info = get_device_info(user_agent_string)
        browser_info = get_browser_info(user_agent_string)
        
        if user and check_password_hash(user.password, password):
            # Check for new device BEFORE logging the current login
            is_new_device_login = is_new_device(user, device_info)

            # Log successful login
            login_record = LoginHistory(
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent_string,
                device_info=device_info,
                browser_info=browser_info,
                success=True
            )
            db.session.add(login_record)

            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()

            # Set session
            session['user_id'] = user.id
            session['user_name'] = user.name

            # Send login alert for new device
            if is_new_device_login:
                send_login_alert_email(user, device_info, browser_info, ip_address)
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Log failed attempt
            if user:
                login_record = LoginHistory(
                    user_id=user.id,
                    ip_address=ip_address,
                    user_agent=user_agent_string,
                    device_info=device_info,
                    browser_info=browser_info,
                    success=False
                )
                db.session.add(login_record)
                db.session.commit()
                
                # Check for suspicious activity
                is_suspicious, failed_count = check_suspicious_activity(user, ip_address)
                if is_suspicious:
                    login_record.is_suspicious = True
                    db.session.commit()
                    send_suspicious_login_email(user, failed_count, ip_address)
            
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    consultations = Consultation.query.filter_by(
        user_id=session['user_id']
    ).order_by(Consultation.created_at.desc()).all()
    
    return render_template('dashboard.html', consultations=consultations)

@app.route('/consultation', methods=['GET', 'POST'])
def consultation():
    """User consultation with combined analysis"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        treatment = request.form.get('treatment')
        
        # Use combined analysis
        result = analyze_treatment_combined(symptoms, treatment)
        
        new_consult = Consultation(
            user_id=session['user_id'],
            symptoms=symptoms,
            recommended_treatment=treatment,
            result=str(result),
            analysis_type=result.get('analysis_type', 'combined')
        )
        db.session.add(new_consult)
        db.session.commit()
        
        return render_template('result.html', 
                             result=result,
                             symptoms=symptoms,
                             treatment=treatment)
    
    return render_template('consultation.html')

@app.route('/history')
def history():
    """View consultation history"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    consultations = Consultation.query.filter_by(
        user_id=session['user_id']
    ).order_by(Consultation.created_at.desc()).all()
    
    return render_template('history.html', consultations=consultations)

@app.route('/api/consultation/<int:consultation_id>')
def get_consultation_api(consultation_id):
    """API endpoint to get consultation data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    consultation = Consultation.query.filter_by(
        id=consultation_id,
        user_id=session['user_id']
    ).first()

    if not consultation:
        return jsonify({'error': 'Consultation not found'}), 404

    try:
        result = ast.literal_eval(consultation.result)
    except (ValueError, SyntaxError):
        return jsonify({'error': 'Unable to parse consultation result'}), 500

    return jsonify({
        'created_at': consultation.created_at.strftime('%B %d, %Y at %I:%M %p'),
        'treatment': consultation.recommended_treatment,
        'symptoms': consultation.symptoms,
        'result': result
    })

@app.route('/api/consultation/<int:consultation_id>/delete', methods=['DELETE'])
def delete_consultation(consultation_id):
    """Delete a consultation record"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401

    consultation = Consultation.query.filter_by(
        id=consultation_id, 
        user_id=session['user_id']
    ).first()
    
    if not consultation:
        return jsonify({'success': False, 'message': 'Consultation not found'}), 404

    try:
        db.session.delete(consultation)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Consultation deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False, 
            'message': f'Error deleting consultation: {str(e)}'
        }), 500

@app.route('/consultation/detail/<int:consultation_id>')
def consultation_detail(consultation_id):
    """View full consultation details"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    consultation = Consultation.query.filter_by(
        id=consultation_id, 
        user_id=session['user_id']
    ).first()
    
    if not consultation:
        flash('Consultation not found', 'error')
        return redirect(url_for('history'))

    try:
        result = ast.literal_eval(consultation.result)
    except (ValueError, SyntaxError):
        result = {'status': 'error', 'message': 'Unable to parse consultation result'}

    return render_template('detail.html', 
                         consultation=consultation, 
                         result=result)

@app.route('/consultation/detail/<int:consultation_id>/pdf')
def download_pdf(consultation_id):
    """Generate and download PDF report"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    consultation = Consultation.query.filter_by(
        id=consultation_id, 
        user_id=session['user_id']
    ).first()
    
    if not consultation:
        flash('Consultation not found', 'error')
        return redirect(url_for('history'))

    try:
        result = ast.literal_eval(consultation.result)
    except (ValueError, SyntaxError):
        result = {'status': 'error', 'message': 'Unable to parse consultation result'}

    if not PDF_ENABLED:
        flash('PDF library not installed. Use browser Print function (Ctrl+P) to save as PDF.', 'info')
        return redirect(url_for('consultation_detail', consultation_id=consultation_id))

    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph("SafeCure Consultation Report", title_style))
        story.append(Spacer(1, 12))

        # Report Info
        user = User.query.get(session['user_id'])
        analysis_type_display = result.get('analysis_type', 'combined').upper()
        primary_source = result.get('primary_source', 'N/A').replace('_', ' ').title()
        
        info_data = [
            ['Report ID:', f'#{consultation.id}'],
            ['Patient:', user.name],
            ['Date:', consultation.created_at.strftime('%B %d, %Y at %I:%M %p')],
            ['Treatment:', consultation.recommended_treatment],
            ['Analysis Type:', analysis_type_display],
            ['Primary Source:', primary_source]
        ]
        
        info_table = Table(info_data, colWidths=[120, 350])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))

        if result.get('status') == 'found':
            # For guideline-based primary source
            if result.get('primary_source') == 'guideline':
                # Cancer Type and Stage
                story.append(Paragraph(f"<b>Cancer Type:</b> {result.get('cancer_type', 'N/A')}", styles['Heading2']))
                story.append(Paragraph(f"<b>Stage:</b> {result.get('stage', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"<b>Stage Description:</b> {result.get('stage_description', 'N/A')}", styles['Normal']))
                story.append(Spacer(1, 12))
                
                # Guideline Information
                story.append(Paragraph(f"<b>Guideline Source:</b> {result.get('guideline_source', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"<b>Evidence Level:</b> {result.get('evidence_level', 'N/A')}", styles['Normal']))
                story.append(Spacer(1, 12))
                
                # Treatment Alignment
                alignment = result.get('alignment', 'N/A')
                story.append(Paragraph(f"<b>Treatment Alignment:</b> {alignment}", styles['Heading2']))
                story.append(Paragraph(result.get('alignment_details', 'N/A'), styles['Normal']))
                story.append(Spacer(1, 12))
                
                # Standard Treatment
                story.append(Paragraph(f"<b>Standard Treatment:</b> {result.get('standard_treatment', 'N/A')}", styles['Normal']))
                story.append(Spacer(1, 12))
                
                # Biomarker Tests
                biomarkers = result.get('biomarker_tests_required', [])
                if biomarkers:
                    story.append(Paragraph("<b>Required Biomarker Tests:</b>", styles['Heading3']))
                    for biomarker in biomarkers:
                        story.append(Paragraph(f"• {biomarker}", styles['Normal']))
                    story.append(Spacer(1, 12))
            
            # Treatment Assessment (for both types)
            appropriateness = result.get('appropriateness', result.get('alignment', 'N/A'))
            story.append(Paragraph(f"<b>Treatment Assessment:</b> {appropriateness}", styles['Heading2']))
            story.append(Spacer(1, 12))

            # Key Metrics
            metrics_data = [
                ['Survival Rate:', result.get('survival_rate', 'N/A')],
                ['Recovery Time:', result.get('recovery_time', 'N/A')],
                ['Estimated Cost (INR):', result.get('estimated_cost', 'N/A')]
            ]
            
            # Add urgency if available (rule-based)
            if result.get('urgency'):
                metrics_data.append(['Urgency:', result.get('urgency')])
            
            # Add cost in USD if available
            if result.get('cost_usd'):
                metrics_data.append(['Estimated Cost (USD):', result.get('cost_usd')])
            
            metrics_table = Table(metrics_data, colWidths=[150, 320])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f5e9')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(metrics_table)
            story.append(Spacer(1, 20))

            # Patient Symptoms
            story.append(Paragraph("<b>Patient Symptoms/Diagnosis:</b>", styles['Heading3']))
            story.append(Paragraph(consultation.symptoms, styles['Normal']))
            story.append(Spacer(1, 12))

            # Risks & Side Effects
            if result.get('risks'):
                story.append(Paragraph("<b>Potential Risks & Side Effects:</b>", styles['Heading3']))
                for risk in result['risks']:
                    story.append(Paragraph(f"• {risk}", styles['Normal']))
                story.append(Spacer(1, 12))

            # Alternative Treatments
            alternatives = result.get('safe_alternatives', result.get('alternative_treatments', []))
            if alternatives:
                story.append(Paragraph("<b>Alternative Treatment Options:</b>", styles['Heading3']))
                if isinstance(alternatives, list) and len(alternatives) > 0:
                    if isinstance(alternatives[0], dict):
                        # Rule-based format
                        for alt in alternatives:
                            story.append(Paragraph(
                                f"<b>{alt.get('name', 'N/A')}:</b> Alternative option "
                                f"(Survival: {alt.get('survival_rate', 'N/A')}, "
                                f"Recovery: {alt.get('recovery_time', 'N/A')})",
                                styles['Normal']
                            ))
                    else:
                        # Guideline format (list of strings)
                        for alt in alternatives:
                            story.append(Paragraph(f"• {alt}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Adjuvant Therapy (guideline-based)
            adjuvant = result.get('adjuvant_therapy')
            if adjuvant and isinstance(adjuvant, dict):
                story.append(Paragraph("<b>Adjuvant Therapy Options:</b>", styles['Heading3']))
                for key, value in adjuvant.items():
                    story.append(Paragraph(f"<b>{key.replace('_', ' ')}:</b> {value}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Contraindications (guideline-based)
            contraindications = result.get('contraindications', [])
            if contraindications:
                story.append(Paragraph("<b>Contraindications:</b>", styles['Heading3']))
                for contra in contraindications:
                    story.append(Paragraph(f"• {contra}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Special Notes
            special_notes = result.get('special_notes')
            if special_notes:
                story.append(Paragraph(f"<b>Special Notes:</b> {special_notes}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Myths & Facts (rule-based)
            myths = result.get('myths', {})
            if myths:
                story.append(Paragraph("<b>Common Myths & Facts:</b>", styles['Heading3']))
                for i in range(1, 3):
                    myth_key = f'myth{i}'
                    fact_key = f'fact{i}'
                    if myth_key in myths and fact_key in myths:
                        story.append(Paragraph(f"<b>Myth:</b> {myths[myth_key]}", styles['Normal']))
                        story.append(Paragraph(f"<b>Fact:</b> {myths[fact_key]}", styles['Normal']))
                        story.append(Spacer(1, 6))
                story.append(Spacer(1, 12))
            
            # Guideline References
            official_guidelines = result.get('official_guidelines', {})
            if official_guidelines:
                story.append(Paragraph("<b>Official Guideline References:</b>", styles['Heading3']))
                for source, url in official_guidelines.items():
                    story.append(Paragraph(f"• {source.upper()}: {url}", styles['Normal']))
                story.append(Spacer(1, 12))

        # Medical Disclaimer
        story.append(Spacer(1, 20))
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey
        )
        story.append(Paragraph(
            "<b>Medical Disclaimer:</b> This information is for educational purposes only. "
            "Always consult qualified healthcare professionals for medical decisions. "
            "This analysis combines guideline-based recommendations (NCCN, ASCO, ESMO) and "
            "general treatment knowledge for comprehensive information.",
            disclaimer_style
        ))

        # Build PDF
        doc.build(story)
        buffer.seek(0)

        # Create response
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=SafeCure_Report_{consultation_id}.pdf'
        
        return response

    except Exception as e:
        print(f"Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        flash('Error generating PDF. Use browser Print function (Ctrl+P) instead.', 'error')
        return redirect(url_for('consultation_detail', consultation_id=consultation_id))

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# Main execution
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    print("\n" + "="*70)
    print("SafeCure Application Started!")
    print("="*70)
    print(f"Analysis System: ✓ Combined (Guideline-Based + Rule-Based)")
    print(f"Guideline Engine: ✓ NCCN/ASCO/ESMO Guidelines")
    print(f"Rule-Based System: ✓ General Treatment Knowledge")
    print(f"PDF Generation: {'✓ Enabled' if PDF_ENABLED else '✗ Disabled'}")
    print(f"Email Alerts: ✓ Enabled (Welcome & Login Alerts)")
    print(f"Login Monitoring: ✓ Active")
    print("="*70)
    print("\nAccess the application at: http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', debug=True)