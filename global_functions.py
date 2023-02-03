from global_variables import *

# Import ENV variables
import os
from dotenv import load_dotenv
load_dotenv()

import uuid

# Importing currency_converter library and AUD to USD function.
from currency_converter import CurrencyConverter
c = CurrencyConverter('https://www.ecb.int/stats/eurofxref/eurofxref-hist.zip')

def get_credentials_and_marketplace_by_country(country_code: str) -> tuple:
    """
    Args:
        country_code (str): Country Code Value (ex: 'AU')
    Returns:
        tuple: Credentials, Marketplace Value(ex: Marketplaces.US)
    """
    
    marketplace = COUNTRY_CODE_TO_MARKETPLACE[country_code] if country_code in COUNTRY_CODE_TO_MARKETPLACE.keys() else ''
    
    if (country_code in ASIA_COUNTRY_CODES):
        refresh_token = ASIA_REFRESH_TOKEN
    elif (country_code in EUROPE_COUNTRY_CODES):
        refresh_token = EUROPE_REFRESH_TOKEN
    elif (country_code in US_COUNTRY_CODES):
        refresh_token = US_REFRESH_TOKEN
    else:
        refresh_token = ''
    
    credentials = dict(
        refresh_token=refresh_token,
        lwa_app_id=LWA_APP_ID,
        lwa_client_secret=CLIENT_SECRET,
        aws_access_key=AWS_ACCESS_KEY,
        aws_secret_key=AWS_SECRET_KEY,
        role_arn=ROLE_ARN
    )
    
    return credentials, marketplace

def generate_unique_id():
    """Generate a unique id in length of 30 characters"""
    return str(uuid.uuid4().int).zfill(30)

def x_to_y_currency_converter(x, y, amount) -> float:
    """
    Args:
        x: The Currency Value to Change From
        y: The Currency Value to Change to
        amount: The x amount.
    Returns:
        float: Returns the converted version of x to y currency.
    """
    try:
        result = round(c.convert(float(amount), x, y), 2)
    except:
        result = 0
        
    return result