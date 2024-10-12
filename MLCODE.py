import streamlit as st
import pandas as pd
import pickle

# Load the models
with open('/Users/raushankumar/Documents/Miles/comodels.pkl', 'rb') as file:
    models = pickle.load(file)
regressor = models['regressor']
classifier = models['classifier']

# Define the function to make predictions
def predict_status(features):
    prediction = classifier.predict([features])
    return "Won" if prediction[0] == 1 else "Lost"

def predict_price(features):
    prediction = regressor.predict([features])
    return prediction[0]

# User interface
st.set_page_config(page_title="Order Prediction", layout="wide", initial_sidebar_state="expanded")
st.title("Order Prediction App")

# Define the sidebar inputs
st.sidebar.header("Input Parameters")

quantity_tons = st.sidebar.number_input("Quantity (tons)", min_value=0.0, value=0.0, step=0.1)
thickness = st.sidebar.number_input("Thickness", min_value=0.0, value=0.0, step=0.1)
width = st.sidebar.number_input("Width", min_value=0.0, value=0.0, step=0.1)
country = st.sidebar.text_input("Country")
application = st.sidebar.text_input("Application")
temperature = st.sidebar.number_input("Temperature", min_value=0.0, value=0.0, step=0.1)
pressure = st.sidebar.number_input("Pressure", min_value=0.0, value=0.0, step=0.1)
item_type = st.sidebar.selectbox("Item Type", ["BXO", "IPL", "NXO", "Others", "PST", "SLAWR", "WI"])
item_type_encoded = {"BXO": 0, "IPL": 1, "NXO": 2, "Others": 3, "PST": 4, "SLAWR": 5, "WI": 6}[item_type]
year = st.sidebar.number_input("Year", min_value=2000, value=2020, step=1)
month = st.sidebar.number_input("Month", min_value=1, max_value=12, value=1, step=1)
day = st.sidebar.number_input("Day", min_value=1, max_value=31, value=1, step=1)

# Assuming your model uses these features for prediction
features = [quantity_tons, thickness, width, country, application, temperature, pressure, item_type_encoded, year, month, day]

if st.sidebar.button("Predict"):
    status = predict_status(features)
    price = predict_price(features)
    
    st.write(f"## Prediction Results")
    st.write(f"**Status**: {status}")
    st.write(f"**Predicted Price**: ${price:.2f}")

# Add some style and animations
st.markdown(
    """
    <style>
    body {
        background-color: #1c1c1c;
        color: #f5f5f5;
    }
    .css-18e3th9 {
        background-color: #1c1c1c;
    }
    .css-1d391kg {
        background-color: #1c1c1c;
    }
    .stButton>button {
        color: #f5f5f5;
        background-color: #4CAF50;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


