# Amazon Compare Marketplaces GUI
This application allows you to compare the prices and other information of products from different marketplaces on Amazon. All the data is retrieved from the Amazon SP-API. The application is written in Python and uses the Tkinter library for the GUI.

## Requirements
- Amazon Developer Account to get the credentials for the SP-API
- Python 3.8 or higher
- Postgres Database Credentials (can be hosted locally or on a server)

## Technologies used
- Python
- Tkinter
- Amazon SP-API
- Postgres Database
- Pandas
- Manipulating Data
- Threading

## Installation Guide
1. Clone the repository
2. Install the requirements with `pip install -r requirements.txt`
3. In the global_variables.py file, enter your credentials for the SP-API and the Postgres Database
4. On database_functions -> comments.py, run the commented lines to create tables in your database.
5. Run the main.py file by typing `python main.py` in the terminal

## Notes
- The application is still in development and is not yet finished, so lots of features are waiting to be implemented.
- You may want to move your credentials to a '.env' file for security reasons.
- You can find an example 'Import File' in the main directory.

## Screenshots
<img width="514" alt="Screenshot 2023-02-04 at 02 18 29" src="https://user-images.githubusercontent.com/53555551/216728730-62a474d8-20a8-4be8-81a5-2e4b9820479c.png">
<img width="1157" alt="Screenshot 2023-02-04 at 02 08 37" src="https://user-images.githubusercontent.com/53555551/216728651-13a964a9-1768-4158-9802-de07f08913f2.png">
