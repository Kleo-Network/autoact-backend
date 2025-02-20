# app/api/form.py
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models import Form, CreateFormRequest
from app.mongodb import get_forms

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/form/{domain}", response_model=dict)
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
            # Form exists, return it
            return JSONResponse(content=existing_form)
        
        # Form doesn't exist, create it if form_request is provided
        if form_request:
            # Ensure domain in URL matches domain in request body
            if domain != form_request.domain:
                form_request.domain = domain
                
            form = Form(
                domain=domain,
                mapping=form_request.mapping,
                parent_container=form_request.parent_container
            )
            result = await form.save()
            return JSONResponse(status_code=201, content=result)
        else:
            # No form found and no data to create one
            raise HTTPException(status_code=404, detail=f"Form with domain '{domain}' not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing form request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process form request: {str(e)}")


async def find_form_by_domain(domain: str):
    """
    Helper function to find a form by domain
    """
    forms_collection = get_forms()
    return await forms_collection.find_one({"domain": domain})