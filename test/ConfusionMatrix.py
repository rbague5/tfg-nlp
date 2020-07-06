class ConfusionMatrix:

    def __init__(self, corpus, results, expected):
        self.corpus = corpus
        self.results = results
        self.expected = expected
        self.FP = [item for item in self.results if item not in self.expected]
        self.FN = [item for item in self.expected if item not in self.results]
        self.TP = len(self.expected) - len(self.FN)
        self.precision = self.TP / (self.TP + len(self.FP))
        self.recall = self.TP / (self.TP + len(self.FN))
        self.F1 = 2 * self.TP / (2 * self.TP + len(self.FP) + len(self.FN))

    def print(self):

        print("FP({}): {}".format(len(self.FP), self.FP))
        print("FN({}): {}".format(len(self.FN), self.FN))
        print("\nEXPECTED RESULTS({})".format(len(self.expected)))
        print("FOUND RESULTS({})".format(len(self.results)))
        print("FP({})".format(len(self.FP)))
        print("FN({})".format(len(self.FN)))
        print("TP({})".format(self.TP))
        print("Precision = {:.2f}".format(self.precision))
        print("Recall = {:.2f}".format(self.recall))
        print("F1 = {:.2f}\n".format(self.F1))
