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
    sender: str
    native: str
    translation: str

    def to_dict(self):
        return {
            "sender": self.sender,
            "native": self.native,
            "translation": self.translation,
        }


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


# Define partner agent with specified parameters
partner = Agent(
    name="boca_partner",
    port=8002,
    endpoint=["http://127.0.0.1:8002/submit"],
)

# Check and top up the agent's fund if low
fund_agent_if_low(partner.wallet.address())


def prompt_for_user_input(ctx):
    while True:
        user_input = input("Enter a message: ")
        asyncio.run(handle_user_input(ctx, user_input))


@partner.on_event("startup")
async def startup(ctx: Context):
    # Prompt the partner for their native language
    while True:
        native_language = input(
            "Enter your native language (English, French, German, or Romanian): "
        )
        native_language = native_language.strip().capitalize()

        # Validate the native language
        if native_language.lower() in ["english", "french", "german", "romanian"]:
            break
        else:
            print("Please provide a valid language.")

    # Prompt the partner for their target language
    while True:
        target_language = input(
            "Enter your target language (English, French, German, or Romanian): "
        )
        target_language = target_language.strip().capitalize()

        # Validate the target language
        if target_language.lower() in ["english", "french", "german", "romanian"]:
            break
        else:
            print("Please provide a valid language.")

        # Check that the native and target languages are not the same
        if native_language == target_language:
            raise Exception("Native Language and Target Language can not be the same.")

    # Store the native and target languages in the agent's storage
    ctx.storage.set("native_language", native_language)
    ctx.storage.set("target_language", target_language)

    # Start a new thread that prompts for partner input
    threading.Thread(target=prompt_for_user_input, args=(ctx,), daemon=True).start()


@partner.on_event("startup")
async def request_match(ctx: Context):
    # on startup, after the user has set their native and target languages, send a MatchRequest to the match_maker agent
    native_language = ctx.storage.get("native_language")
    target_language = ctx.storage.get("target_language")
    try:
        if BOCA_MATCH_MAKER:
            await ctx.send(
                BOCA_MATCH_MAKER,
                MatchRequest(
                    native_language=native_language, target_language=target_language
                ),
            )
            ctx.logger.info(f"Sent MatchRequest to {BOCA_MATCH_MAKER}")
    except Exception as e:
        ctx.logger.info(f"Failed to reach match_maker: {e}")
        await asyncio.sleep(10)
        await ctx.send(
            BOCA_MATCH_MAKER,
            MatchRequest(
                native_language=native_language, target_language=target_language
            ),
        )
        ctx.logger.info(f"Retrying MatchRequest to {BOCA_MATCH_MAKER} after 10 seconds")


async def handle_user_input(ctx: Context, user_input: str):
    # Remove leading and trailing whitespace from the partner input
    user_input = user_input.strip()

    # Check if the partner input is empty
    if not user_input.strip():
        ctx.logger.info("Received empty input, ignoring... please enter a message.")
        return

    # Generate a unique UUID for the new partner input
    input_id = str(uuid.uuid4())

    # Try to get the dictionaries of partner inputs from the context storage
    user_inputs_queue = ctx.storage.get("user_inputs_queue")
    if user_inputs_queue is None:
        user_inputs_queue = {}

    user_inputs_store = ctx.storage.get("user_inputs_store")
    if user_inputs_store is None:
        user_inputs_store = {}

    # Add the new partner input to the dictionaries with the UUID as the key
    user_inputs_queue[input_id] = user_input
    user_inputs_store[input_id] = user_input

    # Save the updated dictionaries back to the context storage
    ctx.storage.set("user_inputs_queue", user_inputs_queue)
    ctx.storage.set("user_inputs_store", user_inputs_store)

    # Try to get the set of sent message ids from the context storage
    sent_message_ids = ctx.storage.get("sent_message_ids")
    if sent_message_ids is None:
        sent_message_ids = []

    # Get the native and target languages from the context storage
    NATIVE_LANGUAGE = ctx.storage.get("native_language")
    TARGET_LANGUAGE = ctx.storage.get("target_language")

    # If there are messages in the queue, send them for translation
    for message_id in list(user_inputs_queue.keys()):
        message = user_inputs_queue[message_id]
        if message_id not in sent_message_ids:
            # Format the input text
            input_text = (
                "translate "
                + NATIVE_LANGUAGE
                + " to "
                + TARGET_LANGUAGE
                + ": "
                + message
            )

            while True:
                try:
                    # Send the TranslationRequest message to the t5_base model
                    if T5_BASE_AGENT_ADDRESS:
                        await ctx.send(
                            T5_BASE_AGENT_ADDRESS,
                            TranslationRequest(id=message_id, text=input_text),
                        )
                        ctx.logger.info(
                            f"Sent TranslationRequest to {T5_BASE_AGENT_ADDRESS}"
                        )

                    # Add the message id to the set of sent message ids
                    sent_message_ids.append(message_id)
                    ctx.storage.set("sent_message_ids", sent_message_ids)

                    break
                except Exception as e:
                    ctx.logger.error(f"An error occurred: {e}")
                    continue

    return input_id


