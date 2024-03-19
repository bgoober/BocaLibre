from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low
import os, ast, threading, time, uuid


### Messages ###


class TranslationRequest(BaseModel):
    text: str
    id: str


class TranslationResponse(BaseModel):
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
    native: str
    translation: str


# NOTE: The first letter of the native language and target language variables MUST be capitalized or the AI model will not properly understand the request.
NATIVE_LANGUAGE = "English"

# if the user did not input one of the options above, ignoring case, raise an exception
if NATIVE_LANGUAGE.lower() not in ["english", "french", "german", "romanian"]:
    raise Exception("Please provide a valid language.")

# NOTE: The first letter of the native language and target language variables MUST be capitalized or the AI model will not properly understand the request.
TARGET_LANGUAGE = "French"

if TARGET_LANGUAGE.lower() not in ["english", "french", "german", "romanian"]:
    raise Exception("Please provide a valid language.")

if NATIVE_LANGUAGE == TARGET_LANGUAGE:
    raise Exception("Native Language and Target Language can not be the same.")

T5_BASE_AGENT_ADDRESS = os.getenv("T5_BASE_AGENT_ADDRESS", "T5_BASE_AGENT_ADDRESS")

if T5_BASE_AGENT_ADDRESS == "T5_BASE_AGENT_ADDRESS":
    raise Exception(
        "You need to provide an T5_BASE_AGENT_ADDRESS, by exporting env, check README file"
    )

# BOCA_MATCH_MAKER = os.getenv("BOCA_MATCH_MAKER", "BOCA_MATCH_MAKER")

# if BOCA_MATCH_MAKER == "BOCA_MATCH_MAKER":
#    raise Exception(
#        "You need to provide an BOCA_MATCH_MAKER, by exporting env, check README file"
#    )


PARTNER = "agent1q0nflz2ll4027d5ufzte9cgmpjzwnvuy87rltdnppzcp7vteyzpp7vy209p"

# Define user agent with specified parameters
user = Agent(
    name="boca_user",
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"],
)

# Check and top up the agent's fund if low
fund_agent_if_low(user.wallet.address())


import uuid


@user.on_event("startup")
async def prompt_user_input(ctx: Context):
    # Prompt the user for input
    user_input = input("Enter a message: ")

    # Generate a unique identifier for this input
    input_id = str(uuid.uuid4())

    # Get the dictionary of user inputs from the context storage
    user_inputs = ctx.storage.get("user_inputs", {})

    # Store the user's input in the dictionary with the unique identifier
    user_inputs[input_id] = user_input

    # Save the dictionary of user inputs back to the context storage
    ctx.storage.set("user_inputs", user_inputs)

    # Format the input text
    input_text = "translate English to French: " + user_input

    # Send a TranslationRequest with the user's input and the unique identifier
    await ctx.send(
        T5_BASE_AGENT_ADDRESS, TranslationRequest(text=input_text, id=input_id)
    )


def wait_for_user_input(ctx):
    # Wait for 2 minutes
    time.sleep(120)

    # Prompt the user for input
    user_input = input("Enter a message: ")

    # Generate a unique identifier for this input
    input_id = str(uuid.uuid4())

    # Get the dictionary of user inputs from the context storage
    user_inputs = ctx.storage.get("user_inputs", {})

    # Store the user's input in the dictionary with the unique identifier
    user_inputs[input_id] = user_input

    # Save the dictionary of user inputs back to the context storage
    ctx.storage.set("user_inputs", user_inputs)

    # Format the input text
    input_text = "translate English to French: " + user_input

    # Send a TranslationRequest with the user's input
    ctx.send(T5_BASE_AGENT_ADDRESS, TranslationRequest(text=input_text, id=input_id))


@user.on_message(model=BocaMessage)
async def handle_boca_message(ctx: Context, sender: str, message: BocaMessage):
    ctx.logger.info(
        f"Received BocaMessage from {sender}: {message.native} -> {message.translation}"
    )
    # add the BocaMessage to the storage as a list with indices for each message received chronologically
    messages = ctx.storage.get("messages", [])
    messages.append(message)
    ctx.storage.set("messages", messages)

    # Start a new thread that waits for user input and then sends a TranslationRequest
    threading.Thread(target=wait_for_user_input, args=(ctx,)).start()


# decorate the user agent to store the partner from the MatchResponse message from the match_maker agent
@user.on_message(model=MatchResponse)
async def store_partner(ctx: Context, sender: str, message: MatchResponse):
    ctx.storage.set("partner", message.partner)
    ctx.logger.info(f"Stored partner: {message.partner}")


# Create an instance of Protocol with a label "T5BaseModelUser"
t5_base_user = Protocol(name="T5BaseModelUser", version="0.0.1")


@user.on_message(model=TranslationResponse)
async def handle_boca_message(ctx: Context, sender: str, response: TranslationResponse):
    ctx.logger.info(f"{response.text}")

    # Convert the response text to a list containing a dictionary
    response_data = ast.literal_eval(response.text)

    # Extract the translated text
    translation = response_data[0]["translation_text"]

    ctx.logger.info(f"Translation: {translation}")

    # Get the dictionary of user inputs from the context storage
    user_inputs = ctx.storage.get("user_inputs", {})

    # Retrieve the native text from the dictionary using the identifier from the response
    native_text = user_inputs.get(response.id)

    if PARTNER:
        await ctx.send(
            PARTNER,
            BocaMessage(native=native_text, translation=translation),
        )
        ctx.logger.info(f"Sent BocaMessage to {PARTNER}")


@t5_base_user.on_message(model=Error)
async def handle_error(ctx: Context, sender: str, error: Error):
    ctx.logger.info(f"Got error from uagent: {error}")


# publish_manifest will make the protocol details available on agentverse.
user.include(t5_base_user, publish_manifest=True)
