from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low
import os, ast, threading, uuid, asyncio, math


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


def prompt_for_user_input(ctx):
    while True:
        user_input = input("Enter a message: ")
        asyncio.run(handle_user_input(ctx, user_input))


# Start the thread in the startup event
@user.on_event("startup")
async def startup(ctx: Context):
    # Start a new thread that prompts for user input
    threading.Thread(target=prompt_for_user_input, args=(ctx,), daemon=True).start()


async def handle_user_input(ctx: Context, user_input: str):
    # Generate a unique UUID for the new user input
    input_id = str(uuid.uuid4())

    # Try to get the dictionaries of user inputs from the context storage
    user_inputs_queue = ctx.storage.get("user_inputs_queue")
    if user_inputs_queue is None:
        user_inputs_queue = {}

    user_inputs_store = ctx.storage.get("user_inputs_store")
    if user_inputs_store is None:
        user_inputs_store = {}

    # Add the new user input to the dictionaries with the UUID as the key
    user_inputs_queue[input_id] = user_input
    user_inputs_store[input_id] = user_input

    # Save the updated dictionaries back to the context storage
    ctx.storage.set("user_inputs_queue", user_inputs_queue)
    ctx.storage.set("user_inputs_store", user_inputs_store)

    # Format the input text
    input_text = (
        "translate " + NATIVE_LANGUAGE + " to " + TARGET_LANGUAGE + ": " + user_input
    )

    while True:
        try:
            # Send the TranslationRequest message to the t5_base model
            if T5_BASE_AGENT_ADDRESS:
                await ctx.send(
                    T5_BASE_AGENT_ADDRESS,
                    TranslationRequest(id=input_id, text=input_text),
                )
                ctx.logger.info(f"Sent TranslationRequest to {T5_BASE_AGENT_ADDRESS}")

            # Remove the input from the queue
            del user_inputs_queue[input_id]
            ctx.storage.set("user_inputs_queue", user_inputs_queue)

            break
        except Exception as e:
            # If the request is not successful due to rate limiting, wait for the estimated time and then try again
            error_message = str(e)
            if (
                "Error: {'error': 'Model google-t5/t5-base is currently loading"
                in error_message
            ):
                estimated_time = float(
                    error_message.split("'estimated_time': ")[1].split("}")[0]
                )
                await asyncio.sleep(math.ceil(estimated_time))
            else:
                raise e

    return input_id


@user.on_message(model=BocaMessage)
async def handle_boca_message(ctx: Context, sender: str, message: BocaMessage):
    ctx.logger.info(
        f"Received BocaMessage from {sender}: {message.native} --> {message.translation}"
    )
    # add the BocaMessage to the storage as a list with indices for each message received chronologically
    try:
        messages = ctx.storage.get("messages")
    except KeyError:
        # If the key is not found, use an empty list as the default value
        messages = []
    messages.append(message)
    ctx.storage.set("messages", messages)


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

    # Try to get the dictionary of user inputs from the context storage
    user_inputs_store = ctx.storage.get("user_inputs_store")
    if user_inputs_store is None:
        user_inputs_store = {}

    # Retrieve the native text from the dictionary using the identifier from the response
    native_text = user_inputs_store.get(response.id)

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


# TODO: Add a message queue for new user input.
# Add the ability to handle the t5_base rate limit error messages, then send those messages to the user
# once the rate limit has been lifted. One message at a time.
# OR send ALL the messages, and refactor t5_base to handle multiple messages at once in a single payload.
