import streamlit as st

st.set_page_config(
    page_title='Introduction'
)
st.title('Food Wastage Management')
st.write('Food is one of the basic need for every one. While many suffer from lack of food and looking to have atleast one meal a day, we have' \
         ' loads of food going to waste due to no sales or overproduction,insufficient storage facilities and consumer habits. This app is to help'\
         'connect these organizations having abundance of food and no use for it with people who need that food to survive')
st.write("""Following are the tables of providers,recievers,food listing and claims used as an example to show how the app works\n
 **Providers:** Provider_ID,Name,Type,Address,City,Contact\n
 **Receivers:** Receiver_ID,Name,Type,City,Contact\n
 **Foodlist :** Food_ID,Food_Name,Quantity,Expiry_Date,Provider_ID,Provider_Type,Location,Food_Type,Meal_Type\n
 **Claims   :** Claim_ID,Food_ID,Receiver_ID,Status,Timestamp""")
