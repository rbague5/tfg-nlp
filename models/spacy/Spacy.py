import time
from operator import itemgetter

import spacy, timeit
from documents import *

from spacy.matcher import Matcher  # import Matcher class from spacy
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters

class SpacyModel:

	def execute_pre_process(self, corpus):
		splitted_sentences = list()
		corpus_string = str()

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

		list_not_clenaned_results_spacy = list()
		list_of_indices = list()

		# LOAD SPACY
		t1 = timeit.default_timer()
		spacy_nlp = spacy.load('es_core_news_sm')
		spacy_nlp.max_length = 1500000
		t2 = timeit.default_timer()
		print(f"Time for loading spaCy model: {t2 - t1}")

		matcher = Matcher(spacy_nlp.vocab)
		document = spacy_nlp(corpus)

		# Print Token and Tag of the document_page
		# for token in document:
		#	print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
		#		  token.shape_, token.is_alpha, token.is_stop)

		matcher.add("FECHAS", None, *self._get_patterns())
		matches = matcher(document)

		# Si no hi ha cap element no cal fer res

		if len(matches) != 0:
			# print the matched results and extract out the results
			for match_id, start, end in matches:
				# Get the string representation
				span = document[start:end]  # The matched span
				list_not_clenaned_results_spacy.append(span.text)
				# print("Match id:", match_id, "start:", start, "end: ", end, "text: ", span.text)
				current_indices = [start, end]
				list_of_indices.append(current_indices)
			results = self._merge_indices(list_of_indices, document)
			return results

	def _get_patterns(self):

		patterns = list()
		meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto',
				 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre', 'enero', 'febrero', 'marzo',
				 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

		# PATRONES DE FECHAS
		# https://spacy.io/usage/rule-based-matching
		patterns.append([{'POS': 'NUM', 'IS_DIGIT': True}, {'POS': 'ADP'}, {'ORTH': {'IN': meses}}, {'POS': 'ADP'},
						 {'POS': 'NUM', 'IS_DIGIT': True, 'LENGTH': {"==": 4}}])
		patterns.append([{'POS': 'NUM', 'IS_DIGIT': True}, {'ORTH': {'IN': meses}}, {'POS': 'NUM', 'IS_DIGIT': True, 'LENGTH':{"==": 4}}])
		# a vegade sho etiquete com a noun
		patterns.append([{'POS': 'NUM', 'IS_DIGIT': True}, {'ORTH': {'IN': meses}},
						 {'POS': 'NOUN', 'IS_DIGIT': True, 'LENGTH': {"==": 4}}])
		patterns.append(
			[{'ORTH': {'IN': meses}}, {'POS': 'ADP'}, {'POS': 'NUM', 'IS_DIGIT': True, 'LENGTH': {"==": 4}}])
		patterns.append([{'POS': 'NUM', 'IS_DIGIT': True}, {'POS': 'ADP', 'LEMMA': 'de'}, {'ORTH': {'IN': meses}}])
		patterns.append(
			[{'POS': 'NUM', 'IS_DIGIT': True}, {'ORTH': 'y'}, {'POS': 'NUM', 'IS_DIGIT': True}, {'ORTH': {'IN': meses}},
			 {'POS': 'NUM', 'IS_DIGIT': True, 'LENGTH': {"==": 4}}])
		patterns.append(
			[{'POS': 'NUM', 'IS_DIGIT': True}, {'ORTH': {'IN': meses}}, {'ORTH': 'y'}, {'POS': 'NUM', 'IS_DIGIT': True},
			 {'ORTH': {'IN': meses}}, {'POS': 'NUM', 'IS_DIGIT': True, 'LENGTH': {"==": 4}}])
		patterns.append([{'POS': 'NUM', 'IS_DIGIT': True}, {'ORTH': {'IN': meses}},
						 {'POS': 'NUM', 'IS_DIGIT': True, 'LENGTH': {"==": 4}}])
		patterns.append([{'ORTH': {'IN': meses}}, {'POS': 'ADP', 'LEMMA': 'del'}, {'POS': 'NOUN', 'LEMMA': 'año'},
						 {'POS': 'NUM', 'IS_DIGIT': True, 'LENGTH': {"==": 4}}])

		# las de puntos las separa
		patterns.append(
			[{'SHAPE': {'REGEX': '^d{1,2}$'}}, {'IS_PUNCT': True}, {'SHAPE': {'REGEX': '^d{1,2}$'}}, {'IS_PUNCT': True},
			 {'SHAPE': {'REGEX': '^d{2}$'}}])
		patterns.append(
			[{'SHAPE': {'REGEX': '^d{1,2}$'}}, {'IS_PUNCT': True}, {'SHAPE': {'REGEX': '^d{1,2}$'}}, {'IS_PUNCT': True},
			 {'SHAPE': {'REGEX': '^d{4}$'}}])

		# Fechas con simbolos y mes al medio escrito
		patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\-x+\-d{4}$'}}])
		patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\.x+\.d{4}$'}}])
		patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\/x+\/d{4}$'}}])

		# Fechas con simbolos y mes al medio en numero
		patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\-d{1,2}\-d{4}$'}}])
		patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\.d{1,2}\.d{4}$'}}])
		patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\/d{1,2}\/d{4}$'}}])
		# Son para cuando en vez de /2016 pongan /16
		patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\-d{1,2}\-d{2}$'}}])
		patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\.d{1,2}\.d{2}$'}}])
		patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\/d{1,2}\/d{2}$'}}])

		patterns.append(
			[{'POS': 'PROPN', 'OP': '?'}, {'LEMMA': {'IN': ['artículo', 'Artículo', 'arts', 'articulos', 'artículos']}},
			 {'POS': 'ADP', 'OP': '?'}, {'IS_PUNCT': True, 'OP': '?'}, {'LEMMA': 'unico'}, {'POS': 'PROPN', 'OP': '*'}])

		return patterns

	def _merge_indices(self, results, document):
		# Recibe una lista con los indices [inicio, final] ordenados por inicio
		# Compara dos a dos todos los indices que se solapan y los reduce solo a una lista [inicio, final]
		# que ocupe el rango completo de los indices eliminados.
		results = sorted(results, key=itemgetter(0))
		filtered_dates = list()
		for i in range(len(results), 1, -1):
			r1 = results[-i]
			r2 = results[-i + 1]
			if r1[1] >= r2[0]:
				results[-i] = [r1[0], max(r1[1], r2[1])]
				results.pop(-i + 1)
		for i in results:
			filtered_dates.append(document[i[0]:i[1]])
		return filtered_dates


def main_spacy():

	f = open("../../documents/12 pag software_cleaned.txt", "r", encoding="utf8")
	file = f.read()

	# Orquestation
	spacy_model = SpacyModel()

	corpus_preprocessed = spacy_model.execute_pre_process(file)

	# passem Spacy directament a tot el text
	t1 = timeit.default_timer()
	result_spacy = spacy_model.execute_core_algorithm(corpus_preprocessed)
	t2 = timeit.default_timer()

	print(f"Total time for spaCy algorithm {t2-t1}")

	if result_spacy is not None:
		for i in result_spacy:
			print(i)


if __name__ == '__main__':

	main_spacy()
