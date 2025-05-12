import pandas as pd
import sqlite3 as sql
import datetime as dt
import streamlit as st
from rapidfuzz import fuzz
import time
import math
import re

st.title('Adding Data')

#Creating connection to database
con = sql.connect('foodwastage.db')
cur = con.cursor()
#defining name match check function
def is_name_in(name,name_list,threshold=70):
    for n in name_list:
      if fuzz.ratio(name,n) >= threshold:
          a = True
          b = n
          break
      else:
          a = False
          b = name
          continue
    return a,b    
#Filter function to filter data in table
def filter(data,*args):
    df = data
    for col in args:
        ops = list(df[col].unique())
        selection = st.sidebar.multiselect(label=f'{col}:',options=ops)
        if len(selection) != 0:
            df = df[df[col].isin(selection)]
    return df

#Selection of provider or receiver
type1 = st.selectbox('**Select an option:**', options=['Provider','Receiver'])
i = 0
name = st.text_input('Enter you Name:',key = 'input')

#Counter in session state for the loop to not repeat itself
if 'Counter' not in st.session_state:
    st.session_state.Counter = 0

#Provider details
if type1 == 'Provider':
    while len(name) > 0 and i < st.session_state.Counter+1:
        cur.execute('SELECT Name From Providers')
        provs_df = pd.DataFrame(cur.fetchall(),columns=['Name'])
        provs = list(provs_df['Name'])
        provider,name = is_name_in(name,provs,60)

#When provider already exists in the database
        if provider == True:
            provider_data = pd.read_sql_query(f'''SELECT *
                                                  FROM Providers
                                                  WHERE Name = "{name}"''',con) 
            list_match=[]
#When there are multiple providers with same name
            for match in provider_data[['Provider_ID','Name','City']].values:
                list_match.append(tuple(match))
            list_match.append('others')
            correct_match = st.selectbox('Select provider',options=list_match,key = f'match{i}')
            i+=1
            if correct_match != 'others':
                provider_data = provider_data[provider_data['Provider_ID']==correct_match[0]]
                Prov_ID = provider_data['Provider_ID'].iloc[0]
                Prov_Type=provider_data['Type'].iloc[0]
                Loc=provider_data['City'].iloc[0]
#Selection of the operation to be performed
                operation = st.selectbox('What to do?',options = ['Update Provider details','Change Provider food listing','Add new food listing'],key = f'operation{i}')
#Operation is to add new food to the listing
                if operation == 'Add new food listing':
                        item = st.text_input('Enter food name',key = f'item{i}')
                        qty = st.number_input('Enter quantity',min_value=1.0,step = 1.0,key = f'qty{i}')
                        today = dt.date.today()
                        exp_date = st.date_input('Enter expiry date(yyyy-mm-dd)',value=today,format='YYYY/MM/DD',min_value=today,key = f'exp_date{i}')
                        fd_typ = st.selectbox('Select food type:',options=['Non-Vegetarian','Vegetarian','Vegan'])
                        ml_typ = st.selectbox('Select meal type:',options=['Breakfast','Lunch','Snacks','Dinner'])
                        if st.button('Add food to list',key = 'Addfood'):
                            if len(item) != 0:
                                if bool(re.search(r'[^A-Za-z]',item)):
                                    st.error('Warning:your item name contains **numbers** or **special characters**')
                                    time.sleep(0.1)
                                else:
                                    exp_date=exp_date.strftime('%Y-%m-%d')
                                    food_details = (item,int(qty),exp_date,int(Prov_ID),Prov_Type,Loc,fd_typ,ml_typ)        
                                    cur.execute(f'''INSERT INTO Foodlist(Food_Name,Quantity,Expiry_Date,Provider_ID,Provider_Type,Location,Food_Type,Meal_Type)
                                                    VALUES {food_details};''')
                                    con.commit()
                                    cur.execute(f'''SELECT Food_ID FROM Foodlist
                                                    WHERE Provider_ID='{Prov_ID}' AND Food_Name='{item}';''')
                                    Food_ID = cur.fetchall()
                                    Food_ID = Food_ID[-1]
                                    Food_ID = Food_ID[-1]
                                    st.success(f'Food added to listing,\n **Your food ID is : {Food_ID}')
                                    if st.button('OK',key='ok'):
                                            break
                                    else:
                                            time.sleep(0.1)
                            else:
                                st.error('Add Food Name')
