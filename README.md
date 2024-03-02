# BocaLibre

An agent-based, peer-to-peer, chat/social messaging application, intended for users that speak differing native languages.

1. Alice speaks Enligsh. Bob Speaks Spanish.

2. Alice types a message in English and sends it to Bob. The original message is sent by Alice's agent to an AI model for translation from English to Spanish.

3. Bob receives Alice's original message in English, and waits for the translation.

4. The translation into Spanish is returned from the model, sent to Bob by Alice's agent, and rendered under the original message in English.

5. Bob see's the translated message in Spanish, and replies in Spanish, and the cycle repeats for each message, by any user.

---

User Agents:

1. boca_user.py
    - Handles MatchRequests and the match_maker protocol
    - Handles t5_base TranslationRequests and the t5_base protocol
    - Handles BocaMessage(s) and the boca_user protocol

Non-user Agents: (Registered services on agentverse.ai)

1. match_maker.py
    - Matches chat participants
    - Handles queue of participant chat requests
2. t5_base.py
    - Handles the TranslationRequest messages from the user's boca agent; just as in the t5_base integration from the uagents repository.

---

Agentverse Flow:

1. The user navigates to [agentverse.ai](https://agentverse.ai)
2. The user creates a boca_user agent.
3. The user supplies 3 things to their boca_user agent's .env file:
    - Their native language
    - Their target language (the native language of the person they'd like to have a conversation with (Which is also the language their native speech will be translated to)).
    - Their [HUGGINGFACE_API_KEY](https://huggingface.co/settings/tokens)
4. The user starts their boca_user agent.
5. On startup, the user's agent requests a new chat partner from the match_maker agent.
6. The user awaits a match from the match_maker agent.
7. Once a match has been received from the match_maker agent, the user can type a message to their chat partner.
8. The user types a message and it is sent to the t5_base agent to be translated into the target language/native language of their chat partner.
9. The translated message is returned to the user.
10. Both the native message and the translated message are sent to the user's chat partner using a BocaMessage.
11. The chat partner's (user #2) boca_user agent receives the BocaMessage from the sender (user #1).
12. The BocaMessage is displayed to the console of user #2.
13. User #2, the partner, then replies in their native language, and the process repeats from step #8.