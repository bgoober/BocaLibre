if NATIVE_LANGUAGE == "":
    raise Exception("Provide a valid native language -- English, French, German, or Romanian.")

if TARGET_LANGUAGE == "":
    raise Exception("Provide a valid native language -- English, French, German, or Romanian.")

if BOCA_LIBRE == "":
    raise Exception("Provide the correct BOCA_LIBRE matchmaking agent address.")

if HUGGING_FACE_ACCESS_TOKEN == "":
    raise Exception("Provide a HuggingFace API key for t5_base translation requests.")

if T5_BASE_AGENT_ADDRESS == "":
    raise Exception("Provide your t5_base_agent address for translation requests.")

# text you want to translate
user_input = input("Type a syntactically correct message in your native language.")

# check if user input is empty
if user_input == "":
    raise Exception("User input is empty. Please provide a valid input.")

INPUT_TEXT = "translate " + NATIVE_LANGUAGE + " to " + TARGET_LANGUAGE + ": " + user_input

### Define the t5_base protocol
t5_base = Protocol()

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

### Define the boca protocol
boca = Protocol()

@boca.on_event("startup")
async def request_chat(ctx: Context, BOCA_LIBRE, message=BocaChatRequest)
    ctx.logger.info(f"Requesting a new chat... {NATIVE_LANGUAGE} to {TARGET_LANGUAGE}.")
    await ctx.send(BOCA_LIBRE, BocaChatRequest(native=NATIVE_LANGUAGE, translation=TARGET_LANGUAGE))

@boca.on_message(model=BocaChatRequestResponse)
async def handle_chat_request_response(ctx: Context, sender: str, message=BocaChatRequestResponse)
    ctx.logger.info(f"Received chat request response.\n
                      New chat partner: {message.interlocutor}")
    ctx.storage.set("interlocutor": message.interlocutor)
    
@boca.on_message(model=TranslationResponse)
# when the agent receives a translation response from the base agent, it will send a BocaMessage to the BOCA_LIBRE using the input text and the translated text from the response
async def send_boca_message(ctx: Context, sender: str, response: TranslationResponse):
    ctx.storage.get("interlocutor")
    await ctx.send(interlocutor, BocaMessage(native=user_input, translation=response.translated_text))
    ctx.logger.info(f"Sent BocaMessage to BOCA_LIBRE: {BOCA_LIBRE}")

@boca.on_message(model=BocaMessage)
async def handle_boca_message(ctx: Context, sender: str, message: BocaMessage):
    ctx.logger.info(f"Received BocaMessage from {sender}: {message.native} -> {message.translation}")
    # add the BocaMessage to the storage as a list with indices for each message received chronologically
    messages = ctx.storage.get("messages", [])
    messages.append(message)
    ctx.storage.set("messages", messages)

# register the protocol with the agent
agent.include(boca, t5_base)

### Define the message models

# to request to the hf agent
class TranslationRequest(Model):
    text: str

# response from the hf agent
class TranslationResponse(Model):
    translated_text: str

# error from hf agent
class Error(Model):
    error: str

# message to send to whoever you are matched with
class BocaMessage(Model):
    native: str
    translation: str

#BocaChatRequest Message Model
class BocaChatRequest(Model):
    native: str
    translation: str

#BocaChatRequest Response Messsage Model
class BocaChatRequestResponse(Model):
    native: str
    translation: str
    interlocutor: str


### Define the boca protocol
boca_match_maker = Protocol()

@boca_match_maker.on_message(model=BocaChatRequest)
async def handle_chat_request(ctx: Context, sender: str, message=BocaChatRequest)
    ctx.logger.info(f"Recieved match making request from {sender}, {message.native} to {message.translation}.")
    ctx.storage.get("pool": [])
    ctx.storage.append("pool", [(sender, message.native, message.translation)])


async def match_make(user_1, user_2)
    pool = ctx.storage.get("pool")

    if pool:
        for i in pool:
            user_1 = ctx.storage.get()


agent.include(boca_match_maker)

#BocaChatRequest Message Model
class BocaChatRequest(Model):
    native: str
    translation: str

#BocaChatRequest Response Messsage Model
class BocaChatRequestResponse(Model):
    native: str
    translation: str
    interlocutor: str