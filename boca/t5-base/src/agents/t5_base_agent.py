from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low
import os
import requests


### Messages ###


class TranslationRequest(Model):
    text: str
    id: str


class TranslationResponse(Model):
    text: str
    id: str


class Error(Model):
    error: str


class MatchRequest(Model):
    native_language: str
    target_language: str


class MatchResponse(Model):
    partner: str
    partner_native_language: str


class UpdateMatchRequest(Model):
    native_language: str
    target_language: str


class UpdateMatchRequestResponse(Model):
    success: bool


class Message(Model):
    message: str


class BocaMessage(Model):
    sender: str
    native: str
    translation: str

    def to_dict(self):
        return {
            "sender": self.sender,
            "native": self.native,
            "translation": self.translation,
        }


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
    seed=HUGGING_FACE_ACCESS_TOKEN,
    port=8000,
    endpoint=["http://127.0.0.1:8000/submit"],
)

# Ensure the agent has enough funds
fund_agent_if_low(agent.wallet.address())


async def translate_text(ctx: Context, sender: str, input_text: str, input_id: str):
    # Prepare the data
    payload = {"inputs": input_text}

    # Make the POST request and handle possible errors
    try:
        response = requests.post(T5_BASE_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            await ctx.send(
                sender, TranslationResponse(text=f"{response.json()}", id=input_id)
            )
            ctx.logger.info(f"payload: {payload}")
            ctx.logger.info(f"Response: {response.text}")
            return
        else:
            await ctx.send(sender, Error(error=f"Error: {response.json()}"))
            return
    except Exception as ex:
        await ctx.send(sender, Error(error=f"Exception Occurred: {ex}"))
        return


# Create an instance of Protocol with a label "T5BaseModelAgent"
t5_base_agent = Protocol(name="T5BaseModelAgent", version="0.0.1")


@t5_base_agent.on_message(
    model=TranslationRequest, replies={TranslationResponse, Error}
)
async def handle_request(ctx: Context, sender: str, request: TranslationRequest):
    # Log the request details
    ctx.logger.info(f"Got request from  {sender}: {request.text}")

    await translate_text(ctx, sender, request.text, request.id)


# publish_manifest will make the protocol details available on agentverse.
agent.include(t5_base_agent, publish_manifest=True)
