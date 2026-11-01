import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def run_notebook(notebook_path, parameters=None):
    with open(notebook_path, 'r', encoding='utf-8') as file:
        notebook = nbformat.read(file, as_version=4)
    if parameters:
        parameter_code = "\n".join([f"{key} = {value!r}" for key, value in parameters.items()])
        notebook.cells.insert(0, nbformat.v4.new_code_cell(parameter_code))
    
    executor = ExecutePreprocessor(
        timeout=600,
        kernel_name="python3"
    )

    executor.preprocess(
        notebook,
        {"metadata": {"path": os.path.dirname(notebook_path)}}
    )


def run_data_pipeline(uploaded_file_path):
    notebook_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "02_notebook"
    )

    uploaded_file_path = os.path.abspath(uploaded_file_path)

    import tempfile

    with tempfile.TemporaryDirectory() as temp:
        cleaned_file = os.path.join(temp, "cleaned.csv")

        run_notebook(
            os.path.join(notebook_dir, "01_data_inspection.ipynb"),
            {"input_file_path": uploaded_file_path}
        )

        run_notebook(
            os.path.join(notebook_dir, "02_data_cleaning.ipynb"),
            {
                "input_file_path": uploaded_file_path,
                "output_file_path": cleaned_file
            }
        )

        run_notebook(
            os.path.join(notebook_dir, "03_data_analysis.ipynb"),
            {"input_file_path": cleaned_file}
        )

        return pd.read_csv(cleaned_file)


def connect_to_mysql():
    connection = mysql.connector.connect(
        host = "localhost",
        user ="root",
        password = os.getenv("MYSQL_PASSWORD"),
        database="healthcare_data_analysis"
    )
    return connection

def test_mysql_connection():
    connection = connect_to_mysql()

    if connection.is_connected():
        print("MySQL connected successfully!")

    connection.close()

def load_data(file_path):
    df = pd.read_csv(file_path)

    print("Dataset loaded successfully!")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    return df


def save_data_to_mysql(df):
    original_types = df.dtypes
    df = df.astype(object).where(pd.notna(df), None)

    connection = connect_to_mysql()
    cursor = connection.cursor()

    try:
        cursor.execute("DROP TABLE IF EXISTS healthcare_data")

        columns = []

        for column in df.columns:
            if pd.api.types.is_numeric_dtype(original_types[column]):
                data_type = "DOUBLE"
            else:
                data_type = "TEXT"

            columns.append(f"`{column}` {data_type}")

        create_table = f"""
        CREATE TABLE healthcare_data (
            {", ".join(columns)}
        )
        """
        cursor.execute(create_table)

        column_names = ", ".join(f"`{column}`" for column in df.columns)
        values = ", ".join(["%s"] * len(df.columns))

        insert_query = f"""
        INSERT INTO healthcare_data ({column_names})
        VALUES ({values})
        """

        data = [tuple(row) for row in df.itertuples(index=False, name=None)]
        print("SQL query:", insert_query)
        print("Column names:", df.columns.tolist())
        print("First row:", data[0] if data else "No data")

        cursor.executemany(insert_query, data)
        

        connection.commit()
        print("Data saved to MySQL successfully!")

    finally:
        cursor.close()
        connection.close()


    # FROM THIS CODE IT WILL CHECK IF THE CSV FILE HAS NUMERICAL OR CATEGORICAL DATA 

def get_column_types(df):
    numerical_columns = []
    categorical_columns = []

    for columns in df.columns:
        if pd.api.types.is_numeric_dtype(df[columns]):
            numerical_columns.append(columns)
        else:
            categorical_columns.append(columns)
    print("Numerical Columns:", numerical_columns)
    print("Categorical Columns:", categorical_columns)
    return numerical_columns, categorical_columns

def get_date_columns(df):
    date_columns = []

    for column in df.columns:

        # Column ka naam check karo
        column_name = str(column).lower()

        # Date ya time wale columns ko check karo
        if "date" in column_name or "time" in column_name:
                converted_dates = pd.to_datetime(df[column],errors="coerce")

            # Check karo ki valid date mili ya nahi
                if converted_dates.notna().any():
                    date_columns.append(column)

    print("Date Columns:", date_columns)

    return date_columns

def get_visualization_options(df):
    numerical_columns, categorical_columns = get_column_types(df)
    options = []
    if numerical_columns:
        options.append("Numerical Analysis")
    if categorical_columns:
        options.append("Categorical Analysis")
    if numerical_columns and categorical_columns:
        options.append("Comparison Chart")

    print("Visualization Options:")
    print(options) 
    return options

def load_cleaned_data():
    connection = connect_to_mysql()
    try:
        query = "SELECT * FROM healthcare_data"
        df = pd.read_sql(query, connection)
        print("Cleaned data loaded from MySQL successfully!")
        return df
    finally:
        connection.close()