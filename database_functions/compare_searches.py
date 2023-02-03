import sys
# setting path
sys.path.append('../seller-plus-gui')

from global_variables import *
import psycopg2
import xlsxwriter
import csv

def create_compare_search(search_id: str, username: str, identifier_type: str, identifiers_list: list, marketplaces_to_look_list: list, marketplace_to_sell: str, status:int=0, date_search_start=None, date_search_end=None):
    """
    Args:
        search_id (str): Unique Search ID
        username (str): Username
        identifier_type (str): Like ASIN, UPC, EAN, ISBN
        identifier_list (list): List contains identifiers
        marketplaces_to_look_list (list): List contains marketplaces [amazon.com, amazon.co.uk, amazon.de, amazon.fr, amazon.it, amazon.es ...]
        marketplace_to_sell (str): Marketplace to sell
        status (int, optional): _description_. Defaults to 0.
        date_search_start (_type_, optional): Defaults to None. [datetime object]
        date_search_end (_type_, optional): Defaults to None. [datetime object]
    Returns:
        JSON Object contains 'status' and 'message'.
    """
    try:
        con = psycopg2.connect(
            host=DATABASE_HOSTNAME,
            dbname=DATABASE_DATABASE,
            user=DATABASE_USERNAME,
            password=DATABASE_PASSWORD,
            port=DATABASE_PORT
        )
        cur=con.cursor()
        
        script = "INSERT INTO compare_searches (search_id, username, identifier_type, identifiers_list, marketplaces_to_look_list, marketplace_to_sell, status, date_search_start, date_search_end) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cur.execute(script, (search_id, username, identifier_type, identifiers_list, marketplaces_to_look_list, marketplace_to_sell, status, date_search_start, date_search_end))
        con.commit()
        
        cur.close()
        con.close()
        
        return {'status': 'success', 'message': f'Compare search [{search_id}] created successfully!'}
    except Exception as error:
        return {'status': 'error', 'message': error}
    
def change_search_status_to_in_progress(search_id: str):
    """
    Args:
        search_id (str): Search ID
    Returns:
        JSON Object contains 'status' and 'message'.
    """
    try:
        con = psycopg2.connect(
            host=DATABASE_HOSTNAME,
            dbname=DATABASE_DATABASE,
            user=DATABASE_USERNAME,
            password=DATABASE_PASSWORD,
            port=DATABASE_PORT
        )
        cur=con.cursor()
        
        date_search_start = datetime.utcnow()
        sql = """UPDATE compare_searches SET status=%s, date_search_start=%s WHERE search_id=%s"""
        cur.execute(sql, (1, date_search_start, search_id))
        
        con.commit()
        
        cur.close()
        con.close()
        
        return {'status': 'success', 'message': f"Compare search [{search_id}] status updated to '1' (in progress) successfully!"}
    except Exception as error:
        return {'status': 'error', 'message': error}
    
def change_search_status_to_finished(search_id: str):
    """
    Args:
        search_id (str): Search ID
    Returns:
        JSON Object contains 'status' and 'message'.
    """
    try:
        con = psycopg2.connect(
            host=DATABASE_HOSTNAME,
            dbname=DATABASE_DATABASE,
            user=DATABASE_USERNAME,
            password=DATABASE_PASSWORD,
            port=DATABASE_PORT
        )
        cur=con.cursor()
        
        date_search_end = datetime.utcnow()
        sql = """UPDATE compare_searches SET status=%s, date_search_end=%s WHERE search_id=%s"""
        cur.execute(sql, (2, date_search_end, search_id))
        
        con.commit()
        
        cur.close()
        con.close()
        
        return {'status': 'success', 'message': f"Compare search [{search_id}] status updated to '2' (finished) successfully!"}
    except Exception as error:
        return {'status': 'error', 'message': error}