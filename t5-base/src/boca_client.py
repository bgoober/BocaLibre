from uagents import Bureau
from agents.boca_user_agent import user

if __name__ == "__main__":
    bureau = Bureau(endpoint="http://127.0.0.1:8001/submit", port=8001)
    print(f"adding boca user agent to bureau: {user.address}")
    bureau.add(user)
    bureau.run()
