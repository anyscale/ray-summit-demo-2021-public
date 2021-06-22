import asyncio
from os import path
import random
from typing import List, Tuple
import warnings

warnings.simplefilter(action="ignore")

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from local_module.data import clean_content, load_data_from_file
from local_module.train import tune_model

def preprocess(msg):
    """Mocked-out preprocessing logic."""
    return [word.lower() for word in msg.strip().split()]

def bug_report_message():
    msgs = [
        "Uh-oh, it seems like you may have run into a bug! Please file an issue on the Ray GitHub.",
        "That's not good, it's possible that you're experiencing a bug. Please file an issue so we can take a look!"
    ]
    return random.choice(msgs)

def confused_message():
    msgs = [
        "I'm sorry, I didn't understand. Could you please try asking again?",
        "Unfortunately I didn't totally get what you're asking. What was your question?",
        "Could you try asking your question in a different way?"
    ]
    return random.choice(msgs)

def greeting_message():
    msgs = [
        "Hi there! I'm here to help -- what are you wondering about?",
        "Welcome, I'm happy to answer any questions you might have about Ray.",
        "What a great day it is to learn about Ray!"
    ]
    msg = random.choice(msgs)
    msg += " Here's a good place to get started:"
    return msg

def information_message(link_header):
    msgs = [
        "Based on your question, it seems like you're looking for more information about {}.",
        "I think what you're looking for is {}. You can find out more in the documentation!"
    ]
    msg = random.choice(msgs)
    return msg.format(link_header)

async def build_response(intent_ref, link_ref):
    # Get the results from the downstream models.
    intent = await intent_ref
    link, header = await link_ref

    if intent == "GREETING":
        message = greeting_message()
    elif intent == "BUG":
        message = bug_report_message()
    elif intent == "QUESTION":
        message = information_message(header)
    else:
        message = confused_message()


    return {
        "message": message,
        "link": link,
        "header": header
    }

def fastapi_app():
    app = FastAPI()

    app.mount("/static", StaticFiles(directory=path.join("frontend", "build", "static")), name="static")

    @app.get("/")
    def index():
        return FileResponse(path.join("frontend", "build", "index.html"))

    return app


class IntentClassifier:
    async def __call__(self, preprocessed: List[str]) -> str:
        """Model is mocked out with a random choice here."""
        return random.choice(["QUESTION", "BUG", "GREETING", "UNKNOWN"])


def load_intent_classifier(model_uri: str):
    print(f"Loading model from {model_uri}...")
    return IntentClassifier()


class SearchModel:
    async def __call__(self, preprocessed: List[str]) -> Tuple[str, str]:
        """Model is mocked out with a random choice here."""
        docs_link, title = random.choice([
            ("tune/index.html", "Ray Tune"),
            ("dask-on-ray.html", "Dask on Ray"),
            ("serve/index.html", "Ray Serve"),
            ("ray-overview/index.html", "Introduction to Ray")
        ])

        return f"https://docs.ray.io/en/master/{docs_link}", title


def load_search_model(model_uri: str):
    print(f"Loading model from {model_uri}...")
    return SearchModel()
