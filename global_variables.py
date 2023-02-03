# Import SP API
from sp_api.api import Products, CatalogItems
from sp_api.base import  Marketplaces, ReportType,ProcessingStatus, Granularity
from sp_api.base.exceptions import SellingApiRequestThrottledException, SellingApiNotFoundException

import time
import xlsxwriter
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
import pytz
import pandas as pd
import json

LWA_APP_ID=''
CLIENT_SECRET=''
AWS_ACCESS_KEY=''
AWS_SECRET_KEY=''
ROLE_ARN=''
EUROPE_REFRESH_TOKEN=''
US_REFRESH_TOKEN=''
ASIA_REFRESH_TOKEN=''
POSTGRE_HOSTNAME=''
POSTGRE_DATABASE=''
POSTGRE_USERNAME=''
POSTGRE_PASSWORD=''
POSTGRE_PORT=''
EXAMPLE_USERNAME = 'example'
EXAMPLE_PASSWORD = 'example'

# AWS CREDENTIALS VARIABLES
credentials = dict(
    refresh_token=ASIA_REFRESH_TOKEN,
    lwa_app_id=LWA_APP_ID,
    lwa_client_secret=CLIENT_SECRET,
    aws_access_key=AWS_ACCESS_KEY,
    aws_secret_key=AWS_SECRET_KEY,
    role_arn = ROLE_ARN
)

# DATABASE VARIABLES
DATABASE_HOSTNAME = POSTGRE_HOSTNAME
DATABASE_DATABASE = POSTGRE_DATABASE
DATABASE_USERNAME = POSTGRE_USERNAME
DATABASE_PASSWORD = POSTGRE_PASSWORD
DATABASE_PORT = POSTGRE_PORT

ASIA_COUNTRY_CODES = ['SG', 'AU', 'JP']
EUROPE_COUNTRY_CODES = ['ES', 'UK', 'FR', 'NL', 'DE', 'IT', 'SE', 'PL', 'EG', 'TR', 'SA', 'AE', 'IN']
US_COUNTRY_CODES = ['CA', 'US', 'MX', 'BR']

