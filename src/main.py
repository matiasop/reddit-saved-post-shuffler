from praw.models import Submission
from dataclasses import dataclass
from dotenv import load_dotenv
from random import shuffle
from airium import Airium
import praw
import os


@dataclass
class SubmissionSummary:
    id: str
    title: str
    author: str
    image_urls: list[str]
    link: str
    subreddit: str


def create_summary(post: Submission) -> SubmissionSummary:
    if hasattr(post, "media_metadata"):
        image_urls = [
            image_item["s"]["u"] for image_item in post.media_metadata.values()
        ]
    else:
        image_urls = [post.url]
    return SubmissionSummary(
        id=post.id,
        title=post.title,
        author=post.author.name,
        image_urls=image_urls,
        link=f"https://www.reddit.com{post.permalink}",
        subreddit=post.subreddit,
    )


def create_html(summaries: list[SubmissionSummary]):
    a = Airium()
    a('<!DOCTYPE html>')
    with a.html(lang="en"):
        with a.head():
            a.meta(charset="utf-8")
            a.title(_t="Saved Posts Shuffler")
        with a.body():
            for summary in summaries:
                with a.h1():
                    a(summary.title)
                with a.p():
                    a(f"author: {summary.author}")
                with a.p():
                    a(f"subreddit: {summary.subreddit}")
                with a.a(href=summary.link):
                    a(f"link: {summary.link}")
                with a.div():
                    for image in summary.image_urls:
                        a.img(src=image, style="max-width: 400px;")

    FILENAME = "index.html"
    with open(FILENAME, "wb") as f:
        f.write(str(a).encode("utf-8"))


def main():
    reddit = praw.Reddit(
        client_id=os.environ.get("CLIENT_ID"),
        client_secret=os.environ.get("CLIENT_SECRET"),
        user_agent=os.environ.get("USER_AGENT"),
        username=os.environ.get("USERNAME"),
        password=os.environ.get("PASSWORD"),
    )
    user = reddit.user.me()
    saved_posts = user.saved(limit=5)
    summaries = [create_summary(post) for post in saved_posts]
    print(summaries)
    shuffle(summaries)
    print()
    print()
    create_html(summaries)


if __name__ == "__main__":
    load_dotenv()
    main()
