import streamlit as st  
from frontend.add_prompt import add_new_prompt
from config import settings
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Prompt

API_URL = settings.api_url

st.set_page_config(page_title="Prompt Evaluator")

## --- DASHBOARD ---
st.title("Prompt Evaluator")

# Add New Prompt Project
add_new_prompt()

# My Prompt Projects 
st.write("My Prompt Projects")


