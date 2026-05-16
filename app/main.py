from tenacity import asyncio
from app.llm_services import main_agent
from app.models import WeddingState
from langchain.messages import HumanMessage


async def run_wedding_agent():
    
    response = await main_agent.ainvoke(
        {
            "messages": [HumanMessage(content="I'm from London and I'd like a wedding in Paris for 100 guests, jazz-genre")],
        },
        config={"tags": ["WP"], "recursion_limit": 40},  #  tag traces to make them easy to find in Langsmith. Increase number of steps the agent can take to 40.
)

if __name__ == "__main__":
    asyncio.run(run_wedding_agent())
