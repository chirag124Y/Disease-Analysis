
import streamlit as st
import os
import tempfile
import sys
from data_processing import run_data_pipeline, save_data_to_mysql

st.title("Data Processing")
st.write("Upload a healthcare CSV file to start processing.")

uploaded_file = st.file_uploader("Upload Healthcare CSV",type=["csv"])

if uploaded_file is not None:
    st.success("CSV uploaded successfully!")
    st.write("File Name:", uploaded_file.name)

    if st.button("Process Dataset"):
        try:
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            if project_dir not in sys.path:
                sys.path.insert(0, project_dir)

            with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                input_path = temp_file.name

            with st.spinner("Processing dataset..."):
                cleaned_df = run_data_pipeline(input_path)

            st.session_state["cleaned_df"] = cleaned_df
            st.session_state["data_processed"] = True
            save_data_to_mysql(cleaned_df)
            st.success("Dataset saved to MySQL successfully!")

            st.success("Dataset processed successfully!")
            st.write("Rows:", len(cleaned_df))
            st.write("Columns:", len(cleaned_df.columns))
            st.dataframe(cleaned_df.head())

        except Exception as e:
            st.error(f"Processing failed: {e}")

        finally:
            if "input_path" in locals() and os.path.exists(input_path):
                os.remove(input_path)
