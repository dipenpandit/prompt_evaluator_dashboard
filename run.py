import streamlit.web.cli as stcli
import sys

if __name__ == '__main__':
    sys.argv = ["streamlit", "run", "src/streamlit_app.py"]
    sys.exit(stcli.main())