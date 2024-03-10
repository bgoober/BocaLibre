from uagents import Model


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
