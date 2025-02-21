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


@router.post("/{domain}", response_model=dict)
async def get_or_create_form(domain: str, dom: str):
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
        #3. parse the json response and if valid 
        #4. create the form and save it to db and return the same. 
            return JSONResponse(status_code=201, content=result)
        else:
            # No form found and no data to create one
            raise HTTPException(status_code=404, detail=f"Form with domain '{domain}' not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing form request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process form request: {str(e)}")