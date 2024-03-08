from uagents import Bureau
from agents.partner_agent import agent

if __name__ == "__main__":
    bureau = Bureau(endpoint="http://127.0.0.1:8002/submit", port=8002)
    print(f"adding interlocutor agent to bureau: {agent.address}")
    bureau.add(agent)
    bureau.run()
