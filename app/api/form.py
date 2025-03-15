# app/api/form.py
import logging
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.form import Form, CreateFormRequest
from app.mongodb import get_forms
from fastapi import APIRouter, HTTPException, Query, Body

from app.services.clean_html import clean_html
from app.services.gemini_prompt import form_widget_detection, extract_form_elements, fill_form_values

from pydantic import BaseModel
from typing import Optional
from bson import json_util
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

class FormRequest(BaseModel):
    url: Optional[str] = None
    dom: Optional[str] = None
    user_prompt: Optional[str] = None
    custom_command: Optional[str] = None


@router.post("/{domain}", response_model=dict)
async def get_or_create_form(
    domain: str,
    form_data: FormRequest = Body(...)
):
    """
    Get an existing form by domain or create a new one if not found.
    
    Steps:
    1. Look for existing form in the database
    2. If not found, process the DOM to extract form elements
    3. Return the structured form data for the extension
    """
    print(domain)
    print(form_data)
    dom = form_data.dom
    user_prompt = form_data.user_prompt
    custom_command = form_data.custom_command
    print(domain)
    
    try:
        # Try to find the form first in the database
        forms_collection = get_forms()
        existing_form = await forms_collection.find_one({"domain": domain})
        
        if existing_form:
            serialized_form = json.loads(json_util.dumps(existing_form))
            query_selector = serialized_form.get("mapping", {}).get("querySelectorAll")
            
            # Skip cleaning the DOM for Typeform domains to preserve window.rendererData
            html_to_process = dom if "typeform" in domain else clean_html(dom)
            
            form_elements = await extract_form_elements(html_to_process, query_selector, domain)
            form_elements = await fill_form_values(form_elements, [
                        {"role": "user", "parts": [user_prompt]},
                        {"role": "user", "parts": [custom_command] if custom_command else ["Please fill this form based on the information provided."]}
                    ], domain)
            logger.info(f"Found existing form for domain: {domain}")
            return JSONResponse(content=form_elements)
        
        # Process the DOM if provided
        if dom:
            query_selector = ""
            form_elements = []
            
            # Skip cleaning the DOM for Typeform domains to preserve window.rendererData
            html_to_process = dom if "typeform" in domain else clean_html(dom)
            
            # For Typeform, we don't need widget detection as we extract from window.rendererData
            if "typeform" in domain:
                # Use a dummy query selector as it will be ignored for Typeform
                query_selector = "form"
                
                # Extract directly from window.rendererData
                form_elements = await extract_form_elements(html_to_process, query_selector, domain)
                
                # Fill form values if user prompt is provided
                if user_prompt:
                    form_elements = await fill_form_values(form_elements, [
                        {"role": "user", "parts": [user_prompt]},
                        {"role": "user", "parts": [custom_command] if custom_command else ["Please fill this form based on the information provided."]}
                    ], domain)
            else:
                # Standard flow for non-Typeform sites
                try:
                    # Step 1: Get the query selector for form widgets
                    widget_detection_result = await form_widget_detection(html_to_process)
                    
                    # Parse the response to get the querySelectorAll
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
                    form_elements = await extract_form_elements(html_to_process, query_selector, domain)
                    
                    # Step 3: Fill form values if user prompt is provided
                    if user_prompt:
                        form_elements = await fill_form_values(form_elements, [
                            {"role": "user", "parts": [user_prompt]},
                            {"role": "user", "parts": [custom_command] if custom_command else ["Please fill this form based on the information provided."]}
                        ], domain)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {str(e)}")
                    raise HTTPException(status_code=422, detail=f"Failed to parse widget detection result: {str(e)}")
            
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
        else:
            # No form found and no DOM to process
            raise HTTPException(status_code=404, detail=f"Form with domain '{domain}' not found and no DOM provided")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing form request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process form request: {str(e)}")

