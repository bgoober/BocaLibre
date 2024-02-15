from uagents import Bureau
from agents.interlocutor import interlocutor

if __name__ == "__main__":
    bureau = Bureau(endpoint="http://127.0.0.1:8002/submit", port=8002)
    print(f"adding interlocutor agent to bureau: {interlocutor.address}")
    bureau.add(interlocutor)
    bureau.run()
