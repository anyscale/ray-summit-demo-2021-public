from local_module import (
    build_response,
    fastapi_app,
    load_intent_classifier,
    load_search_model,
    preprocess
)

import ray
from ray import serve

ray.client().job_name("deploy").namespace("chatbot").connect()
serve.start(detached=True)

@serve.deployment(num_replicas=4, version="v0")
class IntentClassifier:
    def __init__(self, model_uri: str):
        self._model = load_intent_classifier(model_uri)

    async def __call__(self, preprocessed) -> str:
        return await self._model(preprocessed)


@serve.deployment(num_replicas=2, version="v0")
class RelevanceSearch:
    def __init__(self, model_uri: str):
        self._model = load_search_model(model_uri)

    async def __call__(self, preprocessed) -> str:
        return await self._model(preprocessed)


app = fastapi_app()

@serve.deployment(num_replicas=3, route_prefix="/", version="v1")
@serve.ingress(app)
class ChatBot:
    def __init__(self):
        self._intent_classifier = IntentClassifier.get_handle(sync=False)
        self._relevance_search = RelevanceSearch.get_handle(sync=False)

    @app.get("/chat")
    async def chat(self, msg: str):
        # Preprocess the input and put it into shared memory.
        preprocessed = ray.put(preprocess(msg))

        # Kick off requests to two downstream models in parallel.
        link_ref = await self._relevance_search.remote(preprocessed)
        intent_ref = await self._intent_classifier.remote(preprocessed)

        # Build the response based on the output of the two models.
        response = await build_response(intent_ref, link_ref)

        if await intent_ref == "BUG":
            response["link"] = "https://github.com/ray-project/ray/issues"
            response["header"] = "Ray Issues Page"

        return response

print("Deploying models...")
IntentClassifier.deploy("")
RelevanceSearch.deploy("")
ChatBot.deploy()

print("Running basic test...")
handle = ChatBot.get_handle()
assert len(ray.get(handle.chat.remote("Hello!"))["message"]) > 0
print("!!! Success !!!")
