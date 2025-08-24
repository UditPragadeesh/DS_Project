
# Human Voice classification
    
This interactive web application that classifies male and female voices based on voice features. It takes in scan images as '.csv'.

## Workflow

- EDA - Outliers checked and removed, checked for data distribution and checked correlation of data.
- Pre Processing - Data had multiple features based on different features which where clustered based on 4 major categorires pitch, spectrum, mfcc and energy. Scaled using Standard Scaler.
- Model Training - Random forest classifier, support vector classifier and Pytorch linear neural network where Trained and tested through multiple iterations.
- Model Validation - Trained models where tested using accuracy, precision, recall and f1-scores out of which neural network had the best score so it was selecte for further use.
- Web-appliction - Trained clustering models and state dict of neural network where saved using pickle and used in an interactive streamlit application.

## Tools and Libraries used

- PyTorch(neural network) - model training and model validation
- sklearn - StandardScaler, machine learnig models and validation.
- Streamlit - Interactive Web-app development
- Seaborn,Matplotlib - EDA and training visualization

## RUNNING APPLICATION
To run app, use command

```bash
   streamlit run app.py
```

# Hi, I'm Udit Pragadeesh! 👋


## 🚀 About Me
Data scientist with a background in engineering and 2 years’ experience as a design engineer in a manufacturing industry. Skilled in Python programming, data analysis, machine learning and deep learning. Motivated to apply analytical and problem-solving skills in real-world business challenges. 

## 🛠 Skills
 Python, PyTorch, SQL, Scikit-learn, Matplotlib, MLflow, Seaborn,Power BI, MS Office: Excel, Word, PowerPoint, Six sigma, Problem Solving

