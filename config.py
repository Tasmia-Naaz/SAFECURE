import os

class Config:
    SECRET_KEY = 'safecure-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///safecure.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Base URL for external links (change to your local IP for mobile access)
    # Example: 'http://192.168.1.100:5000' or 'http://localhost:5000'
    BASE_URL = 'http://localhost:5000'

    # Email Configuration for Gmail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    # REPLACE WITH YOUR CREDENTIALS
    MAIL_USERNAME = 'safecure.care123@gmail.com'
    MAIL_PASSWORD = 'zweo fsyo lnxl xsle'
    MAIL_DEFAULT_SENDER = 'safecure.care123@gmail.com'

    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = False

    ENABLE_LOGIN_ALERTS = True
    ENABLE_SUSPICIOUS_LOGIN_DETECTION = True
    ENABLE_WELCOME_EMAIL = True
    ENABLE_CONSULTATION_EMAIL = True
