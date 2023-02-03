import sys
# setting path
sys.path.append('../seller-plus-gui')

from global_variables import *
import psycopg2

def create_table_with_script(script):
    try:
        con = psycopg2.connect(
            host=DATABASE_HOSTNAME,
            dbname=DATABASE_DATABASE,
            user=DATABASE_USERNAME,
            password=DATABASE_PASSWORD,
            port=DATABASE_PORT
        )
        cur=con.cursor()
        
        cur.execute(script)
        con.commit()
        
        cur.close()
        con.close()
    except Exception as error:
        print(error)