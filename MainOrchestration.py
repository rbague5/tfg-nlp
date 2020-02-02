import timeit
from models.regex import Regex
from models.spacy import Spacy
from models.custom_model import CustomModel


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
	result_regex = Regex.main_regex(document)
	t2 = timeit.default_timer()
	t_regex += (t2 - t1)

	# SPACY IMPLEMENTATION
	t1 = timeit.default_timer()
	result_spacy = Spacy.main_spacy(document)
	t2 = timeit.default_timer()
	t_spacy += (t2 - t1)

	# CUSTOM MODEL IMPLEMENTATION
	t1 = timeit.default_timer()
	result_custom_model = CustomModel.main_custom_model(document)
	t2 = timeit.default_timer()
	t_custom_model += (t2 - t1)




if __name__ == '__main__':
	main_orchestration()
