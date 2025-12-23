from src.config import settings
import requests

def post_prompt(prompt_name, prompt_content):
    payload = {
        "prompt_name": prompt_name,
        "prompt_content": prompt_content
    }
    try:
        response = requests.post(f"{settings.api_url}/prompts/", json=payload)
        return response
    except requests.exceptions.RequestException as e:
        return None 
    
def post_ques_ans(ques, answer, prompt_id):
    payload = {
        "question": ques,
        "answer": answer,
        "prompt_id": prompt_id,
    }
    try:
        response = requests.post(f"{settings.api_url}/ques_ans/", json=payload)
        return response
    except requests.exceptions.RequestException as e:
        return None

def post_json(json_data: list, prompt_id):
    for item in json_data:
        ques = item.get("question")
        answer = item.get("answer")
        if ques and answer:
            post_ques_ans(ques, answer, prompt_id)
    


