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
                '16 de enero de 2016-2525:2544',
                '6 de abril de 2016-4198:4216',
                '28/01/16-4625:4633',
                '21 de junio de 2016-7077:7096',
                '21 de noviembre de 2016-7377:7400',
                '9 de junio de 2016-7578:7596',
                '23 de junio de 2016-7669:7688',
                '14 de diciembre de 2016-7734:7757',
                '4 de abril de 2017-7853:7871',
                '25 de abril de 2017-7977:7996',
                '28 de enero de 2016-8436:8455',
                '19 de diciembre de 2015-8919:8942',
                '6 de abril de 2016-10201:10219',
                '5 de octubre-11456:11468',
                '30 de marzo-17041:17052',
                '23 de mayo-22597:22607',
                '11 de abril-29021:29032',
                '29 de abril-29049:29060',
                '1 de abril-29077:29087',
                '30 de marzo-29104:29115',
                '11 de mayo-29132:29142',
                '24 de mayo-29161:29171',
                '5 de octubre-31141:31153',
                '18 de noviembre-33493:33508',
                '26 de octubre de 2010-33775:33796',
                '26 de octubre de 2010-35400:35421',
                '10 de septiembre-35993:36009',
                '14 de noviembre-37432:37447',
                '6 de abril de 2016-42854:42872']

    @classmethod
    def setUpClass(cls):
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
        self.assertGreater(cm.F1, 0.8)

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
        self.assertGreater(cm.F1, 0.8)