from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low

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