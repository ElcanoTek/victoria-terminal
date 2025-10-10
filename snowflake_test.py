'''
Advanced Snowflake Query Example

This script demonstrates how to use the Snowflake connection to perform various
readonly operations on your data warehouse. It includes examples of:
- Basic SELECT queries
- Working with pandas DataFrames
- Handling query results
- Error handling best practices

Make sure to set your environment variables before running this script.
'''

import os
import pandas as pd
import snowflake.connector
from snowflake.connector import ProgrammingError

def get_snowflake_connection():
    """
    Establishes a connection to Snowflake using environment variables.
    """
    required_vars = ["SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_ACCOUNT", 
                    "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA"]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Missing environment variables: {', '.join(missing_vars)}")
        return None
    
    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            role=os.getenv("SNOWFLAKE_ROLE", "PUBLIC")
        )
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def list_tables(cursor):
    """
    Lists all tables in the current schema.
    """
    try:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"Found {len(tables)} tables in the current schema:")
        for table in tables:
            print(f"  - {table[1]}")  # Table name is typically in the second column
        return [table[1] for table in tables]
    except ProgrammingError as e:
        print(f"Error listing tables: {e}")
        return []

def describe_table(cursor, table_name):
    """
    Describes the structure of a specific table.
    """
    try:
        cursor.execute(f"DESCRIBE TABLE {table_name}")
        columns = cursor.fetchall()
        print(f"\nTable structure for {table_name}:")
        print("-" * 60)
        for col in columns:
            print(f"  {col[0]:<20} {col[1]:<15} {col[2]}")
    except ProgrammingError as e:
        print(f"Error describing table {table_name}: {e}")

def sample_data(cursor, table_name, limit=5):
    """
    Retrieves a sample of data from a table.
    """
    try:
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"\nSample data from {table_name} (first {limit} rows):")
            print("-" * 60)
            # Get column names
            column_names = [desc[0] for desc in cursor.description]
            print(" | ".join(column_names))
            print("-" * 60)
            for row in results:
                print(" | ".join(str(cell) for cell in row))
        else:
            print(f"No data found in {table_name}")
            
    except ProgrammingError as e:
        print(f"Error sampling data from {table_name}: {e}")

def query_to_pandas(cursor, query):
    """
    Executes a query and returns results as a pandas DataFrame.
    """
    try:
        cursor.execute(query)
        # Fetch all results
        results = cursor.fetchall()
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        # Create DataFrame
        df = pd.DataFrame(results, columns=columns)
        return df
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

def main():
    """
    Main function demonstrating various Snowflake operations.
    """
    print("Snowflake Advanced Query Example")
    print("=" * 50)
    
    conn = get_snowflake_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # List available tables
        tables = list_tables(cursor)
        
        if tables:
            # Describe the first table
            first_table = tables[0]
            describe_table(cursor, first_table)
            
            # Sample data from the first table
            sample_data(cursor, first_table)
            
            # Example: Convert query results to pandas DataFrame
            print(f"\nConverting query results to pandas DataFrame:")
            print("-" * 60)
            df = query_to_pandas(cursor, f"SELECT * FROM {first_table} LIMIT 10")
            if df is not None:
                print(f"DataFrame shape: {df.shape}")
                print(f"Column names: {list(df.columns)}")
                print("\nFirst few rows:")
                print(df.head())
        else:
            print("No tables found in the current schema.")
            print("You may need to adjust your database/schema settings or permissions.")
        
        # Example custom query
        print("\n" + "=" * 50)
        print("Example: Custom aggregation query")
        print("-" * 50)
        
        # This is a generic query that should work in most Snowflake environments
        custom_query = """
        SELECT 
            CURRENT_DATABASE() as database_name,
            CURRENT_SCHEMA() as schema_name,
            CURRENT_USER() as user_name,
            CURRENT_TIMESTAMP() as query_time
        """
        
        df_custom = query_to_pandas(cursor, custom_query)
        if df_custom is not None:
            print(df_custom)
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
        print("\nConnection closed.")

if __name__ == "__main__":
    main()
