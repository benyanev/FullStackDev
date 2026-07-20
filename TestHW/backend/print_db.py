import sys
from pathlib import Path

# Add the backend directory to Python path to import core config and database modules
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

# Ensure console stdout and stderr can output UTF-8 (e.g. Hebrew or Emojis) without crashing
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for older python versions
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from core.database import get_connection
except ImportError as e:
    print(f"Error importing database configuration: {e}")
    sys.exit(1)

def print_table(table_name):
    try:
        conn = get_connection()
        # Using dictionary=True to get columns as keys
        cursor = conn.cursor(dictionary=True)
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        return

    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        print(f"\n=== TABLE: {table_name} ({len(rows)} row(s)) ===")
        if not rows:
            print("(Empty table)")
            return
        
        # Calculate optimal width for each column
        keys = list(rows[0].keys())
        widths = {key: len(key) for key in keys}
        for row in rows:
            for key in keys:
                val_str = str(row[key]) if row[key] is not None else "NULL"
                widths[key] = max(widths[key], len(val_str))
        
        # Print header row
        header = " | ".join(f"{key.upper():<{widths[key]}}" for key in keys)
        print(header)
        print("-" * len(header))
        
        # Print each row
        for row in rows:
            row_str = " | ".join(
                f"{str(row[key]) if row[key] is not None else 'NULL':<{widths[key]}}" 
                for key in keys
            )
            print(row_str)
            
    except Exception as e:
        print(f"Error reading table {table_name}: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print_table("users")
    print_table("posts")
    print_table("sessions")
    print_table("follows")

