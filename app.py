from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
from openai import AsyncOpenAI
from agents import Agent, Runner
from agents import OpenAIChatCompletionsModel

# Velocity-backed OpenAI-compatible client
velocity_client = AsyncOpenAI(
    api_key=os.environ["VELOCITY_API_KEY"],
    base_url=os.environ["VELOCITY_BASE_URL"],
)

agent = Agent(
    name="Support Agent",
    instructions="Help customers with order status",
    # IMPORTANT: pass a Model instance, not a string
    model=OpenAIChatCompletionsModel(
        model="openai.openai/gpt-5.2",   # Velocity's model routing string is fine here
        openai_client=velocity_client,
    ),
)

async def main():
    result = await Runner.run(agent, input="Where is my order?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
