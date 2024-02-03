# BocaLibre

An agent-based, peer-to-peer, chat/social messaging application, intended for users with differing languages.

1. Alice speaks Enligsh. Bob Speaks Spanish.

2. Alice types a message in English and sends it to Bob. The original message is sent by Alice's agent to an AI model for translation from English to Spanish.

3. Bob receives Alice's original message in English, and waits for the translation.

4. The translation into Spanish is returned from the model, sent to Bob by Alice's agent, and rendered under the original message in English.

5. Bob see's the translated message in Spanish, and replies in Spanish, and the cycle repeats for each message, by any user.

---

the user adds their hf_api key.

the user inputs a message natively.

the message is sent as a translation request to the HF model by the user's agent.
    formatted: translate X to X: xxxx

the model returns a translation to the user's agent.

the user's agent handles the response, and transforms the reponse into the next message to be sent to the intended recipient address.

the recipient agent handles the message, and logs it.

the second user repeats from step 2.

So we must have:
    - api key input
    - accept input from terminal, repeatably
    - format input into translation request and send to hf model
    - handle response from model
    - format response into message and send to intended recipient
    - handle message from sender and log to display