# BocaLibre

An agent-based, peer-to-peer, chat/social messaging application, intended for users with differing languages.

1. Alice speaks Enligsh. Bob Speaks Spanish.

2. Alice types a message in English and sends it to Bob. The original message is sent by Alice's agent to an AI model for translation from English to Spanish.

3. Bob receives Alice's original message in English, and waits for the translation.

4. The translation into Spanish is returned from the model, sent to Bob by Alice's agent, and rendered under the original message in English.

5. Bob see's the translated message in Spanish, and replies in Spanish, and the cycle repeats for each message, by any user.

---

User Agents:

1. boca_user.py

Non-user Agents:

1. match_maker.py
    - Matches chat participants
    - Handles queue of participant chat requests
2. t5_base.py
    - Handles the TranslationRequest messages from the user's boca agent; just as in the t5_base integration from the uagents repository.

---

Flow:

1. The user connects their Fetch.ai wallet.
2. The user starts their t5_base_hf_agent.
    - This requires a HuggingFace API key from the user.
3. The user starts their t5_base_user agent.
    - This requires the address of the user's t5_base_hf agent from step 2.
    - This requires a declared native language and a translation language from the user.
4. The user makes a chat request to the Match_Maker agent.
5. The Match_Maker matches two users who have matching criteria to initiate a chat between the two agents.
6. The Match_Maker agent responds to the user's agents with the address of the user's agent with whom they have been matched.
7. A user inputs some text.
8. The user's agent sends a TranslationRequest to the user's t5_base_hf agent.
9. The user's t5_base_hf agent receives the request and makes a subsequent TranslationRequest to the remote HuggingFace t5-base model.
10. The user's t5_base_hf agent awaits a response from the model.
11. Upon receiving the translation response from the remote HF model, the t5_base_hf agent sends the TranslationResponse message to the user's t5_base_user agent.
12. Upon receiving this TranslationResponse, the t5_base_user agent sends a BocaMessage to their chat partner.
13. The partner's t5_base_user agent receives the BocaMessage and displays it.
