from bs4 import BeautifulSoup
import re
import os

# Remove Head of the HTML 
# Remove Script Tags and any kind of javascript present 
# Remove style tags 
# Remove all the comments

def clean_html(html: str):
    input_size = len(html)
    
    # Remove HTML comments
    html = re.sub(r'<!--[\s\S]*?-->', '', html)
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove head section
    if soup.head:
        soup.head.decompose()
    
    # Remove style tags and attributes
    for tag in soup.find_all(style=True):
        del tag['style']
    for style in soup.find_all('style'):
        style.decompose()
    
    # Remove script tags and inline JavaScript
    for script in soup.find_all('script'):
        script.decompose()
    
    # Remove on* attributes (inline JavaScript event handlers)
    for tag in soup.find_all():
        for attr in list(tag.attrs):
            if attr.startswith('on'):
                del tag[attr]
    
    # Write the cleaned HTML to the output file
    cleaned_html = str(soup)
    
    output_size = len(cleaned_html)
    
    # Compare file sizes
    
    print(f"Input HTML size: {input_size} characters")
    print(f"Cleaned HTML size: {output_size} characters")
    print(f"Size reduction: {input_size - output_size} characters")
    print(f"Percentage reduction: {((input_size - output_size) / input_size) * 100:.2f}%")
    
    return soup

# Example usage
if __name__ == "__main__":
    with open("../tests/templates/google_docs.txt", 'r', encoding='utf-8') as f:
        html_content = f.read()
        cleaned_soup = clean_html(html_content)