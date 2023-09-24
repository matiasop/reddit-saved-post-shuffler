from praw.models import Submission
from dataclasses import dataclass
from dotenv import load_dotenv
from airium import Airium
import praw
import os

SCRIPT = """
    function shuffleItems() {
        const container = document.getElementById('summaries'); // Change to your actual container element
        const items = container.querySelectorAll(".item");
        const fragment = document.createDocumentFragment();

        // Convert NodeList to an array for easy shuffling
        const itemArray = Array.from(items);

        // Shuffle the array
        for (let i = itemArray.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [itemArray[i], itemArray[j]] = [itemArray[j], itemArray[i]];
        }

        // Append shuffled items to the fragment
        itemArray.forEach((item) => {
            fragment.appendChild(item);
        });

        // Clear the container and append the shuffled items
        container.innerHTML = "";
        container.appendChild(fragment);
    }

    // Call the shuffleItems function when the button is clicked
    const shuffleButton = document.getElementById("shuffleButton");
    shuffleButton.addEventListener("click", shuffleItems);
"""


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
        try:
            image_urls = [
                image_item.get("s", {}).get("u", "")
                for image_item in post.media_metadata.values()
            ]
        except AttributeError:
            image_urls = []
    else:
        image_urls = [post.url]
    return SubmissionSummary(
        id=post.id,
        title=post.title,
        author=post.author.name if post.author and post.author.name else '',
        image_urls=image_urls,
        link=f"https://www.reddit.com{post.permalink}",
        subreddit=post.subreddit,
    )


def create_html(summaries: list[SubmissionSummary], filename: str):
    a = Airium()
    a('<!DOCTYPE html>')
    with a.html(lang="en"):
        with a.head():
            a.meta(charset="utf-8")
            a.title(_t="Saved Posts Shuffler")
        with a.body():
            with a.button(id="shuffleButton"):
                a("shuffle posts")
            with a.div(id="summaries"):
                for summary in summaries:
                    with a.div(klass="item"):
                        with a.h1():
                            a(summary.title)
                        with a.p():
                            a(f"author: {summary.author}")
                        with a.p():
                            a(f"subreddit: {summary.subreddit}")
                        with a.a(href=summary.link):
                            a(f"{summary.link}")
                        with a.div():
                            for image in summary.image_urls:
                                a.img(src=image, style="max-width: 400px;")
        with a.script():
            a(SCRIPT)

    with open(filename, "wb") as f:
        f.write(str(a).encode("utf-8"))


def get_posts_summaries() -> list:
    reddit = praw.Reddit(
        client_id=os.environ.get("CLIENT_ID"),
        client_secret=os.environ.get("CLIENT_SECRET"),
        user_agent=os.environ.get("USER_AGENT"),
        username=os.environ.get("USERNAME"),
        password=os.environ.get("PASSWORD"),
    )
    user = reddit.user.me()
    saved_posts = user.saved(limit=None)
    summaries = [create_summary(post) for post in saved_posts]
    return summaries


if __name__ == "__main__":
    load_dotenv()
    summaries = get_posts_summaries()
    create_html(summaries, "index.html")
