import sys

def check_libraries():
    required_libs = ['numpy', 'pyopenms', 'streamlit', 'plotly', 'matplotlib', 'pandas', 'psycopg2', 'polars', 'sqlalchemy', 'pymysql', 'scipy', 'pyteomics']
    missing = []
    
    for lib in required_libs:
        try:
            __import__(lib)
        except ImportError:
            missing.append(lib)
    
    if missing:
        print(f"Missing libraries: {', '.join(missing)}")
        sys.exit(1)
    else:
        print("All required libraries are installed.")

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    check_libraries()