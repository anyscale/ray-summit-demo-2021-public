import time
from locust import HttpUser, task, between

class User(HttpUser):
    wait_time = between(0, 0.1)

    @task
    def chat(self):
        self.client.get("/chat?msg=hi")
