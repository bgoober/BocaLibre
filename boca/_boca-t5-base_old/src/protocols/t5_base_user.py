from uagents import Context, Protocol
from messages.t5_base import TranslationRequest, TranslationResponse, Error
from agents.t5_base_agent import T5_BASE_AGENT_ADDRESS, INPUT_TEXT

# Create an instance of Protocol with a label "T5BaseModelUser"
t5_base_user = Protocol(name="T5BaseModelUser", version="0.0.1")


@t5_base_user.on_interval(period=30, messages=TranslationRequest)
async def transcript(ctx: Context):
    TranslationDone = ctx.storage.get("TranslationDone")

    if not TranslationDone:
        await ctx.send(T5_BASE_AGENT_ADDRESS, TranslationRequest(text=INPUT_TEXT))


@t5_base_user.on_message(model=TranslationResponse)
async def handle_data(ctx: Context, sender: str, response: TranslationResponse):
    ctx.logger.info(f"Translated text:  {response.translated_text}")
    ctx.storage.set("TranslationDone", True)


@t5_base_user.on_message(model=Error)
async def handle_error(ctx: Context, sender: str, error: Error):
    ctx.logger.info(f"Got error from uagent: {error}")