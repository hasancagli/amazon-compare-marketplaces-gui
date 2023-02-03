import sys
# setting path
sys.path.append('../seller-plus-gui')

from database_functions.general import create_table_with_script

"""
# Create Compare Prices Results Table
create_script = '''CREATE TABLE IF NOT EXISTS compare_results (
            id SERIAL PRIMARY KEY,
            search_id varchar(50) NOT NULL,
            date TIMESTAMPTZ,
            identifier_type varchar(20),
            identifier_text varchar(30),
            data JSON
            )'''
create_table_with_script(create_script)
"""

"""
# Create Compare Prices Searches Table
create_script = '''CREATE TABLE IF NOT EXISTS compare_searches (
            id SERIAL PRIMARY KEY,
            search_id varchar(50) NOT NULL,
            username varchar(100) NOT NULL,
            status int,
            date_search_start TIMESTAMPTZ,
            date_search_end TIMESTAMPTZ,
            identifier_type varchar(20),
            identifiers_list TEXT [],
            marketplaces_to_look_list TEXT [],
            marketplace_to_sell varchar(20)
            )'''
create_table_with_script(create_script)
"""