#Operation is to update details of the provider
                if operation == 'Update Provider details':
                    provider_cols = list(provider_data.columns)
                    for col in provider_cols:
                        val = list(provider_data[col].values)
                        if col == 'Provider_ID':
                            st.text(f'Your Provider_ID is: \n {val[0]}')
                        elif col == 'Type':
                            provider_types = ['Supermarket','Grocery Store','Restaurant','Catering Service','others']
                            provider_data[col]=st.selectbox('Select your Type',options=provider_types,index=provider_types.index(val[0]))
                        elif col != 'Address':
                            provider_data[col] = st.text_input(f'Enter your {col}',value=f'{val[0]}',key=f'{col,i}')
                        else:
                            provider_data[col] = st.text_area(f'Enter your {col}',value=f'{val[0]}',key=f'{col,i}')
                    if st.button('Update',key=f'updt{i}'):
                        try:
                            for col in provider_cols:
                                val1= provider_data[col].iloc[0]
                                if col != 'Provider_ID':
                                    if col == 'Contact':
                                        if bool(re.search(r'[^0-9]',val1)):
                                            st.error('Warning:your item name contains **special characters** or **numbers**')
                                            st.stop()
                                        else:
                                            cur.execute(f'''Update Providers
                                              SET {col} = '{val1}'
                                              WHERE Provider_ID = {Prov_ID}''')
                                    elif  col != 'Address':
                                        if bool(re.search(r'[^A-Za-z\s]',val1)):
                                            st.error('Warning:your item name contains **special characters** or **numbers**')
                                            st.stop()
                                        else:
                                            cur.execute(f'''Update Providers
                                              SET {col} = '{val1}'
                                              WHERE Provider_ID = {Prov_ID}''')
                                    else:
                                        cur.execute(f'''Update Providers
                                              SET {col} = '{val1}'
                                              WHERE Provider_ID = {Prov_ID}''')
                            con.commit()            
                            st.success('Provider details updated')
                            if st.button('OK',key='ok'):
                                i+=1
                                break
                            else:
                                time.sleep(0.1)
                        except:
                            st.error('Provider details not updated')
                            if st.button('OK',key=f'rtr{i}'):
                                break
                            else:
                                time.sleep(0.1)           
#Operation is to change details of a listing by provider
                if operation == 'Change Provider food listing':
                    listings = pd.read_sql_query(f'''SELECT * FROM Foodlist
                                                    WHERE Provider_ID={Prov_ID};''',con)
                    if len(listings) != 0:
                        list_food = []
                        for food in listings[['Food_ID','Food_Name','Quantity']].values:
                            food = list(food)
                            list_food.append(tuple(food))
                        correct_food = st.selectbox('Select Food to update',options=list_food,key = f'food{i}')
                        if correct_food != 'others':
                            listings=listings[listings['Food_ID']==correct_food[0]]
                            foodlist_cols = list(listings.columns)
                            for col in foodlist_cols:
                                val = list(listings[col].values)
                                if col == 'Food_ID':
                                    st.text(f'Your Food_ID is: \n {val[0]}')
                                elif col == 'Food_Type':
                                    food_types = ['Non-Vegetarian','Vegetarian','Vegan']
                                    listings[col]=st.selectbox('Select your Type',options=food_types,index=food_types.index(val[0]))
                                elif col == 'Meal_Type':
                                    meal_types = ['Breakfast','Lunch','Snacks','Dinner']
                                    listings[col]=st.selectbox('Select your Type',options=meal_types,index=meal_types.index(val[0]))
                                elif col == 'Quantity':
                                    listings[col] = st.number_input('Enter quantity',min_value=1.0,step = 1.0,value=float(val[0]),key = f'qty1{i}')
                                elif col == 'Expiry_Date':
                                    today = dt.date.today()
                                    try:
                                        listings[col] = st.date_input('Enter expiry date(yyyy-mm-dd)',value=val[0],format='YYYY/MM/DD',min_value=today,key = f'exp_date{i}')
                                    except:
                                        listings[col] = st.date_input('Enter expiry date(yyyy-mm-dd)',value=val[0],format='YYYY/MM/DD',min_value=val[0],key = f'exp_date{i}')
                                elif col != 'Provider_ID' and col != 'Provider_Type':
                                    listings[col] = st.text_input(f'Enter your {col}',value=f'{val[0]}',key=f'{col,i}')
                            if st.button('Update',key=f'updtfd{i}'):
                                FD_ID = listings['Food_ID'].iloc[0]
                                try:
                                    for col in foodlist_cols:
                                            val2= listings[col].iloc[0]
                                            if col in ['Food_Name','Location']:
                                                if bool(re.search(r'[^A-Za-z\s]',val2)):
                                                    st.error('Warning:your item name contains **special characters** or **numbers**')
                                                    st.stop()
                                                else:
                                                    cur.execute(f'''Update Foodlist
                                                    SET {col} = '{val2}'
                                                    WHERE Food_ID= {FD_ID}''')
                                            elif col not in ['Food_ID','Provider_ID','Provider_Type']:

                                                cur.execute(f'''Update Foodlist
                                                    SET {col} = '{val2}'
                                                    WHERE Food_ID= {FD_ID}''')
                                    con.commit()
                                    df = pd.read_sql_query(f'''SELECT * FROM Foodlist
                                                                WHERE Food_ID = {FD_ID}''',con)
                                    st.write(df)
                                    st.success('Food listing updated')
                                    i+=1
                                    if st.button('OK',key=f'ok{i}'):
                                            break
                                    else:
                                            time.sleep(0.1)
                                except:
                                    st.error('Foodlist not updated')
                                    i+=1
                                    if st.button('OK',key=f'rty{i}'):
                                            break
                                    else:
                                            time.sleep(0.1)
                    else:    
                        st.error('No matching food listed')
            else:
                provider = False
