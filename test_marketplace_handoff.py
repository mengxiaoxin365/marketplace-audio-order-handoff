import json

from marketplace_handoff import SellerAsset, decide_order


class FakeCompletions:
    def create(self, **_: object):
        class Message:
            content = json.dumps({"status": "ready", "note": "Packed for dispatch."})

        class Choice:
            message = Message()

        class Response:
            choices = [Choice()]

        return Response()


class FakeClient:
    chat = type("Chat", (), {"completions": FakeCompletions()})()


def test_packed_transcript_hands_order_to_dispatch():
    update = decide_order(SellerAsset("a-1", "Packed and ready to ship."), "o-9", FakeClient())
    assert update.status == "ready"
    assert update.order_id == "o-9"
