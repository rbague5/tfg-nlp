import unittest
import spacy
import timeit

from models.spacy.Spacy import SpacyModel
from test.ConfusionMatrix import ConfusionMatrix


class TestEj1Es(unittest.TestCase):
    corpus = ""
    expected = ['28/01/2019-150:160',
                '28 de enero de 2019-1092:1111',
                '14 de marzo de 2016-1323:1342',
                '30 de enero de 2015-1494:1513',
                '30 de enero de 2015-1945:1964',
                '15 de septiembre de 2014-2419:2443',
                '15-09-2014-2660:2670',
                '4 de octubre de 2002-4474:4494',
                '9 de julio de 2014-5080:5098',
                '15 de septiembre-5113:5129',
                '14 de marzo de 2016-5895:5914',
                '30 de enero de 2015-6137:6156',
                '24 de octubre de 2014-6897:6918',
                '16 de octubre de 2018-7199:7220',
                '21 de noviembre de 2018-7249:7272',
                '16 de enero-7600:7611',
                '14-03-2016-8232:8242',
                '30-01-2015-8327:8337',
                '04-10-2002-8657:8667',
                '09-07-2014-9084:9094',
                '15-09-2014-9117:9127',
                '13-03-2014-9737:9747',
                '24-10-2014-9787:9797',
                '24-10-2014-13122:13132',
                '12-12-2014-13226:13236',
                '12-12-2014-13326:13336',
                '01-06-2017-13558:13568',
                '22-06-2017-13589:13599',
                '13 de marzo de 2014-14398:14417',
                '13 de marzo de 2014-16746:16765',
                '01-06-2017-16942:16952',
                '22-06-2017-17123:17133',
                '13 de marzo de 2014-18829:18848',
                '24-10-2014-18997:19007',
                '1997 a junio de 2013-19097:19117',
                'junio de 2013-19380:19393',
                '13 de marzo de 2014-20009:20028',
                '13-03-2014-21782:21792',
                '13-03-2014-21961:21971',
                '22-06-2017-22111:22121',
                '21 de septiembre-22346:22362',
                '12 de abril-22434:22445',
                '24 de marzo-23693:23704',
                '30 de abril-24535:24546',
                '19-06-1985-24597:24607',
                '18-03-1999-26195:26205',
                '28 de junio de 1999-26273:26292',
                '10-07-1999-26397:26407',
                '13-03-2014-28804:28814',
                '18 de marzo de 1999-28994:29013',
                '28 de junio de 1999-29081:29100',
                '13-03-2014-37986:37996',
                '14-09-2016-38150:38160',
                '13-03-2014-38201:38211',
                '01-06-2017-38330:38340',
                '22-06-2017-38366:38376',
                '01-06-2017-38992:39002',
                '01-06-2017-39172:39182',
                '21 de diciembre-39415:39430',
                '12 de abril-39495:39506',
                '01-06-2017-42254:42264',
                '22-06-2017-43632:43642',
                '13 de marzo de 2014-43935:43954',
                '22-06-2017-44200:44210',
                '15-02-2018-44927:44937',
                '19-07-2018-46353:46363',
                '11-04-2018-46946:46956',
                '13-03-2014-48422:48432',
                '13-03-2014-48669:48679',
                '04-10-2002-50530:50540',
                '09-07-2014-50774:50784',
                '15-09-2014-50798:50808',
                'septiembre del año 2014-51691:51714',
                '22-06-2017-52965:52975',
                '15-02-2018-52996:53006',
                '13-03-2014-53051:53061',
                '13-03-2014-53160:53170',
                '14-marzo-2016-55795:55808',
                '30-enero-2015-55960:55973']

    @classmethod
    def setUpClass(cls):
        print("\n######### RUNNING TESTS FOR EJ_1_ES #########")
        f = open("documents/ej_1_es_cleaned.txt", encoding="utf8")
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
        self.assertGreater(cm.F1, 0.7)

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
        self.assertGreater(cm.F1, 0.7)

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
        self.assertGreater(cm.F1, 0.7)

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
        self.assertGreater(cm.F1, 0.7)