#When provider does not exist in the database
        if provider == False:
            if len(name) > 0:
                st.error('Provider not found')
#Storing a variable in session state NP
            if 'NP' not in st.session_state:
                st.session_state.NP = False
            if not st.session_state.NP:
                if st.button('New Provider',key = f'np{i}'):
                    st.session_state.NP = True
#Getting Provider details to create new provider
            if st.session_state.NP:
                Name = st.text_input('Enter you name here',key = 'newprov')
                Type = st.selectbox('Select provider type',options= ['Supermarket','Grocery Store','Restaurant','Catering Service','others'])
                Address = st.text_area('Enter your address',key = 'address')
                City = st.text_input('Enter your City',key = 'city')
                Contact = st.text_input('Enter your contact',key = 'contact')
#Adding the collected provider details to the database
                if st.button('Add Provider'):
                    values = [Name,Type,Address,City,Contact]
                    for v in values:
                        if len(v) == 0:
                            st.error('Please fill all details')
                            if st.button('Cancel',key=f'APcnl{i}'):
                                st.session_state.NP=False  
                            st.stop()
                    if bool(re.search(r'[^A-Za-z\s]',values[0])) or bool(re.search(r'[^A-Za-z\s]',values[3])):
                        st.error('Warning:your input contains **special characters** or **numbers**')
                        if st.button('Cancel',key=f'APcnl{i}'):
                                st.session_state.NP=False  
                        st.stop()
                    elif bool(re.search(r'[^0-9]',values[4])):
                        st.error('Warning:your contact should only be **numbers**')
                        if st.button('Cancel',key=f'APcnl{i}'):
                                st.session_state.NP=False  
                        st.stop()
                    else:
                        values = tuple(values)
                        cur.execute(f'''INSERT INTO Providers(Name,Type,Address,City,Contact)
                                    VALUES {values};''')
                        con.commit()
                        cur.execute(f'''SELECT MAX(Provider_ID) FROM Providers''')
                        pvdr_ID = cur.fetchall()
                        pvdr_ID = pvdr_ID[-1]
                        pvdr_ID = pvdr_ID[-1]
                        st.success(f'Provider added\n Your Provider_ID is {pvdr_ID}')
                        if st.button('OK',key='ok'):
                            st.session_state.show_form=False
                            break
                        else:
                            time.sleep(0.1)
                if st.button('Cancel'):
                        st.session_state.NP=False  
            i += 1
            name = ''
            continue
