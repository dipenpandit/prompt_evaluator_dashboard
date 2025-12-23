import streamlit as st  
import requests
from src.config import settings
import json
from src.utils.post_req import post_ques_ans, post_json, post_prompt

def add_new_prompt():
    # Use session state to toggle form visibility
    if "show_form" not in st.session_state:
        st.session_state.show_form = False
    
    if st.button("Create Project"):
        st.session_state.show_form = not st.session_state.show_form
    
    # Show form if toggle is True
    if st.session_state.show_form:
        with st.form("new_prompt_project_form", clear_on_submit=True):
            prompt_name = st.text_input("Prompt Name")
            prompt_content = st.text_area("Prompt Content")

            st.divider()

            st.subheader("Add Test Cases (Select one method)")
            json_file = st.file_uploader(
                "Upload JSON in format {\"test_cases\": [{\"question\": \"...\", \"answer\": \"...\"}, ...]}",
                type=["json"]
            )

            st.markdown("**OR**")
            question = st.text_input("Question")
            answer = st.text_area("Answer")
            submitted = st.form_submit_button("Create Prompt Project")

            if submitted:
                # Required fields
                if not prompt_name or not prompt_content:
                    st.error("Both Prompt Name and Prompt Content are required.")

                # Either JSON OR (Question + Answer)
                elif not json_file and not (question and answer):
                    st.error("Provide either a JSON file OR both Question and Answer.")

                # Question + Answer provided
                else:
                    prompt_response = post_prompt(prompt_name, prompt_content)
                    
                    if prompt_response and prompt_response.status_code == 201:
                        prompt_id = prompt_response.json().get("prompt_id")
                        if json_file is not None:
                            try:
                                json_data = json.load(json_file).get("test_cases", [])
                                post_json(json_data, prompt_id)
                            except json.JSONDecodeError:
                                st.error("Invalid JSON file format.") 
                        if question and answer:
                            post_ques_ans(question, answer, prompt_id)

                        st.success("Prompt Project created successfully!")
                        
                        