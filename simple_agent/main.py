import asyncio
import logging
import os
import traceback

from dotenv import load_dotenv
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

model = ChatOpenAI(
    model_name=os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
    temperature=float(os.getenv("MODEL_TEMPERATURE", 0.0)),
    max_tokens=int(os.getenv("MODEL_MAX_TOKENS", 1000)),
)

server_params = StdioServerParameters(
    command="npx",
    env={"FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY")},
    args=["firecrawl-mcp"],
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            try:
                agent = create_react_agent(
                    model=model,
                    tools=tools,
                )
                logging.info("Agent is ready. Type your input:")
            except Exception as e:
                logging.error(f"Error creating agent: {e}")
                traceback.print_exc()
                return

            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can scrape web,"
                    " crawl and extract information  using firecrawl tools. Think step by step and help the user.",
                }
            ]

            print("Available tools:", *[tool.name for tool in tools])
            while True:
                user_input = input("\nYou: ")
                if user_input.lower() in ["exit", "quit"]:
                    print("Exiting the chat.")
                    break
                messages.append(
                    {"role": "user", "content": user_input[:175000]}
                )  # Limit input size for openai
                try:
                    agent_response = await agent.ainvoke({"messages": messages})
                    ai_message = agent_response["messages"][-1].content
                    print(f"\nAI: {ai_message}")
                except Exception as e:
                    logging.error(f"Error during agent invocation: {e}")
                    traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting the chat.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
