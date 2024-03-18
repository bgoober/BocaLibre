from uagents import Agent

from protocols.match_maker import boca_match_maker

agent = Agent(
    name="boca_match_maker_agent",
    port=8000,
    endpoint=["http://127.0.0.1:8000/submit"],
)

# register the protocol with the agent
agent.include(boca_match_maker, publish_manifest=True)


agent.run()


# import match_maker protocol
