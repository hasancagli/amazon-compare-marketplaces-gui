import sys
# setting path
sys.path.append('../seller-plus-gui')

from tkinter import *
import tkinter as tk
from tkcalendar import *
from tkinter import ttk
from tkinter import filedialog

from global_variables import *
from global_functions import *

from functions import *
from tools_functions.general import *
from tools_functions.compare import *

def create_multiselect_list(root, items):
    listbox = Listbox(root, selectmode=MULTIPLE, width=50)
    for item in items:
        listbox.insert(END, item)
    listbox.pack(anchor='w')
    return listbox

def get_selected_marketplaces(listbox, items):
    selected_indices = listbox.curselection()
    selected_items = [items[index] for index in selected_indices]
    return selected_items

def browse_file(chosen_file_label):
    global asins, file_name
    
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        file_name = os.path.basename(file_path)
        df = pd.read_excel(file_path)
        # Do something with the data in df
        columns = df.columns
        
        if 'ASIN' in columns:
            asins = df['ASIN'].tolist()
            chosen_file_label.config(text=file_name)
        else :
            print("No ASIN column found in the file.")

def tab_compare(root, my_notebook):
    marketplace_to_sell = tk.StringVar()
    marketplace_to_sell.set(MARKETPLACES[0])
    tab = Frame(my_notebook, width=1200, height=1000)
    
    # CHOOSE MARKETPLACES TO LOOK FOR < SECTION >
    choose_marketplaces_section_title = show_label(root=tab,
          text="Choose Marketplaces to Look For",
          bold=True,
          anchor='w',
          pady=(0, 0))
    choose_marketplaces_section_description = show_label(root=tab,
          text="Choose the marketplaces that you want to compare.",
          bold=False,
          anchor='w',
          pady=(0, 5),
          font_size=10)
    listbox = create_multiselect_list(tab, MARKETPLACES)
    
    # CHOOSE THE MARKETPLACE TO SELL < SECTION >
    choose_marketplaces_section_title = show_label(root=tab,
          text="Choose the Marketplace to Sell",
          bold=True,
          anchor='w',
          pady=(20, 0))
    choose_marketplaces_section_description = show_label(root=tab,
          text="Choose the marketplace you want to sell.",
          bold=False,
          anchor='w',
          pady=(0, 5),
          font_size=10)
    marketplace_to_sell_dropdown = show_dropdown(root=tab,
                                                 value_chosen=marketplace_to_sell,
                                                 values=MARKETPLACES)
    
    # CHOOSE ASINS TO LOOK FOR < SECTION >
    choose_asins_section_title = show_label(root=tab,
          text="Choose ASINs",
          bold=True,
          anchor='w',
          pady=(20, 0))
    choose_asins_section_description = show_label(root=tab,
          text="Upload a file or choose a category to look for.",
          bold=False,
          anchor='w',
          pady=(0, 5),
          font_size=10)
    upload_file_button = show_button(
        root=tab,
        text="Upload File",
        padx=0,
        pady=0,
        command=lambda: background(browse_file, {'chosen_file_label': chosen_file_label})
    )
    chosen_file_label = show_label(root=tab,
                                   text="No file chosen.",
                                   bold=False,
                                   anchor='w',
                                   font_size=8)
    
    # START SEARCH < SECTION >
    show_button(
        root=tab,
        text="Start Search",
        padx=0,
        pady=(20, 0),
        command=lambda: background(start_compare_search, {
            'marketplaces_to_look_for': get_selected_marketplaces(listbox, MARKETPLACES),
            'marketplace_to_sell': marketplace_to_sell.get(),
            'identifiers': asins if 'asins' in globals() else [],
            'error_label': error_label,
        })
    )
    
    error_label = show_label(root=tab,
                             text="",
                             bold=False,
                             anchor='w',
                             fg='green',
                             font_size=8,
                             pady=5)
    
    tab.pack(fill=BOTH, expand=1, padx=20, pady=20)
    return tab