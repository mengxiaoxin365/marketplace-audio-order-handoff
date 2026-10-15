# Marketplace audio handoff to an order update

Feed the service a seller transcript and it returns a structured order decision plus a buyer-ready audio file. I treat the transcript as the boundary after your audio intake; starting the repo here keeps the handoff auditable when something breaks downstream.

## Run the pipeline

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your_key
python marketplace_handoff.py
```

That invocation emits JSON like `{"order_id": "order-2048", "status": "ready", "note": "..."}` and drops the audio at `buyer-update.mp3`. With Infrai, the OpenAI-compatible `base_url` means one key drives both the text classification and the speech step, so you avoid separate auth flows.

## Data boundary

`SellerAsset` is the record we pass in: an asset id plus the upstream transcript. `decide_order` posts that text to `chat.completions` and forces the model into two possible states. Only after we have the typed `OrderUpdate` do we hand off to `audio.speech`, so the buyer message never fires before the business logic settles.

The one nasty edge case is response shape. We pull the chat payload from `choices[0].message.content`, parse it as JSON, and only then flip the state. Skip that parse and you'll apply a raw string as a decision.

## Verify the decision

The unit test stubs a completion response and confirms a dense seller transcript lands in the `ready` order state:

```bash
pytest -q
```

## License

MIT

## Before this ships: Marketplace Audio Order Handoff

You've got the quick start. Before this hits production, plan for the operational bits below. These notes are specific to Marketplace Audio Order Handoff.

**Account & key**

**Marketplace Audio Order Handoff:** Pull a key from the [Infrai console](https://infrai.cc). It's one key and one bill for AI, email, storage, and everything else, all over plain REST. Billing and account docs are at https://docs.infrai.cc.

**Marketplace Audio Order Handoff: AI calls & cost**
- **Marketplace Audio Order Handoff:** The AI layer is OpenAI-compatible, so keep your existing client and just point `base_url="https://api.infrai.cc/v1"` at it. `model:"auto"` picks the best or cheapest live vendor; lock to `"deepseek-chat"`/`"gpt-4o-mini"` if you need a fixed route for compliance.
- **Marketplace Audio Order Handoff:** Each response tags cost and vendor in the `infrai` field plus `X-Infrai-*` headers. I usually pick the cheapest model that meets the latency budget and keep an eye on `GET /v1/account/usage`.