from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager
from src.graph_db import GraphDB, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

# --- App State ---
# We'll store the database connection in the app's state
# to be managed by the lifespan event handler.
app_state = {}

# --- Lifespan Event Handler ---
# This code runs on startup and shutdown.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup:
    print("API starting up...")
    db = GraphDB(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    app_state["db"] = db
    yield
    # On shutdown:
    print("API shutting down...")
    app_state["db"].close()

# Create the FastAPI app with the lifespan handler
app = FastAPI(lifespan=lifespan)

# --- Static Files Mounting ---
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

# --- API Endpoints ---

@app.get("/api/hello")
async def read_root():
    """A simple test endpoint."""
    return {"message": "Hello from the Hydropower KG API!"}

from pydantic import BaseModel
from typing import Dict, Any

class NodeUpdatePayload(BaseModel):
    id: str
    properties: Dict[str, Any]

@app.get("/api/search")
async def search_graph_endpoint(q: str = ""):
    """
    Searches the knowledge graph for a given query term.
    Returns nodes and links for visualization.
    """
    db = app_state.get("db")
    if not db or not db.driver:
        return {"error": "Database not connected"}

    # If the query is empty, return all nodes (or a limited sample)
    return db.search_graph(q)

from src.qa_system import get_recommendation

class QARequest(BaseModel):
    station: str
    flow: float
    level: float

@app.post("/api/node/update")
async def update_node_endpoint(payload: NodeUpdatePayload):
    """
    Updates the properties of a specific node.
    """
    db = app_state.get("db")
    if not db or not db.driver:
        return {"error": "Database not connected"}

    return db.update_node_properties(payload.id, payload.properties)

@app.post("/api/qna")
async def qna_endpoint(payload: QARequest):
    """
    Provides a dispatch recommendation based on current conditions.
    """
    db = app_state.get("db")
    if not db or not db.driver:
        return {"error": "Database not connected"}

    # Step 1: Find relevant rules from the knowledge graph
    rules = db.find_rules_for_station(payload.station)
    if not rules:
        return {"recommendation": f"No specific dispatch rules found for station '{payload.station}' in the knowledge graph."}

    # Step 2: Use LLM to get a recommendation based on the rules and conditions
    recommendation = get_recommendation(
        station=payload.station,
        flow=payload.flow,
        level=payload.level,
        rules=rules
    )

    return {"recommendation": recommendation}
