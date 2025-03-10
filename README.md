# AutoAct Backend

AutoAct Backend is a FastAPI application that serves as the backend for autoact chrome extension, its' 
from the same team as Kleo Network

## Table of Contents

- [AutoAct Backend](#AutoAct-backend)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Kleo-Network/autoact-backend.git
cd autoact-backend
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
