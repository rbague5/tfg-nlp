import timeit

from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters

class CustomModel:

	def execute_pre_process(self, corpus):
		splitted_sentences = list()

		t1 = timeit.default_timer()
		sentences = self._nltk_tokenizer(corpus)
		t2 = timeit.default_timer()
		print(f"Time for NLTK tokenizer: {t2 - t1}")

		for sentence in sentences:
			# Mirem si hi ha newline per ajuntar-ho
			if "\n" in sentence:
				sentence = sentence.replace("\n", " ")

			# eliminamos el título de las frases y su simbolo raro
			if "\x0c" in sentence:
				sentence = sentence.replace("\x0c", "")
			if "JURISPRUDENCIA" in sentence:
				sentence = sentence.replace("JURISPRUDENCIA", "")
			# Mirem la llargada de la frase, per saber si tractar-la o no
			if len(sentence) <= 3:
				continue

			# S'ha de treure les cometes que sino trenquen el json
			if '"' in sentence:
				sentence = sentence.replace('"', " ")

			splitted_sentences.append(sentence)
		corpus_string = ' '.join(splitted_sentences)

		return corpus_string

	def _nltk_tokenizer(self, document):
		abbreviation = ['sra', 'dª', 'dña', 'sras', 'sres', 'sr', 'excmos', 'excmo', 'excma', 'excmas', 'ilma', 'ilmas',
						'ilmo', 'ilmos', 'ilma', 'ilmas', 'art', 'arts', 'núm', 'cp', 'c.p', 's.l', 'rcud', 'rcuds',
						'rec']

		punkt_param = PunktParameters()

		punkt_param.abbrev_types = set(abbreviation)
		sentence_splitter = PunktSentenceTokenizer(punkt_param)
		text = document
		sentences = sentence_splitter.tokenize(text)

		return sentences

	def execute_core_algorithm(self, corpus):
		pass

def main_custom_model():

	f = open("../../documents/STS_175_2020.txt", "r", encoding="utf8")
	file = f.read()

	# Orquestation
	custom_model = CustomModel()

	corpus_preprocessed = custom_model.execute_pre_process(file)

	t1 = timeit.default_timer()
	result_custom_model = custom_model.execute_core_algorithm(corpus_preprocessed)
	t2 = timeit.default_timer()
	print(f"Total time for Custom Model algorithm {t2-t1}")

	if result_custom_model is not None:
		for i in result_custom_model:
			print(i)


if __name__ == '__main__':
	main_custom_model()
