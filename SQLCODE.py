import streamlit as st
import mysql.connector
import pandas as pd

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
    SELECT item_type, SUM(status = 'Win') AS win_count
    FROM orders
    GROUP BY item_type
    ORDER BY win_count DESC
    LIMIT 1;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def query_top_bottom_customers(n):
    conn = create_connection()
    query = f"""
    (SELECT customer, SUM(price) AS revenue
     FROM orders
     GROUP BY customer
     ORDER BY revenue DESC
     LIMIT {n}) 
    UNION 
    (SELECT customer, SUM(price) AS revenue
     FROM orders
     GROUP BY customer
     ORDER BY revenue ASC
     LIMIT {n});
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

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

# Streamlit app
st.set_page_config(page_title="Order Data Analysis", page_icon=":bar_chart:", layout="wide")



st.title("Order Data Analysis")

# Upload the dataset
file_path = '/Users/raushankumar/Documents/sql/cleaned_data_powerbi.csv'

# Create the table and upload the dataset
create_table()
upload_data(file_path)

# Select a query to run
st.sidebar.header("Select a Query")
option = st.sidebar.selectbox(
    "Choose a query:",
    ["Select Query",
     "Maximum Quantity-Tons by Item Type",
     "Highest and Lowest Average Order Quantity by Application",
     "Item Type with the Maximum Number of 'Win' Status",
     "Top and Bottom N Customers by Revenue",
     "Country-Wise Sum of Sales"
    ]
)

if option == "Select Query":
    st.write("Please select a query from the sidebar.")

elif option == "Maximum Quantity-Tons by Item Type":
    st.subheader("Maximum Quantity-Tons Ordered in Each Item-Type Category")
    df = query_max_quantity_tons()
    st.dataframe(df)

elif option == "Highest and Lowest Average Order Quantity by Application":
    st.subheader("Highest and Lowest Average Order Quantity by Application")
    highest_app, lowest_app = query_highest_lowest_application()
    if highest_app is not None:
        st.write(f"Highest Average Order Quantity: Application {highest_app['application']} with Quantity {highest_app['avg_order_quantity']:.2f}")
        st.write(f"Lowest Average Order Quantity: Application {lowest_app['application']} with Quantity {lowest_app['avg_order_quantity']:.2f}")
    else:
        st.write("No data available.")

elif option == "Item Type with the Maximum Number of 'Win' Status":
    st.subheader("Item Type with the Maximum Number of 'Win' Status")
    df = query_max_win_status_item_type()
    st.dataframe(df)

elif option == "Top and Bottom N Customers by Revenue":
    st.subheader("Top and Bottom N Customers by Revenue")
    n = st.number_input("Select the value of N:", min_value=1, value=5, step=1)
    df = query_top_bottom_customers(n)
    st.dataframe(df)

elif option == "Country-Wise Sum of Sales":
    st.subheader("Country-Wise Sum of Sales")
    df = query_country_wise_sum_sales()
    st.dataframe(df)
