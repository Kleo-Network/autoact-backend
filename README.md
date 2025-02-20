# KLEO Backend

KLEO Backend is a FastAPI application that serves as the backend for the KLEO project.

## Table of Contents

- [KLEO Backend](#kleo-backend)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/kleo-backend.git
cd kleo-backend
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables for MongoDB connection:

- We have given `.env.example` file. Just copy that and rename it to `.env` and replace the variables inside with appropriate values.

## Usage

To start the FastAPI application, run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You can now access the API at http://127.0.0.1:8000.

Also you can checkout Swagger documentation at http://127.0.0.1:8000/docs.


```
// update script execute 
curl -X PUT "http://0.0.0.0:8000/api/v1/script_play/script-execute/675afb3b1da15c9ef8fa9a6e" \
     -H "Content-Type: application/json" \
     -d '{
           "earn_points": 20,
           "spend_points": 10,
           "completed": true
         }'
{"updated_document":{"_id":"675afb3b1da15c9ef8fa9a6e","user_address":"0xUserAddress123","earn_points":20,"spend_points":10,"data_hash":"someDataHash","transaction_hash":"someTransactionHash","script_id":"60c72b2f9b1e8b5f6c8e4d9a","current_step":1,"completed":true,"created_at":"2024-12-12T15:01:08.177000","updated_at":"2024-12-12T15:10:09.329000"},"message":"Script execution data updated successfully."}%

// create script play
 curl -X POST "http://0.0.0.0:8000/api/v1/script_play/script-execute" \
     -H "Content-Type: application/json" \
     -d '{
           "user_address": "0xUserAddress123",
           "earn_points": 10,
           "spend_points": 5,
           "data_hash": "someDataHash",
           "transaction_hash": "someTransactionHash",
           "script_id": "60c72b2f9b1e8b5f6c8e4d9a",
           "current_step": 1,
           "completed": false
         }'

{"inserted_id":"675afb3b1da15c9ef8fa9a6e","message":"Script execution data inserted successfully."}%

// create script 
curl -X POST "http://0.0.0.0:8000/api/v1/script/new" \
     -H "Content-Type: application/json" \
     -d '{
           "creator_address": "0xCreatorAddress123",
           "transaction_hash": "0xTransactionHashABC123",
           "script": "print(\"Hello, World!\")",
           "used": 0,
           "earn_points": 50,
           "rating": 4.5,
           "description": "A simple hello world script.",
           "name": "HelloWorldScript",
           "sponsored": "0xSponsorAddress456",
           "logo": "https://example.com/logo.png",
           "verified": true
         }'

{"message":"Script created successfully!","script_id":"675afdda32a0fd227ac13c09"}%

// get all verified scripts 
curl -X GET "http://0.0.0.0:8000/api/v1/script/"
{"scripts":[{"_id":"675afdda32a0fd227ac13c09","creator_address":"0xCreatorAddress123","transaction_hash":"0xTransactionHashABC123","script":"print(\"Hello, World!\")","used":0,"earn_points":50,"rating":4.5,"description":"A simple hello world script.","name":"HelloWorldScript","sponsored":"0xSponsorAddress456","logo":"https://example.com/logo.png","created_at":"2024-12-12T15:14:34.994000","verified":true}]}%

// view script with id
curl -X GET "http://0.0.0.0:8000/api/v1/script/675afdda32a0fd227ac13c09" \
     -H "Accept: application/json"
{"script":{"_id":"675afdda32a0fd227ac13c09","creator_address":"0xCreatorAddress123","transaction_hash":"0xTransactionHashABC123","script":"print(\"Hello, World!\")","used":0,"earn_points":50,"rating":4.5,"description":"A simple hello world script.","name":"HelloWorldScript","sponsored":"0xSponsorAddress456","logo":"https://example.com/logo.png","created_at":"2024-12-12T15:14:34.994000","verified":true}}

// get user api 
curl -X GET "http://localhost:8000/get-user/0x1234567890abcdef" -H "Accept: application/json"
curl -X GET "http://0.0.0.0:8000/api/v1/user/get-user/0x1234567890abcdef" \
     -H "Accept: application/json"

// create user api 
curl -X POST "http://0.0.0.0:8000/api/v1/user/create-user" \
     -H "Content-Type: application/json" \
     -d '{
           "address": "0x1234567890abcdef"
         }'

// write save history curl as well. 
curl -X POST "http://0.0.0.0:8000/api/v1/user/save-history" \
     -H "Content-Type: application/json" \
     -d '{
           "address": "0x1234567890abcdef",
           "signup": false,
           "history": [
             {
               "title": "Example Title 1",
               "category": "Category1",
               "subcategory": "Subcategory1",
               "url": "https://example.com/page1",
               "domain": "example.com",
               "content": "Content of the first page.",
               "lastVisitTime": 1690000000
             },
             {
               "title": "Example Title 2",
               "category": "Category2",
               "subcategory": "Subcategory2",
               "url": "https://example.com/page2",
               "domain": "example.com",
               "content": "Content of the second page.",
               "lastVisitTime": 1690003600
             }
           ]
         }'


```