#Reciever details
if type1 == 'Receiver':
    while len(name) > 0 and i < st.session_state.Counter+1:
        cur.execute('SELECT Name From Receivers')
        rcvrs_df = pd.DataFrame(cur.fetchall(),columns=['Name'])
        rcvrs = list(rcvrs_df['Name'])
        receiver,name = is_name_in(name,rcvrs,60)
#When receiver already exists in the database
        if receiver == True:
            receiver_data1 = pd.read_sql_query(f'''SELECT *
                                                  FROM Receivers
                                                  WHERE Name = "{name}"''',con)
#For multiple Receivers with same name
            list_match=[]
            for match in receiver_data1[['Receiver_ID','Name','City']].values:
                list_match.append(tuple(match))
            list_match.append('others')
            correct_match = st.selectbox('Select Receiver',options=list_match,key = f'mat1{i}')
            i+=1
            if correct_match != 'others':
                receiver_data = receiver_data1[receiver_data1['Receiver_ID']==correct_match[0]]
                Rcvr_ID = receiver_data['Receiver_ID'].iloc[0]
                Rcvr_Type=receiver_data['Type'].iloc[0]
                Loc=receiver_data['City'].iloc[0]
#Selection of operation to be done
                operation1 = st.selectbox('What to do?',options = ['Update Receiver details','Claim food'],key = 'operation1')
#Operation is to claim food from list
                if operation1 == 'Claim food':
                    cur.execute('''SELECT Food_ID,Food_Name,Quantity,Expiry_Date,Location,Food_Type,Meal_Type
                                FROM Foodlist''')
                    df_fl = pd.DataFrame(cur.fetchall(),columns=['Food_ID','Food_Name','Quantity','Expiry_Date','Location','Food_Type','Meal_Type'])
                    exp_prod = st.sidebar.checkbox('Include expired products')
                    fst = filter(df_fl,'Food_ID','Food_Name','Location','Food_Type','Meal_Type')
                    today = dt.date.today()
                    fst['Expiry_Date'] = pd.to_datetime(fst['Expiry_Date'])
#Expired products
                    if exp_prod == False:
                        fst = fst[fst['Expiry_Date'].dt.date > today]
                    fst['Expiry_Date'] = fst['Expiry_Date'].dt.strftime('%Y-%m-%d')
                    qty_min=0
                    qty_max=100
                    try:
                        qty_min,qty_max = st.sidebar.slider(label='Quantity',min_value=0,max_value=(math.ceil(max(fst['Quantity'])/100))*100,value=(10,60))
                    except:
                        pass
                    fst = fst[(fst['Quantity']>= qty_min) & (fst['Quantity']<= qty_max)]
                    st.write(fst)
                    ops = list(fst['Food_ID'])
                    Food_Id = st.selectbox('Enter the required food_ID',options=ops)
                    sts = 'Pending'
                    Time = dt.datetime.now()
                    Time = Time.strftime('%Y-%m-%d %H:%M:%S')
                    if st.button('Claim',key =f'claim{i}'):
                        Claim = (int(Food_Id),int(Rcvr_ID),sts,Time)
                        try:
                            cur.execute(f'''INSERT INTO Claimedfood
                                                SELECT * FROM Foodlist
                                                WHERE Food_ID='{Food_Id}';''')
                            cur.execute(f'''DELETE FROM Foodlist
                                                WHERE Food_ID='{Food_Id}';''')
                            cur.execute(f'''INSERT INTO Claims(Food_ID,Receiver_ID,Status,Timestamp)
                                                VALUES {Claim};''')
                            con.commit()
                            cur.execute(f'''SELECT Claim_ID FROM Claims
                                                WHERE Receiver_ID='{Rcvr_ID}';''')
                            claim_ID = cur.fetchall()
                            claim_ID = claim_ID[-1]
                            claim_ID = claim_ID[-1]
                            st.success(f'Claim successfully placed, your claim ID is {claim_ID}')
                            if st.button('OK',key='ok'):
                                break
                            else:
                                time.sleep(0.1)
                        except:
                            st.error('Claim Failed')
                            
                            if st.button('Retry',key=f'ret{i}'):
                                break
                            else:
                                time.sleep(0.1)
