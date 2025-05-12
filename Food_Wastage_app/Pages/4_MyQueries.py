import pandas as pd
import sqlite3 as sql
import seaborn as sns
import matplotlib.pyplot as plt
import datetime as dt
import streamlit as st

st.title('SQL Queries')

#Creating connection to database
con = sql.connect('foodwastage.db')
cur = con.cursor()

#Functions to be used  
def maximum(df,col):
    a = df[df[col] == max(df[col])]
    return a

def top(df,col,q=5):
    df = df.sort_values(col,ascending=False,ignore_index=False)
    a = df.iloc[0:q]
    return a

def filter(data,*args):
    df = data
    for col in args:
        ops = list(df[col].unique())
        selection = st.sidebar.multiselect(label=f'{col}:',options=ops)
        if len(selection) != 0:
            df = df[df[col].isin(selection)]
    return df

queries = ['What is the most common meal_Type listed for each Provider_Type',\
           'What is the total Quantity of food for each food_type',\
           'Which Receiver has the most cancelled claims',\
           'What is the percentage of quantity of each food_type listed',\
           'Which Provider has the most vegan food listings',\
           'What is the most common provider city',\
           'Who are the recievers of the food listing by providers',\
           'What is the quantity of each food name',\
           'What is the ratio of each receiver type',\
           'What is the ratio of each Provider type']

query = st.selectbox('Select query:',options=queries)

if query == 'What is the most common meal_Type listed for each Provider_Type':
    MQ1 = '''WITH RM AS (
            SELECT
                Provider_Type,Meal_Type,COUNT(Food_ID) AS meal_count,
                            RANK() OVER (PARTITION BY Provider_Type ORDER BY COUNT(Food_ID) DESC) AS rank
                FROM Foodlist
                GROUP BY Provider_Type,Meal_Type)
            SELECT Provider_Type,Meal_Type
            FROM RM
            WHERE rank=1;'''
    cur.execute(MQ1)
    df1_1 = pd.DataFrame(cur.fetchall(),columns=['Provider_Type','Common_Meal_Type'])
    st.write(df1_1)

if query == 'What is the total Quantity of food for each food_type':
    MQ2 = '''SELECT Food_Type, SUM(Quantity) AS TQ
             FROM Foodlist
             GROUP BY Food_Type'''
    cur.execute(MQ2)
    df1_2 = pd.DataFrame(cur.fetchall(),columns=['Food_Type','Total_Quantity'])
    df1_2 = df1_2.sort_values('Total_Quantity',ascending=False)
    st.write(df1_2)

if query == 'Which Receiver has the most cancelled claims':
    MQ3 = '''SELECT Receivers.Name, COUNT(Claim_ID)
             FROM Claims
             INNER JOIN Receivers ON Receivers.Receiver_ID = Claims.Receiver_ID
             WHERE Status = 'Pending'
             GROUP BY Claims.Claim_ID
            '''
    cur.execute(MQ3)
    df1_3 = pd.DataFrame(cur.fetchall(),columns=['Receiver_Name','Cancelled_Orders'])
    df1_3 = df1_3.sort_values('Cancelled_Orders',ascending=False)
    df1_3 = filter(df1_3,'Receiver_Name')
    st.write(df1_3)

if query == 'What is the percentage of quantity of each food_type listed':
    MQ4 = '''SELECT Food_Type,SUM(Quantity)
             FROM Foodlist
             GROUP BY Food_Type'''
    cur.execute(MQ4)
    df1_4 = pd.DataFrame(cur.fetchall(),columns=['Food_Type','Count'])
    sum = df1_4['Count'].sum()
    df1_4['Percentage'] = round((df1_4['Count']/sum)*100,2)
    df1_4=df1_4.set_index('Food_Type')
    st.write(df1_4)
    fig,ax = plt.subplots()
    plt.pie(df1_4['Count'],labels=df1_4.index, autopct='%.2f%%')
    st.pyplot(fig)

