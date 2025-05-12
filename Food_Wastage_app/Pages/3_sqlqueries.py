import pandas as pd
import sqlite3 as sql
import seaborn as sns
import matplotlib.pyplot as plt
import datetime as dt
import streamlit as st

st.title('SQL Queries')
#connecting to sql Database
con = sql.connect('foodwastage.db')
cur = con.cursor()

#Read data files
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

#list of queries
queries = ['1. How many food providers and receivers are there in each city?',\
           '2. Which type of food provider (restaurant, grocery store, etc.) contributes the most food?',\
           '3. What is the contact information of food providers in a specific city?',\
           '4. Which receivers have claimed the most food?',\
           '5. What is the total quantity of food available from all providers?',\
           '6. Which city has the highest number of food listings?',\
           '7. What are the most commonly available food types?',\
           '8. Which receiver type has placed most claims?',\
           '9. How many food claims have been made for each food item?',\
           '10. Which provider has had the highest number of successful food claims?',\
           '11.what is the most common food type in each meal type?',\
           '12. What percentage of food claims are completed vs. pending vs. canceled?',\
           '13. What is the average quantity of food claimed per receiver?',\
           '14. Which meal type (breakfast, lunch, dinner, snacks) is claimed the most?',\
           '15. What is the total quantity of food donated by each provider?']

query = st.selectbox('Select query:',options=queries)

if query == '1. How many food providers and receivers are there in each city?':
    #Count of food providers and recievers by city
        Q1 = '''SELECT City,COUNT(Provider_ID) AS No_of_Providers
                FROM Providers
                GROUP BY City
                ORDER BY No_of_Providers DESC;
            '''
        Q1_1 = '''SELECT City,COUNT(Receiver_ID) AS No_of_Receivers
                FROM Receivers
                GROUP BY City
                ORDER BY No_of_Receivers DESC;
                '''
        cur.execute(Q1)
        Providers_Count = pd.DataFrame(cur.fetchall(),columns = ['City','No_of_Providers'])
        cur.execute(Q1_1)
        Receivers_Count = pd.DataFrame(cur.fetchall(),columns = ['City','No_of_Receivers'])

        df1 = Providers_Count.merge(Receivers_Count,on='City',how='outer')
        df1 = df1.sort_values('City',axis=0,ascending=True)
        df1 = df1.fillna(0)
        df1 = filter(df1,'City')
        st.write(df1)

if query == '2. Which type of food provider (restaurant, grocery store, etc.) contributes the most food?':
    # Type of food provider with the most food
        Q2 = '''SELECT Type,SUM(Quantity) as TQ
                FROM Foodlist
                INNER JOIN Providers ON Foodlist.Provider_ID = Providers.Provider_ID
                GROUP BY Type
                ORDER BY TQ DESC'''
        cur.execute(Q2)
        df2 = pd.DataFrame(cur.fetchall(),columns = ['Type','Quantity'])
        r2 =maximum(df2,'Quantity')
        st.write(f"**Provider type with the most food is :** {r2['Type'].iloc[0]}")
        st.dataframe(df2)
if query == '3. What is the contact information of food providers in a specific city?':
        #Contact information of providers in city
        Q3 = '''SELECT City, Name, Contact
                FROM Providers
                GROUP BY City'''
        cur.execute(Q3)
        df3 = pd.DataFrame(cur.fetchall(),columns = ['City', 'Name', 'Contact'])
        a = filter(df3,'City')
        st.dataframe(a)

if query == '4. Which receivers have claimed the most food?':
     #Reciever who claimed the most food
        Q4 = '''SELECT Receivers.Name ,SUM(Quantity)
                FROM Receivers
                INNER JOIN Claims ON Receivers.Receiver_ID = Claims.Receiver_ID
                INNER JOIN Foodlist ON Claims.Food_ID = Foodlist.Food_ID
                WHERE Status='Completed'
                GROUP BY Claims.Receiver_ID'''
        cur.execute(Q4)
        df4 = pd.DataFrame(cur.fetchall(),columns=['Name','Total_claims'])
        max_r = maximum(df4,'Total_claims')
        st.write(f'**Receiver with the most claims is :** {max_r['Name'].iloc[0]}')
        st.dataframe(top(df4,'Total_claims'))

if query == '5. What is the total quantity of food available from all providers?':
     #Total quantity from all providers
        Q5 = '''SELECT Providers.Name, SUM(Quantity)
                FROM Providers
                INNER JOIN Foodlist ON Providers.Provider_ID = Foodlist.Provider_ID
                GROUP BY Foodlist.Provider_ID
                '''
        cur.execute(Q5)
        df5 = pd.DataFrame(cur.fetchall(),columns=['Provider_Name','Total_Qty'])
        total1 = int(df5['Total_Qty'].sum())
        st.write(f"**Total quantity from all providers =** {total1}")
        a = filter(df5,'Provider_Name')
        total = int(a['Total_Qty'].sum())
        a.loc[len(a)] = ['Total',total]
        st.write(f"**Total quantity from selected providers =** {total}")
        st.write(a)

if query == '6. Which city has the highest number of food listings?':
     #City with highest food listings
        Q6= '''SELECT Location AS City,COUNT(Food_ID) AS listings
                FROM Foodlist
                GROUP BY Location
                '''
        cur.execute(Q6)
        df6 = pd.DataFrame(cur.fetchall(),columns=['City','No_of_listings'])
        df6 = df6.sort_values(by='No_of_listings',ascending=False)
        r6 = maximum(df6,'No_of_listings')
        if len(r6) <= 1:
              st.write(f'**City with maximum food listings is :** {r6["City"].iloc[0]}')
        if len(r6) > 1:
              st.write(f'**Cities with maximum food listings are :** {r6['City'].iloc[0]},{r6['City'].iloc[1]}')
        st.write(r6)

