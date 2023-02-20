from .Workflow import Workflow


class Sentry(Workflow):
    def __init__(self, name, description=""):
        super().__init__(name, description)

    def run_task(self):
        print("checking download logs")
