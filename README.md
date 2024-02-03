# BocaLibre

An agent-based, peer-to-peer, chat/social messaging application, intended for users with differing languages.

1. Alice speaks Enligsh. Bob Speaks Spanish.

2. Alice types a message in English and sends it to Bob. The original message is sent by Alice's agent to an AI model for translation from English to Spanish.

3. Bob receives Alice's original message in English, and waits for the translation.

4. The translation into Spanish is returned from the model, sent to Bob by Alice's agent, and rendered under the original message in English.

5. Bob see's the translated message in Spanish, and replies in Spanish, and the cycle repeats for each message, by any user.

Like all chats, they are asynchronous, and any user may send a message in any order, with its translation duly returned and positioned for reading.





