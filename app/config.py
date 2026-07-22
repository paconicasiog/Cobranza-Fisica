import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials', 'config.json')

with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

REDSHIFT_HOST = config.get('REDSHIFT_HOST')
REDSHIFT_USER = config.get('REDSHIFT_USER')
REDSHIFT_PASSWORD = config.get('REDSHIFT_PASSWORD')
REDSHIFT_DB = config.get('REDSHIFT_DB')
REDSHIFT_PORT = config.get('REDSHIFT_PORT', '5439')

GOOGLE_CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), config.get('GOOGLE_CREDENTIALS_PATH', 'credentials/service_account_google.json'))
