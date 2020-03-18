import spacy, timeit


class NERFrameworksTest:

    def SPACY(self, corpus, spacy_nlp):

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
                # print(ent.text, ent.label_)
        return list_results_spacy



def mainTest():

    """CASTELLANO"""

    f = open("../../documents/12 pag software_cleaned.txt", encoding="utf8")
    corpus = f.read()


    # Orquestation
    ner = NERFrameworksTest()

    # LOAD SPACY
    t1 = timeit.default_timer()
    # es_core_news_sm
    spacy_nlp = spacy.load('blank_model')
    spacy_nlp.max_length = 2000000
    t2 = timeit.default_timer()

    print(f"Time to load Own Model: {t2-t1}")

    result_Spacy = ner.SPACY(corpus, spacy_nlp)
    for i in result_Spacy:
        print(i)


if __name__ == '__main__':

    mainTest()