if query == '7. What are the most commonly available food types?':
      #most commonly available food types
        Q7 = '''SELECT Food_Type,COUNT(Food_ID) AS Type_Count
                FROM Foodlist
                GROUP BY Food_Type'''
        cur.execute(Q7)
        df7 = pd.DataFrame(cur.fetchall(),columns=['Food_Type','No_of_listings'])
        df7 = df7.sort_values(by='No_of_listings',ascending=False)
        st.write(f'**The most common food type is:** {df7['Food_Type'].iloc[0]}')
        st.write(df7)

if query == '8. Which receiver type has placed most claims?':
      #food listings expiring soon (within the next 3 days)
        Q8 = '''SELECT Receivers.Type,COUNT(Claim_ID) as claims,
                        RANK() OVER (ORDER BY COUNT(Claim_ID) DESC) AS Rank
                FROM Receivers
                INNER JOIN Claims ON Receivers.Receiver_ID=Claims.Receiver_ID
                GROUP BY Receivers.Type;
        '''
        r8 = pd.read_sql_query(Q8,con)
        st.write(f'**Receiver type with the most claims is:** {r8['Type'].iloc[0]}')
        st.write(r8)

if query == '9. How many food claims have been made for each food item?':
        Q9 = '''SELECT Food_Name, COUNT(Claim_ID) 
                FROM Claims
                INNER JOIN Foodlist ON Claims.Food_ID = Foodlist.Food_ID
                WHERE Status='Completed'
                GROUP BY Food_Name'''
        cur.execute(Q9)
        df9 = pd.DataFrame(cur.fetchall(),columns=['food_item','No_of_claims'])
        st.write(df9)
if query == '10. Which provider has had the highest number of successful food claims?':
        Q10 = '''SELECT Providers.Name,COUNT(Claim_ID)
            FROM Providers 
            INNER JOIN Foodlist ON Providers.Provider_ID=Foodlist.Provider_ID
            INNER JOIN Claims ON Foodlist.Food_ID = Claims.Food_ID
            WHERE Status='Completed'
            GROUP BY Foodlist.Provider_ID'''
        cur.execute(Q10)
        df10 = pd.DataFrame(cur.fetchall(),columns=['Provider','No_of_claims'])
        df10 = df10.sort_values(by='No_of_claims',ascending=False)
        st.write(f'**Provider with most number of successful claims is:** {df10['Provider'].iloc[0]}')
        df10 = filter(df10,'Provider')
        st.write(df10)

if query == '11.what is the most common food type in each meal type?':
       Q11 = '''WITH RM AS(SELECT 
                                Meal_Type,Food_Type,COUNT(Food_ID) AS Meal_Count,
                                RANK() OVER (PARTITION BY Meal_Type ORDER BY COUNT(Food_ID) DESC) AS Rank
                           FROM Foodlist
                           GROUP BY Meal_Type,Food_Type)
                SELECT Meal_Type,Food_Type,Meal_Count
                FROM RM
                WHERE Rank=1;'''
       r11 = pd.read_sql_query(Q11,con)
       st.write(r11)

if query == '12. What percentage of food claims are completed vs. pending vs. canceled?':
      #percentage of food claims are completed vs. pending vs. canceled
        Q12 = '''SELECT Status,COUNT(Claim_ID)
                FROM Claims
                GROUP BY Status'''
        cur.execute(Q12)
        df12 = pd.DataFrame(cur.fetchall(),columns=['Status','Count'])
        sum = df12['Count'].sum()
        df12['Percentage(%)'] = (df12['Count']/sum)*100
        fig,ax = plt.subplots()
        plt.pie(df12['Percentage(%)'],labels=df12['Status'],autopct='%.2f%%')
        st.write(df12)
        st.pyplot(fig)
if query ==  '13. What is the average quantity of food claimed per receiver?':
      #average quantity of food claimed per receiver
        Q13 = '''SELECT ROUND(SUM(Quantity)/COUNT(Receiver_ID),2)
                FROM Claims
                INNER JOIN Foodlist ON Claims.Food_ID = Foodlist.Food_ID
                WHERE Status='Completed'
                '''
        cur.execute(Q13)
        r13 =cur.fetchall()
        r13 = r13[0]
        r13 = float(r13[0])
        st.write(f'**Average quantity of food claimed per receiver is :** {r13}/receiver')

if query == '14. Which meal type (breakfast, lunch, dinner, snacks) is claimed the most?':
      #meal type (breakfast, lunch, dinner, snacks) claimed the most
        Q14 = '''SELECT Meal_Type, COUNT(Claim_ID) 
                FROM Foodlist 
                INNER JOIN Claims ON Claims.Food_ID=Foodlist.Food_ID
                GROUP BY Meal_Type'''
        cur.execute(Q14)
        df14 = pd.DataFrame(cur.fetchall(),columns=['Meal_Type','Count'])
        df14 = df14.sort_values(by='Count',ascending=False)
        st.write(f'**Most common meal type is:** {df14['Meal_Type'].iloc[0]}')
        st.write(df14)
if query == '15. What is the total quantity of food donated by each provider?':
        #total quantity of food donated by each provider
        Q15 = '''SELECT Providers.Name, SUM(Quantity) AS Total_Quantity
                FROM Providers
                INNER JOIN Foodlist ON Providers.Provider_ID=Foodlist.Provider_ID
                GROUP BY Foodlist.Provider_ID'''
        cur.execute(Q15)
        df15 = pd.DataFrame(cur.fetchall(),columns=['Provider_Name','Total_donations'])
        df15 = df15.sort_values(by='Total_donations',ascending=False)
        df = filter(df15,'Provider_Name')
        st.write(df)