#When operation is to change receiver details in database
                if operation1 == 'Update Receiver details':
                    receiver_cols =list(receiver_data.columns)
                    for col in receiver_cols:
                        val = list(receiver_data[col].values)
                        if col == 'Receiver_ID':
                            st.text(f'Your Receiver_ID is: \n {val[0]}')
                        elif col == 'Type':
                            receiver_types = ['Shelter','NGO','Individual','Charity','others']
                            receiver_data['Type']=st.selectbox('Select receiver type',options= receiver_types,index=receiver_types.index(val[0]))
                        else:
                            receiver_data[col] = st.text_input(f'Enter your {col}',value=f'{val[0]}',key=f'{col,i}')
                    if st.button('Update',key=f'updt{i}'):
                        st.write(receiver_data)
                        try:
                            for col in receiver_cols:
                                val1= receiver_data[col].iloc[0]
                                qry = f'''Update Receivers
                                            SET {col} = ?
                                            WHERE Receiver_ID=?'''
                                if col != 'Receiver_ID':
                                    if col == 'Contact':
                                        if bool(re.search(r'[^0-9]',val1)):
                                            st.error('Warning:your contact should only have **numbers**')
                                            st.stop()
                                        else:
                                            cur.execute(f'''Update Receivers
                                            SET {col} = '{val1}'
                                            WHERE Receiver_ID={Rcvr_ID}''')
                                    else:
                                        if bool(re.search(r'[^A-Za-z\s]',val1)):
                                            st.write(val1)
                                            st.error('Warning:your input contains **special characters** or **numbers**')
                                            st.stop()
                                        else:
                                            cur.execute(f'''Update Receivers
                                            SET {col} = '{val1}'
                                            WHERE Receiver_ID={Rcvr_ID}''')
                            con.commit()         
                            st.success('Receiver details updated')
                            if st.button('OK',key='ok'):
                                i+=1
                                break
                            else:
                                time.sleep(0.1)
                        except:
                            st.error('Receiver details not updated')
                            if st.button('OK',key=f'rtr{i}'):
                                break
                            else:
                                time.sleep(0.1)  
            else:
                receiver = False
#When receiver does not exist in the database
        if receiver == False:
            if len(name) > 0:
                st.error('Receiver not found')
            if 'NR' not in st.session_state:
                st.session_state.NR = False
            if not st.session_state.NR:
                if st.button('New Receiver',key = f'nr{i}'):
                    st.session_state.NR = True
#Adding new receiver to database
            if st.session_state.NR:
                name1 = st.text_input('Enter you name here',key = 'newrcvr')
                type = st.selectbox('Select receiver type',options= ['Shelter','NGO','Individual','Charity','others'])
                city = st.text_input('Enter your City',key = 'rcity')
                contact = st.text_input('Enter your contact',key = 'rcontact')
                if st.button('Add Receiver'):
                    values = [name1,type,city,contact]
                    for v in values:
                        if len(v) == 0:
                            st.error('Please fill all details')
                            if st.button('Cancel',key=f'ARcnl{i}'):
                                st.session_state.NR=False  
                            st.stop()
                    if bool(re.search(r'[^A-Za-z\s]',values[0])) or bool(re.search(r'[^A-Za-z\s]',values[2])):
                        st.error('Warning:your input contains **special characters** or **numbers**')
                        if st.button('Cancel',key=f'ARcnl{i}'):
                                st.session_state.NR=False  
                        st.stop()
                    elif bool(re.search(r'[^0-9]',values[3])):
                        st.error('Warning:your contact should only be **numbers**')
                        if st.button('Cancel',key=f'ARcnl{i}'):
                                st.session_state.NR=False  
                        st.stop()
                    else:
                        values = tuple(values)
                    cur.execute(f'''INSERT INTO Receivers(Name,Type,City,Contact)
                                VALUES {values};''')
                    con.commit()
                    cur.execute(f'''SELECT MAX(Receiver_ID) FROM Receivers''')
                    rcvr_ID = cur.fetchall()
                    rcvr_ID = rcvr_ID[-1]
                    rcvr_ID = rcvr_ID[-1]
                    st.success(f'Receiver added\n Your Receiver_ID is {rcvr_ID}')
                    if st.button('OK',key=f'ok{i}'):
                        st.session_state.NR=False
                        break
                    else:
                        time.sleep(0.1)
                if st.button('Cancel'):
                    st.session_state.NR=False
            i += 1
            name = ''
            continue
