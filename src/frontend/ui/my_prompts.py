import streamlit as st
from src.config import settings 
import requests
from src.frontend.ui.test_cases import test_case_dialog

def my_prompts():
    # Session state to track selected prompt
    if "selected_prompt" not in st.session_state:         
        st.session_state.selected_prompt = None

    response = requests.get(f"{settings.api_url}/prompts/")      

    if response.status_code != 200:
        st.error("Failed to fetch prompts")
        return 
    
    prompts = response.json()

    # Render prompts as clickable buttons
    for prompt in prompts:
        with st.expander(f"{prompt['prompt_name']} (v: {prompt['version_number']})", expanded=False):
            st.write(prompt['prompt_content'])
            if st.button("Edit Prompt", key=prompt['prompt_id']):
                st.session_state.selected_prompt = prompt   
                selected = st.session_state.selected_prompt
                with st.form(key="Edit Prompt", clear_on_submit=True):
                    new_content = st.text_area("Prompt Content", value=selected['prompt_content'])
                    submit = st.form_submit_button("Update Prompt")
                    if submit:
                        if new_content.strip() == "":
                            st.error("Prompt content cannot be empty.")
                        else:
                            # update prompt via API
                            pass
            
            if st.button("Test Cases", key=f"add_{prompt['prompt_id']}"):
                st.session_state.selected_prompt = prompt   
                selected = st.session_state.selected_prompt
                test_case_dialog()
                


