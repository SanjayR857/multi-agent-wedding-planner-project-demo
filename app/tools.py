from langchain_core.messages import ToolMessage
from langchain_protocol.protocol import Command
from app.llm_services import travel_agent,venue_agent,playlist_agent
from openai.types.responses import response
from datetime import date
from langgraph.prebuilt.tool_node import ToolRuntime
from typing import Dict, Any 
from tavily import TavilyClient 
from langchain_community.utilities import SQLDatabase
from langchain.tools import tool 
from langchain.messages import HumanMessage


tavily_client = TavilyClient()


@tool
def web_search(query: str, search_number: int =1, max_search_number: int= 11) -> Dict[str, Any]:
    """ Search th web for information. You must track your search count by providing  search_number (starting 1) and max_search_number on every call. 
    Queries must use only plain text charcters. Do not use accented orspecial characters.
    (e.g., use 'capacite' instead of 'capacité')
    """
    if search_number>max_search_number:
        return {"message": "Maximum search number reached"}
    try:
        response = tavily_client.search(query=query)
        return response
    except Exception as e:
        return {"message": "Error searching the web: " + str(e)}


db = SQLDatabase.from_uri("sqlite:///resources/Chinook.db")


@tool
def query_playlist_db(query: str) -> str:

    """Query the database for playlist information"""

    try:
        return db.run(query)
    except Exception as e:
        return f"Error querying database: {e}"


@tool 
async def search_flights(runtime: ToolRuntime) -> str:
    """Travel agent searches for flights to the desired destination wedding location"""
    origin = runtime.state['origin']
    destination = runtime.state['destination']
    response = await travel_agent.ainvoke([HumanMessage(content="Find flights from {origin} to {destination}")])
    return response


@tool
async def search_venue(runtime: ToolRuntime) -> str:
    """Venue agent searches for the best venue for the desired destination wedding location"""
    destination = runtime.state['destination']
    response = await venue_agent.ainvoke([HumanMessage(content="Find the best venues in {destination}")])
    return response
    

@tool
async def search_playlist(runtime: ToolRuntime) -> str:
    """Playlist agent searches for the best playlist for the desired destination wedding location"""
    destination = runtime.state['destination']
    response = await playlist_agent.ainvoke([HumanMessage(content="Find the best playlists in {destination}")])
    return response 


@tool
async def update_state(origin: str, destination: str, guest_count: str, genre: str, runtime: ToolRuntime) -> str:
    """Update the state when you know all of the values: origin, destination, guest_count, genre. 
    This tool must be called alone, without any other tool calls. It must complete and return to make,
    the information available to other tools."""
    
    return Command(update={
        "origin": runtime.state['origin'],
        "destination": runtime.state['destination'],
        "guest_count": runtime.state['guest_count'],
        "genre": runtime.state['genre'],
        "messages": [ToolMessage(content="State updated successfully", tool_call_id=runtime.tool_call_id)]
    })