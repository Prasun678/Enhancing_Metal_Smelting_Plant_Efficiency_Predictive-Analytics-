import streamlit as st
import pandas as pd
import mysql.connector
import pickle
import random

# Load the models
with open('E:\\Internship\\MILES_PROJECT_WEBPAGE\\regressor4.pkl', 'rb') as file:
    regressor = pickle.load(file)
with open('E:\\Internship\\MILES_PROJECT_WEBPAGE\\classifier4.pkl', 'rb') as file:
    classifier = pickle.load(file)

# Function to establish a connection to the MySQL database
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Prasun@678",
        database="bronze2"
    )

# Function to create the table in the MySQL database
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        ID VARCHAR(255) PRIMARY KEY,
        date DATE,
        customer INT,
        quantity_tons FLOAT,
        thickness FLOAT,
        width FLOAT,
        country INT,
        item_type VARCHAR(255),
        application INT,
        temperature FLOAT,
        pressure FLOAT,
        status VARCHAR(255),
        price FLOAT
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Function to upload data from a CSV file to the MySQL database
@st.cache_data
def upload_data(file_path):
    df = pd.read_csv(file_path)

    # Convert necessary columns to the appropriate formats
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['ID'] = df['ID'].astype(str)
    df['customer'] = df['customer'].astype(int)
    df['country'] = df['country'].astype(int)
    df['application'] = df['application'].astype(int)

    conn = create_connection()
    cursor = conn.cursor()

    # Drop existing data and insert new data
    cursor.execute("TRUNCATE TABLE orders;")
    for index, row in df.iterrows():
        sql = """
        INSERT INTO orders (ID, date, customer, quantity_tons, thickness, width, country, item_type, application, temperature, pressure, status, price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, tuple(row))

    conn.commit()
    cursor.close()
    conn.close()

# Query functions
def query_max_quantity_tons():
    conn = create_connection()
    query = """
    SELECT item_type, MAX(quantity_tons) AS max_quantity_tons
    FROM orders
    WHERE quantity_tons > 0  # Ensure valid quantities
    GROUP BY item_type;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def query_highest_lowest_application():
    conn = create_connection()
    query = """
    SELECT application, AVG(quantity_tons) AS avg_order_quantity
    FROM orders
    WHERE quantity_tons > 0  # Ensure valid quantities
    GROUP BY application
    ORDER BY avg_order_quantity DESC;
    """
    df = pd.read_sql(query, conn)
    highest_app = df.iloc[0] if not df.empty else None
    lowest_app = df.iloc[-1] if len(df) > 1 else highest_app
    conn.close()
    return highest_app, lowest_app

def query_max_win_status_item_type():
    conn = create_connection()
    query = """
    SELECT item_type, COUNT(*) AS win_count
    FROM orders
    WHERE status = 'Won'
    GROUP BY item_type
    ORDER BY win_count DESC
    LIMIT 1;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def query_top_bottom_customers(n):
    conn = create_connection()
    query_top = f"""
    SELECT customer, SUM(price) AS revenue
    FROM orders
    GROUP BY customer
    ORDER BY revenue DESC
    LIMIT {n};
    """
    query_bottom = f"""
    SELECT customer, SUM(price) AS revenue
    FROM orders
    GROUP BY customer
    ORDER BY revenue ASC
    LIMIT {n};
    """
    df_top = pd.read_sql(query_top, conn)
    df_bottom = pd.read_sql(query_bottom, conn)
    # Sort bottom customers by revenue in descending order for display
    df_bottom = df_bottom.sort_values('revenue', ascending=False)
    conn.close()
    return df_top, df_bottom

def query_country_wise_sum_sales():
    conn = create_connection()
    query = """
    SELECT country, SUM(price) AS total_sales
    FROM orders
    GROUP BY country;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Define the function to make predictions
def predict_status(features):
    prediction = classifier.predict([features])
    return "Won" if prediction[0] == 1 else "Lost"

