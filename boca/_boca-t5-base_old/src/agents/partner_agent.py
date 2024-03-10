from uagents import Agent, Context, Protocol
from messages.t5_base import TranslationRequest, TranslationResponse, Error
from messages.boca_message import BocaMessage
from uagents.setup import fund_agent_if_low
import os

NATIVE_LANGUAGE = input(
    "What is your native language? -- English, French, German, or Romanian?"
)

# if the user did not input one of the options above, ignoring case, raise an exception
if NATIVE_LANGUAGE.lower() not in ["english", "french", "german", "romanian"]:
    raise Exception("Please provide a valid language.")

TARGET_LANGUAGE = input(
    "What is your target language? -- English, French, German, or Romanian?"
)

if TARGET_LANGUAGE.lower() not in ["english", "french", "german", "romanian"]:
    raise Exception("Please provide a valid language.")

if NATIVE_LANGUAGE == TARGET_LANGUAGE:
    raise Exception("Native Language and Target Language can not be the same.")

# text you want to translate
user_input = input("Type a syntactically correct message in your native language.")

# check if user input is empty, and if it is clean, meaning no malicious activity is attempted in terms of security violations
if user_input == "":
    raise Exception("User input is empty. Please provide a valid input.")

INPUT_TEXT = (
    "translate " + NATIVE_LANGUAGE + " to " + TARGET_LANGUAGE + ": " + user_input
)

T5_BASE_AGENT_ADDRESS = os.getenv("T5_BASE_AGENT_ADDRESS", "T5_BASE_AGENT_ADDRESS")

if T5_BASE_AGENT_ADDRESS == "T5_BASE_AGENT_ADDRESS":
    raise Exception(
        "You need to provide an T5_BASE_AGENT_ADDRESS, by exporting env, check README file"
    )

PARTNER = os.getenv(
    "PARTNER", "PARTNER"
)  # the address of the agent that we are going to send our BocaMessage to

if PARTNER == "PARTNER":
    raise Exception(
        "You need to provide an PARTNER, by exporting env, check README file"
    )

# Define user agent with specified parameters
agent = Agent(
    name="partner_agent",
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"],
)

# Check and top up the agent's fund if low
fund_agent_if_low(agent.wallet.address())


@agent.on_event("startup")
async def initialize_storage(ctx: Context):
    ctx.storage.set("TranslationDone", False)


# Create an instance of Protocol with a label "BocaT5Base"
boca_t5_base = Protocol(name="BocaT5Base", version="0.0.1")


@boca_t5_base.on_event("")
@boca_t5_base.on_interval(period=30, messages=TranslationRequest)
async def transcript(ctx: Context):
    TranslationDone = ctx.storage.get("TranslationDone")

    if not TranslationDone:
        await ctx.send(T5_BASE_AGENT_ADDRESS, TranslationRequest(text=INPUT_TEXT))


@boca_t5_base.on_message(model=TranslationResponse)
async def handle_data(ctx: Context, sender: str, response: TranslationResponse):
    ctx.logger.info(f"Translated text:  {response.translated_text}")
    ctx.storage.set("TranslationDone", True)


@boca_t5_base.on_message(model=TranslationResponse)
# when the agent receives a translation response from the base agent, it will send a BocaMessage to the interlocutor using the input text and the translated text from the response
async def send_boca_message(ctx: Context, sender: str, response: TranslationResponse):
    await ctx.send(
        PARTNER,
        BocaMessage(native=user_input, translation=response.translated_text),
    )
    ctx.logger.info(f"Sent BocaMessage to interlocutor: {PARTNER}")


@boca_t5_base.on_message(model=BocaMessage)
async def handle_boca_message(ctx: Context, sender: str, message: BocaMessage):
    ctx.logger.info(
        f"Received BocaMessage from {sender}: {message.native} -> {message.translation}"
    )
    # add the BocaMessage to the storage as a list with indices for each message received chronologically
    messages = ctx.storage.get("messages", [])
    messages.append(message)
    ctx.storage.set("messages", messages)


@boca_t5_base.on_message(model=Error)
async def handle_error(ctx: Context, sender: str, error: Error):
    ctx.logger.info(f"Got error from uagent: {error}")


# publish_manifest will make the protocol details available on agentverse.
agent.include(boca_t5_base, publish_manifest=True)

agent.run()


# TODO: test locally

# to test locally, the partner agent must be the exact same as the main user agent, as they are two halves of the same product, in terms of a user.
