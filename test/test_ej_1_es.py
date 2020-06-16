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
                '15 de septiembre de 2014-2420:2444',
                '15-09-2014-2663:2673',
                '4 de octubre de 2002-4481:4501',
                '9 de julio de 2014-5087:5105',
                '15 de septiembre-5120:5136',
                '14 de marzo de 2016-5903:5922',
                '30 de enero de 2015-6146:6165',
                '24 de octubre de 2014-6907:6928',
                '16 de octubre de 2018-7209:7230',
                '21 de noviembre de 2018-7259:7282',
                '16 de enero-7610:7621',
                '14-03-2016-8242:8252',
                '30-01-2015-8337:8347',
                '04-10-2002-8667:8677',
                '09-07-2014-9096:9106',
                '15-09-2014-9129:9139',
                '13-03-2014-9751:9761',
                '24-10-2014-9801:9811',
                '24-10-2014-13136:13146',
                '12-12-2014-13240:13250',
                '12-12-2014-13340:13350',
                '01-06-2017-13572:13582',
                '22-06-2017-13603:13613',
                '13 de marzo de 2014-14412:14431',
                '13 de marzo de 2014-16760:16779',
                '01-06-2017-16956:16966',
                '22-06-2017-17137:17147',
                '13 de marzo de 2014-18843:18862',
                '24-10-2014-19011:19021',
                '1997 a junio de 2013-19111:19131',
                'junio de 2013-19394:19407',
                '13 de marzo de 2014-20023:20042',
                '13-03-2014-21798:21808',
                '13-03-2014-21977:21987',
                '22-06-2017-22127:22137',
                '21 de septiembre-22362:22378',
                '12 de abril-22450:22461',
                '24 de marzo-23710:23721',
                '30 de abril-24555:24566',
                '19-06-1985-24617:24627',
                '18-03-1999-26219:26229',
                '28 de junio de 1999-26297:26316',
                '10-07-1999-26421:26431',
                '13-03-2014-28842:28852',
                '18 de marzo de 1999-29032:29051',
                '28 de junio de 1999-29119:29138',
                '13-03-2014-38032:38042',
                '14-09-2016-38196:38206',
                '13-03-2014-38247:38257',
                '01-06-2017-38376:38386',
                '22-06-2017-38412:38422',
                '01-06-2017-39038:39048',
                '01-06-2017-39220:39230',
                '21 de diciembre-39463:39478',
                '12 de abril-39543:39554',
                '01-06-2017-42304:42314',
                '22-06-2017-43682:43692',
                '13 de marzo de 2014-43985:44004',
                '22-06-2017-44250:44260',
                '15-02-2018-44977:44987',
                '19-07-2018-46403:46413',
                '11-04-2018-46996:47006',
                '13-03-2014-48476:48486',
                '13-03-2014-48725:48735',
                '04-10-2002-50590:50600',
                '09-07-2014-50834:50844',
                '15-09-2014-50858:50868',
                'septiembre del año 2014-51753:51776',
                '22-06-2017-53029:53039',
                '15-02-2018-53060:53070',
                '13-03-2014-53115:53125',
                '13-03-2014-53224:53234',
                '14-marzo-2016-55873:55886',
                '30-enero-2015-56038:56051'
            ]

    @classmethod
    def setUpClass(cls):
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