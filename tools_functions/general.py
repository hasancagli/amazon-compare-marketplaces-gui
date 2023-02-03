import sys
# setting path
sys.path.append('../gui-amazon-tool')

import threading
from tkinter import *
from global_variables import *

def background(func, argsDict):
    th = threading.Thread(target=func, kwargs=argsDict)
    th.start()

def break_list_into_chunks(list, chunk_size):
    """
    In example, if n == 5, then
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] -> [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]
    """
    return [list[i:i+chunk_size] for i in range(0, len(list), chunk_size)]

def retry_function_for_quote_exceed_sp_api(func, max_attempts=3):
    """
    Args:
        func (_type_): Function to retry
        max_attempts (int, optional): Max attempts to retry. Defaults to 3.
    Raises:
        Exception: Max attempts reached, giving up
    Returns:
        _type_: Returns the result of the function
    """
    attempt = 1
    while attempt <= max_attempts:
        try:
            return func()
        except SellingApiRequestThrottledException as e:
            print(f"Attempt {attempt}/{max_attempts} failed: {e}")
            attempt += 1
            time.sleep(attempt * 2)
    raise Exception("Max attempts reached, giving up")

def write_headers_to_excel(worksheet, headers):
    for i in range(len(headers)):
        worksheet.write(0, i, headers[i])