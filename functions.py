from tkinter import *
    
def show_button(root, text, padx, pady, command):
    """
    Args:
        root: The root that text will appear.
        text: The button Text
        padx: Padding amount in X.
        pady: Padding amount in Y.
        command: The function that will work when button presses. Generally it is a lambda callback function.
    """
    button = Button(root, text=text, command=command)
    button.pack(fill='both', padx=padx, pady=pady)
    
    return button
    
def show_label(root, text: str, bold: bool, anchor: str, font_size=12, fg='white', padx=0, pady=0):
    """
    Args:
        root (_type_): The root that text will appear.
        text (str): Text will appear.
        bold (bool): If True, text will be bold.
        anchor (str): The alignment of the text. It can be 'w', 'center' and etc.
        font_size (int): Default: 12.
        fg (_type_): Default: 'white'.
        padx (_type_): Default: 0.
        pady (_type_): Default: 0.
    """
    font = ("Arial", font_size) if not bold else ("Arial", font_size, 'bold')
    
    label = Label(root, text=text, font=font, anchor=anchor, fg=fg)
    label.pack(fill='both', padx=padx, pady=pady)
    
    return label

def show_dropdown(root, value_chosen: str, values: list):
    """
    Args:
        root (_type_): Root of the dropdown.
        value_chosen (str): The value that will be chosen.
        values (list): Values that will be shown in the dropdown.
    Returns:
        drop (_type_): The dropdown object.
    """
    
    drop = OptionMenu(root, value_chosen, *values)
    drop.pack(fill='both', anchor='w')
    
    return drop