COUNTRY_CODE_TO_MARKETPLACE = {
    'SG': Marketplaces.SG,
    'AU': Marketplaces.AU,
    'JP': Marketplaces.JP,
    'ES': Marketplaces.ES,
    'UK': Marketplaces.UK,
    'FR': Marketplaces.FR,
    'NL': Marketplaces.NL,
    'DE': Marketplaces.DE,
    'IT': Marketplaces.IT,
    'SE': Marketplaces.SE,
    'PL': Marketplaces.PL,
    'EG': Marketplaces.EG,
    'TR': Marketplaces.TR,
    'SA': Marketplaces.SA,
    'AE': Marketplaces.AE,
    'IN': Marketplaces.IN,
    'CA': Marketplaces.CA,
    'US': Marketplaces.US,
    'MX': Marketplaces.MX,
    'BR': Marketplaces.BR
}
MARKETPLACE_IDS = {
    'A2EUQ1WTGCTBG2': {
        'country_code': 'CA',
        'country': 'Canada'
    },
    'ATVPDKIKX0DER': {
        'country_code': 'US',
        'country': 'United States of America'
    },
    'A1AM78C64UM0Y8': {
        'country_code': 'MX',
        'country': 'Mexico'
    },
    'A2Q3Y263D00KWC': {
        'country_code': 'BR',
        'country': 'Brazil'
    },
    'A1RKKUPIHCS9HS': {
        'country_code': 'ES',
        'country': 'Spain'
    },
    'A1F83G8C2ARO7P': {
        'country_code': 'UK',
        'country': 'United Kingdom'
    },
    'A13V1IB3VIYZZH': {
        'country_code': 'FR',
        'country': 'France'
    },
    'A1805IZSGTT6HS': {
        'country_code': 'NL',
        'country': 'Netherlands'
    },
    'A1PA6795UKMFR9': {
        'country_code': 'DE',
        'country': 'Germany'
    },
    'APJ6JRA9NG5V4': {
        'country_code': 'IT',
        'country': 'Italy'
    },
    'A2NODRKZP88ZB9': {
        'country_code': 'SE',
        'country': 'Sweden'
    },
    'A1C3SOZRARQ6R3': {
        'country_code': 'PL',
        'country': 'Poland'
    },
    'ARBP9OOSHTCHU': {
        'country_code': 'EG',
        'country': 'Egypt'
    },
    'A33AVAJ2PDY3EV': {
        'country_code': 'TR',
        'country': 'Turkey'
    },
    'A17E79C6D8DWNP': {
        'country_code': 'SA',
        'country': 'Saudi Arabia'
    },
    'A2VIGQ35RCS4UG': {
        'country_code': 'AE',
        'country': 'United Arab Emirates'
    },
    'A21TJRUUN4KGV': {
        'country_code': 'IN',
        'country': 'India'
    },
    'A19VAU5U5O7RUS': {
        'country_code': 'SG',
        'country': 'Singapore'
    },
    'A39IBJ37TRP1C6': {
        'country_code': 'AU',
        'country': 'Australia'
    },
    'A1VC38T7YXB528': {
        'country_code': 'JP',
        'country': 'Japan'
    },
}
MARKETPLACE_ID_TO_COUNTRY_CODE = {
    'A2EUQ1WTGCTBG2': 'CA',
    'ATVPDKIKX0DER': 'US',
    'A1AM78C64UM0Y8': 'MX',
    'A2Q3Y263D00KWC': 'BR',
    'A1RKKUPIHCS9HS': 'ES',
    'A1F83G8C2ARO7P': 'UK',
    'A13V1IB3VIYZZH': 'FR',
    'A1805IZSGTT6HS': 'NL',
    'A1PA6795UKMFR9': 'DE',
    'APJ6JRA9NG5V4': 'IT',
    'A2NODRKZP88ZB9': 'SE',
    'A1C3SOZRARQ6R3': 'PL',
    'ARBP9OOSHTCHU': 'EG',
    'A33AVAJ2PDY3EV': 'TR',
    'A17E79C6D8DWNP': 'SA',
    'A2VIGQ35RCS4UG': 'AE',
    'A21TJRUUN4KGV': 'IN',
    'A19VAU5U5O7RUS': 'SG',
    'A39IBJ37TRP1C6': 'AU',
    'A1VC38T7YXB528': 'JP'
}
MARKETPLACES = [
    'amazon.ca',
    'amazon.com',
    'amazon.com.mx',
    'amazon.com.br',
    'amazon.es',
    'amazon.co.uk',
    'amazon.fr',
    'amazon.nl',
    'amazon.de',
    'amazon.it',
    'amazon.se',
    'amazon.pl',
    'amazon.eg',
    'amazon.com.tr',
    'amazon.sa',
    'amazon.ae',
    'amazon.in',
    'amazon.sg',
    'amazon.com.au',
    'amazon.co.jp'
]
MARKETPLACE_URL_TO_MARKETPLACE_ID = {
    'amazon.ca': 'A2EUQ1WTGCTBG2',
    'amazon.com': 'ATVPDKIKX0DER',
    'amazon.com.mx': 'A1AM78C64UM0Y8',
    'amazon.com.br': 'A2Q3Y263D00KWC',
    'amazon.es': 'A1RKKUPIHCS9HS',
    'amazon.co.uk': 'A1F83G8C2ARO7P',
    'amazon.fr': 'A13V1IB3VIYZZH',
    'amazon.nl': 'A1805IZSGTT6HS',
    'amazon.de': 'A1PA6795UKMFR9',
    'amazon.it': 'APJ6JRA9NG5V4',
    'amazon.se': 'A2NODRKZP88ZB9',
    'amazon.pl': 'A1C3SOZRARQ6R3',
    'amazon.eg': 'ARBP9OOSHTCHU',
    'amazon.com.tr': 'A33AVAJ2PDY3EV',
    'amazon.sa': 'A17E79C6D8DWNP',
    'amazon.ae': 'A2VIGQ35RCS4UG',
    'amazon.in': 'A21TJRUUN4KGV',
    'amazon.sg': 'A19VAU5U5O7RUS',
    'amazon.com.au': 'A39IBJ37TRP1C6',
    'amazon.co.jp': 'A1VC38T7YXB528'
}
MARKETPLACE_ID_TO_MARKETPLACE_URL = {
    'A2EUQ1WTGCTBG2': 'amazon.ca',
    'ATVPDKIKX0DER': 'amazon.com',
    'A1AM78C64UM0Y8': 'amazon.com.mx',
    'A2Q3Y263D00KWC': 'amazon.com.br',
    'A1RKKUPIHCS9HS': 'amazon.es',
    'A1F83G8C2ARO7P': 'amazon.co.uk',
    'A13V1IB3VIYZZH': 'amazon.fr',
    'A1805IZSGTT6HS': 'amazon.nl',
    'A1PA6795UKMFR9': 'amazon.de',
    'APJ6JRA9NG5V4': 'amazon.it',
    'A2NODRKZP88ZB9': 'amazon.se',
    'A1C3SOZRARQ6R3': 'amazon.pl',
    'ARBP9OOSHTCHU': 'amazon.eg',
    'A33AVAJ2PDY3EV': 'amazon.com.tr',
    'A17E79C6D8DWNP': 'amazon.sa',
    'A2VIGQ35RCS4UG': 'amazon.ae',
    'A21TJRUUN4KGV': 'amazon.in',
    'A19VAU5U5O7RUS': 'amazon.sg',
    'A39IBJ37TRP1C6': 'amazon.com.au',
    'A1VC38T7YXB528': 'amazon.co.jp'
}

PADDING_BETWEEN_EACH_SECTION = 5