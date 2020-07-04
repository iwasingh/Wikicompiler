from ..config import TEST_DATA


class FromFile:
    def __init__(self, filename):
        self.filename = filename

    def __call__(self, func):
        with open(TEST_DATA / self.filename)as file:
            text = file.read()
            func(text)

        return func