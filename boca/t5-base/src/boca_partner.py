from uagents import Bureau
from agents.boca_partner import partner

if __name__ == "__main__":
    bureau = Bureau(endpoint="http://127.0.0.1:8002/submit", port=8002)
    print(f"adding boca_partner agent to bureau: {partner.address}")
    bureau.add(partner)
    bureau.run()