if query ==  'Which Provider has the most vegan food listings':
    MQ5 = '''SELECT Providers.Name,COUNT(Food_ID) 
             FROM Providers
             INNER JOIN Foodlist ON Providers.Provider_ID=Foodlist.Provider_ID
             WHERE Food_Type='Vegan'
             GROUP BY Foodlist.Provider_ID'''
    cur.execute(MQ5)
    df1_5=pd.DataFrame(cur.fetchall(),columns=['Provider_name','Vegan_listings'])
    df1_5 = df1_5.sort_values(by='Vegan_listings',ascending=False)
    r5 = maximum(df1_5,'Vegan_listings')
    if len(r5) <= 1:
            st.write(f'**Provider with the most vegan food listings is :** {r5['Provider_name'].iloc[0]}')
    if len(r5) > 1:
            st.write(f'**Providers with most vegan food listings are :** {r5['Provider_name'].iloc[0]},{r5['Provider_name'].iloc[1]}')
    st.write(r5)
if query ==  'What is the most common provider city':
     MQ6 = '''SELECT City,MAX(X.P_COUNT)
              FROM (SELECT City,COUNT(Provider_ID) AS P_COUNT
                    FROM Providers
                    GROUP BY City) X
           '''
     cur.execute(MQ6)
     df1_6 = pd.DataFrame(cur.fetchall(),columns=['City','No_of_Providers'])
     st.write(f"City with the most number of providers is: '{df1_6['City'].iloc[0]}'")
     st.write(df1_6)

if query ==  'Who are the recievers of the food listing by providers':
     MQ7= '''SELECT Providers.Name,Providers.City,Receivers.Name,Receivers.City
        FROM Providers
        INNER JOIN Foodlist ON Providers.Provider_ID=Foodlist.Provider_ID
        INNER JOIN Claims ON Foodlist.Food_ID=Claims.Food_ID
        INNER JOIN Receivers ON Claims.Receiver_ID=Receivers.Receiver_ID
        WHERE Claims.Status='Completed'
        '''
     cur.execute(MQ7)
     df1_7 = pd.DataFrame(cur.fetchall(),columns=['Provider_Name','Provider_City','Receiver_Name','Receiver_City'])
     a = filter(df1_7,'Provider_Name','Provider_City','Receiver_Name','Receiver_City')
     st.write(a)

if query == 'What is the quantity of each food name':
     MQ8='''SELECT Food_Name,SUM(Quantity)
       FROM Foodlist
       GROUP BY Food_Name'''
     cur.execute(MQ8)
     df1_8=pd.DataFrame(cur.fetchall(),columns=['Food_Name','Total_Quantity'])
     df1_8 = df1_8.sort_values('Total_Quantity',ascending=False)
     df1_8 = filter(df1_8,'Food_Name')
     st.write(df1_8)
     fig,ax = plt.subplots()
     sns.barplot(data=df1_8,x='Food_Name',y='Total_Quantity',zorder = 2)
     plt.grid(True,color = 'grey',alpha = 0.3,zorder=0)
     plt.xticks(rotation=45)
     st.pyplot(fig)

if query == 'What is the ratio of each receiver type':
     MQ9 = '''SELECT Type,COUNT(Receiver_ID)
              FROM Receivers
              GROUP BY Type'''
     cur.execute(MQ9)
     df1_9 = pd.DataFrame(cur.fetchall(),columns=['Receiver_Type','Count'])
     sum = df1_9['Count'].sum()
     df1_9['Ratio'] = round((df1_9['Count']/sum),2)
     st.write(df1_9)
     fig,ax = plt.subplots()
     plt.pie(df1_9['Count'],labels=df1_9['Receiver_Type'],autopct='%.1f%%')
     st.pyplot(fig)
if query == 'What is the ratio of each Provider type':
     MQ10 = '''SELECT Type,COUNT(Provider_ID)
         FROM Providers
         GROUP BY Type'''
     cur.execute(MQ10)
     df1_10 = pd.DataFrame(cur.fetchall(),columns=['Provider_Type','Count'])
     sum = df1_10['Count'].sum()
     df1_10['Ratio'] = round((df1_10['Count']/sum),2)
     st.write(df1_10)
     fig,ax = plt.subplots()
     plt.pie(df1_10['Count'],labels=df1_10['Provider_Type'], autopct='%.2f%%')
     st.pyplot(fig)