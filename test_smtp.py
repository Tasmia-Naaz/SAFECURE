# flask_mail_test.py
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

# Gmail SMTP configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'safecure.care123@gmail.com'
app.config['MAIL_PASSWORD'] = 'zweofsyolnxlxsle'  # same app password that worked

mail = Mail(app)

with app.app_context():
    msg = Message(
        subject='Test Email from Flask-Mail',
        sender=app.config['MAIL_USERNAME'],
        recipients=['safecure.care123@gmail.com'],  # replace with the real recipient
        body='Flask-Mail email test successful!'
    )
    mail.send(msg)
    print("Email sent successfully!")
