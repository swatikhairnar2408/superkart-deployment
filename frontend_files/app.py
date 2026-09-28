# Streamlit UI for the SuperKart sales forecasting API
import os
import requests
import pandas as pd
import streamlit as st

# Backend URL: inside the Docker network the Flask container is reachable by its name
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860")

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒")
st.title("SuperKart Sales Forecasting")
st.write("Predict the total sales revenue of a product in a SuperKart store.")

# ---------------- Online prediction ----------------
st.subheader("Online prediction")

col1, col2 = st.columns(2)
with col1:
    product_weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66, step=0.1)
    product_sugar = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    product_area = st.number_input("Product Allocated Area (ratio)", min_value=0.0, max_value=1.0,
                                   value=0.027, step=0.001, format="%.3f")
    product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=500.0, value=117.08, step=0.5)
    product_code = st.selectbox("Product Id prefix", ["FD", "NC", "DR"],
                                help="FD = Food, NC = Non-consumable, DR = Drinks")
with col2:
    product_category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])
    store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
    store_city = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
    store_type = st.selectbox("Store Type", ["Departmental Store", "Supermarket Type1",
                                             "Supermarket Type2", "Food Mart"])
    store_age = st.number_input("Store Age (years)", min_value=0, max_value=100, value=16, step=1)

payload = {
    "Product_Weight": product_weight,
    "Product_Sugar_Content": product_sugar,
    "Product_Allocated_Area": product_area,
    "Product_MRP": product_mrp,
    "Store_Size": store_size,
    "Store_Location_City_Type": store_city,
    "Store_Type": store_type,
    "Product_Id_char": product_code,
    "Store_Age_Years": int(store_age),
    "Product_Type_Category": product_category,
}

if st.button("Predict", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()["Predicted Sales"]
            st.success(f"Predicted Product Store Sales Total: {result:,.2f}")
        else:
            st.error(f"API error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")

# ---------------- Batch prediction ----------------
st.subheader("Batch prediction")
uploaded_file = st.file_uploader("Upload a CSV file with the model's feature columns", type=["csv"])

if uploaded_file is not None and st.button("Predict batch"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predictbatch",
                                 files={"file": uploaded_file.getvalue()}, timeout=60)
        if response.status_code == 200:
            preds = response.json()
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file)
            df["Predicted_Sales"] = [preds[str(i)] for i in df.index]
            st.dataframe(df)
            st.download_button("Download predictions", df.to_csv(index=False),
                               file_name="superkart_predictions.csv", mime="text/csv")
        else:
            st.error(f"API error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")
