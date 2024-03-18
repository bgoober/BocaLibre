from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low


class BocaMessage(Model):
    native: str
    translation: str


# Define user agent with specified parameters
simple = Agent(
    name="simple_agent", port=8004, endpoint=["http://127.0.0.1:8004/submit"]
)

fund_agent_if_low(simple.wallet.address())


@simple.on_event("startup")
# print the agent's address
async def say_address(ctx: Context):
    ctx.logger.info(f"Simple agent address: {simple.address}")


@simple.on_message(model=BocaMessage)
async def handle_boca_message(ctx: Context, sender: str, message: BocaMessage):
    ctx.logger.info(f"Received BocaMessage from {sender}")
    ctx.logger.info(message)


simple.run()
