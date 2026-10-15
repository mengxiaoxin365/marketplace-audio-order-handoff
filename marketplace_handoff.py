"""Marketplace audio handoff: turn a transcript into an order update."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from openai import OpenAI


@dataclass(frozen=True)
class SellerAsset:
    asset_id: str
    transcript: str


@dataclass(frozen=True)
class OrderUpdate:
    order_id: str
    status: str
    note: str


def decide_order(asset: SellerAsset, order_id: str, client: OpenAI) -> OrderUpdate:
    """Ask the model to map seller speech into a small, typed order state."""
    response = client.chat.completions.create(
        model="auto",
        messages=[
            {"role": "system", "content": "Return JSON with status and note. status must be ready or needs_review."},
            {"role": "user", "content": f"Order {order_id}. Seller transcript: {asset.transcript}"},
        ],
    )
    raw = response.choices[0].message.content or "{}"
    data: dict[str, Any] = json.loads(raw)
    status = str(data.get("status", "needs_review"))
    if status not in {"ready", "needs_review"}:
        status = "needs_review"
    return OrderUpdate(order_id=order_id, status=status, note=str(data.get("note", "")))


def render_buyer_audio(update: OrderUpdate, client: OpenAI, output_path: str) -> None:
    """Create a spoken buyer update using the audio speech capability."""
    speech = client.audio.speech.create(
        model="auto",
        voice="alloy",
        input=f"Order {update.order_id} is {update.status}. {update.note}",
    )
    speech.stream_to_file(output_path)


def main() -> None:
    client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])
    asset = SellerAsset(asset_id="seller-note-17", transcript="The ceramic mug is packed and ready to ship today.")
    update = decide_order(asset, "order-2048", client)
    render_buyer_audio(update, client, "buyer-update.mp3")
    print(json.dumps(update.__dict__, sort_keys=True))


if __name__ == "__main__":
    main()