def predict_price(features):
    prediction = regressor.predict([features])
    return prediction[0]

# Streamlit app
st.set_page_config(page_title="Order Data Analysis & Prediction", page_icon=":bar_chart:", layout="wide")





# Custom CSS, Google Fonts import, and title styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Josefin+Sans&display=swap');
    
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1523655391416-89d6c3f81f4c?q=80&w=3538&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    .stApp::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.3);  /* White overlay with 30% opacity */
        backdrop-filter: blur(3px);  /* This adds the blur effect */
        z-index: 0;
    }
    
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }
    
   
    
    /* Change all text colors to #D4D4CE except for main headers */
    body, .stTextInput > div > div > input, .stSelectbox, .stMultiSelect, .stSlider, .stDateInput {
        color: #D4D4CE !important;
    }
    
    /* Preserve main page header colors */
    .main h1, .main h2, .main h3, .main p {
        color: #023246 !important;
    }
    
    
    
    
    
    /* New Sidebar styles with gradient overlay for glass effect */
    [data-testid="stSidebar"] {
        position: relative;
        background: transparent !important;
        overflow: hidden;
    }

    [data-testid="stSidebar"]::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(to bottom right, rgba(1, 25, 44, 1), rgba(1, 25, 44, 0.8));
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        z-index: -1;
    }

    [data-testid="stSidebar"] > div:first-child {
        background-color: transparent !important;
    }

    [data-testid="stSidebar"] .sidebar-content {
        background-color: transparent !important;
    }

    [data-testid="stSidebar"] * {
        color: #D4D4CE !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        background-color: rgba(1, 25, 44, 0.6) !important;
        color: #D4D4CE !important;
        border: 1px solid rgba(246, 246, 246, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(1, 25, 44, 0.8) !important;
        border-color: rgba(246, 246, 246, 0.5) !important;
    }

    /* Ensure content in sidebar is readable */
    [data-testid="stSidebar"] .stTextInput > div > div > input,
    [data-testid="stSidebar"] .stSelectbox > div > div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] .stSelectbox > div > div[data-baseweb="select"] > div > div {
        background-color: rgba(1, 25, 44, 0.4) !important;
        color: #D4D4CE !important;
        border-color: rgba(246, 246, 246, 0.3) !important;
    }

    /* Additional styles to ensure sidebar elements are visible */
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stNumberInput label {
        color: #D4D4CE !important;
    }


   
    
    
    
    
    
    /* Force dropdown text color */
    .stSelectbox > div > div[data-baseweb="select"] > div,
    .stSelectbox > div > div[data-baseweb="select"] > div > div,
    .stMultiSelect > div > div[data-baseweb="select"] > div,
    .stMultiSelect > div > div[data-baseweb="select"] > div > div {
        color: #D4D4CE !important;
    }
    
    /* Force input text color */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        color: #D4D4CE !important;
    }
    
    /* Sidebar styles */
    [data-testid="stSidebar"] {
        background-color: #01192C;
    }
    
    [data-testid="stSidebar"] * {
        color: #D4D4CE !important;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background-color: #01192C !important;
        color: #D4D4CE !important;
        border: 2px solid #F6F6F6 !important;
    }
    
    /* Additional styles to ensure all text is #D4D4CE except main headers */
    .stText, .stDataFrame, .stMarkdown:not(.main h1):not(.main h2):not(.main h3):not(.main p) {
        color: #D4D4CE !important;
    }
    
    .stSlider label, .stSlider [data-baseweb="tooltip"],
    .stDateInput label, .stDateInput input {
        color: #D4D4CE !important;
    }
    
    /* Ensure dropdown options are visible */
    .stSelectbox ul li, .stMultiSelect ul li {
        color: #D4D4CE !important;
        background-color: #01192C !important;
    }
    
    /* Custom class for main content that should retain #023246 color */
    .main-content {
        color: #023246 !important;
    }
    
    /* Increase size of 'Prediction Result' subheader */
    .prediction-result-header {
        font-size: 40px !important;
        font-weight: bold !important;
        margin-bottom: 15px !important;
    }

    /* Increase size of the prediction result text */
    .prediction-result {
        font-size: 40px !important;
        font-weight: bold !important;
    }
    
    .big-font {
    font-size:20px !important;
    font-weight: bold;
    }
    
    </style>
