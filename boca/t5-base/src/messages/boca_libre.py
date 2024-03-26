from uagents import Model


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