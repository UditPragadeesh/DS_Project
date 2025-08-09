
# Tuberculosis Detection
    This interactive web application predicts if someone as tuberculosis or not based on a scan of their lungs. It takes in scan images as '.jpg','.jpeg' or '.png'.

## Workflow
    - EDA - to check distribution of data and image sizes
    - Pre Processing - to resize, normalize and convert images to tensor.
    - Model Training - Resnet50, vgg16 and effecientnet_b0 pre-trained image procession models were loaded and further trained on our dataset and tested one by one.
    - Model Validation - trained models were validated using precision,accuracy, recall and f1 scores and model with best scores was selected.
    - Web-appliction - Selected model was used to create an interactive web-application using streamlit to upload and check images.
    - AWS deployment - This web-application is uploaded and hosted using aws and can be accessed through http://13.49.57.51:8501/
## Tools and Libraries used:
    - PyTorch(torchvision,torch) - Data preprocessing, model training and model validation
    - Streamlit - Interactive Web-app development
    - Seaborn,Matplotlib - EDA and training visualization
    - aws - online of application

## RUNNING APPLICATION
Application can be accessed through this link - http://13.49.57.51:8501/
To run app, use command

```bash
   streamlit run Tuberculosis_app.py
```

# Hi, I'm Udit Pragadeesh! 👋


## 🚀 About Me
Aspiring Data scientist with a background in aeronautical engineering and 2 years’ experience as a design engineer in a manufacturing industry. Skilled in Python programming for machine learning and deep learning. Motivated to apply analytical and problem-solving skills in real-world business challenges. 

## 🛠 Skills
 Python, PyTorch, SQL, Scikit-learn, Matplotlib, MLflow, Seaborn,Power BI, MS Office: Excel, Word, PowerPoint, Six sigma, Problem Solving

