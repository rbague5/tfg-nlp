import unittest
import spacy
import timeit

from models.spacy.Spacy import SpacyModel
from test.ConfusionMatrix import ConfusionMatrix


class TestEj2Es(unittest.TestCase):
    corpus = ""
    expected = ['31/05/2017-151:161',
                '31 de mayo de 2017-446:464',
                '6 de abril de 2016-689:707',
                '28 de enero de 2016-1052:1071',
                '28 de enero de 2016-1851:1870',
                '19.12.2015-2148:2158',
                '16 de enero de 2016-2523:2542',
                '6 de abril de 2016-4196:4214',
                '28/01/16-4623:4631',
                '21 de junio de 2016-7075:7094',
                '21 de noviembre de 2016-7375:7398',
                '9 de junio de 2016-7576:7594',
                '23 de junio de 2016-7667:7686',
                '14 de diciembre de 2016-7732:7755',
                '4 de abril de 2017-7851:7869',
                '25 de abril de 2017-7975:7994',
                '28 de enero de 2016-8434:8453',
                '19 de diciembre de 2015-8917:8940',
                '6 de abril de 2016-10197:10215',
                '5 de octubre-11452:11464',
                '30 de marzo-17035:17046',
                '23 de mayo-22577:22587',
                '11 de abril-28999:29010',
                '29 de abril-29027:29038',
                '1 de abril-29055:29065',
                '30 de marzo-29082:29093',
                '11 de mayo-29110:29120',
                '24 de mayo-29139:29149',
                '5 de octubre-31117:31129',
                '18 de noviembre-33467:33482',
                '26 de octubre de 2010-33748:33769',
                '26 de octubre de 2010-35366:35387',
                '10 de septiembre-35958:35974',
                '14 de noviembre-37393:37408',
                '6 de abril de 2016-42811:42829']

    @classmethod
    def setUpClass(cls):
        print("\n######### RUNNING TESTS FOR EJ_2_ES #########")
        f = open("documents/ej_2_es_cleaned.txt", encoding="utf8")
        cls.corpus = f.read()
        f.close()

    def test_es_core_legal_sm(self):
        t1 = timeit.default_timer()
        spacy_nlp = spacy.load('models/custom_model/es_core_legal_sm')
        spacy_nlp.max_length = 2000000
        t2 = timeit.default_timer()

        print("\nModel es_core_legal_sm")
        print(f"Time to load : {t2 - t1}")

        ents = spacy_nlp(self.corpus).ents
        results = [f"{ent.text}-{ent.start_char}:{ent.end_char}" for ent in ents if ent.label_ == 'FECHA']

        cm = ConfusionMatrix(self.corpus, results, self.expected)
        cm.print()
        self.assertGreater(cm.F1, 0.8)

    def test_es_core_legal_md(self):
        t1 = timeit.default_timer()
        spacy_nlp = spacy.load('models/custom_model/es_core_legal_md')
        spacy_nlp.max_length = 2000000
        t2 = timeit.default_timer()

        print("\nModel es_core_legal_md")
        print(f"Time to load : {t2 - t1}")

        ents = spacy_nlp(self.corpus).ents
        results = [f"{ent.text}-{ent.start_char}:{ent.end_char}" for ent in ents if ent.label_ == 'FECHA']

        cm = ConfusionMatrix(self.corpus, results, self.expected)
        cm.print()
        self.assertGreater(cm.F1, 0.8)

    def test_blank_model(self):
        t1 = timeit.default_timer()
        spacy_nlp = spacy.load('models/custom_model/blank_model')
        spacy_nlp.max_length = 2000000
        t2 = timeit.default_timer()

        print("\nModel blank_model")
        print(f"Time to load : {t2 - t1}")

        ents = spacy_nlp(self.corpus).ents
        results = [f"{ent.text}-{ent.start_char}:{ent.end_char}" for ent in ents if ent.label_ == 'FECHA']

        cm = ConfusionMatrix(self.corpus, results, self.expected)
        cm.print()
        self.assertGreater(cm.F1, 0.9)

    def test_spacy(self):
        t1 = timeit.default_timer()
        spacy_model = SpacyModel()
        results = spacy_model.execute_core_algorithm(self.corpus)
        t2 = timeit.default_timer()

        print("\nSpacy")
        print(f"Time to load : {t2 - t1}")

        results = [f"{span.text}-{span.start_char}:{span.end_char}" for span in results]

        cm = ConfusionMatrix(self.corpus, results, self.expected)
        cm.print()
        self.assertGreater(cm.F1, 0.9)