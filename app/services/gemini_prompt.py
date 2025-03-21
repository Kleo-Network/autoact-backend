import os
import json
import google.generativeai as genai # type: ignore
from google.ai.generativelanguage_v1beta.types import content # type: ignore
from typing import Dict, Any, List, Union
import re
import ast
import logging
logger = logging.getLogger(__name__)
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Configuration for form values filling
generation_config_form_values = {
  "temperature": 0.3,  # Lower temperature for more predictable outputs
  "top_p": 0.45,
  "top_k": 70,
  "max_output_tokens": 0,  # Will be dynamically set based on form elements length
  "response_schema": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "querySelectorInput": {"type": "string"},
        "label": {"type": "string"},
        "value": {"type": "string"}
      },
      "required": ["querySelectorInput", "label", "value"]
    }
  },
  "response_mime_type": "application/json",
}

# Configuration for widget detection
generation_config_widget_detection = {
  "temperature": 0.2,  # Even lower temperature for consistent widget detection
  "top_p": 0.4,
  "top_k": 40,
  "max_output_tokens": 100,
  "response_schema": {
    "type": "object",
    "properties": {
      "querySelectorAll": {"type": "string"}
    },
    "required": ["querySelectorAll"]
  },
  "response_mime_type": "application/json",
}

# Configuration for element extraction
generation_config_element_extraction = {
  "temperature": 0.2,
  "top_p": 0.4,
  "top_k": 40,
  "max_output_tokens": 2000,
  "response_schema": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "querySelectorInput": {"type": "string"},
        "label": {"type": "string"}
      },
      "required": ["querySelectorInput", "label"]
    }
  },
  "response_mime_type": "application/json",
}

# Improved system instruction for widget detection
system_instruction_widget_detection = """
You are a specialized form parser. Your job is to analyze HTML form content and identify the common pattern 
for selecting all form sections or elements that contain both labels and inputs.

Guidelines:
1. Examine the HTML closely to identify the container elements that group input fields with their labels
2. Focus on elements like div, section, fieldset, tr, li that might contain both a label and input
3. Return a single CSS selector that will match ALL form element containers
4. The selector should be specific enough to only target form element containers
5. Ensure your selector works across the entire form regardless of its length

Your response must be a JSON object with exactly one property: "querySelectorAll" containing the proper CSS selector.
Example: {"querySelectorAll": ".form-group"} or {"querySelectorAll": "form div.field-container"}
"""

# System instruction for form element extraction
system_instruction_element_extraction = """
You are a specialized form analyzer. Given a form's HTML and a CSS selector for form element containers, 
extract all the input elements and their corresponding labels.

For each form element container:
1. Find the input element (input, select, textarea) within the container
2. Find the associated label text within the container
3. Return a CSS selector for the specific input and the label text

Your response must be a JSON array where each item contains:
- "querySelectorInput": The specific CSS selector for the input element (must be precise to target exactly one element)
- "label": The text of the label associated with this input

Examples:
[
  {"querySelectorInput": "input[id='some_id']", "label": "First Name"},
  {"querySelectorInput": "input[name='email']", "label": "Email Address"}
]

Ensure each querySelectorInput is unique and specific enough to target exactly one element.
"""

# System instruction for form values filling
system_instruction_form_values = """
You are a specialized form filler. Given form elements with labels and the user's instructions,
fill in appropriate values for each form field.

Guidelines:
1. Analyze the user's input carefully to extract relevant information, fill dummy data where not available
2. Match the information to the appropriate form fields based on field labels
3. For fields not explicitly mentioned in the input, provide reasonable defaults
4. Handle all common input types appropriately (text, email, phone, dates, etc.)
5. Format values appropriately for each field type (e.g., dates in the right format)

Your response must maintain the structure of the input, adding a "value" field to each element:
[
  {"querySelectorInput": "input[id='some_id']", "label": "First Name", "value": "John"},
  {"querySelectorInput": "input[name='email']", "label": "Email Address", "value": "john.doe@example.com"}
]

Do not add any explanations in your response, just return the JSON array with filled values.
"""

async def form_widget_detection(form_html: str) -> Dict:
    """Get the CSS selector for form widget containers"""
    try:
        response = await gemini_response(
            system_instruction=system_instruction_widget_detection,
            message=form_html, 
            config=generation_config_widget_detection, 
            model="gemini-2.0-flash"
        )
        
        # Parse response to ensure it matches expected format
        if isinstance(response, str):
            return json.loads(response)
        
        response_dict = response
        
        # Validate response has the expected structure
        if not isinstance(response_dict, dict) or "querySelectorAll" not in response_dict:
            logger.error(f"Invalid response format from widget detection: {response}")
            return {"querySelectorAll": "form *"}  # Fallback to a generic selector
            
        return response_dict
    except Exception as e:
        logger.error(f"Error in form widget detection: {str(e)}")
        return {"querySelectorAll": "form *"}  # Fallback to a generic selector

