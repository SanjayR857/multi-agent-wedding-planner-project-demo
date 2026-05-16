from dotenv import load_dotenv
load_dotenv()
import os 
import asyncio
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_agent
from app.prompts import TravelAgentPrompts, VenueAgentPrompts, PlaylistAgentPrompts, Main_Agent_Prompts
from app.models import WeddingState
from app.tools import query_playlist_db, web_search

class WeddingAgentService:
    """Service class for initializing and managing agents."""
    
    def __init__(self):
        self.model = AzureChatOpenAI(
            azure_deployment=os.getenv("OPENAI_DEFAULT_DEPLOYMENT"),  
            api_version="2025-04-01-preview",  
            azure_endpoint=os.getenv("OPENAI_ENDPOINT"),  
        )

    async def create_travel_agent(self):
        """Creates the Travel Agent with MCP tools."""
        from app.MCP import get_tools
        mcp_tools = await get_tools()
        return create_agent(
            model=self.model,
            tools=mcp_tools,
            system_prompt=TravelAgentPrompts.SYSTEM_PROMPT
        )

    async def create_venue_agent(self):
        """Creates the Venue Agent."""
        return create_agent(
            model=self.model,
            tools=[web_search],
            system_prompt=VenueAgentPrompts.SYSTEM_PROMPT
        )

    async def create_playlist_agent(self):
        """Creates the Playlist Agent."""
        return create_agent(
            model=self.model,
            tools=[query_playlist_db],
            system_prompt=PlaylistAgentPrompts.SYSTEM_PROMPT
        )

    async def create_main_agent(self):
        """Creates the Main Coordinator Agent. Imports tools locally to avoid circular dependencies."""
        from app.tools import search_flights, search_venue, search_playlist, update_state
        return create_agent(
            model=self.model,
            tools=[search_flights, search_venue, search_playlist, update_state],
            state_schema=WeddingState,
            system_prompt=Main_Agent_Prompts.SYSTEM_PROMPT
        )

    async def initialize_all_agents(self):
        """Initialize all agents concurrently."""
        travel_agent = await self.create_travel_agent()
        venue_agent = await self.create_venue_agent()
        playlist_agent = await self.create_playlist_agent()
        main_agent = await self.create_main_agent()
        return travel_agent, venue_agent, playlist_agent, main_agent


# Instantiate the service
agent_service = WeddingAgentService()

# Export the agent instances for compatibility with tools.py
try:
    travel_agent, venue_agent, playlist_agent, main_agent = asyncio.run(agent_service.initialize_all_agents())
except RuntimeError:
    import nest_asyncio
    nest_asyncio.apply()
    travel_agent, venue_agent, playlist_agent, main_agent = asyncio.run(agent_service.initialize_all_agents())
