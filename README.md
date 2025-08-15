# Hydropower Dispatch Knowledge Graph System

## 1. Overview

This project is a comprehensive Python-based system for building, visualizing, and querying a knowledge graph for hydropower dispatch operations. The system is designed to process unstructured documents (like PDFs of dispatch rules), extract key information using Large Language Models (LLMs), store it in a graph database (Neo4j), and provide a web-based interface for visualization and question-answering.

The project is divided into three main parts:
1.  **Knowledge Extraction**: Parses PDFs, extracts text and tables, and uses an LLM to build a knowledge graph in Neo4j.
2.  **Knowledge Visualization**: A web UI to explore the knowledge graph with features like fuzzy search, gravity-based layout, and property editing.
3.  **Knowledge Q&A**: A question-answering interface that takes operational conditions and recommends the optimal dispatch rule.

## 2. Features

### Knowledge Extraction (Part 1)
*   **PDF Processing**: Extracts text from both native and scanned PDFs using PyMuPDF and Tesseract OCR.
*   **Configurable Ontology**: Graph structure is defined in a human-readable `config/ontology.yaml` file.
*   **LLM-Powered Extraction**: Uses an LLM to parse text and convert it into structured graph data.
*   **Graph Database Integration**: Imports the structured data into a Neo4j database.
*   **End-to-End Pipeline**: A script (`src/knowledge_extraction/main_pipeline.py`) orchestrates the entire workflow.

### Visualization & Q&A (Part 2 & 3)
*   **FastAPI Backend**: A robust asynchronous backend serves the API and frontend.
*   **Dynamic Graph Visualization**: An interactive, force-directed graph visualization built with D3.js.
*   **Search**: Fuzzy search functionality to find nodes within the graph.
*   **Interactive UI**: Nodes can be dragged and clicked to inspect their properties.
*   **Node Property Editing**: Select a node to view its properties in a form and submit changes back to the database.
*   **AI-Powered Q&A**: A decision-support system that takes station conditions (flow, water level) and uses an LLM to recommend the most appropriate dispatch rule from the knowledge graph.

## 3. Project Structure

```
.
├── config/                  # Configuration files for the extraction pipeline
├── data/                    # Data files (PDFs, JSON outputs)
├── src/
│   ├── knowledge_extraction/ # Module for the Part 1 data pipeline
│   ├── static/               # Frontend files (HTML, CSS, JS)
│   │   ├── index.html
│   │   ├── style.css
│   │   └── app.js
│   ├── graph_db.py           # Handles all Neo4j queries for the web app
│   ├── main.py               # The FastAPI application server
│   └── qa_system.py          # Handles the Q&A logic with the LLM
├── tests/                   # Unit tests
├── .env.example             # Example environment variables file
├── pytest.ini               # Configuration for pytest
└── requirements.txt         # Python package dependencies
```

## 4. Setup and Installation

### Step 1: Prerequisites

*   **Python 3.10+**
*   **Tesseract OCR Engine**: Required for Part 1 (Knowledge Extraction).
    ```bash
    # On Debian/Ubuntu
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr tesseract-ocr-chi-sim
    ```
*   **Docker** and **Docker Compose**: Recommended for running the Neo4j database.

### Step 2: Clone the Repository

```bash
git clone <repository_url>
cd <repository_name>
```

### Step 3: Set up Neo4j Database

The easiest way to run Neo4j is with Docker.
1.  Create a `docker-compose.yml` file in the root of the project with the following content:
    ```yaml
    version: '3.8'
    services:
      neo4j:
        image: neo4j:5.20.0
        container_name: neo4j_hydropower
        ports:
          - "7474:7474"
          - "7687:7687"
        volumes:
          - ./neo4j-data:/data
        environment:
          - NEO4J_AUTH=neo4j/password  # Sets the username to 'neo4j' and password to 'password'
          - NEO4J_PLUGINS=["apoc"]
    ```
2.  Start the database:
    ```bash
    docker-compose up -d
    ```
    You can now access the Neo4j Browser at `http://localhost:7474`.

### Step 4: Configure Environment Variables

1.  Create a `.env` file from the example:
    ```bash
    cp .env.example .env
    ```
2.  Edit the `.env` file. If you used the Docker setup above, the default Neo4j credentials will work. You must add your **DeepSeek API Key**.
    ```
    NEO4J_URI="neo4j://localhost:7687"
    NEO4J_USER="neo4j"
    NEO4J_PASSWORD="password"
    LLM_API_BASE_URL="https://api.deepseek.com"
    LLM_API_KEY="sk-..." # <-- PASTE YOUR KEY HERE
    ```

### Step 5: Install Python Dependencies

Create and activate a virtual environment, then install the packages.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 5. Usage

### Step 1: Populate the Knowledge Graph

First, you need to run the knowledge extraction pipeline to process the PDF and populate your Neo4j database.
```bash
python3 src/knowledge_extraction/main_pipeline.py
```
This script uses the dummy data in `data/extracted_knowledge.json` to populate the database.

### Step 2: Run the Web Application

Start the FastAPI server using uvicorn.
```bash
uvicorn src.main:app --reload
```
The `--reload` flag automatically reloads the server when you make code changes.

### Step 3: Use the Application

1.  Open your web browser and navigate to `http://localhost:8000`.
2.  **Visualize the Graph**: The graph should load automatically. You can search for specific nodes using the search bar (e.g., "淋部沟").
3.  **Interact**: Drag nodes around. Click on a node to see its properties appear in the panel on the right.
4.  **Edit Properties**: Modify the properties in the form and click "Save Changes". The graph will refresh to show the updated data.
5.  **Get Recommendations**: In the Q&A section, enter a station name and conditions (e.g., Station: `淋部沟水电站`, Flow: `1500`, Level: `3020`) and click "Get Recommendation" to see the LLM-powered advice.

## 6. API Endpoints

The FastAPI server provides the following endpoints:
*   `GET /`: Serves the frontend application (`index.html`).
*   `GET /api/search?q={query}`: Searches the graph. Returns nodes and links.
*   `POST /api/node/update`: Updates a node's properties. Expects a JSON body with `id` and `properties`.
*   `POST /api/qna`: Gets a dispatch recommendation. Expects a JSON body with `station`, `flow`, and `level`.
