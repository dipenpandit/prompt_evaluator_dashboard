import streamlit as st  
import requests
from config import settings

## Add New Prompt Project
def add_new_prompt():
    # Use session state to toggle form visibility
    if "show_form" not in st.session_state:
        st.session_state.show_form = False
    
    if st.button("Add New Prompt Project"):
        st.session_state.show_form = not st.session_state.show_form
    
    # Show form if toggle is True
    if st.session_state.show_form:
        with st.form("new_prompt_project_form", clear_on_submit=True):
            prompt_name = st.text_input("Prompt Project Name")
            prompt_version = st.text_input("Version")
            prompt_content = st.text_area("Prompt Content")
            submitted = st.form_submit_button("Create Prompt Project")

            if submitted:
                if not prompt_name or not prompt_version or not prompt_content:
                    st.error("Please fill in all fields.")
                else:
                    payload = {
                        "prompt_name": prompt_name,
                        "version": prompt_version,
                        "prompt_content": prompt_content
                    }
                    try:
                        response = requests.post(f"{settings.api_url}/prompts/", json=payload)
                        if response.status_code == 201:
                            st.success("Prompt Project created successfully!")
                            st.session_state.show_form = False  # Hide form after success
                            st.rerun()  # Refresh to show updated state
                        else:
                            st.error(f"Failed to create Prompt Project. Status code: {response.status_code}")
                            st.write(response.text)
                    except requests.exceptions.RequestException as e:
                        st.error(f"An error occurred: {e}")