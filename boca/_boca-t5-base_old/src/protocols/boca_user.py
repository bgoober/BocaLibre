from uagents import Protocol, Context
from messages.boca_message import (
    BocaMessage,
    MatchRequest,
    MatchResponse,
    TranslationResponse,
)
from agents.user_agent import (
    NATIVE_LANGUAGE,
    TARGET_LANGUAGE,
    BOCA_MATCH_MAKER,
    user_input,
    partner,
)


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
