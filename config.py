# Environment Configuration
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Azure Configuration
AZURE_SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID')
AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID')
AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
AZURE_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')

# Flask Configuration
SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this-in-production')
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
ENV = os.getenv('FLASK_ENV', 'production')

# Security Configuration
SESSION_COOKIE_SECURE = ENV == 'production'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# File Upload Configuration
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'xml', 'drawio', 'vsdx', 'svg'}

# Output Configuration
OUTPUT_FOLDER = 'output'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
