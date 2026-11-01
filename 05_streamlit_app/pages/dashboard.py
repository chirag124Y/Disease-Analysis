import streamlit as st
from data_processing import load_cleaned_data, get_column_types
import data_processing 
st.write("Imported file:", data_processing.__file__)

st.title("Healthcare Data Dashboard")

df = load_cleaned_data()
numerical_columns, categorical_columns = get_column_types(df)

st.subheader("Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Records", len(df))
with col2:
    st.metric("Total Columns", len(df.columns))
with col3:
    st.metric("Numerical Columns", len(numerical_columns))
with col4:
    st.metric("Categorical Columns", len(categorical_columns))

st.subheader("Data Preview")

st.dataframe(
    df.head(10),
    use_container_width=True
)