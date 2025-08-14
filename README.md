# Hydropower Dispatch Knowledge Graph System

## Overview

This project is a comprehensive Python-based system for building, visualizing, and querying a knowledge graph for hydropower dispatch operations. The system is designed to process unstructured documents (like PDFs of dispatch rules), extract key information using Large Language Models (LLMs), store it in a graph database, and provide interfaces for visualization and question-answering.

The project is divided into three main parts:
1.  **Knowledge Extraction**: Parses PDFs, extracts text and tables, and uses an LLM to build a knowledge graph in Neo4j.
2.  **Knowledge Visualization**: A Python-based UI to explore the knowledge graph with features like fuzzy search, gravity-based layout, and property editing. (Future Work)
3.  **Knowledge Q&A**: A question-answering interface that takes operational conditions (e.g., water level, flow) and recommends the optimal dispatch rule by querying the graph and summarizing with an LLM. (Future Work)

This initial implementation focuses on completing **Part 1: Knowledge Extraction**.

## Features (Part 1: Knowledge Extraction)

*   **PDF Processing**: Extracts text from both native and scanned PDFs using PyMuPDF and Tesseract OCR.
*   **Configurable Ontology**: Knowledge graph structure (nodes and relationships) is defined in a human-readable `config/ontology.yaml` file.
*   **LLM-Powered Extraction**: Uses an LLM to parse the extracted text and convert it into structured graph data (entities and relationships).
    *   Supports both local models (via Ollama) and remote APIs (e.g., DeepSeek, OpenAI).
    *   Uses a detailed prompt template (`config/extraction_prompt.txt`) for reliable, structured JSON output.
*   **Graph Database Integration**: Imports the structured data into a Neo4j database using `MERGE` queries to prevent duplication.
*   **End-to-End Pipeline**: A main script (`src/knowledge_extraction/main_pipeline.py`) orchestrates the entire workflow from PDF to Neo4j.

## Project Structure

```
.
├── config/                  # Configuration files
│   ├── ontology.yaml        # Defines the knowledge graph structure
│   └── extraction_prompt.txt # Prompt template for the LLM
├── data/                    # Data files
│   ├── example.pdf          # An example PDF document
│   └── extracted_knowledge.json # (Simulated) output from the LLM
├── src/
│   └── knowledge_extraction/ # Source code for the extraction pipeline
│       ├── pdf_parser.py     # Handles PDF reading and OCR
│       ├── llm_extractor.py  # Handles interaction with the LLM
│       ├── neo4j_importer.py # Handles importing data into Neo4j
│       └── main_pipeline.py  # Orchestrates the entire pipeline
├── tests/                   # Unit tests
├── .env.example             # Example environment variables file
├── pytest.ini               # Configuration for pytest
└── requirements.txt         # Python package dependencies
```

## Setup and Installation

### 1. Prerequisites

You must have the Tesseract OCR engine installed on your system.

On Debian/Ubuntu:
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-chi-sim
```
The `tesseract-ocr-chi-sim` package is for Simplified Chinese language support.

### 2. Clone the Repository

```bash
git clone <repository_url>
cd <repository_name>
```

### 3. Set up Environment

It is recommended to use a Python virtual environment.
```bash
python3 -m venv venv
source venv/bin/activate
```

Create a `.env` file by copying the example and fill in your details:
```bash
cp .env.example .env
```
Now, edit the `.env` file to add your API keys and database credentials.

### 4. Install Dependencies

Install all the required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

The main pipeline can be run from the root of the project directory:

```bash
python3 src/knowledge_extraction/main_pipeline.py
```

This script will:
1.  Read the text from `data/extracted_text_ocr.txt`.
2.  Check for a pre-existing `data/extracted_knowledge.json`. If it exists (as the dummy file does), it will use it. Otherwise, it would call the LLM API defined in your `.env` file.
3.  Attempt to connect to the Neo4j database specified in your `.env` file, clear it, and import the knowledge graph data.

**Note on the current implementation:** Due to limitations in the development environment (aggressive timeouts), the LLM extraction and Neo4j import steps could not be fully tested. The pipeline is designed to use a dummy data file (`data/extracted_knowledge.json`) and fail gracefully if it cannot connect to the database, allowing the overall structure to be demonstrated.

## Next Steps

*   **Part 2: Knowledge Visualization**: Develop a web-based interface using FastAPI to query the Neo4j database and visualize the graph results dynamically.
*   **Part 3: Knowledge Q&A**: Build the question-answering system to provide decision support for hydropower dispatch operations.
