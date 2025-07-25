import streamlit as st
import pickle as pkl
import pandas as pd
import datetime as dt
import os

st.title('Delivery Time Predictor')
pred_type = st.sidebar.radio('Select type of prediction:',options=['Single Prediction','Multiple Prediction'])
pipe = pkl.load(open(r'model.pkl','rb'))
# ['Agent_Age', 'Agent_Rating', 'Weather', 'Traffic', 'Vehicle', 'Area','Category', 'Month', 'Order_Day', 'Order_Dayofweek', 'Order_hour','Pickup_Day', 'Pickup_Dayofweek', 'Pickup_hour', 'Distance']
sample_df = pkl.load(open('ipex.sav','rb'))
if pred_type == 'Single Prediction':
    st.markdown("\n <h1 style='font-size:20px;'> Agent Details\U0001F69A :</h1>",unsafe_allow_html=True)
    col1,col2,col3 = st.columns(3)
    Agent_Age = col1.number_input('Age:',min_value=18,max_value=60,step=1,value=25,key='Age')
    Agent_Rating = col2.number_input('Rating\u2605:',min_value=1.0,max_value=5.0,step=0.1,value=5.0,key='Rate')
    Vehicle = col3.selectbox('Vehicle\U0001F6F5:',options=['motorcycle', 'scooter', 'van', 'bicycle'],key='Veh')
    st.markdown("\n <h1 style='font-size:20px;'> Location Details\U0001F30F\U0001F4CD :</h1>",unsafe_allow_html=True)
    col1,col2 = st.columns(2)
    Weather = col1.selectbox('Weather\u2600\U0001F327:',options=['Sunny', 'Stormy', 'Sandstorms', 'Cloudy', 'Fog', 'Windy'],key='Weat')
    Traffic = col1.selectbox('Traffic\U0001F697\U0001F6A6:',options=['Low','Medium','High','Jam'],key='Traff')
    Area = col2.selectbox('Area\U0001F4CD:',options=['Other','Semi-Urban','Urban','Metropolitian'],key='Area')
    Distance = col2.number_input('Distance  from store(km):',min_value=0.1,step=0.1,value = 10.0,key='Dist')
    st.markdown("\n <h1 style='font-size:20px;'> Order Details\U0001F6D2\U0001F4E6 :</h1>",unsafe_allow_html=True)
    Category = st.selectbox('Category:',options=['Clothing', 'Electronics', 'Sports', 'Cosmetics', 'Toys', 'Snacks','Shoes', 'Apparel',
                                                'Jewelry', 'Outdoors', 'Grocery', 'Books','Kitchen', 'Home', 'Pet Supplies', 'Skincare'],key='Cat')
    col1,col2 = st.columns(2)
    Order_date = col1.date_input('Order Date\U0001F4C5',key='Date')
    Order_time = col2.time_input('Order_Time\U0001F550',key='Time')
    Month = Order_date.month
    Order_Day = Order_date.day
    Order_Dayofweek = Order_date.weekday()
    Order_hour = Order_time.hour
    if (Order_hour + 4 < 20) and (Order_hour + 4 > 8):
        Pickup_Day = Order_Day
        Pickup_Dayofweek = Order_Dayofweek
        Pickup_hour= Order_hour
    else:
        Pickup_Day = Order_Day+1
        Pickup_Dayofweek = Order_Dayofweek+1
        Pickup_hour = 8
    if 'pred_bt' not in st.session_state:
        st.session_state.pred_bt = False
    if st.button('Predict'):
        st.session_state.pred_bt = True
    if st.session_state.pred_bt:
        try:
            req_data ={'Agent_Age':Agent_Age,'Agent_Rating':Agent_Rating,'Vehicle':Vehicle,'Weather':Weather,'Traffic':Traffic,
                                    'Area':Area,'Distance':Distance,'Category':Category,'Month':Month,'Order_Day':Order_Day,'Order_Dayofweek':Order_Dayofweek,
                                    'Order_hour':Order_hour,'Pickup_Day':Pickup_Day,'Pickup_Dayofweek':Pickup_Dayofweek,'Pickup_hour':Pickup_hour}
            data_df = pd.concat([sample_df,pd.DataFrame([req_data])],ignore_index=True)
            Result = pipe.predict(data_df).round().astype(int)
            st.markdown(f"Delivery time is :\n <h1 style='font-size:32px;'>{Result[1]} hours</h1> ",unsafe_allow_html=True)
            st.balloons()
            if st.button('OK'):
                st.session_state.pred_bt = False
        except Exception as e:
            st.error(f'Error making prediction:{e}')
if pred_type == 'Multiple Prediction':
    file = st.file_uploader('Upload details here:',type=['csv','xlx','xlsx'])
    if 'pred_bt2' not in st.session_state:
        st.session_state.pred_bt2 = False
    if st.button('Predict'):
        st.session_state.pred_bt2 = True
    if st.session_state.pred_bt2:
        file_ext = os.path.splitext(file.name)[1].lower()
        try:
            if file_ext == '.csv':
                data_df = pd.read_csv(file)
            elif file_ext in ['.xlx','.xlsx']:
                data_df = pd.read_excel(file)
            else:
                st.error('File type is not supported')
            if data_df is not None:
                try:
                    cols = list(sample_df.columns)
                    missing_cols = []
                    for col in cols:
                        if col not in list(data_df.columns):
                            missing_cols.append(col)
                        else:
                            continue
                    if len(missing_cols) != 0:
                        st.error(f'Columns missing:{missing_cols}')
                    else:
                        X = data_df[cols]
                        y = pipe.predict(X)
                        data_df['Delivery_Time'] = y
                        st.write(data_df)
                        csv = data_df.to_csv(index=False).encode('utf-8')
                        st.download_button('Download table as csv',data = csv, file_name='Predicted_Delivery_Time.csv',key='download')
                except Exception as e:
                    st.error(f'Error predicting Delivery Time:{e}')
        except Exception as e:
            st.error(f'Error reading file:{e}')
        if st.button('OK'):
            st.session_state.pred_bt2 = False
