from uagents import Agent, Context

agent = Agent()


@agent.on_event("startup")
async def say_hi(ctx: Context):
    ctx.logger.info("Hello, world!")
    ctx.logger.info(agent.address)


agent.run()
