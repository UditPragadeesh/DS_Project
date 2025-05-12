import streamlit as st
import sqlite3 as sql
import pandas as pd
import datetime as dt
from rapidfuzz import fuzz

st.title('View Tables')
#connecting to sql
con = sql.connect('foodwastage.db')
cur = con.cursor()

#loading tables
providers = pd.read_sql_query('SELECT * FROM Providers',con)
receivers = pd.read_sql_query('SELECT * FROM Receivers',con)
foodlistings = pd.read_sql_query('SELECT * FROM Foodlist',con)
claims = pd.read_sql_query('SELECT * FROM Claims',con)

#Assining date columns to datatime datatype
foodlistings['Expiry_Date']=pd.to_datetime(foodlistings['Expiry_Date'])
claims['Timestamp'] = pd.to_datetime(claims['Timestamp'])

#Filter function to filter data in table
def filter(data,*args):
    df = data
    for col in args:
        ops = list(df[col].unique())
        selection = st.sidebar.multiselect(label=f'{col}:',options=ops)
        if len(selection) != 0:
            df = df[df[col].isin(selection)]
    return df

table = st.selectbox('Select table:', options = ['Providers','Receivers','Food Listings','Claims'])

# Viewing selected table with filters
if table == 'Providers':
    st.subheader('Providers')
    st.sidebar.subheader('Search & Filters')
    a = filter(providers,'Provider_ID','Name','City','Type')
    st.write(a)

if table == 'Receivers':
    st.subheader('Receivers')
    st.sidebar.subheader('Search & Filters')
    a = filter(receivers,'Receiver_ID','Name','City','Type')
    st.write(a)

if table == 'Food Listings':
    st.subheader('Food Listings')
    st.sidebar.subheader('Search & Filters')
    exp_prod = st.sidebar.checkbox('Include expired products')
    a = filter(foodlistings,'Food_ID','Food_Name','Expiry_Date','Provider_Type','Provider_ID','Location','Food_Type','Meal_Type')
    today = dt.date.today()
    if exp_prod == False:
        a = a[a['Expiry_Date'].dt.date > today]
    a['Expiry_Date'] = a['Expiry_Date'].dt.strftime('%Y-%m-%d')
    st.write(a)

if table == 'Claims':
    st.subheader('Claims')
    st.sidebar.subheader('Search & Filters')
    a = filter(claims,'Claim_ID','Food_ID','Receiver_ID','Status','Timestamp')
    st.write(a)
    


