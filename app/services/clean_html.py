# app/services/clean_html.py
import re
from bs4 import BeautifulSoup

def clean_html(html: str) -> str:
    """
    Clean HTML by removing unnecessary elements and attributes
    
    This improves the quality of form processing by:
    1. Removing script tags
    2. Removing style tags
    3. Removing comments
    4. Preserving important form elements and their attributes
    5. Keeping structural elements like div, section, etc.
    6. Keeping text nodes and labels
    """
    try:
        # Parse HTML
        input_size = len(html)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove scripts
        for script in soup.find_all('script'):
            script.decompose()
        
        # Remove styles
        for style in soup.find_all('style'):
            style.decompose()
        
        # Remove comments
        for comment in soup.find_all(text=lambda text: isinstance(text, (str, bytes)) and text.strip().startswith('<!--')):
            comment.extract()
        
        # Remove data-* attributes that aren't necessary for form identification
        for tag in soup.find_all(True):
            attrs_to_remove = [attr for attr in tag.attrs if attr.startswith('data-') and 
                              attr not in ['data-id', 'data-name', 'data-field', 'data-label']]
            for attr in attrs_to_remove:
                del tag[attr]
            
            # Also remove event handlers
            event_attrs = [attr for attr in tag.attrs if attr.startswith('on')]
            for attr in event_attrs:
                del tag[attr]
        
        # Retain only the necessary attributes for form processing
        allowed_attrs = {
            'input': ['type', 'name', 'id', 'placeholder', 'value', 'required', 'class', 'aria-label'],
            'select': ['name', 'id', 'multiple', 'required', 'class', 'aria-label'],
            'textarea': ['name', 'id', 'placeholder', 'required', 'class', 'aria-label'],
            'label': ['for', 'class'],
            'form': ['id', 'name', 'class', 'action', 'method'],
            'option': ['value', 'selected'],
            'button': ['type', 'class', 'id'],
            'div': ['class', 'id'],
            'span': ['class', 'id'],
            'fieldset': ['class', 'id'],
            'legend': ['class', 'id'],
            'section': ['class', 'id'],
            'h1': ['class', 'id'],
            'h2': ['class', 'id'],
            'h3': ['class', 'id'],
            'p': ['class', 'id'],
        }
        
        for tag in soup.find_all():
            if tag.name in allowed_attrs:
                tag.attrs = {attr: value for attr, value in tag.attrs.items() if attr in allowed_attrs[tag.name]}
        
        # Convert the soup back to a string
        cleaned_html = str(soup)
        
        # Remove empty lines
        cleaned_html = re.sub(r'^\s*$', '', cleaned_html, flags=re.MULTILINE)
        
        output_size = len(cleaned_html)
        print(f"Input HTML size: {input_size} characters")
        print(f"Cleaned HTML size: {output_size} characters")
        print(f"Size reduction: {input_size - output_size} characters")
        print(f"Percentage reduction: {((input_size - output_size) / input_size) * 100:.2f}%")
        return cleaned_html
    
    except Exception as e:
        # If any error occurs, return the original HTML
        return html