import grpc
from concurrent import futures
import os
import re

from google import genai

import hashtagging_pb2
import hashtagging_pb2_grpc

# Configure Gemini
MODEL = "gemini-3.5-flash"
PORT = 50051
DEFAULT = "#bskypost"

PROMPT = (
    "Read the social media post and reply with one hashtag that describes it."
    "Reply with only the hashtag, in the format #_____."
    "Post: {post}"
)

_client = None


def get_client():
    """Create the Gemini client on first use so importing this module needs no API key."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    return _client


def clean_hashtag(text):
    """Turn Gemini response into hashtag, cleaning if needed."""
    if not text:
        return DEFAULT
    word = text.strip().split()[0] if text.strip() else ""
    if not word:
        return DEFAULT
    return word


def generate_hashtag(post_content):
    """Ask Gemini for a hashtag."""
    try:
        response = get_client().models.generate_content(
            model=MODEL,
            contents=PROMPT.format(post=post_content),
        )
        return clean_hashtag(response.text)
    except Exception as e:
        print(f"Gemini call failed, using default hashtag: {e}")
        return DEFAULT


class HashtagServiceServicer(hashtagging_pb2_grpc.HashtagServiceServicer):
    def GetHashtag(self, request, context):
        hashtag = generate_hashtag(request.post_content)
        return hashtagging_pb2.HashtagResponse(hashtag=hashtag)


def serve():
    ser = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    hashtagging_pb2_grpc.add_HashtagServiceServicer_to_server(
        HashtagServiceServicer(), ser
    )
    ser.add_insecure_port(f"[::]:{PORT}")
    ser.start()
    print(f"Hashtagging gRPC service listening on port {PORT}")
    ser.wait_for_termination()


if __name__ == "__main__":
    serve()
