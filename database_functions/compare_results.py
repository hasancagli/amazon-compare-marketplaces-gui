import sys
# setting path
sys.path.append('../seller-plus-gui')

from global_variables import *
import psycopg2
import xlsxwriter
import csv

def create_compare_result(search_id: str, identifier_type: str, identifier_text: str, data: dict, date = datetime.utcnow()):
    """
    Args:
        search_id (str): Search ID
        identifier_type (str): ASIN, UPC, EAN, ISBN
        identifier_text (str): For example, B07XVJQZ7Y
        data (dict): data contains search results
        date (_type_): Datetime object, Default: datetime.utcnow()
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
        
        script = "INSERT INTO compare_results (search_id, date, identifier_type, identifier_text, data) VALUES (%s, %s, %s, %s, %s)"
        cur.execute(script, (search_id, date, identifier_type, identifier_text, json.dumps(data)))
        con.commit()
        
        cur.close()
        con.close()
        
        return {'status': 'success', 'message': f'Result for {identifier_text} created successfully!'}
    except Exception as error:
        return {'status': 'error', 'message': error}

def create_compare_result_in_bulk(search_id: str, identifier_type: str, sub_result, date = datetime.utcnow()):
    """
    Args:
        search_id (str): Search ID
        identifier_type (str): ASIN, UPC, EAN, ISBN
        sub_result (dict): sub_result contains search results (asin, data)
        date (_type_, optional): _description_. Defaults to datetime.utcnow().
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
        
        for asin in sub_result:
            identifier_text = asin
            data = sub_result[asin]
            
            script = "INSERT INTO compare_results (search_id, date, identifier_type, identifier_text, data) VALUES (%s, %s, %s, %s, %s)"
            cur.execute(script, (search_id, date, identifier_type, identifier_text, json.dumps(data)))
            
        con.commit()
        
        cur.close()
        con.close()
        
        return {'status': 'success', 'message': f'Bulk results created on database successfully!'}
    except Exception as error:
        return {'status': 'error', 'message': error}

def get_compare_results_by_search_id(search_id: str):
    """
    Args:
        search_id (str): Search ID
    Returns:
        dict: Return a dictionary contains search results and search info (status, message, result(dict))
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
        
        return_data = {}
        
        # Get search info
        script_search = "SELECT search_id, username, status, date_search_start, date_search_end, identifier_type, identifiers_list, marketplaces_to_look_list, marketplace_to_sell FROM compare_searches WHERE search_id = %s"
        cur.execute(script_search, (search_id,))
        search_id, username, status, date_search_start, date_search_end, identifier_type, identifiers_list, marketplaces_to_look_list, marketplace_to_sell = cur.fetchone()
        
        return_data['search_id'] = search_id
        return_data['username'] = username
        return_data['status'] = status
        return_data['date_search_start'] = date_search_start
        return_data['date_search_end'] = date_search_end
        return_data['identifier_type'] = identifier_type
        return_data['identifiers_list'] = identifiers_list
        return_data['marketplaces_to_look_list'] = marketplaces_to_look_list
        return_data['marketplace_to_sell'] = marketplace_to_sell
        
        # Get search results info
        return_data['data'] = {} # start as empty dict
        
        script = "SELECT search_id, date, identifier_type, identifier_text, data FROM compare_results WHERE search_id = %s"
        cur.execute(script, (search_id,))
        result = cur.fetchall()
        
        for item in result:
            search_id, date, identifier_type, identifier_text, data = item
            return_data['data'][identifier_text] = {
                'date': date,
                'identifier_type': identifier_type,
                'data': data
            }
        
        cur.close()
        con.close()
        
        return {'status': 'success',
                'message': f'Got results for {search_id} successfully!',
                'result': return_data}
    except Exception as error:
        return {'status': 'error',
                'message': error,
                'result': {}}