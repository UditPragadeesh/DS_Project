import streamlit as st
import pickle as pkl
import torch
from PIL import Image

st.title('TUBERCULOSIS DETECTOR')

model = torch.load(r'Tuberclosis_Detection/TB_Detector.sav',weights_only=False,map_location=torch.device('cpu'))
transform = pkl.load(open(r'Tuberclosis_Detection/transform.pkl','rb'))
path = st.file_uploader('Upload Scan Image',type=["jpg", "jpeg", "png"])
if path is not None:
    image = Image.open(path)
if 'predb' not in st.session_state:
    st.session_state.predb = False
if st.button('Check'):
    st.session_state.predb = True

if st.session_state.predb:
    if path is not None:
        try:
            image = transform(image)
            image = image.unsqueeze(0)
            op = model(image)
            col1,col2,col3= st.columns(3)
            if int(op)<=0:
                col2.markdown("<h1 style='font-size:20px;text-align:center;color:white;background-color:green;padding:10px;border-radius:10px;'> " \
                "NO TUBERCULOSIS DETECTED </h1>",unsafe_allow_html=True)
                st.write('    ')
            elif int(op)>0:
                col2.markdown("<h1 style='font-size:20px;text-align:center;color:white;background-color:red;padding:10px;border-radius:10px;'> " \
                "TUBERCULOSIS DETECTED </h1>",unsafe_allow_html=True)
                st.write('    ')
            col1,col2,col3= st.columns([5,1,5])
            if col2.button('OK'):
                st.session_state.predb=False
        except Exception as e:
            st.error(f'Checking Error:{e}')
            if st.button('OK'):
                st.session_state.predb=False
    else:
        st.error('Upload an Image')
        if st.button('OK'):
            st.session_state.predb=False

