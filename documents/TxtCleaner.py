import re

from nltk.tokenize.punkt import PunktParameters, PunktSentenceTokenizer


def execute_pre_process(corpus):
    splitted_sentences = list()

    sentences = _nltk_tokenizer(corpus)

    for sentence in sentences:
        # Mirem si hi ha newline per ajuntar-ho
        if "\n" in sentence:
            sentence = sentence.replace("\n", " ")
        # eliminamos el título de las frases y su simbolo raro
        sentence = clean_spaces(sentence)
        if "\x0c" in sentence:
            sentence = sentence.replace("\x0c", "")
        if "JURISPRUDENCIA" in sentence:
            sentence = sentence.replace("JURISPRUDENCIA", "")
        # S'ha de treure les cometes que sino trenquen el json
        if '"' in sentence:
            sentence = sentence.replace('"', "")

        splitted_sentences.append(sentence)
    splitted_sentences = (" ".join(splitted_sentences))
    return splitted_sentences


def clean_spaces(sentence):

    sentence = re.sub(' +', ' ', sentence)
    return sentence


def _nltk_tokenizer(document):
    abbreviation = ['sra', 'dª', 'dña', 'sras', 'sres', 'sr', 'excmos', 'excmo', 'excma', 'excmas', 'ilma', 'ilmas',
                    'ilmo', 'ilmos', 'ilma', 'ilmas', 'art', 'arts', 'núm', 'cp', 'c.p', 's.l', 'rcud', 'rcuds', 'rec']

    punkt_param = PunktParameters()

    punkt_param.abbrev_types = set(abbreviation)
    sentence_splitter = PunktSentenceTokenizer(punkt_param)
    text = document
    sentences = sentence_splitter.tokenize(text)

    return sentences


if __name__ == "__main__":
    f = open("./ej_2_es.txt", "r", encoding="utf8")

    document = f.read()

    splitted_text = execute_pre_process(document)
    result = clean_spaces(splitted_text)

    f = open("ej_2_es_cleaned.txt", "w", encoding="utf8")
    f.write(str(splitted_text))
    f.close()