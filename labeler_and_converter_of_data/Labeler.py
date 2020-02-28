#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from spacy.lang.es import Spanish
import timeit
import itertools
import spacy, timeit

from operator import itemgetter
import es_core_news_sm
import json


# new things
from nltk import sent_tokenize
from spacy.matcher import Matcher  # import Matcher class from spacy




class Labeler:

    def execute_pre_process(self, corpus):

        splitted_sentences = list()

        t1 = timeit.default_timer()
        sentences = self._nltk_tokenizer(corpus)
        t2 = timeit.default_timer()
        print(f"Time for NLTK tokenizer: {t2-t1}")

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
        return splitted_sentences

    def _nltk_tokenizer(self, document):
        abbreviation = ['sra', 'dª', 'dña', 'sras', 'sres', 'sr', 'excmos', 'excmo', 'excma', 'excmas', 'ilma', 'ilmas',
                        'ilmo', 'ilmos', 'ilma', 'ilmas', 'art', 'arts', 'núm', 'cp', 'c.p', 's.l', 'rcud', 'rcuds', 'rec']

        punkt_param = PunktParameters()

        punkt_param.abbrev_types = set(abbreviation)
        sentence_splitter = PunktSentenceTokenizer(punkt_param)
        text = document
        sentences = sentence_splitter.tokenize(text)

        return sentences

    def execute_core_algorithm(self, corpus):

        t_spacy = 0

        spacy_nlp = self._load_spacy()
        result = str()

        for sentence in corpus:
            # passem Spacy per sentències
            t1 = timeit.default_timer()
            # Teninm indexos de casa entitat (inici, final)
            indexes_entity = self.spacy_main(sentence, spacy_nlp)
            t2 = timeit.default_timer()
            t_spacy += (t2 - t1)

            # Si no troba cap entitat, necessitem que al json fico empty
            if indexes_entity is None:
                indexes_entity = '[]'

            # pre modifico la frase per que tingui les cometes
            # sentence = "'"+str(sentence)+"'"
            # print(f"Sentence: {sentence}")
            sentence_with_entity = '{"content":"' +str(sentence) + '", "entities":' + str(indexes_entity) +'},'

            result = result + sentence_with_entity
        # Borrem la ultima coma i afegim els brackets de llista pel json
        result = "["+result[:-1]+"]"
        # print(result)

        return result

    def spacy_main(self, corpus, spacy_nlp):

        json_result = list()

        list_not_clenaned_results_spacy = list()
        list_of_indices = list()

        t1 = timeit.default_timer()
        document = spacy_nlp(corpus)
        t2 = timeit.default_timer()
        # print(f"Time for spacy_nlp {t2 - t1}")

        # Print Token and Tag of the document_page

        # for token in document:
        #     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
        #           token.shape_, token.is_alpha, token.is_stop)

        t1 = timeit.default_timer()
        matcher = Matcher(spacy_nlp.vocab)
        matcher.add("FECHAS", None, *self._get_patterns())
        matches = matcher(document)
        t2 = timeit.default_timer()
        # print(f"Time for matcher {t2 - t1}")

        # for ent in document.ents:
        #     print(ent.text, ent.start_char, ent.end_char, ent.label_)

        # Si no hi ha cap element no cal fer res
        if len(matches) is not 0:
            time1 = timeit.default_timer()
            # print the matched results and extract out the results
            for match_id, start, end in matches:
                # Get the string representation
                span = document[start:end]  # The matched span
                list_not_clenaned_results_spacy.append(span.text)
                # print("Match id:", match_id, "start:", start, "end: ", end, "text: ", span.text)

                current_indices = [start, end]
                list_of_indices.append(current_indices)
            time2 = timeit.default_timer()
            results = self._merge_indices(results=list_of_indices, document=document)
            time3 = timeit.default_timer()
            indexes = self._get_indexes(results=results)

            # # Afegeixo la entitat als indexos
            for i in indexes:
                i.append("FECHAS")
                json_result.append(json.dumps(i))

            time4 = timeit.default_timer()
            # cleaned_indexes = self._clean_punctuation(indexes=indexes, document=corpus)
            time5 = timeit.default_timer()

            # print(f"Time to FULL clean and get entities {time5 - time1}")
            # print(f"Time FOR matches {time2 - time1}")
            # print(f"Time to merge indexes {time3 - time2}")
            # print(f"Time to GET INDEXES {time4 - time3}")
            # print(f"Time to CLEAN REUSLTS {time5 - time4}")
            # for i in results:
            #     print(i)
            #
            # print(json.dumps(indexes))
            # serveix per ficar les douyble quotes
            return json.dumps(indexes)

    def _get_patterns(self):
        patterns = list()
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto',
                 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre', 'enero', 'febrero', 'marzo',
                 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

        # PATRONES DE FECHAS
        # https://spacy.io/usage/rule-based-matching
        patterns.append([{'POS': 'NUM', 'IS_DIGIT': True}, {'POS': 'ADP'}, {'ORTH': {'IN': meses}}, {'POS': 'e'}, {'POS': 'NUM', 'IS_DIGIT': True, 'LENGTH': {"==": 4}}])
        patterns.append([{'ORTH': {'IN': meses}}, {'POS': 'ADP'}, {'POS': 'NUM', 'IS_DIGIT': True, 'LENGTH': {"==": 4}}])
        patterns.append([{'POS': 'NUM', 'IS_DIGIT': True}, {'POS': 'ADP', 'LEMMA': 'de'}, {'ORTH': {'IN': meses}}])
        patterns.append([{'POS': 'NUM', 'IS_DIGIT': True}, {'ORTH': 'y'}, {'POS': 'NUM', 'IS_DIGIT': True}, {'ORTH': {'IN': meses}}, {'POS': 'NUM', 'IS_DIGIT': True, 'LENGTH': {"==": 4}}])
        patterns.append([{'POS': 'NUM', 'IS_DIGIT': True}, {'ORTH': {'IN': meses}}, {'ORTH': 'y'}, {'POS': 'NUM', 'IS_DIGIT': True}, {'ORTH': {'IN': meses}}, {'POS': 'NUM', 'IS_DIGIT': True, 'LENGTH': {"==": 4}}])
        patterns.append([{'POS': 'NUM', 'IS_DIGIT': True}, {'ORTH': {'IN': meses}}, {'POS': 'NUM', 'IS_DIGIT': True, 'LENGTH': {"==": 4}}])
        patterns.append([{'ORTH': {'IN': meses}}, {'POS': 'ADP', 'LEMMA': 'del'}, {'POS': 'NOUN', 'LEMMA': 'año'}, {'POS': 'NUM', 'IS_DIGIT': True, 'LENGTH': {"==": 4}}])

        # las de puntos las separa
        patterns.append([{'SHAPE': {'REGEX': '^d{1,2}$'}}, {'IS_PUNCT': True}, {'SHAPE': {'REGEX': '^d{1,2}$'}}, {'IS_PUNCT': True}, {'SHAPE': {'REGEX': '^d{2}$'}}])
        patterns.append([{'SHAPE': {'REGEX': '^d{1,2}$'}}, {'IS_PUNCT': True}, {'SHAPE': {'REGEX': '^d{1,2}$'}}, {'IS_PUNCT': True}, {'SHAPE': {'REGEX': '^d{4}$'}}])

        # Fechas con simbolos y mes al medio escrito
        patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\-x+\-d{4}$'}}])
        patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\.x+\.d{4}$'}}])
        patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\/x+\/d{4}$'}}])

        # Fechas con simbolos y mes al medio en numero
        patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\-d{1,2}\-d{4}$'}}])
        patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\.d{1,2}\.d{4}$'}}])
        patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\/d{1,2}\/d{4}$'}}])
        #Son para cuando en vez de /2016 pongan /16
        patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\-d{1,2}\-d{2}$'}}])
        patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\.d{1,2}\.d{2}$'}}])
        patterns.append([{'SHAPE': {'REGEX': '^d{1,2}\/d{1,2}\/d{2}$'}}])

        patterns.append([{'POS': 'PROPN', 'OP': '?'}, {'LEMMA': {'IN': ['artículo', 'Artículo', 'arts', 'articulos', 'artículos']}},{'POS': 'ADP', 'OP': '?'}, {'IS_PUNCT': True, 'OP': '?'}, {'LEMMA': 'unico'},{'POS': 'PROPN', 'OP': '*'}])

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

    def _clean_punctuation(self, indexes, document):
        result = list()
        for index in indexes:
            clean_indexes = self._clean_word(index, document)
            result.append((clean_indexes, document[clean_indexes[0]:clean_indexes[1]]))
        return result

    def _clean_word(self, str_indexes, document):
        punkt = ["?", "¿", "¡", "!", ",", ".", ";", ":", "(", "-", " ", "--"]
        # print(word)
        start, end = str_indexes
        if (document[end-1] in punkt) or (document[end-1] is ")" and "(" not in document[start:end]):
            return self._clean_word((start, end-1), document)
        else:
            return str_indexes

    def _get_indexes(self, results):
        return [[result.start_char, result.end_char] for result in results]

    def _load_spacy(self, ):
        # LOAD SPACY
        t1 = timeit.default_timer()
        spacy_nlp = es_core_news_sm.load()
        spacy_nlp.max_length = 1500000
        t2 = timeit.default_timer()
        print(f"Time to load spaCy: {t2 - t1}")
        return spacy_nlp


def _check_and_build_json():
    # Check if json is in valid format
    try:
        json_object = json.loads(corpus_json_formated)
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(json_object, f, ensure_ascii=False)
        print("####### Json in VALID format #######")
        return json_object
    except ValueError as e:
        print("####### Json NOT in valid format #######")
        print(e)


if __name__ == "__main__":

    # VARIABLES OF TIME MANAGEMENT
    t_nltk = 0

    sentences = list()
    splitted_sentences = list()

    f = open("../documents/STS_175_2020.txt", "r", encoding="utf8")
    file = f.read()

    labeler = Labeler()

    prepoceced_corpus = labeler.execute_pre_process(file)

    corpus_json_formated = labeler.execute_core_algorithm(prepoceced_corpus)
    # print(corpus_json_formated)

    _check_and_build_json()


    # print(corpus_json_formated)
