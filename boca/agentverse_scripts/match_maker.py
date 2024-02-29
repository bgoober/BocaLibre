# MatchMaker Protocol

boca_match_maker = Protocol(name="BocaMatchMaker", version="0.0.1")

@boca_match_maker.on_event("startup")
async def clear_set_storage(ctx: Context):
    ctx.storage.clear()
    ctx.storage.set("match_queue", [])

# upon receiving a MatchRequest message, add the agent adress of the sender, the native language and the target language from the sender's message to the match_queue
@boca_match_maker.on_message(model=MatchRequest)
async def handle_match_request(ctx: Context, sender: str, message: MatchRequest):
    match_queue = ctx.storage.get("match_queue")
    # check if the sender agent is already in the match_queue, and if so, reject the request
    for match in match_queue:
        if match["agent"] == sender:
            ctx.logger.info("User already in queue. Please send an UpdateMatchRequest to change your match request settings.")
    match_queue.append({"agent": sender, "native_language": message.native_language, "target_language": message.target_language})
    ctx.storage.append("match_queue", match_queue)
    ctx.send(sender, Message(message="Match request added to queue."))
    # the MatchResponse message is sent when two users are matched. A match occurs when the 1st user's native language is the 2nd user's target language and vice versa
    # the address of the 1st user and their native language are sent to the 2nd user, and vice versa
    # once the two user's are matched, they are removed from the match_queue in storage
    for match in match_queue:
        for match2 in match_queue:
            if match["native_language"] == match2["target_language"] and match["target_language"] == match2["native_language"]:
                ctx.send(match["agent"], MatchResponse(partner=match2["agent"], partner_native_language=match2["native_language"]))
                ctx.send(match2["agent"], MatchResponse(partner=match["agent"], partner_native_language=match["native_language"]))
                match_queue.remove(match)
                match_queue.remove(match2)
                ctx.storage.set("match_queue", match_queue)
                ctx.logger.info(f"Match found for {match['agent']} and {match2['agent']}.")
                ctx.logger.info(f"Match queue updated.")
                ctx.logger.info(f"Match queue: {match_queue}")
            else:
                ctx.logger.info("No matching users found, yet.")

# upon receiving an UpdateMatchRequest message, the agent updates the match_queue with the new native language and target language from the sender's message
@boca_match_maker.on_message(model=UpdateMatchRequest)
async def handle_update_match_request(ctx: Context, sender: str, message: UpdateMatchRequest):
    ctx.logger.info(f"Received UpdateMatchRequest from {sender}.")
    match_queue = ctx.storage.get("match_queue")
    for match in match_queue:
        if match["agent"] == sender:
            match["native_language"] = message.native_language
            match["target_language"] = message.target_language
            ctx.storage.set("match_queue", match_queue)
            ctx.logger.info(f"Match request for {sender} updated.")
            ctx.send(sender, UpdateMatchRequestResponse(success=True))
        else:
            ctx.logger.info(f"Agent {sender} not found in match queue. Please send a MatchRequest to add your request to the queue.")
            ctx.send(sender, UpdateMatchRequestResponse(success=False))

# Messages

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

# register the protocol with the agent
agent.include(boca_match_maker, publish_manifest=True)