# Create an instance of Protocol with a label "T5BaseModelUser"
t5_base_user = Protocol(name="T5BaseModelUser", version="0.0.1")


@t5_base_user.on_message(model=BocaMessage)
async def handle_boca_message(ctx: Context, sender: str, message: BocaMessage):
    ctx.logger.info(f"Received BocaMessage from {sender}:")
    ctx.logger.info(f"Native: {message.native}")
    ctx.logger.info(f"Translation: {message.translation}")
    # add the BocaMessage to the storage as a dictionary with sender's address as the key
    messages = ctx.storage.get("messages")
    if messages is None:
        # If the key is not found, use an empty dictionary as the default value
        messages = {}
    messages[sender] = message.to_dict()  # convert the BocaMessage object to a dict
    ctx.storage.set("messages", messages)


# decorate the partner agent to store the partner from the MatchResponse message from the match_maker agent
@t5_base_user.on_message(model=MatchResponse)
async def store_partner(ctx: Context, sender: str, message: MatchResponse):
    ctx.storage.set("partner", message.partner)
    ctx.logger.info(f"Stored partner: {message.partner}")


@t5_base_user.on_message(model=TranslationResponse)
async def handle_response_message(
    ctx: Context, sender: str, response: TranslationResponse
):
    ctx.logger.info(f"{response.text}")

    # Convert the response text to a list containing a dictionary
    response_data = ast.literal_eval(response.text)

    # Extract the translated text
    translation = response_data[0]["translation_text"]

    # Get the dictionaries of partner inputs from the context storage
    user_inputs_queue = ctx.storage.get("user_inputs_queue")
    user_inputs_store = ctx.storage.get("user_inputs_store")

    # Retrieve the native text from the dictionary using the identifier from the response
    native_text = user_inputs_store.get(response.id)

    # If the partner input is in the queue, remove it
    if response.id in user_inputs_queue:
        del user_inputs_queue[response.id]
        ctx.storage.set("user_inputs_queue", user_inputs_queue)
        ctx.logger.info(f"Removed message with id {response.id} from the queue")

    # Get the partner address from the context storage
    PARTNER = ctx.storage.get("partner")

    if PARTNER:
        await ctx.send(
            PARTNER,
            BocaMessage(
                sender=ctx.address, native=native_text, translation=translation
            ),
        )
        ctx.logger.info(f"Sent BocaMessage to {PARTNER}")


@t5_base_user.on_message(model=Error)
async def handle_error(ctx: Context, sender: str, error: Error):
    ctx.logger.info(f"Got error from uagent: {error}")

    error_message = str(error)
    if (
        "Error: {'error': 'Model google-t5/t5-base is currently loading"
        in error_message
    ):
        estimated_time = float(
            error_message.split("'estimated_time': ")[1].split("}")[0]
        )
        ctx.logger.info(
            f"Received timeout: {math.ceil(estimated_time)} seconds, retrying after timeout..."
        )
        await asyncio.sleep(math.ceil(estimated_time))

        # Get the last sent message id and its corresponding partner input
        sent_message_ids = ctx.storage.get("sent_message_ids")
        last_sent_message_id = sent_message_ids[-1]
        user_inputs_store = ctx.storage.get("user_inputs_store")
        last_user_input = user_inputs_store.get(last_sent_message_id)

        # Get the native and target languages from the context storage
        NATIVE_LANGUAGE = ctx.storage.get("native_language")
        TARGET_LANGUAGE = ctx.storage.get("target_language")

        # Format the input text
        input_text = (
            "translate "
            + NATIVE_LANGUAGE
            + " to "
            + TARGET_LANGUAGE
            + ": "
            + last_user_input
        )

        # Retry sending the TranslationRequest message to the t5_base model
        if T5_BASE_AGENT_ADDRESS:
            await ctx.send(
                T5_BASE_AGENT_ADDRESS,
                TranslationRequest(id=last_sent_message_id, text=input_text),
            )
            ctx.logger.info(f"Retried TranslationRequest to {T5_BASE_AGENT_ADDRESS}")


@t5_base_user.on_message(model=Message)
async def handle_message(ctx: Context, sender: str, message: Message):
    ctx.logger.info(f"Received message from {sender}: {message.message}")


# publish_manifest will make the protocol details available on agentverse.
partner.include(t5_base_user, publish_manifest=False)


# TODO: The AI model is not translating German to English. It is returning the same text as the input.
# The prefixes that we used for translating English to another language seem to not be working for a non-English
# native language to a different language. We need to update the prefixes to handle this case, maybe?
# It is unknown how the AI model is accepting non-english to something else.
