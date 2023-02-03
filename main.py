from tabs.compare import *

# General Customizings
root = Tk()
root.minsize(600, 600)

width= root.winfo_screenwidth()
height= root.winfo_screenheight()
root.geometry("%dx%d" % (width, height))

root.title("Seller Plus")

# Notebook Settings
my_notebook = ttk.Notebook()
my_notebook.pack(padx=0, pady=0)

# Add some style
style = ttk.Style()
style.configure(
    "Treeview",
	rowheight=25,
)

# Tools
compareTool = tab_compare(root, my_notebook)

# Add tabs to notebook
my_notebook.add(compareTool, text="Compare")

# Run the mainloop
root.mainloop()