""", unsafe_allow_html=True)




# Set the file path of the input dataset
file_path = 'E:\\Internship\\MILES_PROJECT_WEBPAGE\\datasql.csv'

# Create the table and upload the dataset
with st.spinner('Creating table and uploading data...'):
    create_table()
    upload_data(file_path)

# Sidebar buttons for sections
st.sidebar.markdown('<p style="color: #D4D4CE; font-weight: bold; font-size: 1.5em;">Sections</p>', unsafe_allow_html=True)

if st.sidebar.button("Home"):
    st.session_state.section = "Select Section"
if st.sidebar.button("SQL Queries"):
    st.session_state.section = "SQL Queries"
if st.sidebar.button("Order Prediction"):
    st.session_state.section = "Order Prediction"
if st.sidebar.button("Dashboard"):
    st.session_state.section = "Dashboard"

section = st.session_state.get("section", "Select Section")

if section == "Select Section":
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Josefin+Sans&display=swap');

        .home-content {
            font-family: 'Josefin Sans', sans-serif;
            font-size: 24px;
            line-height: 1.6;
            color: #023246;
            max-width: 1000px;
            margin: 0 auto;
            padding-top: 10px; /* Reduced top padding */
            padding-bottom: 10px; /* Reduced bottom padding */
        }

        .home-content h1 {
            font-size: 70px;
            margin-bottom: 20px; /* Reduced bottom margin */
        }

        .home-content h2 {
            font-size: 40px;
            margin-top: 20px; /* Reduced top margin */
            margin-bottom: 10px; /* Reduced bottom margin */
        }

        .home-content ul {
            list-style-type: none;
            padding-left: 0;
        }

        .home-content li {
            font-size: 24px;  /* Increased font size */
            margin-bottom: 10px; /* Reduced bottom margin */
        }

        .home-content p {
            font-size: 24px;  /* Increased font size */
            margin-bottom: 10px; /* Reduced bottom margin */
        }
        </style>

        <div class="home-content">
        <h1>Bronze Order Prediction</h1>

        <p>Welcome to our Bronze Metal Order Prediction platform. This tool leverages machine learning to predict order statuses and prices for bronze metal products.</p>

        <h2>Key Features:</h2>
        <ul>
        <li>• Prediction using Random Forest models</li>
        <li>• Interactive dashboard visualizing dataset insights</li>
        <li>• SQL queries for data analysis</li>
        </ul>

        <h2>How It Works:</h2>
        <p>Our system uses Random Forest Classifier for status prediction and Random Forest Regressor for price estimation. These models analyze various factors to provide accurate predictions for bronze metal orders.</p>

        <p>Explore the different sections to discover insights, make predictions, and visualize data from our bronze metal dataset.</p>
        </div>
    """, unsafe_allow_html=True)