async def extract_form_elements(form_html: str, query_selector: str, domain: str = "") -> List[Dict]:
    """Extract form elements using the provided query selector"""
    try:
        # Special handling for Typeform
        if "typeform" in domain:
            # Look for window.rendererData in the DOM for Typeform
            logger.info("Detected typeform domain, using specialized extraction")
            
            # Try to find the rendererData in the HTML
            renderer_data_pattern = r'window\.rendererData\s*=\s*({.+?});'
            render_data_match = re.search(renderer_data_pattern, form_html, re.DOTALL)
            
            if render_data_match:
                # Get the full rendererData string
                render_data_str = render_data_match.group(1).strip()
                # Instead of parsing the entire JSON, use regex to extract just the form object
                form_pattern = r'form:\s*({.+?"_links":.+?})(?=,\s*(?:messages|hubspotIntegration|intents|integrations|messages):|$)'

                form_match = re.search(form_pattern, render_data_str, re.DOTALL)
                print(form_match.group(1))
                if form_match:
                    form_json_str = form_match.group(1)
                    logger.info("Successfully extracted form JSON from rendererData")
                    
                    # Clean the extracted form JSON
                    form_json_str = re.sub(r',\s*}', '}', form_json_str)
                    form_json_str = re.sub(r',\s*]', ']', form_json_str)
                    
                    try:
                        # Try to parse the form JSON
                        form_data = json.loads(form_json_str)
                        logger.info("Successfully parsed form JSON")
                        
                        # Extract fields from the form data
                        fields = form_data.get('fields', [])
                        logger.info(f"Found {len(fields)} form fields")
                        form_elements = []
                        
                        for field in fields:
                            field_type = field.get('type', '')
                            field_ref = field.get('ref', '')
                            field_title = field.get('title', '')
                            
                            if field_type and field_ref:
                                # Create the selector based on the type and ref
                               
                                query_selector_input = (f"*[aria-labelledby^=\"{field_type}-{field_ref}\"], "f"*[aria-describedby^=\"{field_type}-{field_ref}\"]")
                                print(query_selector_input)
                                print(field_title)
                                form_elements.append({
                                    "querySelectorInput": query_selector_input,
                                    "label": field_title
                                })
                        
                        if form_elements:
                            logger.info(form_elements)
                            logger.info(f"Successfully extracted {len(form_elements)} elements from Typeform form data")
                            return form_elements
                    except json.JSONDecodeError as je:
                        pass
        
        # Standard extraction for non-Typeform sites
        # Combine the HTML and query selector in a structured message
        message = {
            "html": form_html,
            "querySelectorAll": query_selector
        }
        
        response = await gemini_response(
            system_instruction=system_instruction_element_extraction,
            message=json.dumps(message), 
            config=generation_config_element_extraction, 
            model="gemini-2.0-flash"
        )
        
        # Parse response to ensure it matches expected format
        if isinstance(response, str):
            try:
                parsed_response = json.loads(response)
                if isinstance(parsed_response, list) and len(parsed_response) > 0:
                    return parsed_response
            except json.JSONDecodeError:
                logger.warning("Failed to parse Gemini response as JSON, falling back to DOM extraction")
        
        # Handle when response is already parsed
        if isinstance(response, list) and len(response) > 0:
            return response
        
        # If we reached here, the Gemini API didn't return a valid result
        # Use the DOM extraction utility as a fallback
        from app.services.dom_utils import extract_form_elements_from_dom
        logger.info(f"Using DOM extraction fallback with selector: {query_selector}")
        form_elements = extract_form_elements_from_dom(form_html, query_selector)
        
        if form_elements and len(form_elements) > 0:
            return form_elements
            
        # Last resort: return empty list
        logger.warning("Both Gemini extraction and DOM fallback failed to find form elements")
        return []
    except Exception as e:
        logger.error(f"Error in form element extraction: {str(e)}")
        # Try the DOM extraction as a last resort
        try:
            from app.services.dom_utils import extract_form_elements_from_dom
            return extract_form_elements_from_dom(form_html, query_selector)
        except Exception as inner_e:
            logger.error(f"DOM extraction fallback also failed: {str(inner_e)}")
            return []

async def fill_form_values(form_elements: List[Dict], history: List[Dict], domain: str = "") -> Union[Dict, List[Dict]]:
    """Fill form values based on user input"""
    try:
        form_values_config = generation_config_form_values.copy()
        form_values_config["max_output_tokens"] = len(form_elements) * 200
        
        response = await gemini_response(
            system_instruction=system_instruction_form_values,
            message=str(json.dumps(form_elements)),
            history=history, 
            config=form_values_config,  # Use the modified config
            model="gemini-2.0-flash"
        )
        print(response)
        
        # Parse response to ensure it matches expected format
        filled_form = None
        if isinstance(response, str):
            filled_form = json.loads(response)
        # Handle when response is already parsed
        elif isinstance(response, list):
            filled_form = response
        else:
            filled_form = form_elements  # Return original if parsing fails
        
        # Format the response based on domain
        if "typeform" in domain:
            # For Typeform domains, use the special format
            return {
                "type": "enter",
                "domain": "typeform.com",
                "fillJSON": filled_form
            }
        else:
            # For all other domains, use the standard format
            return {
                "type": "direct",
                "domain": domain,
                "fillJSON": filled_form
            }
    except Exception as e:
        logger.error(f"Error in form values filling: {str(e)}")
        # Return in the standard format even on error
        if "typeform" in domain:
            return {
                "type": "enter", 
                "domain": "typeform.com", 
                "fillJSON": form_elements
            }
        else:
            return {
                "type": "direct", 
                "domain": domain, 
                "fillJSON": form_elements
            }

async def gemini_response(
    system_instruction: str = "", 
    message: str = "",  
    history: List[Dict] = [], 
    config: Dict[str, Any] = None,
    model: str = "gemini-2.0-flash"
) -> Union[Dict, List, str]:
    """Send a request to Gemini API and get a response"""
    try:
        model_instance = genai.GenerativeModel(
            model_name=model,
            generation_config=config,
            system_instruction=system_instruction,
        )
        
        chat_session = model_instance.start_chat(history=history)
        response = chat_session.send_message(message)
        
        # Try to parse the response
        try:
            if hasattr(response, 'text'):
                return json.loads(response.text)
            else:
                return response
        except json.JSONDecodeError:
            # If response is not valid JSON, return it as is
            return response.text if hasattr(response, 'text') else str(response)
            
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return f"API Error: {str(e)}"