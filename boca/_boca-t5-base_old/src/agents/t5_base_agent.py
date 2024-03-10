from uagents import Agent, Context, Protocol
from messages.t5_base import TranslationRequest, TranslationResponse, Error
from protocols.t5_base_agent import t5_base_agent
from uagents.setup import fund_agent_if_low
import os
import requests

# Get the HUGGING_FACE_ACCESS_TOKEN from environment variable or default to a placeholder string if not found.
HUGGING_FACE_ACCESS_TOKEN = os.getenv(
    "HUGGING_FACE_ACCESS_TOKEN", "HUGGING_FACE_ACCESS_TOKEN"
)

if HUGGING_FACE_ACCESS_TOKEN == "HUGGING_FACE_ACCESS_TOKEN":
    raise Exception(
        "You need to provide an HUGGING_FACE_ACCESS_TOKEN, by exporting env, follow README"
    )

T5_BASE_URL = "https://api-inference.huggingface.co/models/t5-base"

# Define headers for HTTP request, including content type and authorization details
HEADERS = {"Authorization": f"Bearer {HUGGING_FACE_ACCESS_TOKEN}"}

# Create an agent with predefined properties
agent = Agent(
    name="t5_base_agent",
    port=8002,
    endpoint=["http://127.0.0.1:8002/submit"],
)

# Ensure the agent has enough funds
fund_agent_if_low(agent.wallet.address())


async def translate_text(ctx: Context, sender: str, input_text: str):
    # Prepare the data
    payload = {"inputs": input_text}

    # Make the POST request and handle possible errors
    try:
        response = requests.post(T5_BASE_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            await ctx.send(
                sender, TranslationResponse(translated_text=f"{response.json()}")
            )
            return
        else:
            await ctx.send(sender, Error(error=f"Error: {response.json()}"))
            return
    except Exception as ex:
        await ctx.send(sender, Error(error=f"Exception Occurred: {ex}"))
        return


# publish_manifest will make the protocol details available on agentverse.
agent.include(t5_base_agent, publish_manifest=True)

agent.run()


# TODO: test locally, test client
