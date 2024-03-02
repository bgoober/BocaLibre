# This agent script is designed to be used on the agentverse.ai website as a hosted agent.
# As such, is does not import all of the necessary modules to run locally.
# the boca user agent communicates with the t5_base agent, as well as the match_maker agent, as well as the another boca_user agent that they have been paired with for a chat (from the match_maker agent)

# to be stored in the .env file
if NATIVE_LANGUAGE == "":
    raise Exception(
        "Provide a valid native language -- English, French, German, or Romanian."
    )

# to be stored in the .env file
if TARGET_LANGUAGE == "":
    raise Exception(
        "Provide a valid native language -- English, French, German, or Romanian."
    )

# to be stored in the .env file
if BOCA_MATCH_MAKER == "":
    raise Exception("Provide the correct BOCA_MATCH_MAKER agent address.")

# to be stored in the .env file
if HUGGING_FACE_ACCESS_TOKEN == "":
    raise Exception("Provide a HuggingFace API key for t5_base translation requests.")

# to be stored in the .env file
if T5_BASE_AGENT_ADDRESS == "":
    raise Exception("Provide a t5_base_agent address for translation requests.")

# text you want to translate
user_input = input("Type a syntactically correct message in your native language.")

# check if user input is empty
if user_input == "":
    raise Exception("User input is empty. Please provide a valid input.")

INPUT_TEXT = (
    "translate " + NATIVE_LANGUAGE + " to " + TARGET_LANGUAGE + ": " + user_input
)

### Define the t5_base protocol
t5_base = Protocol(name="t5_base", version="0.0.1")


@t5_base.on_interval(period=30, messages=TranslationRequest)
async def transcript(ctx: Context):
    TranslationDone = ctx.storage.get("TranslationDone")
    if not TranslationDone:
        await ctx.send(T5_BASE_AGENT_ADDRESS, TranslationRequest(text=INPUT_TEXT))


@t5_base.on_message(model=TranslationResponse)
async def handle_data(ctx: Context, sender: str, response: TranslationResponse):
    ctx.logger.info(f"Translated text:  {response.translated_text}")
    ctx.storage.set("TranslationDone", True)


@t5_base.on_message(model=Error)
async def handle_error(ctx: Context, sender: str, error: Error):
    ctx.logger.info(f"Got error from uagent: {error}")


# Define the boca_user protocol
boca_user = Protocol(name="boca_user", version="0.0.1")


@boca_user.on_event("startup")
async def request_chat(ctx: Context, BOCA_MATCH_MAKER, message=MatchRequest):
    ctx.logger.info(f"Requesting a new chat... {NATIVE_LANGUAGE} to {TARGET_LANGUAGE}.")
    await ctx.send(
        BOCA_MATCH_MAKER,
        MatchRequest(native=NATIVE_LANGUAGE, translation=TARGET_LANGUAGE),
    )


@boca_user.on_message(model=MatchResponse)
async def handle_chat_request_response(
    ctx: Context, sender: str, message=MatchResponse
):
    ctx.logger.info(
        f"Received chat request response.\n" f"New chat partner: {message.partner}"
    )
    ctx.storage.set("partner", message.partner)


@boca_user.on_message(model=TranslationResponse)
# when the agent receives a translation response from the base agent, it will send a BocaMessage to the BOCA_LIBRE using the input text and the translated text from the response
async def send_boca_message(ctx: Context, sender: str, response: TranslationResponse):
    ctx.storage.get("partner")
    await ctx.send(
        partner, BocaMessage(native=user_input, translation=response.translated_text)
    )
    ctx.logger.info(f"Sent BocaMessage to BOCA_MATCH_MAKER agent: {BOCA_MATCH_MAKER}")


@boca_user.on_message(model=BocaMessage)
async def handle_boca_message(ctx: Context, sender: str, message: BocaMessage):
    ctx.logger.info(
        f"Received BocaMessage from {sender}: {message.native} -> {message.translation}"
    )
    # add the BocaMessage to the storage as a list with indices for each message received chronologically
    messages = ctx.storage.get("messages", [])
    messages.append(message)
    ctx.storage.set("messages", messages)


# register the protocol with the agent
agent.include(boca_user, t5_base)

# Messages


# to request to the hf agent
class TranslationRequest(Model):
    text: str


# response from the hf agent
class TranslationResponse(Model):
    translated_text: str


# error from hf agent
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


# Boca message to send to whoever you are matched with
class BocaMessage(Model):
    native: str
    translation: str


# TODO: write boca_user protocol
# send match request message to match_maker
# hanlde match response message from match_maker
# send update match request message to match_maker
# handle update match request response from match_maker
# store match response partner in storage
# send boca message to partner agent
# handle boca message from partner agent
# store message in storage

# TODO: Review t5_base protocol
# send translation request message to t5_base
# handle translation response message from t5_base
# handle error message from t5_base
