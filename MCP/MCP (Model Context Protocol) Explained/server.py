import sqlite3
import argparse
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server with a custom name
database_server = FastMCP('employee-database-service')

class DatabaseManager:
    """Manages SQLite database operations for employee records."""
    
    def __init__(self, db_path='employees.db'):
        self.db_path = db_path
        self._setup_database()
    
    def _setup_database(self):
        """Initialize the database with the employees table."""
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    years_of_age INTEGER NOT NULL,
                    job_title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            connection.commit()
    
    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)

# Create database manager instance
db_manager = DatabaseManager()

@database_server.tool()
def insert_employee_record(sql_statement: str) -> bool:
    """Insert a new employee record into the database using SQL.

    Args:
        sql_statement (str): SQL INSERT statement in the following format:
            INSERT INTO employees (full_name, years_of_age, job_title)
            VALUES ('Jane Doe', 28, 'Software Developer')
        
    Database Schema:
        - full_name: Text field (required) - Employee's complete name
        - years_of_age: Integer field (required) - Employee's age in years  
        - job_title: Text field (required) - Employee's current position
        - employee_id: Auto-incremented primary key
        - created_at: Timestamp automatically set on record creation
    
    Returns:
        bool: True if the employee record was successfully inserted, False otherwise
    
    Example Usage:
        >>> sql_cmd = '''
        ... INSERT INTO employees (full_name, years_of_age, job_title)
        ... VALUES ('Sarah Johnson', 32, 'Product Manager')
        ... '''
        >>> insert_employee_record(sql_cmd)
        True
    """
    try:
        with db_manager.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql_statement)
            connection.commit()
            return True
    except sqlite3.Error as database_error:
        print(f"Database insertion failed: {database_error}")
        return False

@database_server.tool()
def fetch_employee_data(sql_query: str = "SELECT * FROM employees") -> list:
    """Retrieve employee records from the database using SQL queries.

    Args:
        sql_query (str, optional): SQL SELECT statement for data retrieval. 
            Defaults to "SELECT * FROM employees".
            
            Example queries:
            - "SELECT * FROM employees"
            - "SELECT full_name, job_title FROM employees WHERE years_of_age > 30"
            - "SELECT * FROM employees ORDER BY created_at DESC LIMIT 10"
            - "SELECT COUNT(*) FROM employees WHERE job_title LIKE '%Manager%'"
    
    Returns:
        list: Collection of tuples containing query results.
              Default query returns: (employee_id, full_name, years_of_age, job_title, created_at)
    
    Example Usage:
        >>> # Retrieve all employee records
        >>> fetch_employee_data()
        [(1, 'Jane Doe', 28, 'Software Developer', '2024-01-15 10:30:00'), 
         (2, 'John Smith', 35, 'Senior Engineer', '2024-01-16 09:15:00')]
        
        >>> # Custom query for specific data
        >>> fetch_employee_data("SELECT full_name, job_title FROM employees WHERE years_of_age < 35")
        [('Jane Doe', 'Software Developer'), ('Mike Wilson', 'Junior Developer')]
    """
    try:
        with db_manager.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql_query)
            return cursor.fetchall()
    except sqlite3.Error as database_error:
        print(f"Database query failed: {database_error}")
        return []



def start_server():
    """Initialize and start the MCP database server."""
    print("🚀 Launching Employee Database Server...")
    print("📋 Available operations: insert_employee_record, fetch_employee_data")
    
    # Configure command line arguments
    argument_parser = argparse.ArgumentParser(
        description="Employee Database MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    argument_parser.add_argument(
        "--connection_mode", 
        type=str, 
        default="sse", 
        choices=["sse", "stdio"],
        help="Server connection mode: 'sse' for HTTP Server-Sent Events or 'stdio' for standard input/output"
    )

    parsed_args = argument_parser.parse_args()
    
    # Launch the server with specified connection mode
    database_server.run(parsed_args.connection_mode)


if __name__ == "__main__":
    start_server()


# Alternative usage examples (commented out for production):
"""
Example operations that can be performed:

# Sample employee insertion
sample_insert = '''
INSERT INTO employees (full_name, years_of_age, job_title)
VALUES ('Michael Chen', 29, 'Data Scientist')
'''

# Execute insertion
if insert_employee_record(sample_insert):
    print("✅ Employee record added successfully")

# Retrieve all employee records
all_employees = fetch_employee_data()
print("👥 Current employee roster:")
for employee in all_employees:
    print(f"ID: {employee[0]}, Name: {employee[1]}, Age: {employee[2]}, Role: {employee[3]}")
"""