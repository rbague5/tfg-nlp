import timeit
from ner_regex import ner_regex
from ner_spacy import ner_spacy
from ner_custom_model import ner_custom_model


import spacy
from spacy.matcher import Matcher  # import Matcher class from ner_spacy


class NerRegex:

	def regex(self, corpus):
		pass


def main_orchestration():

	# RESULTS FOR EACH IMPLEMENTATION
	result_regex = list()
	result_spacy = list()
	result_custom_model = list()

	# VARIABLES OF TIME MANAGEMENT
	t_regex = 0
	t_spacy = 0
	t_custom_model = 0

	document = "Sentencia Procés.txt"

	print(f"Document to test: {document}")
	document = open("documents/"+document, encoding="utf8")
	# print(document.read())

	# ORQUESTRATION

	# REGEX IMPLEMENTATION
	t1 = timeit.default_timer()
	result_regex = ner_regex.main_regex(document)
	t2 = timeit.default_timer()
	t_regex += (t2 - t1)

	# SPACY IMPLEMENTATION
	t1 = timeit.default_timer()
	result_spacy = ner_spacy.main_spacy(document)
	t2 = timeit.default_timer()
	t_spacy += (t2 - t1)

	# CUSTOM MODEL IMPLEMENTATION
	t1 = timeit.default_timer()
	result_custom_model = ner_custom_model.main_custom_model(document)
	t2 = timeit.default_timer()
	t_custom_model += (t2 - t1)




if __name__ == '__main__':
	main_orchestration()
