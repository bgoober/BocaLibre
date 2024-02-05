from uagents import Agent, Context
from messages.wallet_messaging import WalletMessage
from uagents.setup import fund_agent_if_low
from messages.t5_base import TranslationRequest, TranslationResponse
import os

# text you want to translate
INPUT_TEXT = "Hello, it is very nice to meet you! Would you like to go for a walk in the park? I think it is a beautiful day. I hope you are having a good time."

T5_BASE_AGENT_ADDRESS = os.getenv(
    "T5_BASE_AGENT_ADDRESS", "T5_BASE_AGENT_ADDRESS")

RECIPIENT = os.getenv(
    "RECIPIENT", "RECIPIENT")

# Define the native language and desired translation language
NATIVE_LANGUAGE = "English"
TRANSLATION_LANGUAGE = "German"

if T5_BASE_AGENT_ADDRESS == "T5_BASE_AGENT_ADDRESS" or RECIPIENT == "RECIPIENT":
    raise Exception(
        "You need to provide an T5_BASE_AGENT_ADDRESS and RECIPIENT, by exporting env, check README file")

# Define user agent with specified parameters
user = Agent(
    name="boca_user",
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"],
    enable_wallet_messaging=True
)

# Check and top up the agent's fund if low
fund_agent_if_low(user.wallet.address())



@user.on_event("startup")
async def initialize_storage(ctx: Context):
    ctx.storage.set("TranslationDone", False)
    ctx.storage.set("NativeLanguage", NATIVE_LANGUAGE)
    ctx.storage.set("TranslationLanguage", TRANSLATION_LANGUAGE)

@user.on_interval(period=30)
async def send_message(ctx: Context):
    TranslationDone = ctx.storage.get("TranslationDone")

    if not TranslationDone:
        ctx.logger.info("Sending message...")
        NativeLanguage = ctx.storage.get("NativeLanguage")
        TranslationLanguage = ctx.storage.get("TranslationLanguage")
        formatted_text = f"translate {NativeLanguage} to {TranslationLanguage}: {INPUT_TEXT}"
        await ctx.send(T5_BASE_AGENT_ADDRESS, TranslationRequest(text=formatted_text))

@user.on_message(model=TranslationResponse)
async def handle_translation_response(ctx: Context, sender: str, response: TranslationResponse):
    ctx.logger.info(f"Got translation: {response.translated_text}")
    await ctx.send_wallet_message(RECIPIENT, f"Original text: {INPUT_TEXT}\nTranslated text: {response.translated_text}")
    ctx.storage.set("TranslationDone", True)

# Initiate the task
if __name__ == "__main__":
    user.run()