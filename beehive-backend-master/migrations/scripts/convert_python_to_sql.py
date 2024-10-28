import sys

def main():
    """
    This file converts any Python script to a format that can be copy-pasted into an SQL query to be added to the honeycombs.

    To use it, run:
        python convert_python_to_sql.py [[file_name]]
    where [[file_name]] is the name of your Python file.
    """
    for file_name in sys.argv[1:]:
        with open(file_name, 'r') as f:
            file_content = f.read()
            print(file_content.replace('\n', r'\\n').replace('\t', r'\\t').replace('"', r'\\"').replace("'", r"''"))

if __name__ == '__main__':
    main()
