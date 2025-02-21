import requests
import json
domains = ["forms.fillout.com", "forms.google.com", "taiwan.visa.gov.tw", "luma.com"]
template_files = ["templates/forms_fillout.txt", "templates/google_docs.txt", "templates/forms_typeform.txt"]
base_url = "http://0.0.0.0:8000/api/v1/form/{domain}"



def send_post_requests():
    for domain, template_file in zip(domains, template_files):
        print(f"\n=== Processing {domain} ===")
        url = base_url.replace("{domain}", domain)
        
        try:
            with open(template_file, "r") as file:
                dom_content = file.read()
        except FileNotFoundError:
            print(f"Error: File '{template_file}' not found.")
            continue
        
        payload = {
            "dom": dom_content
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                print("Request successful!")
                print("Response:")
                response_json = response.json()
                print(json.dumps(response_json, indent=2))
                
                # Validate the response
                has_domain = "domain" in response_json and isinstance(response_json["domain"], str)
                has_mapping = "mapping" in response_json and isinstance(response_json["mapping"], dict)
                has_parent = "parent_container" in response_json and isinstance(response_json["parent_container"], str)
                
                if has_domain and has_mapping and has_parent:
                    print("✓ Response has the correct structure")
                else:
                    print("✗ Response does not have the expected structure")
            else:
                print(f"Request failed with status code: {response.status_code}")
                print("Response:")
                print(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")

if __name__ == "__main__":
    send_post_requests()
    
