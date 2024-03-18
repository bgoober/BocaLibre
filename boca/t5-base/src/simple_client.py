from uagents import Bureau
from agents.simple_agent import simple

if __name__ == "__main__":
    bureau = Bureau(endpoint="http://127.0.0.1:8004/submit", port=8004)
    print(f"adding simple agent to bureau: {simple.address}")
    bureau.add(simple)
    bureau.run()
