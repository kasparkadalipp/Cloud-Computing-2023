from locust import User,HttpUser, TaskSet, events, task, constant
from locust import LoadTestShape
 
class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        self.client.get("/")
    wait_time = constant(1)
 
class StagesShape(LoadTestShape):
    stages = [{'users': 100, 'duration': 60, 'spawn_rate': 10}]
 
    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data
        return None
