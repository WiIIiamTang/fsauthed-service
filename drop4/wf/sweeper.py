from .Workflow import Workflow


class Sweeper(Workflow):
    def __init__(self, name, description=""):
        super().__init__(name, description)

    def run_task(self):
        print("cleaning files")
