import time
import pandas
from metaflow import step, FlowSpec

class HelloWorld(FlowSpec):
    @step
    def start(self):
        self.data = "Hello World"
        self.next(self.end)

    @step
    def end(self):
        print("the shape of data is still: %", self.data)


if __name__ == "__main__":
    HelloWorld()