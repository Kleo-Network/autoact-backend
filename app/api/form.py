# app/api/form.py
import logging
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.form import Form, CreateFormRequest
from app.mongodb import get_forms

from app.services.clean_html import clean_html
from app.services.gemini_prompt import form_widget_detection, extract_form_elements, fill_form_values

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
    Get an existing form by domain or create a new one if not found.
    
    Steps:
    1. Look for existing form in the database
    2. If not found, process the DOM to extract form elements
    3. Return the structured form data for the extension
    """
    try:
        # Try to find the form first in the database
        forms_collection = get_forms()
        existing_form = await forms_collection.find_one({"domain": domain})
        
        if existing_form:
            logger.info(f"Found existing form for domain: {domain}")
            return JSONResponse(content=existing_form)
        
        # Process the DOM if provided
        if dom:
            # Clean the DOM HTML
            cleaned_dom = clean_html(dom)
            
            # Step 1: Get the query selector for form widgets
            widget_detection_result = await form_widget_detection(cleaned_dom)
            
            # Parse the response to get the querySelectorAll
            try:
                if isinstance(widget_detection_result, str):
                    # Handle string response (potentially error or raw JSON)
                    widget_detection_data = json.loads(widget_detection_result)
                else:
                    # Handle object response from Gemini
                    widget_detection_data = widget_detection_result
                
                query_selector = widget_detection_data.get("querySelectorAll")
                
                if not query_selector:
                    logger.error("No query selector found in widget detection response")
                    raise HTTPException(status_code=400, detail="Could not detect form widgets")
                
                # Step 2: Extract form elements using the querySelectorAll
                form_elements = await extract_form_elements(cleaned_dom, query_selector)
                
                # Step 3: Fill form values if user prompt is provided
                if user_prompt:
                    form_elements = await fill_form_values(form_elements, [
                        {"role": "user", "parts": [user_prompt]},
                        {"role": "user", "parts": [custom_command] if custom_command else ["Please fill this form based on the information provided."]}
                    ])
                
                # Create and save the form
                new_form = Form(
                    domain=domain,
                    mapping={"querySelectorAll": query_selector},
                    parent_container="form",  # Default container, could be updated based on DOM analysis
                    verified=False
                )
                
                # Save form to database
                await new_form.save()
                
                # Return the form elements for the extension
                return JSONResponse(status_code=201, content=form_elements)
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                raise HTTPException(status_code=422, detail=f"Failed to parse widget detection result: {str(e)}")
            
        else:
            # No form found and no DOM to process
            raise HTTPException(status_code=404, detail=f"Form with domain '{domain}' not found and no DOM provided")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing form request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process form request: {str(e)}")

