from uagents import Agent, Protocol, Context, Model

from uagents.setup import fund_agent_if_low
import asyncio, time

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


match_maker = Agent(
    name="match_maker", port=8003, endpoint=["http://127.0.0.1:8003/submit"]
)


# use the match_queue to find a match
def find_match(match_queue):
    i = 0
    while i < len(match_queue):
        match = match_queue[i]
        j = i + 1
        while j < len(match_queue):
            match2 = match_queue[j]
            if (
                match["native_language"] == match2["target_language"]
                and match["target_language"] == match2["native_language"]
            ):
                del match_queue[j]
                del match_queue[i]
                return match, match2
            else:
                j += 1
        else:
            i += 1
    return None, None


# Add a new function to remove old match requests
async def cleanup_match_queue(ctx: Context):
    try:
        while True:
            await asyncio.sleep(3600)  # Wait for 1 hour
            async with lock:
                match_queue = ctx.storage.get("match_queue")
                if match_queue is None:
                    match_queue = {}
                current_time = time.time()
                for sender, match in list(match_queue.items()):
                    # If the match request is more than 24 hours old, remove it
                    if current_time - match["timestamp"] > 24 * 3600:
                        del match_queue[sender]
                ctx.storage.set("match_queue", match_queue)
    except Exception as e:
        ctx.logger.error(f"An error occurred during match queue cleanup: {str(e)}")



lock = asyncio.Lock()

# Agent section

@match_maker.on_event("startup")
async def clear_set_storage(ctx: Context):
    ctx.storage.set("match_queue", {})


# Start the cleanup function when the agent starts
@match_maker.on_event("startup")
async def startup(ctx: Context):
    asyncio.create_task(cleanup_match_queue(ctx))
    ctx.storage.set("match_queue", {})


# Protocol section

boca_match_maker = Protocol(name="BocaMatchMaker", version="0.0.1")


# upon receiving a MatchRequest message, add the agent adress of the sender, the native language and the target language from the sender's message to the match_queue
@boca_match_maker.on_message(model=MatchRequest)
async def handle_match_request(ctx: Context, sender: str, message: MatchRequest):
    try:
        ctx.logger.info(f"Received MatchRequest from {sender}.")
        async with lock:
            match_queue = ctx.storage.get("match_queue")
            if match_queue is None:
                match_queue = {}

            # check if the sender agent is already in the match_queue, and if so, reject the request
            if sender in match_queue:
                ctx.logger.info(
                    "User already in queue. Please send an UpdateMatchRequest to change your match request settings."
                )
                return

            # Add the sender to the match_queue with their native and target languages
            match_queue[sender] = {
                "native_language": message.native_language,
                "target_language": message.target_language,
                "timestamp": time.time(),  # Add a timestamp
            }

            ctx.storage.set("match_queue", match_queue)
            await ctx.send(sender, Message(message="Match request added to queue."))

        # the MatchResponse message is sent when two users are matched. A match occurs when the 1st user's native language is the 2nd user's target language and vice versa
        # the address of the 1st user and their native language are sent to the 2nd user, and vice versa
        # once the two user's are matched, they are removed from the match_queue in storage
        match1, match2 = find_match(match_queue)
        if match1 and match2:
            await ctx.send(
                match1["agent"],
                MatchResponse(
                    partner=match2["agent"],
                    partner_native_language=match2["native_language"],
                ),
            )
            await ctx.send(
                match2["agent"],
                MatchResponse(
                    partner=match1["agent"],
                    partner_native_language=match1["native_language"],
                ),
            )
            ctx.storage.set("match_queue", match_queue)
            ctx.logger.info(f"Match found for {match1['agent']} and {match2['agent']}.")
            ctx.logger.info(f"Match queue updated.")
            ctx.logger.info(f"Match queue: {match_queue}")
    except Exception as e:
        ctx.logger.error(f"An error occurred: {str(e)}")


# upon receiving an UpdateMatchRequest message, the agent updates the match_queue with the new native language and target language from the sender's message
@boca_match_maker.on_message(model=UpdateMatchRequest)
async def handle_update_match_request(
    ctx: Context, sender: str, message: UpdateMatchRequest
):
    try:
        ctx.logger.info(f"Received UpdateMatchRequest from {sender}.")
        async with lock:
            match_queue = ctx.storage.get("match_queue")
            for match in match_queue:
                if match["agent"] == sender:
                    match["native_language"] = message.native_language
                    match["target_language"] = message.target_language
                    match["timestamp"] = time.time()  # Update the timestamp
                    ctx.storage.set("match_queue", match_queue)
                    ctx.logger.info(f"Match request for {sender} updated.")
                    ctx.send(sender, UpdateMatchRequestResponse(success=True))
                    return  # Exit the function after updating the match

            # If we get here, the sender was not found in the match_queue
            ctx.logger.info(
                f"Agent {sender} not found in match queue. Please send a MatchRequest to add your request to the queue."
            )
            ctx.send(sender, UpdateMatchRequestResponse(success=False))
    except Exception as e:
        ctx.logger.error(f"An error occurred: {str(e)}")


# register the protocol with the agent
match_maker.include(boca_match_maker, publish_manifest=False)

fund_agent_if_low(match_maker.wallet.address())
