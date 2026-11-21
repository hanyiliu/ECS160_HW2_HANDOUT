from fastapi import FastAPI
from pydantic import BaseModel
import grpc

import hashtagging_pb2
import hashtagging_pb2_grpc

app = FastAPI()

HASHTAG_SERVICE = "localhost:50051"
DEFAULT = "#bskypost"

BANNED_WORDS = [
    "illegal",
    "fraud",
    "scam",
    "exploit",
    "dox",
    "swatting",
    "hack",
    "crypto",
    "bots",
]

class ModerateRequest(BaseModel):
    post_content: str

class ModerateResponse(BaseModel):
    result: str

def check_moderation(text):
    """True if the post doesn't contain banned words."""
    lowered = text.lower()
    return not any(word in lowered for word in BANNED_WORDS)

def get_hashtag_from_service(post_content):
    """Ask hashtagging service for a hashtag."""
    try:
        with grpc.insecure_channel(HASHTAG_SERVICE) as channel:
            stub = hashtagging_pb2_grpc.HashtagServiceStub(channel)
            res = stub.GetHashtag(
                hashtagging_pb2.HashtagRequest(post_content=post_content),
                timeout=15,
            )
            return res.hashtag or DEFAULT
    except grpc.RpcError as e:
        print(f"Hashtagging service call failed with exception {e}")
        return DEFAULT

@app.post("/moderate", response_model=ModerateResponse)
def moderate(request: ModerateRequest):
    if check_moderation(request.post_content):
        return ModerateResponse(result=get_hashtag_from_service(request.post_content))

    return ModerateResponse(result="FAILED")