# Update the SQL Queries section
# Update the SQL Queries section
elif section == "SQL Queries":
    st.header("SQL Queries")
    
    # Add custom CSS for consistent text color and reduced input width
    st.markdown("""
    <style>
    .big-font {
        font-size: 20px !important;
        font-weight: bold;
        color: #023246 !important;
    }
    .stNumberInput > div > div > input {
        width: 80px !important;
    }
    .dataframe {
        color: #023246 !important;
    }
    .stDataFrame {
        color: #023246 !important;
    }
    div[data-testid="stTable"] table {
        color: #023246 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create two columns
    col1, col2 = st.columns(2)
    
    with col1:
        # Query 1
        st.markdown('<h3 class="subheader" style="color: #023246;">• Maximum Quantity-Tons Ordered in Each Item-Type Category</h3>', unsafe_allow_html=True)
        df_max_quantity_tons = query_max_quantity_tons()
        st.dataframe(df_max_quantity_tons)
        
        # Query 2
        st.markdown('<h3 class="subheader" style="color: #023246;">• Highest and Lowest Average Order Quantity by Application</h3>', unsafe_allow_html=True)
        highest_app, lowest_app = query_highest_lowest_application()
        if highest_app is not None:
            st.markdown(f'<p class="big-font">• Highest Average Order Quantity:<br>Application {highest_app["application"]} with Quantity {highest_app["avg_order_quantity"]:.2f}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-font">• Lowest Average Order Quantity:<br>Application {lowest_app["application"]} with Quantity {lowest_app["avg_order_quantity"]:.2f}</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="big-font">No data available.</p>', unsafe_allow_html=True)
        
        # Query 3
        st.markdown('<h3 class="subheader" style="color: #023246;">• Item Type with the Maximum Number of Win Status</h3>', unsafe_allow_html=True)
        df_max_win_status_item_type = query_max_win_status_item_type()
        if not df_max_win_status_item_type.empty:
            st.markdown(f'<p class="big-font">Item Type: {df_max_win_status_item_type["item_type"].values[0]}<br>Win Count: {df_max_win_status_item_type["win_count"].values[0]}</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="big-font">No data available.</p>', unsafe_allow_html=True)
    
    with col2:
        # Query 4
        st.markdown('<h3 class="subheader" style="color: #023246;">• Top and Bottom N Customers by Revenue</h3>', unsafe_allow_html=True)
        n = st.number_input("N:", min_value=1, value=5, step=1)
        df_top_customers, df_bottom_customers = query_top_bottom_customers(n)
        
        # Create two sub-columns for top and bottom customers
        subcol1, subcol2 = st.columns(2)
        
        with subcol1:
            st.markdown('<h4 style="color: #023246;">Top Customers</h4>', unsafe_allow_html=True)
            st.dataframe(df_top_customers)
        
        with subcol2:
            st.markdown('<h4 style="color: #023246;">Bottom Customers</h4>', unsafe_allow_html=True)
            st.dataframe(df_bottom_customers)
        
        # Query 5
        st.markdown('<h3 class="subheader" style="color: #023246;">• Country-Wise Sum of Sales</h3>', unsafe_allow_html=True)
        df_country_wise_sum_sales = query_country_wise_sum_sales()
        st.dataframe(df_country_wise_sum_sales)

elif section == "Order Prediction":
    st.header("Order Prediction")
    
    # Create two columns
    col1, col2 = st.columns([2, 1])  # 2:1 ratio, adjust as needed

    with col1:
        # Display the dataset
        dataset_path = 'E:\\Internship\\MILES_PROJECT_WEBPAGE\\datafetch.csv'  # Replace with your actual dataset path
        try:
            df = pd.read_csv(dataset_path)
            st.subheader("Dataset")
            st.dataframe(df, height=800)  # Display dataframe in Streamlit
        except FileNotFoundError:
            st.error(f"Error: Dataset file not found.")

    with col2:
        # Prediction Result
        st.markdown('<p class="prediction-result-header">Prediction Result</p>', unsafe_allow_html=True)
        prediction_placeholder = st.empty()  # Create a placeholder for the prediction result
        
    def load_input_data():
        path = 'E:\\Internship\\MILES_PROJECT_WEBPAGE\\datafetch.csv'
        return pd.read_csv(path)
    # Load the dataset
    input_data = load_input_data()
    # User interface for order prediction (keep this in the sidebar)
    st.sidebar.header("Input Parameters")
    
    # User interface for order prediction
    # Function to fill input fields with random row data
    def fill_random_row():
        if input_data is not None:
            random_row = input_data.sample(1).iloc[0]
            st.session_state.day = random_row['day']
            st.session_state.month = random_row['month']
            st.session_state.year = random_row['year']
            st.session_state.quantity_tons = random_row['quantity_tons']
            st.session_state.thickness = random_row['thickness']
            st.session_state.width = random_row['width']
            st.session_state.country = random_row['country']
            st.session_state.item_type = random_row['item_type']
            st.session_state.application = random_row['application']
            st.session_state.temperature = random_row['temperature']
            st.session_state.pressure = random_row['pressure']
            # Store actual price and status
            st.session_state.actual_price = random_row['price']
            st.session_state.actual_status = random_row['status']

    if st.sidebar.button("Fill Random Row"):
        fill_random_row()
        
    day = st.sidebar.number_input("Day", min_value=1, max_value=31, value=1, step=1, key='day')    
    month = st.sidebar.number_input("Month", min_value=1, max_value=12, value=1, step=1, key='month')
    year = st.sidebar.number_input("Year", min_value=2000, value=2020, step=1, key='year')
    quantity_tons = st.sidebar.number_input("Quantity (tons)", format="%.10f", min_value=0.0, value=0.0, step=0.0000000001, key='quantity_tons')
    thickness = st.sidebar.number_input("Thickness", format="%.10f", min_value=0.0, value=0.0, step=0.0000000001, key='thickness')
    width = st.sidebar.number_input("Width", format="%.10f", min_value=0.0, value=0.0, step=0.0000000001, key='width')
    country = st.sidebar.number_input("Country", min_value=0, value=0, step=1, key='country')
    item_type = st.sidebar.selectbox("Item Type", ["BXO", "IPL", "NXO", "Others", "PST", "SLAWR", "WI"], key='item_type')
    item_type_encoded = {"BXO": 0, "IPL": 1, "NXO": 2, "Others": 3, "PST": 4, "SLAWR": 5, "WI": 6}[item_type]
    application = st.sidebar.number_input("Application", min_value=0, value=0, step=1, key='application')
    temperature = st.sidebar.number_input("Temperature", format="%.10f", min_value=0.0, value=0.0, step=0.0000000001, key='temperature')
    pressure = st.sidebar.number_input("Pressure", format="%.10f", min_value=0.0, value=0.0, step=0.0000000001, key='pressure')

    # Assuming your model uses these features for prediction
    features = [quantity_tons, thickness, width, country, application, temperature, pressure, item_type_encoded, year, month, day]

    if st.sidebar.button("Predict"):
        with st.spinner('Making prediction...'):
            features = [quantity_tons, thickness, width, country, application, temperature, pressure, item_type_encoded, year, month, day]
            status = predict_status(features)
            price = predict_price(features)
            with col2:
                actual_price = st.session_state.get('actual_price', 'N/A')
                actual_status = st.session_state.get('actual_status', 'N/A')
                
                # Convert actual_status to 'Won' or 'Lost'
                if actual_status != 'N/A':
                    actual_status_text = 'Won' if actual_status == 1 else 'Lost'
                else:
                    actual_status_text = 'N/A'
                
                prediction_placeholder.markdown(
                    f'<p class="prediction-result">'
                    f'Predicted Status: {status}<br>'
                    f'Actual Status: {actual_status_text}<br>'
                    f'Predicted Price: ${price:.2f}<br>'
                    f'Actual Price: ${actual_price if actual_price != "N/A" else "N/A"}'
                    f'</p>', 
                    unsafe_allow_html=True
                )

elif section == "Dashboard":
    st.subheader("Dashboard")
    st.markdown(
        """
        <iframe title="PowerBI Report" width="1500" height="860" src="https://app.powerbi.com/view?r=eyJrIjoiN2YyYmEyMzctODM4ZS00MDkxLWI1Y2UtYTM3Y2U3NmM5MWIzIiwidCI6ImUxNGU3M2ViLTUyNTEtNDM4OC04ZDY3LThmOWYyZTJkNWE0NiIsImMiOjEwfQ%3D%3D" frameborder="0" allowFullScreen="true"></iframe>
        """,
        unsafe_allow_html=True
    )

