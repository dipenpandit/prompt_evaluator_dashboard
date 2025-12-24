import streamlit as st 
import requests 
from src.config import settings

# @st.dialog("View Test Cases") 
def test_case_dialog(prompt_id):
    try: 
        response = requests.get(f"{settings.api_url}/test_cases/{prompt_id}")
        if response.status_code != 200:
            st.error("Failed to fetch test cases")
            return
        test_cases = response.json()
        for tc in test_cases:
            st.markdown(f"**Ques:** {tc['question']}")
            st.markdown(f"**Ans:** {tc['answer']}")
    except Exception as e:
        st.error(f"Error fetching test cases: {e}")

        
            
