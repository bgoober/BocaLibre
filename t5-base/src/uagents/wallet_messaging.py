# Importing necessary libraries and modules
import asyncio
import base64
import functools
import logging
from typing import List, Optional

from babble import (  # pylint: disable=unused-import
    Client,
    Identity as BabbleIdentity,
    Message as WalletMessage,
)
from cosmpy.aerial.wallet import LocalWallet
from requests import HTTPError, JSONDecodeError

from uagents.config import (
    WALLET_MESSAGING_POLL_INTERVAL_SECONDS,
    get_logger,
)
from uagents.context import Context, WalletMessageCallback
from uagents.crypto import Identity

# Defining the WalletMessagingClient class
class WalletMessagingClient:
    # Initialization method for the class
    def __init__(
        self,
        identity: Identity,
        wallet: LocalWallet,
        chain_id: str,
        logger: Optional[logging.Logger] = None,
    ):
        # Preparing necessary data for the client
        delegate_pubkey = identity.pub_key
        delegate_pubkey_b64 = base64.b64encode(bytes.fromhex(delegate_pubkey)).decode()
        public_key = base64.b64decode(wallet.public_key().public_key).hex()
        signed_bytes, signature = identity.sign_arbitrary(public_key.encode())
        # Creating the client
        self._client = Client(
            identity.address,
            delegate_pubkey_b64,
            signature,
            signed_bytes,
            BabbleIdentity(wallet.signer().private_key_bytes),
            chain_id,
        )
        # Setting up other class attributes
        self._poll_interval = WALLET_MESSAGING_POLL_INTERVAL_SECONDS
        self._logger = logger or get_logger("wallet_messaging")
        self._message_queue = asyncio.Queue()
        self._message_handlers: List[WalletMessageCallback] = []

    # Method to add message handlers
    def on_message(
        self,
    ):
        def decorator_on_message(func: WalletMessageCallback):
            @functools.wraps(func)
            def handler(*args, **kwargs):
                return func(*args, **kwargs)

            # Adding the function to the list of message handlers
            self._message_handlers.append(func)

            return handler

        return decorator_on_message

    # Method to send a message
    async def send(self, destination: str, msg: str, msg_type: int = 1):
        try:
            # Attempt to send the message
            self._client.send(destination, msg, msg_type)
        except Exception as ex:
            # Log any exceptions that occur
            self._logger.exception(f"Failed to send message to {destination}: {ex}")

    # Method to poll the server for messages
    async def poll_server(self):
        self._logger.info("Connecting to wallet messaging server")
        while True:
            try:
                # Attempt to receive messages and put them in the queue
                for msg in self._client.receive():
                    await self._message_queue.put(msg)
            except (
                HTTPError,
                ConnectionError,
                JSONDecodeError,
                Exception,
            ) as ex:
                # Log any exceptions that occur
                self._logger.warning(
                    f"Failed to get messages from wallet messaging server: {ex}"
                )
            # Sleep for the poll interval before trying again
            await asyncio.sleep(self._poll_interval)

    # Method to process the message queue
    async def process_message_queue(self, ctx: Context):
        while True:
            # Get a message from the queue
            msg = await self._message_queue.get()
            # Process the message with each handler
            for handler in self._message_handlers:
                await handler(ctx, msg)