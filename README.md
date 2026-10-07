# 🤖 Semantic Web & AI Assistant for Kindergartens

## 📌 Overview
This repository contains a full-stack Semantic Web application built with Python. It serves as an AI-powered assistant (chatbot) that helps users (e.g., parents) find and filter kindergartens and optional classes in Sibiu. The project leverages both traditional RESTful architectures and Semantic Web technologies (RDF4J), unified through a modern FastAPI backend and OpenAI's GPT-4o-mini model.

## 🚀 Key Features
* **AI-Powered Chatbot:** Integrates the OpenAI API for natural language understanding, allowing users to query kindergarten information in plain text.
* **Semantic Database Integration (RDF4J):** Stores and queries structured data (kindergartens, optional courses, pricing) using SPARQL on a Graph Database (RDF4J Server).
* **Multi-Source Data Fetching:** Seamlessly routes queries between a JSON Server (GraphQL/REST) and the RDF4J semantic database depending on the user's intent.
* **Function Calling (Tools):** The OpenAI model dynamically selects and executes Python backend functions (e.g., `cauta_gradinita_dupa_cartier`, `adauga_curs_rdf4j`) to fetch real-time data.
* **Responsive UI:** A clean, modern HTML/CSS interface with AJAX to handle real-time chat interactions.

## 🛠️ Technologies Used
* **Backend:** Python, FastAPI, Uvicorn, Requests
* **AI Integration:** OpenAI API (gpt-4o-mini), Function Calling
* **Semantic Web Data:** RDF4J Server, SPARQLWrapper, Turtle (`.ttl`) format
* **Databases:** JSON Server, JSON GraphQL Server
* **Frontend:** HTML5, CSS3, JavaScript (AJAX/Fetch)

## ⚙️ How It Works
1. The user types a query in the frontend interface (e.g., "Find kindergartens in the Centru neighborhood").
2. The frontend sends the prompt to the FastAPI backend via an AJAX request.
3. The backend communicates with OpenAI. Based on the intent, the AI triggers specific tools/functions.
4. Python executes the triggered function (e.g., querying the JSON Server via REST or the RDF4J server via SPARQL).
5. The extracted data is returned to the AI, which formulates a natural, user-friendly response that is then displayed in the chat interface.

## 🚀 Setup and Execution
To run this project locally, you need to start the backend, the mock databases, and the RDF4J server.

### Prerequisites
* Python 3.8+
* Node.js (for `json-server` and `json-graphql-server`)
* RDF4J Server running on `localhost:8080`

### 1. Install Dependencies
```bash
pip install fastapi uvicorn openai requests python-dotenv SPARQLWrapper pydantic
npm install -g json-server json-graphql-server

### 2. Configure Environment
Create a .env file in the root directory and add your OpenAI API Key:
  OPENAI_API_KEY=your_openai_api_key_here

###3. Start the Servers
Open separate terminal windows and run the following commands:

Terminal 1 — REST API Server:
  npx json-server db.json --port 4000

Terminal 2 — GraphQL Server:
npx json-graphql-server db.json --port 3000

Terminal 3 — FastAPI Backend:
python -m uvicorn main:app --reload

###4. Open the Interface
Open index.html in your web browser to interact with the assistant.
