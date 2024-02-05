from uagents import Bureau
from agents.alice import alice

if __name__ == "__main__":
    bureau = Bureau(endpoint="http://127.0.0.1:8002/submit", port=8002)
    print(f"adding Alice agent to bureau: {alice.address}")
    bureau.add(alice)
    bureau.run()
