# app/services/dom_utils.py
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def extract_form_elements_from_dom(html: str, query_selector: str) -> List[Dict[str, Any]]:
    """
    Extract form elements directly from the DOM using the provided query selector
    
    This is a fallback mechanism in case the Gemini API fails to extract elements properly
    """
    try:
        # Parse the HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Initialize result list
        result = []
        
        # Try to find all elements matching the query selector
        # Note: BeautifulSoup doesn't directly support complex CSS selectors
        # For complex selectors, we'd need to use a more sophisticated approach
        # This is a simplified implementation
        
        # Convert query selector to something BeautifulSoup can understand
        selector_parts = query_selector.split()
        target_elements = soup.select(query_selector)
        
        if not target_elements:
            logger.warning(f"No elements found using selector: {query_selector}")
            # Fallback to find all form elements
            form_elements = soup.find_all(['input', 'select', 'textarea'])
            
            for element in form_elements:
                # Try to find associated label
                label_text = ""
                
                # Check for label with for attribute
                input_id = element.get('id')
                if input_id:
                    label = soup.find('label', attrs={'for': input_id})
                    if label:
                        label_text = label.get_text(strip=True)
                
                # If no label found, look for placeholder or name
                if not label_text:
                    label_text = element.get('placeholder', '') or element.get('name', '') or element.get('aria-label', '')
                
                # Generate a CSS selector for this input
                if input_id:
                    input_selector = f"#{input_id}"
                elif element.get('name'):
                    input_selector = f"{element.name}[name='{element.get('name')}']"
                else:
                    # Generate a path-based selector as last resort
                    parent_classes = []
                    parent = element.parent
                    for _ in range(3):  # Look up to 3 levels up
                        if not parent:
                            break
                        if parent.get('class'):
                            parent_classes.append('.'.join(parent.get('class')))
                        parent = parent.parent
                    
                    if parent_classes:
                        input_selector = f"{' '.join(reversed(parent_classes))} {element.name}"
                    else:
                        input_selector = element.name
                
                result.append({
                    "querySelectorInput": input_selector,
                    "label": label_text
                })
            
            return result
        
        # Process found elements
        for container in target_elements:
            # Find input elements in this container
            inputs = container.find_all(['input', 'select', 'textarea'])
            
            for input_element in inputs:
                input_id = input_element.get('id', '')
                input_name = input_element.get('name', '')
                
                # Determine input selector
                if input_id:
                    input_selector = f"#{input_id}"
                elif input_name:
                    input_selector = f"{input_element.name}[name='{input_name}']"
                else:
                    # Create a fallback selector
                    input_selector = f"{query_selector} {input_element.name}"
                
                # Extract label text
                label_text = ""
                
                # Try finding associated label
                if input_id:
                    label = container.find('label', attrs={'for': input_id})
                    if label:
                        label_text = label.get_text(strip=True)
                
                # If no label with 'for' attribute, try checking for label as direct parent/ancestor
                if not label_text:
                    labels = container.find_all('label')
                    if labels:
                        label_text = labels[0].get_text(strip=True)
                
                # If still no label, try other text in the container
                if not label_text:
                    # Get all text in container excluding text in other input elements
                    container_text = container.get_text(strip=True)
                    input_text = ''.join([i.get_text(strip=True) for i in container.find_all(['input', 'select', 'textarea'])])
                    label_text = container_text.replace(input_text, '').strip()
                
                # Final fallback to placeholder or name attribute
                if not label_text:
                    label_text = input_element.get('placeholder', '') or input_element.get('name', '') or input_element.get('aria-label', '')
                
                result.append({
                    "querySelectorInput": input_selector,
                    "label": label_text
                })
        
        return result
    
    except Exception as e:
        logger.error(f"Error extracting form elements from DOM: {str(e)}")
        return []