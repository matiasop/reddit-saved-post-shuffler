from dotenv import load_dotenv
import praw
import os


def main():
    reddit = praw.Reddit(
        client_id=os.environ.get("CLIENT_ID"),
        client_secret=os.environ.get("CLIENT_SECRET"),
        user_agent=os.environ.get("USER_AGENT"),
        username=os.environ.get("USERNAME"),
        password=os.environ.get("PASSWORD"),
    )
    user = reddit.user.me()
    saved_posts = list(user.saved(limit=None))


if __name__ == "__main__":
    load_dotenv()
    main()
