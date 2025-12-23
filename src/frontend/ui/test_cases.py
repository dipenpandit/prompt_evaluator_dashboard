import streamlit as st 
import requests 
from src.config import settings

@st.dialog("View Test Cases")
def test_case_dialog():
    try: 
        response = requests.get(f"{settings.api_url}/ques_ans/")
        if response.status_code != 200:
            st.error("Failed to fetch test cases")
            return
        test_cases = response.json()
        for tc in test_cases:
            st.markdown(f"**Q:** {tc['question']}")
            st.markdown(f"**A:** {tc['answer']}")
    except Exception as e:
        st.error(f"Error fetching test cases: {e}")

        
            
