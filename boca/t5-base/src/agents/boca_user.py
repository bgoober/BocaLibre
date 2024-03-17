from uagents import Agent, Context, Protocol
from messages.t5_base import TranslationRequest, TranslationResponse, Error
from messages.boca_libre import BocaMessage
from messages.match_maker import MatchRequest, MatchResponse, UpdateMatchRequest, UpdateMatchRequestResponse, Message
from uagents.setup import fund_agent_if_low
import os

NATIVE_LANGUAGE = "english"

# if the user did not input one of the options above, ignoring case, raise an exception
if NATIVE_LANGUAGE.lower() not in ["english", "french", "german", "romanian"]:
    raise Exception("Please provide a valid language.")

TARGET_LANGUAGE = "french"

if TARGET_LANGUAGE.lower() not in ["english", "french", "german", "romanian"]:
    raise Exception("Please provide a valid language.")

if NATIVE_LANGUAGE == TARGET_LANGUAGE:
    raise Exception("Native Language and Target Language can not be the same.")

# text you want to translate
user_input = input("input:")

T5_BASE_AGENT_ADDRESS = os.getenv("T5_BASE_AGENT_ADDRESS", "T5_BASE_AGENT_ADDRESS")

if T5_BASE_AGENT_ADDRESS == "T5_BASE_AGENT_ADDRESS":
    raise Exception(
        "You need to provide an T5_BASE_AGENT_ADDRESS, by exporting env, check README file"
    )

BOCA_MATCH_MAKER = os.getenv("BOCA_MATCH_MAKER", "BOCA_MATCH_MAKER")

if BOCA_MATCH_MAKER == "BOCA_MATCH_MAKER":
    raise Exception(
        "You need to provide an BOCA_MATCH_MAKER, by exporting env, check README file"
    )

INPUT_TEXT = (
    "translate " + NATIVE_LANGUAGE + " to " + TARGET_LANGUAGE + ": " + user_input
)

# Define user agent with specified parameters
user = Agent(
    name="boca_user",
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"],
)

# Check and top up the agent's fund if low
fund_agent_if_low(user.wallet.address())


@user.on_event("startup")
async def initialize_storage(ctx: Context):
    ctx.storage.set("TranslationDone", False)

# decorate user with a startup event to send a MatchRequest message to the match_maker agent
@user.on_event("startup")
async def request_chat(ctx: Context, BOCA_MATCH_MAKER, message=MatchRequest):
    ctx.logger.info(f"Requesting a new chat... {NATIVE_LANGUAGE} to {TARGET_LANGUAGE}.")
    await ctx.send(
        BOCA_MATCH_MAKER,
        MatchRequest(native=NATIVE_LANGUAGE, translation=TARGET_LANGUAGE),
   )


@user.on_message(model=BocaMessage)
async def handle_boca_message(ctx: Context, sender: str, message: BocaMessage):
    ctx.logger.info(
        f"Received BocaMessage from {sender}: {message.native} -> {message.translation}"
    )
    # add the BocaMessage to the storage as a list with indices for each message received chronologically
    messages = ctx.storage.get("messages", [])
    messages.append(message)
    ctx.storage.set("messages", messages)

# decorate the user agent to store the partner from the MatchResponse message from the match_maker agent
@user.on_message(model=MatchResponse)
async def store_partner(ctx: Context, sender: str, message: MatchResponse):
    ctx.storage.set("partner", message.partner)
    ctx.logger.info(f"Stored partner: {message.partner}")


# Create an instance of Protocol with a label "T5BaseModelUser"
t5_base_user = Protocol(name="T5BaseModelUser", version="0.0.1")


@t5_base_user.on_interval(period=30, messages=TranslationRequest)
async def transcript(ctx: Context):
    TranslationDone = ctx.storage.get("TranslationDone")

    if not TranslationDone:
        await ctx.send(T5_BASE_AGENT_ADDRESS, TranslationRequest(text=INPUT_TEXT))


@t5_base_user.on_message(model=TranslationResponse)
# when the agent receives a translation response from the base agent, it will send a BocaMessage to the interlocutor using the input text and the translated text from the response
async def send_boca_message(ctx: Context, sender: str, response: TranslationResponse):
    # get partner from storage and send partner the BocaMessage
    PARTNER = ctx.storage.get("partner")
    await ctx.send(
        PARTNER,
        BocaMessage(native=user_input, translation=response.translated_text),
    )
    ctx.logger.info(f"Sent BocaMessage to interlocutor: {PARTNER}")


@t5_base_user.on_message(model=Error)
async def handle_error(ctx: Context, sender: str, error: Error):
    ctx.logger.info(f"Got error from uagent: {error}")


# publish_manifest will make the protocol details available on agentverse.
user.include(t5_base_user, publish_manifest=True)

# Initiate the task
if __name__ == "__main__":
    t5_base_user.run()
