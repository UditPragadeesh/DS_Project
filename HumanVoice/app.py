import torch
from torch import nn
import pickle as pkl
import pandas as pd
import streamlit as st
import numpy as np

st.title('HUMAN VOICE CLASSIFIER 🗣️')

class fblock(nn.Module):
    def __init__(self,ip, op):
        super().__init__()
        self.f1 = nn.Sequential(nn.Linear(ip,64),nn.ELU())
        self.f2 = nn.Sequential(nn.Linear(64,128),nn.ELU())
        self.f3 = nn.Sequential(nn.Linear(128,256),nn.ELU())
        self.f4 = nn.Sequential(nn.Linear(256,512),nn.ELU())
        self.f5 = nn.Sequential(nn.Linear(512,op),nn.ELU(),nn.Dropout(0.1))
    def forward(self,x):
        x = self.f1(x)
        x = self.f2(x)
        x = self.f3(x)
        x = self.f4(x)
        x = self.f5(x)
        return x
class binaryNet(nn.Module):
    def __init__(self,ip):
        super().__init__()
        self.f1 = fblock(ip,512)
        self.f2 = fblock(512,1024)
        self.f3 = nn.Sequential(nn.Linear(1024,1),nn.Sigmoid())
    def forward(self,x):
        x = self.f1(x)
        x = self.f2(x)
        x = self.f3(x)
        return x
        
model = binaryNet(5)
model.load_state_dict(torch.load('Voice_predictor_dict.sav'))
pitch_c = pkl.load(open('pitch_cluster.sav','rb'))
spec_c  = pkl.load(open('spectral_cluster.sav','rb'))
mfcc_c  = pkl.load(open('mfcc_cluster.sav','rb'))
energy_c = pkl.load(open('energy_cluster.sav','rb'))
pred_df = pkl.load(open('df.sav','rb'))
scaler = pkl.load(open('scaler.sav','rb'))
file_path = st.file_uploader('Upload voice features file(.csv)📁:',type='.csv')

if pred_df not in st.session_state:
    st.session_state.pred_bt = False
if st.button('Find'):
    st.session_state.pred_bt = True
if st.session_state.pred_bt:
    if file_path is not None:
        try:
            df = pd.read_csv(file_path)
            pitch = np.array(pitch_c.predict(df))
            spectrum = spec_c.predict(df)
            mfcc = mfcc_c.predict(df)
            energy = energy_c.predict(df)
            zero_cr = df['zero_crossing_rate']
            clustered_df = pd.DataFrame({'zero_crossing_rate':zero_cr,'pitch_cluster':pitch,'Spectral_cluster':spectrum,
                                        'mfcc_cluster':mfcc,'energy_cluster':energy})
            x = pd.concat([pred_df,clustered_df])
            x = scaler.transform(x)
            x = torch.tensor(x,dtype=torch.float32)
            result = list(model(x).detach().numpy())
            result = [i>0.6 for i in result]
            result_df = df.copy()
            result_df['male'] = result
            st.write(result_df)
            col1,col2,col3 = st.columns([4,6,1])
            if col3.button('OK'):
                st.session_state.pred_bt = False
            csv = result_df.to_csv(index=False).encode('utf-8')
            col1.download_button('Download table as csv',data = csv, file_name='Humanvoiceclassification.csv',key='download')
        except Exception as e:
            st.error(e)

    else:
        st.error('File not uploaded')

    