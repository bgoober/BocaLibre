from uagents import Protocol, Context

from messages.t5_base import TranslationRequest, TranslationResponse, Error

from agents.t5_base_agent import translate_text

# Create an instance of Protocol with a label "T5BaseModelAgent"
t5_base_agent = Protocol(name="T5BaseModelAgent", version="0.0.1")


@t5_base_agent.on_message(
    model=TranslationRequest, replies={TranslationResponse, Error}
)
async def handle_request(ctx: Context, sender: str, request: TranslationRequest):
    # Log the request details
    ctx.logger.info(f"Got request from  {sender}")

    await translate_text(ctx, sender, request.text)
