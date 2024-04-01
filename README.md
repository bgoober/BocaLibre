# BocaLibre

An agent-based, peer-to-peer, chat/social messaging application, intended for users that speak differing native languages. Built on Fetch.ai's uAgents framework and t5-base integration.

Currently, the application is based on the t5-base integration in fetch.ai's uAgents repository. It hits HuggingFace's hosted t5-base model for translations. Unfortunately, the t5-base only works with four languages -- English, German, French, and Romanian. It seems to only be capable of translating FROM English to another language, but not back. Nor does it seem capable of translating from a non-English language to a second non-English language; or, at least it doesn't do it very well. In fact, slang would be tricky and likely confuse the model, or not be translated at all. Proper grammar is essential as input.

To run the application locally in your terminal, first start your t5_base agent, with your hugging_face api key exported to its local environment. Record the t5_base agent's address. Then, start the match_maker agent and record the match_maker agent's address. Export both the match_maker and t5_base agent's addresses to your boca_user and boca_partner agent's local environments, then start them.

In your boca_user and boca_partner agent terminals, input your native and target languages. If you input the corresponding languages needed for a match, then the match_maker agent will match your agents. If not, then the match_maker will store your requests until a matching request is found. You could clone either boca_user or boca_partner (this would require you to change the localhost endpoints in the agent and its client so no conflict occurs), and create multiple user agents in order to test further matches and conversations.

User input is accepted at all times, and the agents will resend messages that were timed out from the AI model's end once the estimated wait time has elapsed. Messages are cleared from your agent's input_queue once sent, and received messages are stored in your agent's Context.

Although the agents understand message models such as UpdateMatchRequest, there exists no ability to actually send this message. Also, the user agents only store a single partner at the moment, so the ability to store multiple chat partners and bounce inbetween them (much like you do on your phone when text-messaging) does not exist yet; essentially you can talk to only 1 person at a time (stored as "partner" in the agent's Context). Further development is needed to build out these capabilities on both the front end and back end.

Ideally, the application is built out to be a fully hosted web application, much like Agentverse.ai is, and is purpose built to facilitate conversations between people that speak differing languages. **I envision it as a social chat application to connect people around the world.** Users would navigate to the site, login via their web3/fetchai wallet, create an agent, request a chat, match with someone, then start talking! Social-fi (without the fi, really) facilitated by agents! Maybe they pay a small fee for each MatchRequest message??

To this end, using Google's google/flan-t5-base model would likely be superior to t5-base. Flan-t5-base has integrated many more languages than t5-base, and would thus open the application to more users. However, Google's models refuse to translate certain things. For instance, if you input the famous line from the 1987 movie _The Pincess Bride_ -- "Hello. My name is Inigo Montoya. You killed my father. Prepare to die." -- It will not translate the "Prepare to die" part, but translate the rest. This makes t5-base untrustworthy at best, and useless at worst (at least as a translator). A model capable of as-near 1:1 translation as possible is needed to ensure a quality product, no matter the input.

Several quality-of-life and code-clarity improvements could also be made, but the application works as intended locally with the four agents mentioned above, and is sufficient to prove the concept.

---

### The Idea

1. Alice speaks Enligsh. Bob Speaks Spanish. They both want to chat with someone who speaks a different language, so they request a chat partner from the match_maker agent, which matches them.

2. Alice types a message to Bob in English, and it is sent to the t5_base agent for translation to Spanish. She awaits the translated response from the t5_base agent.

3. The TranslationResponse is returned to Alice from the t5_base agent, and a BocaMessage is sent to Bob, containing both the original native message in English, and the translated message in Spanish.

4. Bob receives the BocaMessage from Alice, containing both the English, and Spanish versions of her message.

5. Bob types his response in Spanish, it is translated by t5_base into English, and a new BocaMessage is sent back to Alice.

6. The cycle repeats.

---

### Local setup

User Agents: ( All located in the ./boca/t5-base directory )

1. boca_user.py / boca_partner.py
    - Handles MatchRequests to the match_maker agent and the match_maker protocol
    - Handles t5_base TranslationRequests and the t5_base protocol
    - Handles BocaMessage(s) and the boca_user protocol

Non-user Agents: 

1. match_maker.py
    - Matches chat participants
    - Handles queue of participant chat requests
2. t5_base.py
    - Handles the TranslationRequest messages from the user's boca agent; just as in the t5_base integration from the uagents repository.