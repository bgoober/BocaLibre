1. Base agent -- export huggingface token
2. run base_agent_client.py
3. run alice_client.py
4. boca_user_agent -- export alice.address as recipient, and t5_base agent
5. run client.py


1.

export HUGGING_FACE_ACCESS_TOKEN="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"

poetry run python agent.py

agent address: agent1qgj087vjxtp056jj3ww73gn87uj9pjd8ds53rn7ugx7se2qx9qpv55jlpcg
(this address changes if you start over)



2. 

export T5_BASE_AGENT_ADDRESS="agent1qgj087vjxtp056jj3ww73gn87uj9pjd8ds53rn7ugx7se2qx9qpv55jlpcg"

poetry run python summarization_client.py

agent address: agent1qwl8nw79dakws0cj4ms5uknq22gjtpelaxd7tzj8hgp7ngxgcl97gumkde9
(this address changes if you start over)



3.
Alice's address:
export RECIPIENT="agent1q0zeajdcr5s9jwcj7hcjsj9n3y9e2t0hr7d9dxpfrs07gm4gxk20kftjj4u"

export T5_BASE_AGENT_ADDRESS="agent1qgj087vjxtp056jj3ww73gn87uj9pjd8ds53rn7ugx7se2qx9qpv55jlpcg"

poetry run python boca_client.py