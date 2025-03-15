# app/api/form_detect.py
import logging
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from urllib.parse import urlparse
from typing import List

from app.models.form_detect import find_form_detection_by_domain, FormDetectionResponse
from pydantic import BaseModel

class UrlRequest(BaseModel):
    url: str

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/form-detect", response_model=FormDetectionResponse)
async def detect_form_from_urls(
    urls: List[str] = Body(...)
):
    """
    API endpoint to detect if any of the provided URLs have domains that exist in our form detection database.
    
    Request:
        - List of URLs to check
        
    Response:
        - form: Boolean indicating if any URL domain is detected in our database
    """
    try:
        # Extract domains from the URLs
        domains = []
        for url in urls:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            if domain:
                domains.append(domain)
        
        # Check if any domain exists in the database
        for domain in domains:
            existing_record = await find_form_detection_by_domain(domain)
            if existing_record:
                return FormDetectionResponse(form=True)
        
        return FormDetectionResponse(form=False)
        
    except Exception as e:
        logger.error(f"Error in URL domain checking API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check domains: {str(e)}")

@router.post("/false_positive_forms", response_model=FormDetectionResponse)
async def blacklisted_domains(
    request: UrlRequest
):
    """
    API endpoint to check if a domain is blacklisted (has form=false in the database).
    
    Request:
        - url: Single URL to check
        
    Response:
        - form: Boolean value "false" if the domain is present in the database with form=false
    """
    try:
        # Extract domain from the URL
        url = request.url
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        if not domain:
            logger.warning(f"Invalid URL provided: {url}")
            return FormDetectionResponse(form=False)  # Default to true if we can't extract domain
        
        # Check if domain exists in the database
        existing_record = await find_form_detection_by_domain(domain)
        
        # If domain exists and form is False, return form=False
        if existing_record and existing_record.get("form") is False:
            return FormDetectionResponse(form=False)
        
        # Otherwise return form=True (domain not blacklisted)
        return FormDetectionResponse(form=True)
        
    except Exception as e:
        logger.error(f"Error in blacklisted domain checking API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check domain: {str(e)}")