import pandas as pd
import sqlite3 as sql

providers = pd.read_csv('Pages\providers_data.csv')
receivers = pd.read_csv('Pages\sreceivers_data.csv')
claims = pd.read_csv('Pages\claims_data.csv')
foodlistings = pd.read_csv('Pages\sfood_listings_data.csv')

#Dates to date time data type
foodlistings['Expiry_Date'] = pd.to_datetime(foodlistings['Expiry_Date'])
foodlistings['Expiry_Date'] = foodlistings['Expiry_Date'].dt.strftime('%Y-%m-%d')

claims['Timestamp'] = pd.to_datetime(claims['Timestamp'])
claims['Timestamp'] = claims['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

#Removing unwanted characters
map = ['x','.','-','(',')','+']
for i in map:
    providers['Contact'] = providers['Contact'].str.replace(i,'')
    receivers['Contact'] = receivers['Contact'].str.replace(i,'')

#Creating and connecting a database
con = sql.connect('foodwastage.db')
cur = con.cursor()

#Clearing the database
tables = ['Providers','Receivers','Foodlist','Claims','Claimedfood']
for i in tables:
    cur.execute(f'''DROP TABLE IF EXISTS {i}''')

#Functions to be used
def add_data(df,table):
    cols = tuple(df.columns)
    for index,row in df.iterrows():
        cur.execute(f''' INSERT INTO {table}{cols}
                     VALUES {tuple(row)}''')
    con.commit()

#Adding the data tables to database
cur.execute(''' CREATE TABLE IF NOT EXISTS Providers(
                Provider_ID INTEGER PRIMARY KEY,
                Name VARCHAR(150),
                Type VARCHAR(150),
                Address TEXT,
                City VARCHAR(100),
                Contact VARCHAR(50)
                )''')
con.commit()
add_data(providers,'Providers')

cur.execute(''' CREATE TABLE IF NOT EXISTS Receivers(
                Receiver_ID INTEGER PRIMARY KEY,
                Name VARCHAR(150),
                Type VARCHAR(150),
                City VARCHAR(100),
                Contact VARCHAR(50)
                )''')
con.commit()

add_data(receivers,'Receivers')

cur.execute(''' CREATE TABLE IF NOT EXISTS Foodlist(
                Food_ID INTEGER PRIMARY KEY,
                Food_Name VARCHAR(150),
                Quantity INTEGER,
                Expiry_Date DATE,
                Provider_ID INTEGER FORIEGN KEY,
                Provider_Type VARCHAR(150),
                Location VARCHAR(100),
                Food_Type VARCHAR(150),
                Meal_Type VARCHAR(150)
                )''')
con.commit()
add_data(foodlistings,'Foodlist')

cur.execute(''' CREATE TABLE IF NOT EXISTS Claims(
                Claim_ID INTEGER PRIMARY KEY,
                Food_ID INTEGER FORIEGN KEY,
                Receiver_ID INTEGER FORIEGN KEY,
                Status TEXT,
                Timestamp DATETIME
                )''')
con.commit()
add_data(claims,'Claims')

#Table to check for claimed food
cur.execute(''' CREATE TABLE IF NOT EXISTS Claimedfood(
                Food_ID INTEGER PRIMARY KEY,
                Food_Name VARCHAR(150),
                Quantity INTEGER,
                Expiry_Date DATE,
                Provider_ID INTEGER FORIEGN KEY,
                Provider_Type VARCHAR(150),
                Location VARCHAR(100),
                Food_Type VARCHAR(150),
                Meal_Type VARCHAR(150)
                )''')
con.commit()