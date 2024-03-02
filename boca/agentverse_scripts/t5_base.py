# this is designed to be used on the agentverse.ai website as a hosted agent.
# add the HUGGING_FACE_ACCESS_TOKEN to the .env file in agentverse for your agent.

T5_BASE_URL = "https://api-inference.huggingface.co/models/t5-base"

# Define headers for HTTP request, including content type and authorization details
HEADERS = {"Authorization": f"Bearer {HUGGING_FACE_ACCESS_TOKEN}"}

# Ensure the agent has enough funds
fund_agent_if_low(agent.wallet.address())


async def translate_text(ctx: Context, sender: str, input_text: str):
    # Prepare the data
    payload = {"inputs": input_text}

    # Make the POST request and handle possible errors
    try:
        response = requests.post(T5_BASE_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            await ctx.send(
                sender, TranslationResponse(translated_text=f"{response.json()}")
            )
            return
        else:
            await ctx.send(sender, Error(error=f"Error: {response.json()}"))
            return
    except Exception as ex:
        await ctx.send(sender, Error(error=f"Exception Occurred: {ex}"))
        return


# Create an instance of Protocol with a label "T5BaseModelAgent"
t5_base_agent = Protocol(name="T5BaseModelAgent", version="0.0.1")


@t5_base_agent.on_message(
    model=TranslationRequest, replies={TranslationResponse, Error}
)
async def handle_request(ctx: Context, sender: str, request: TranslationRequest):
    # Log the request details
    ctx.logger.info(f"Got request from  {sender}")

    await translate_text(ctx, sender, request.text)


# publish_manifest will make the protocol details available on agentverse.
agent.include(t5_base_agent, publish_manifest=True)


# to request to the hf agent
class TranslationRequest(Model):
    text: str
    api_key: str


# response from the hf agent
class TranslationResponse(Model):
    translated_text: str


# error from hf agent
class Error(Model):
    error: str
