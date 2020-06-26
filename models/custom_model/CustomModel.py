import timeit

import spacy
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

	def execute_core_algorithm(self, corpus, model):
		# load spacy model
		t1 = timeit.default_timer()
		# es_core_news_sm
		spacy_nlp = spacy.load(model)
		spacy_nlp.max_length = 2000000
		t2 = timeit.default_timer()

		print(f"Time to load Own Model: {t2 - t1}")
		list_results_spacy = list()
		list_of_indices = list()

		document = spacy_nlp(corpus)
		# for token in document:
		#     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
		#         token.shape_, token.is_alpha, token.is_stop)

		for ent in document.ents:
			# print(ent.text, ent.start_char, ent.end_char, ent.label_)
			if ent.label_ == 'FECHA':
				list_results_spacy.append(ent.text)
				# print(f"'{ent.text}-{ent.start_char}:{ent.end_char}',")
			# print(i)
			# print(ent.text, ent.label_)
		return list_results_spacy

def main_custom_model():

	f = open("../../documents/ej_2_es_cleaned.txt", "r", encoding="utf8")
	file = f.read()

	# Orquestation
	custom_model = CustomModel()
	model_name = "es_core_legal_sm"

	corpus_preprocessed = custom_model.execute_pre_process(file)

	t1 = timeit.default_timer()
	result_custom_model = custom_model.execute_core_algorithm(corpus_preprocessed, model_name)
	t2 = timeit.default_timer()
	print(f"Total time for Custom Model algorithm {t2-t1}")

	if result_custom_model is not None:
		for i in result_custom_model:
			print(i)


if __name__ == '__main__':
	main_custom_model()
