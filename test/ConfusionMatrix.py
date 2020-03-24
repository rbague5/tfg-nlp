class ConfusionMatrix:

    def __init__(self, corpus, results, expected):
        self.corpus = corpus
        self.results = results
        self.expected = expected
        self.FP = [item for item in self.results if item not in self.expected]
        self.FN = [item for item in self.expected if item not in self.results]
        self.TP = len(self.expected)
        self.precision = self.TP / (self.TP + len(self.FP))
        self.recall = self.TP / (self.TP + len(self.FN))
        self.F1 = 2 * self.TP / (2 * self.TP + len(self.FP) + len(self.FN))

    def print(self):
        print("FP({}): {}".format(len(self.FP), self.FP))
        print("FN({}): {}".format(len(self.FN), self.FN))
        print("Precision = {}".format(self.precision))
        print("Recall = {}".format(self.recall))
        print("F1 = {}\n".format(self.F1))
