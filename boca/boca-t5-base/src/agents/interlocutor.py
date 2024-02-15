from uagents import Agent, Context
from messages.boca_message import BocaMessage

interlocutor = Agent(
    name="interlocutor",
    port=8002,
    endpoint=["http://127.0.0.1:8002/submit"],)



@interlocutor.on_message(model=BocaMessage)
async def handle_boca_message(ctx: Context, sender: str, message: BocaMessage):
    ctx.logger.info(f"Received BocaMessage from {sender}: {message.native} -> {message.translation}")
    # add the BocaMessage to the storage as a list with indices for each message received chronologically
    messages = ctx.storage.get("messages", [])
    messages.append(message)
    ctx.storage.set("messages", messages)



if __name__ == "__main__":
    interlocutor.run()