from uagents import Bureau
from agents.match_maker import match_maker

if __name__ == "__main__":
    bureau = Bureau(endpoint="http://127.0.0.1:8003/submit", port=8003)
    print(f"adding match-maker agent to bureau: {match_maker.address}")
    bureau.add(match_maker)
    bureau.run()
