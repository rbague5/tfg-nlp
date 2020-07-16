# TFP-NLP
## Final project of my university degree

The aim of this project is to compare different methodologies for NER in court texts in Spanish.
The entities that I will extract from the text are dates.

The comparison is between regex, rule-base matcher with spaCy, building a custom model and updating an existing one with Transfer Learning.

## TESTING
Run all tests:
python -m unittest

Run all test for ej_2_es:
python -m unittest test.test_ej_2_es.TestEj2Es

Run test for es_core_legal_sm on ej_2_es:
python -m unittest test.test_ej_2_es.TestEj2Es.test_es_core_legal_sm