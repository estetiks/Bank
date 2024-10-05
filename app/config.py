
import os

class Config:
    SECRET_KEY = 'e02f65616d3d2f009f1f859180ea60626e954245a8d7746d7585e940e4892c9b'
    SQLALCHEMY_DATABASE_URI = 'postgresql://admin:crypto@db/crypto_exchange'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = 'static'
    

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FILES_DIRECTORY = os.path.join(BASE_DIR, 'share')


EXCHANGE_RATES = {
    ('USD', 'EUR'): 0.85,
    ('USD', 'RUB'): 70.0,
    ('USD', 'RUB'): 70.0,
    ('EUR', 'USD'): 1.18,
    ('EUR', 'RUB'): 82.0,
    ('RUB', 'USD'): 0.014,
    ('RUB', 'EUR'): 0.012,
}


EXCHANGE_RATES_SHARES = {
    ('HL', 'EUR'): 0.56,
    ('HL', 'USD'): 0.70,
    ('HL', 'RUB'): 76.0,
    ('TUBE', 'USD'): 1.18,
    ('TUBE', 'RUB'): 82.0,
    ('TUBE', 'EUR'): 1.14,
    }