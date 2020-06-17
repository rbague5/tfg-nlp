import unittest
import spacy
import timeit

from models.spacy.Spacy import SpacyModel
from test.ConfusionMatrix import ConfusionMatrix


class TestEj0Es(unittest.TestCase):
    corpus = ""
    expected = ['07/12/2016-150:160',
                '7 de diciembre de 2016-382:404',
                '13 de noviembre de 2014-604:627',
                '26 de junio de 2014-783:802',
                '26 de junio de 2014-1188:1207',
                '4 de marzo de 2009-1447:1465',
                '23 de noviembre de 2012-1651:1674',
                '18 de junio de 2013-1951:1970',
                '1 de julio de 2013-2033:2051',
                '1 de julio de 2013-2237:2255',
                '5 de junio de 2012-2661:2679',
                'julio de 2011-2848:2861',
                '14 de mayo de 2012-2963:2981',
                '7 de marzo de 2013-3245:3263',
                '14 de marzo de 2013-3422:3441',
                '1 de agosto de 2013-3626:3645',
                '1 de enero de 2014-3676:3694',
                '10 de febrero de 2014-4206:4227',
                '23 de mayo de 2013-4453:4471',
                '18 de julio de 2013-4557:4576',
                '23 de julio de 2012-4902:4921',
                '3 de septiembre-5165:5180',
                '15 de enero de 2013-6116:6135',
                '30 de enero de 2013-6177:6196',
                '28 de febrero de 2014-6662:6683',
                '17 de marzo-6742:6753',
                '13 de noviembre de 2014-7579:7602',
                '26 de Junio de 2014-7793:7812',
                '25 de febrero de 2014-8370:8391',
                '14 de octubre de 2015-8457:8478',
                '22 de noviembre de 2016-8983:9006',
                '25 de febrero de 2014-10039:10060',
                '12 y 14 mayo 2015-11457:11474',
                '2 junio 2016-11517:11529',
                '9 abril 2014-11927:11939',
                '20 julio 2015-12009:12022',
                '10 marzo 2016-12157:12170',
                '10 de diciembre de 1999-12952:12975',
                '3 noviembre 2015-13107:13123',
                '22 junio 2016-13431:13444',
                '16 de septiembre-14389:14405',
                '13 de noviembre de 2014-15326:15349',
                '26 de junio de 2014-15505:15524']

    @classmethod
    def setUpClass(cls):
        print("\n######### RUNNING TESTS FOR EJ_0_ES #########")
        f = open("documents/ej_0_es_cleaned.txt", encoding="utf8")
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
        self.assertGreater(cm.F1, 0.8)

    def test_spacy(self):
        t1 = timeit.default_timer()
        spacy_model = SpacyModel()
        results = spacy_model.execute_core_algorithm(self.corpus)
        t2 = timeit.default_timer()

        print("\nSpacy")
        print(f"Time to load : {t2 - t1}")

        results = [f"{span.text}-{span.start_char}:{span.end_char}" for span in results]
        # for i in results:
        #     print(f"'{i}',")
        cm = ConfusionMatrix(self.corpus, results, self.expected)
        cm.print()
        self.assertGreater(cm.F1, 0.8)