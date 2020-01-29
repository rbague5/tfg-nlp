import timeit


class NerSpacy:

	def spacy(self, corpus):
		pass


def main_spacy(corpus):
	print("|-------------------------|")
	print("| STARTING NER WITH SPACY |")
	print("|-------------------------|")

	# Orquestation
	ner_spacy = NerSpacy()

	dates_spacy = list()

	# VARIABLES OF TIME MANAGEMENT
	t_spacy = 0

	t1 = timeit.default_timer()
	result_spacy = ner_spacy.spacy(corpus)
	t2 = timeit.default_timer()
	t_spacy += (t2 - t1)

	if result_spacy is not None:
		dates_spacy += result_spacy


if __name__ == '__main__':
	main_spacy()
