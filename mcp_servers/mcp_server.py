import json
import sys
import io
import os
import pandas as pd
from contextlib import redirect_stdout
from pjrpc.server.integration import stdio
from snowflake import connector
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

def excel_query(file_path: str, sheet_name: str) -> str:
    """
    Queries an Excel file and returns the data as a string.
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df.to_string()
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except Exception as e:
        return f"An error occurred: {e}"

def python_exec(script: str) -> str:
    """
    Executes a Python script and returns the output.
    WARNING: This tool allows for arbitrary code execution and should be used with caution.
    """
    try:
        f = io.StringIO()
        with redirect_stdout(f):
            exec(script)
        return f.getvalue()
    except Exception as e:
        return f"An error occurred during script execution: {e}"

def snowflake_query(query: str) -> str:
    """
    Queries Snowflake and returns the data as a string.
    """
    try:
        engine = create_engine(URL(
            account=os.environ.get("SNOWFLAKE_ACCOUNT"),
            user=os.environ.get("SNOWFLAKE_USER"),
            password=os.environ.get("SNOWFLAKE_PASSWORD"),
            database=os.environ.get("SNOWFLAKE_DATABASE"),
            schema=os.environ.get("SNOWFLAKE_SCHEMA"),
            warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE"),
            role=os.environ.get("SNOWFLAKE_ROLE"),
        ))
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
        return df.to_string()
    except SQLAlchemyError as e:
        return f"Database error: {e}"
    except KeyError as e:
        return f"Missing Snowflake environment variable: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    server = stdio.Server()
    server.add_method("excel_query", excel_query)
    server.add_method("python_exec", python_exec)
    server.add_method("snowflake_query", snowflake_query)
    server.serve()
