import os
import google.generativeai as genai # type: ignore
from google.ai.generativelanguage_v1beta.types import content # type: ignore
from typing import  Dict, Any

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
generation_config_form_values ={
  "temperature": 0.6,
  "top_p": 0.45,
  "top_k": 70,
  "max_output_tokens": 1000,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    properties = {
      "label": content.Schema(
        type = content.Type.STRING,
      ),
      "value": content.Schema(
        type = content.Type.STRING,
      ),
    },
  ),
  "response_mime_type": "application/json",
}

generation_config_widget_detection = {
  "temperature": 0.6,
  "top_p": 0.45,
  "top_k": 40,
  "max_output_tokens": 100,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    properties = {
      "querySelectorAll": content.Schema(
        type = content.Type.STRING,
      ),
    },
  ),
  "response_mime_type": "application/json",
}

system_instruction_widget_detection = """
  The below prompts will have form elements in it. 
  This form will be split into multiple sections (divs/sections/spans/table rows/columns/ other html elements),
  your job is to give me the queryselector for each section containing the input / form input elements and label (question of the form),
  the queryselector you give should apply to all the form elements irrespective of lenght of the form or number of sections of the form. 
  The output should contain only the queryselector of each section and nothing else. 
"""

system_instruction_form_values = """
  You will be given a json object with the label and empty value field, 
  Return the same json with the value filled, use the following document information to fill that value. 
"""

def form_widget_detection(form_html: str):
  response = gemini_response(system_instruction=system_instruction_widget_detection,
                             message=form_html, 
                             config=generation_config_widget_detection, 
                             model="gemini-2.0-flash")
  return response

def fill_form_values(form_values: dict, history: list):
  response = gemini_response(system_instruction=system_instruction_form_values,
                             message=form_values,
                             history=history, 
                             config=generation_config_form_values, 
                             model="gemini-2.0-flash")
  return response

def gemini_response(system_instruction: str = "", message: str = "",  history: list = [], config: Dict[str, Any] = None  ,   model: str = "gemini-2.0-flash"):
  model = genai.GenerativeModel(
    model_name=model,
    generation_config=config,
    system_instruction=system_instruction,
  )
  chat_session = model.start_chat(history=history)
  try:
    response = chat_session.send_message(message)
    return response
  except Exception as e:
    return f"API Error: {e}"
    