from metaflow import FlowSpec, step
import time

class ForeachFlow(FlowSpec):
    @step
    def start(self):
        self.titles = ["Stranger Things", "House of Cards", "Narcos","Aaa","Bbbb","Ddddd","Cccc","Eeee","Fffff","Gggg"]
        self.next(self.a, foreach="titles")

    @step
    def a(self):
        self.title = "%s processed" % self.input
        time.sleep(5)
        self.next(self.join)

    @step
    def join(self, inputs):
        self.results = [input.title for input in inputs]
        self.next(self.end)

    @step
    def end(self):
        print("\n".join(self.results))


if __name__ == "__main__":
    ForeachFlow()
