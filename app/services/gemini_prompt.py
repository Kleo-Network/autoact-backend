import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
generation_config = {
  "temperature": 0.6,
  "top_p": 0.7,
  "top_k": 40,
  "max_output_tokens": 200,
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
  system_instruction="The below prompts will have form elements in it. This form will be split into multiple sections (divs/sections/spans/table rows/columns/ other html elements), your job is to give me the queryselector for each section containing the input / form input elements and label (question of the form), the queryselector you give should apply to all the form elements irrespective of lenght of the form or number of sections of the form. \n\nThe output should contain only the queryselector of each section and nothing else. ",
)

chat_session = model.start_chat(
  history=[
  ]
)

response = chat_session.send_message("INSERT_INPUT_HERE")

print(response.text)