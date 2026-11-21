import csv
import requests
import sys
from dataclasses import dataclass

MODERATION_URL = "http://localhost:8001/moderate"

@dataclass
class Post:
    cid: str
    author_handle: str
    author_avatar_url: str
    created_at: str
    text: str
    reply_count: int
    like_count: int

def load_posts(input_path):
    """Parse CSV rows into Post object."""
    posts = []
    with open(input_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            posts.append(
                Post(
                    cid=row["cid"],
                    author_handle=row["author_handle"],
                    author_avatar_url=row["author_avatar_url"],
                    created_at=row["created_at"],
                    text=row["text"],
                    reply_count=int(row["reply_count"] or 0),
                    like_count=int(row["like_count"] or 0),
                )
            )
    return posts

def like_count_of(post):
    """Helper function to get like count of posts."""
    return post.like_count

def get_top_posts(posts, limit=10):
    """Return the most liked posts, limited by limiter."""
    return sorted(posts, key=like_count_of, reverse=True)[:limit]

def send_to_pipeline(post_content):
    """Send a post to the moderation service."""
    response = requests.post(
        MODERATION_URL,
        json={"post_content": post_content},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["result"]

def process_post(post, index):
    """Process a given post through pipeline."""
    try:
        result = send_to_pipeline(post.text)
    except Exception as e:
        print(f"Post {index}: [ERROR] Could not reach moderation service: {e}\n")
        return

    if result == "FAILED":
        print(f"Post {index}: [DELETED]\n")
    else:
        print(f"Post {index}: {post.text} {result}\n")

def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "input.csv"

    posts = load_posts(input_path)
    top_posts = get_top_posts(posts, limit=10)

    print(f"Processing top {len(top_posts)} posts\n")

    for i, post in enumerate(top_posts, start=1):
        process_post(post, i)


if __name__ == "__main__":
    main()
