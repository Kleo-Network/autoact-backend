# app/api/form.py
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.form import Form, CreateFormRequest
from app.mongodb import get_forms

from app.services.clean_html import clean_html
from app.services.gemini_prompt import get_gemini_response

router = APIRouter()
logger = logging.getLogger(__name__)

'''
mapping = {
    "querySelectorAll": "query selector for individual widgets for specific form"
}

Final Output of the JSON
[{
    "querySelectorInput": [".classNameOfInput / Identifier of Input"],
    "label": "Text for the Input"
},...]

mapping to final output,
 dom_element = document.querySelectorAll( mapping.querySelectorAll )
 result = []
 dom_element.forEach( (element) => {
    result.push({
        "label": element.innerText,
        "querySelectorInput": element.querySelectorAll("input")
    })
}

Send the Final Output of the JSON +
user_prompt + 
custom_command to gemini api

response from gemini should be in the json format, 
[{
    "label": "Text for the Input",
    "value": "Value of the Input"
}]

API response to extension should be in the format
[{ 
    querySelectorInput: "input querySelector", 
    label: "Text for the Input",
    value: "Value of the Input"
}] 
'''
@router.post("/{domain}", response_model=dict)
async def get_or_create_form(domain: str, dom: str, user_prompt: str, custom_command: str = None):
    """
    Get an existing form by domain or create it if not found.
    
    If form_request is provided, it will be used to create a new form when the domain is not found.
    If form_request is not provided and the domain is not found, returns a 404 error.
    """
    try:
        # Try to find the form first
        forms_collection = get_forms()
        existing_form = await forms_collection.find_one({"domain": domain})
        
        if existing_form:
            return JSONResponse(content=existing_form)
        
        
        #1. filter out the DOM html - remove styles, tags, inputs etc 
        #2. send the filtered DOM to gemini api along with the system prompt
        #3. parse the json response
        #4. run the querySelectorAll on the DOM to get the form elements, ensure all labels / inputs are captured 
        #5. create the form and save it to db
        #6. send the prompt and 
            return JSONResponse(status_code=201, content=result)
        else:
            # No form found and no data to create one
            raise HTTPException(status_code=404, detail=f"Form with domain '{domain}' not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing form request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process form request: {str(e)}")