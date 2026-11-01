import pandas as pd
import streamlit as st
from data_processing import get_date_columns, load_data, get_column_types, get_visualization_options

st.title("Healthcare Visualization")

df = st.session_state.get("cleaned_df")
if df is None:
    st.info("Please upload and clean the data first.")
    st.stop()
numerical_columns, categorical_columns = get_column_types(df)
date_columns = get_date_columns(df)
options = get_visualization_options(df)

st.subheader("Available Data")

st .write("Numerical Columns:")
st.write(numerical_columns)

st.write("Categorical Columns:")
st.write(categorical_columns)

st.subheader("Visualization")
st.write(options)

st.subheader("Create a Chart")

if categorical_columns:
    selected_column = st.selectbox(
        "Select a category column",
        categorical_columns)

    chart_data = df[selected_column].value_counts()

    st.bar_chart(chart_data)

# NUMERICAL VISUALIZATION
if numerical_columns:
    selected_column = st.selectbox(
        "Select a numerical column",
        numerical_columns)

    st.header("Numerical Distribution")
    st.bar_chart(df[selected_column].value_counts().sort_index())

st.subheader("Numerical vs Category Comparison")

if numerical_columns and categorical_columns:

    selected_number = st.selectbox(
        "Select numerical column",
        numerical_columns,
        key="comparison_number"
    )

    selected_category = st.selectbox(
        "Select category column",
        categorical_columns,
        key="comparison_category"
    )

    comparison_data = df.groupby(selected_category)[selected_number].mean()

    st.bar_chart(comparison_data)

# TIME AND DATE VISUALIZATION
st.header("Time and Date Visualization")

if date_columns and numerical_columns:

    selected_date = st.selectbox(
        "Select a date column",
        date_columns,
        key="date_column")
    selected_numerical = st.selectbox(
        "select a numerical column",
        numerical_columns,
        key="date_number"
    )

    time_date = df[[selected_date, selected_numerical]].copy()
    time_date[selected_date] = pd.to_datetime(
        time_date[selected_date], errors="coerce"
    )

    time_date = time_date.dropna(
        subset=[selected_date, selected_numerical]
    )

    if not time_date.empty:
        time_date = time_date.sort_values(selected_date)
        time_date = time_date.set_index(selected_date)

        st.subheader("Numerical Trend Over Time")
        st.line_chart(time_date[selected_numerical])
    else:
        st.info("No valid date and numerical values available to plot.")
else:
    st.info("Date and numerical columns are required for a time-based chart.")
