from metaflow import FlowSpec, step
import time

class ForeachFlow(FlowSpec):
    @step
    def start(self):
        self.titles = [
            "apple",
            "banana",
            "cherry",
            "date",
            "elderberry",
            "fig",
            "grape",
            "honeydew",
            "kiwi",
            "lemon",
            "mango",
            "nectarine",
            "orange",
            "papaya",
            "quince",
            "raspberry",
            "strawberry",
            "tangerine",
            "ugli fruit",
            "violet",
            "watermelon",
            "xigua",
            "yellow watermelon",
            "zucchini",
            "apricot",
            "blackberry",
            "cantaloupe",
            "dragonfruit",
            "eggplant",
            "feijoa",
            "grapefruit",
            "huckleberry",
            "jackfruit",
            "kumquat",
            "lime",
            "mulberry",
            "olive",
            "peach",
            "pomegranate",
            "rhubarb",
        ]
        self.next(self.a, foreach="titles")

    @step
    def a(self):
        time.sleep(5)
        self.title = "%s processed" % self.input
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
