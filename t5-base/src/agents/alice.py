from uagents import Agent, Context, Protocol
from messages.wallet_messaging import WalletMessage
from uagents.setup import fund_agent_if_low
from messages.wallet_messaging import WalletMessage

alice = Agent(
    name="alice",
    port=8002,
    endpoint=["http://127.0.0.1:8002/submit"],
    enable_wallet_messaging=True)

# Check and top up the agent's fund if low
fund_agent_if_low(alice.wallet.address())

# Create an instance of Protocol with a label "T5BaseModelUser"
alice_recipient = Protocol(name="AliceRecipientTest", version="0.0.1")

@alice.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("agent address: " + ctx.address)

@alice.on_wallet_message()
async def log(ctx: Context, msg: WalletMessage):
    ctx.logger.info(f"Got wallet message: {msg.text}")

# publish_manifest will make the protocol details available on agentverse.
alice.include(alice_recipient, publish_manifest=True)

if __name__ == "__main__":
    alice.run()