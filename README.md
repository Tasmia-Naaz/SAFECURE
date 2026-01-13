# SafeCure - Smart Second Opinion System

SafeCure is a web application that provides second opinions on cancer treatments by analyzing them against trusted oncology guidelines (NCCN, ASCO, ESMO).

## 🎯 Features

- **Guideline-Based Analysis**: Compare treatments with NCCN/ASCO/ESMO guidelines
- **Rule-Based System**: General treatment knowledge for various cancer types
- **Treatment Verification**: Check if recommended treatments align with standards
- **Risk Assessment**: Understand potential side effects and complications
- **Cost Estimation**: Get estimated treatment costs (INR & USD)
- **Myths vs Facts**: Separate medical facts from common misconceptions
- **Email Alerts**: Login notifications and security monitoring
- **PDF Reports**: Download comprehensive consultation reports
- **Consultation History**: Track all your previous consultations

## 🏥 Supported Cancer Types

- Breast Cancer (All stages: 0-IV)
- Lung Cancer / NSCLC (All stages: I-IV)
- Colorectal Cancer (All stages: I-IV)
- Prostate Cancer (Low/Intermediate/High risk, Metastatic)

## 🛠️ Technologies Used

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, Bootstrap 5
- **Email**: Flask-Mail (Gmail SMTP)
- **PDF Generation**: ReportLab (optional)
- **Security**: Werkzeug password hashing, session management

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Gmail account (for email functionality)

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/safecure.git
cd safecure
```

### 2. Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
BASE_URL=http://localhost:5000
```

**Important**: For Gmail, you need to:
1. Enable 2-Factor Authentication
2. Generate an App Password (not your regular password)
3. Use the App Password in `.env`

### 5. Initialize the database
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### 6. Run the application
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## 📁 Project Structure
```
safecure/
│
├── templates/              # HTML templates
│   ├── index.html         # Landing page
│   ├── signup.html        # Registration
│   ├── login.html         # Login
│   ├── dashboard.html     # User dashboard
│   ├── consultation.html  # New consultation form
│   ├── result.html        # Analysis results
│   ├── detail.html        # Detailed report
│   └── history.html       # Consultation history
│
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── guidelines_engine.py   # Guideline analysis engine
├── oncology_guidelines.py # Oncology guidelines database
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔒 Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Login attempt monitoring
- New device detection
- Suspicious activity alerts
- Email notifications for security events

## 📊 How It Works

1. **User Registration**: Create an account with email verification
2. **Input Symptoms**: Provide cancer type, stage, and symptoms
3. **Select Treatment**: Choose recommended treatment
4. **Analysis**: System analyzes using:
   - Guideline-based engine (NCCN/ASCO/ESMO)
   - Rule-based knowledge system
5. **Report**: Receive comprehensive analysis including:
   - Treatment alignment with guidelines
   - Required biomarker tests
   - Survival rates and recovery time
   - Potential risks and side effects
   - Alternative treatment options
   - Cost estimates

## ⚠️ Medical Disclaimer

This system provides **informational support only**. It is **NOT** a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for medical decisions.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Your Name - [Tasmia Naaz](https://github.com/Tasmia-Naaz)

## 🙏 Acknowledgments

- NCCN (National Comprehensive Cancer Network)
- ASCO (American Society of Clinical Oncology)
- ESMO (European Society for Medical Oncology)
- Cancer Care Ontario

## 📧 Support

For support, email: safecure.care123@gmail.com

## 🔗 Links

- [Live Demo](https://your-deployment-url.com)
- [Documentation](https://github.com/yourusername/safecure/wiki)
- [Report Issues](https://github.com/yourusername/safecure/issues)

---

**Made with ❤️ for better healthcare decisions**
