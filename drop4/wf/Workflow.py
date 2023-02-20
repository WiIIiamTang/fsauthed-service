from abc import abstractmethod, ABC


class Workflow(ABC):
    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    def __str__(self):
        return self.name + " " + self.description

    @abstractmethod
    def run_task(self):
        pass
