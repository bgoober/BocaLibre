from uagents import Bureau
from agents.boca_t5_base_user import boca_user

if __name__ == "__main__":
    bureau = Bureau(endpoint="http://127.0.0.1:8001/submit", port=8001)
    print(f"adding boca_user agent to bureau: {boca_user.address}")
    bureau.add(boca_user)
    bureau.run()
