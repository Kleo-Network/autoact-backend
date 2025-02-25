import requests
import json
domains = ["forms.fillout.com"]
template_files = ["templates/forms_fillout.txt"]
base_url = "http://0.0.0.0:8000/api/v1/form/{domain}"

custom_message = """
My name is Vaibhav Maheshwari My handle is vaibhavgeek on almost all platforms.
zkcash.xyz
It was a solo project which was a privacy mixer which allowed one to send and receive 1 MATIC  / 500 USDC via the UI. We also published guidelines on how the service can be used to be completely anonymous. It also bans a list of addresses from using the solution in order to be compliant with the authorities (without much latency). 
Receive payments anonymously via a link [ Created a circom circuit for creating link ]
Send payments anonymously to another account [ Created a merkle tree circuit for sending payments ]
Created smart contracts to receive and withdraw tokens, created $ZKC token for private handling. 
Created frontend in react to interact with the smart contracts / circuits. 
Languages: React - Typescript, NEXT JS, Solidity (Hardhat) , Circom
[https://github.com/vaibhavgeek/zkpay]
zkcalendar
It was a solo project which was privacy preserving calendly clone. It used tech specified by baseline-protocol. Received 6000$ for the project. 
Schedule Appointments via Circom Circuit without revealing time availabilities. 
Created backend in NodeJS and PostgreSQL 
Created frontend in ReactJS 
Adhered to strict parameters given by Baseline Protocol regarding code quality. 
Languages - React - Typescript, NodeJS (Express JS), Circom, Solidity (Truffle) , Baseline  
[https://github.com/eea-oasis/baseline/tree/feature-calendar-BLIP/examples/calendar]
weescore.xyz
It was a solo projects which allowed discord groups to distribute NFTs to members and create a real time dashboard for ranking of the group members. It received 3000$ by Polygon Fellowship. 
Created discord Bot to send private links 
Created admin dashboard which linked the discord usernames / address analytics. 
Create a claim page where users can claim the NFT of the members. 
Handled deployment, UI UX and everything for this project. 
Languages - React - Typescript, Redux, NEXT JS
swanky-manky-math-game
I worked on this project with a friend (@aish96). The idea was to allow people intellectually challenge themselves via a math puzzle. Form a number on displayed on lock with the given operators (addition.division.subtraction.multiplication)
Created API for NFTs allocation. 
Created frontend in react. 
VITEPAY.JS - Create a react SDK to integrate to vitepay payments with any react based Dapp. Total 600+ downloads till date. 
Flower NFT - Created a NFTs that have different properties at different times. 
Sheety Bot - Created a Telegram Bot which would ask you about your habits and update google sheets respectively. Producthunt 
KPI Token Distribution Superfluid  - Distribute Long UMA KPI Tokens via Superfluid Stream, allows you to reward users on a real time basis based on their performance metrics, can be extended to measure productivity and incentivise users. 

Chesstopia [Backend] - Stake and play chess. Acts as escrow and winner gets all. 

Patreon Web3 Clone - A tier based subscription with exclusive posts / content for the creators,  built on top of zilliqa smart contracts. 

Decentralised Index Fund - Decentralised Index Fund smart contract enables a person to batch NFTs and create fungible tokens that can be traded and distributed. The tokens are minted based on token bonding emission cruve y = x ^ 2 where y is the price of token issues and x is total tokens sold, implemented in zilliqa. 

NFT Fractionalisation - Creation of fungible tokens from a NFT and a simple voting of >50% votes to reinstitute the NFT together. 
Experience
Ricochet Exchange : Contributed to writing solidity tests, along with contributing work to frontend tasks. I worked on multiple issues in writing smart contract code, testing smart contracts and improving user interface/experience for a period of 3 months. 
 
Zesty Bob Bot : Contributed to creating of a backend which would listen to events on chain and trigger APIs and notifications to end user based on the on chain activity. Creation of centralised database structure along with taking care of deployment. I worked on it for a period of 3 months. 

MatchBox DAO Grant : Creation of merkle tree in cairo to handle queues which allow automated tasks to execute in a more optimized manner, this was based on top of yagi.fi keeper network. Have good understanding of Cairo Language. I worked on it for a period of 2 months.

GigIndia : Responsible for full stack development at GigIndia, I worked here for a period 1.5 years.

Articles  
Understanding Modular Blockchains

Deep dive into Zero Knowledge Ecosystem

When blockchain can be used in a project

Real Value of Cryptocurrencies

AWS Lambda Seminar GDG 

"""

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
            "dom": dom_content,
            "user_prompt": custom_message
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                print("Request successful!")
                print("Response:")
                response_json = response.json()
                print(json.dumps(response_json, indent=2))
                
                # Validate the response
                # has_domain = "domain" in response_json and isinstance(response_json["domain"], str)
                # has_mapping = "mapping" in response_json and isinstance(response_json["mapping"], dict)
                # has_parent = "parent_container" in response_json and isinstance(response_json["parent_container"], str)
                
                # if has_domain and has_mapping and has_parent:
                #     print("✓ Response has the correct structure")
                # else:
                #     print("✗ Response does not have the expected structure")
            else:
                print(f"Request failed with status code: {response.status_code}")
                print("Response:")
                print(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")

if __name__ == "__main__":
    send_post_requests()
    
