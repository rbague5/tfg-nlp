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
import sys


class Labeler:

    def execute_pre_process(self, corpus):

        splitted_sentences = list()

        t1 = timeit.default_timer()
        sentences = self._nltk_tokenizer(corpus)
        t2 = timeit.default_timer()
        print(f"Length of sentences: {len(sentences)} \n Time for NLTK tokenizer: {t2-t1}")

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
            print(f"Sentence spacy: {sentence}")
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

    def spacy_main(self, sentence, spacy_nlp):
        json_result = list()
        double_quotes_ent = ""

        list_not_clenaned_results_spacy = list()
        list_of_indices = list()
        indexes = list()

        t1 = timeit.default_timer()
        document = spacy_nlp(sentence)
        t2 = timeit.default_timer()
        # print(f"Time for spacy_nlp {t2 - t1}")

        # Print Token and Tag of the document_page
        # for token in document:
        #     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
        #           token.shape_, token.is_alpha, token.is_stop)

        t1 = timeit.default_timer()
        matcher = Matcher(spacy_nlp.vocab)
        matcher.add("FECHA", None, *self._get_patterns())
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

            # Afegeixo la entitat als indexos
            for i in indexes:
                # print(f"i: {i}")
                i.append("FECHA")
                json_result.append(json.dumps(i))
            # print(f"json_result {json_result}")
            time4 = timeit.default_timer()
            # cleaned_indexes = self._clean_punctuation(indexes=indexes, document=corpus)
            time5 = timeit.default_timer()
            pre_entities = []
        print(f"sentence: {sentence}")
        for ent in document.ents:
            pre_entities = [int(ent.start_char), int(ent.end_char), str(ent.label_)]
            print(pre_entities)
            indexes.append(pre_entities)

            # print(json.dumps(indexes))
            # serveix per ficar les double quotes
            # print(f"pre_entities: {pre_entities}")
            # print(f"indexes: {indexes}")
            # print(f"json.dumps(indexes): {json.dumps(indexes)}")
        clean_entities = self.check_index_entities(indexes)
        return json.dumps(clean_entities)

    def check_index_entities(self, indexes):

        # print(f"Indices que me entran: {indexes} \n")
        indices_fechas = list()
        result = list()

        for index in indexes:
            if index[2] is "FECHA":
                for i in range(index[0], index[1]+1):
                    indices_fechas.append(i)
                result.append(index)
            else:
                # print(f"No soy una fecha {index}, i[0]: {index[0]}, i[0]: {index[1]}")
                elem_to_find = list()
                # El +1 es pq pilli el ultim num del range
                # iterem per tots els elements del index en questió
                for i in range(index[0], index[1]+1):
                    elem_to_find.append(i)
                # print(f"I have current indices {elem_to_find}")
                indices_fechas_set = set(indices_fechas)
                elem_to_find_set = set(elem_to_find)
                if indices_fechas_set & elem_to_find_set:
                    pass
                    # print(f"Index: {index} IS IN {indices_fechas}")
                else:
                    # print(f"Index: {index} NOT IN {indices_fechas}")
                    result.append(index)

        print(f"Result: {result}")
        return result

    def _get_patterns(self):
        patterns = list()
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto',
                 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre', 'enero', 'febrero', 'marzo',
                 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

        # PATRONES DE FECHAS
        # https://spacy.io/usage/rule-based-matching
        patterns.append([{'POS': 'NUM', 'IS_DIGIT': True}, {'POS': 'ADP'}, {'ORTH': {'IN': meses}}, {'POS': 'ADP'}, {'POS': 'NUM', 'IS_DIGIT': True, 'LENGTH': {"==": 4}}])
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
        spacy_nlp.max_length = 3000000
        t2 = timeit.default_timer()
        print(f"Time to load spaCy: {t2 - t1}")
        return spacy_nlp


def _check_and_build_json(corpus):
    # Check if json is in valid format
    try:
        json_object = json.loads(corpus)
        with open('data_not_blank.json', 'w', encoding='utf-8') as f:
            json.dump(json_object, f, ensure_ascii=False)
        print("####### Json in VALID format #######")
        return json_object
    except ValueError as e:
        print("####### Json NOT in valid format #######")
        print(e)


if __name__ == "__main__":

    # VARIABLES OF TIME MANAGEMENT
    t_nltk = 0
    document = str()
    sentences = list()
    splitted_sentences = list()

    labeler = Labeler()

    f1 = open("../documents/22 pag_cleaned.txt", "r", encoding="utf8")
    file = f1.read()
    prepoceced_corpus = labeler.execute_pre_process(file)
    f1.close()

    f2 = open("../documents/31 pag_cleaned.txt", "r", encoding="utf8")
    file = f2.read()
    result = labeler.execute_pre_process(file)
    prepoceced_corpus+result
    f2.close()

    f3 = open("../documents/84 pag_cleaned.txt", "r", encoding="utf8")
    file = f3.read()
    result = labeler.execute_pre_process(file)
    prepoceced_corpus + result
    f3.close()

    f4 = open("../documents/133 pag_cleaned.txt", "r", encoding="utf8")
    file = f4.read()
    result = labeler.execute_pre_process(file)
    prepoceced_corpus + result
    f4.close()

    f5 = open("../documents/493 pag_cleaned.txt", "r", encoding="utf8")
    file = f5.read()
    result = labeler.execute_pre_process(file)
    prepoceced_corpus + result
    f5.close()

    # document = f1.read() + f2.read() + f3.read() + f4.read() + f5.read()



    # prepoceced_corpus = labeler.execute_pre_process(document)
    # print(prepoceced_corpus)
    # print(len(prepoceced_corpus))
    # print(type(prepoceced_corpus))

    corpus_json_formated = labeler.execute_core_algorithm(prepoceced_corpus)
    # print(corpus_json_formated)

    _check_and_build_json(corpus=corpus_json_formated)

    # print(corpus_json_formated)
