from enum import Enum
from models.regex.regex_generator import RegexGenerator


class DictionaryType(Enum):
    complete = 0
    enrere = 1

class NerType(Enum):
    fechas = 2

class LanguageType(Enum):
    es = "es"

class Parameters:
    """
    Encapsulamiento a los diccionarios y operaciones comunes de inicialización
    """
    def __init__(self):
        # RegEx NUEVO
        self.regex_generator = RegexGenerator()
        # Inicialización diccionarios fechas
        self._dict_completo_fechas_es = self._aux_regex_get_regex()

    def _aux_regex_get_regex(self):
        dict_regex_ner = {
                    '0_va': {
                        '0_time': {
                            '0_CONTENT': ',?\\b(?:sobre)?\\b',
                            '1_opt1': {
                                '0_CONTENT': 'a? *las'
                            },
                            '2_CONTENT': '? *',
                            '3_val': {
                                '0_CONTENT': '\\d{1,2}[:,]\\d{1,2} *(?:h|horas)?'
                            },
                            '4_CONTENT': ' *(?:sobre)? *',
                            '5_opt2': {
                                '0_CONTENT': 'del|$'
                            },
                            '6_CONTENT': '? *'
                        }
                    },
                    '1_CONTENT': '?(?:',
                    '2_v1': {
                        '0_day': {
                            '0_val': {
                                '0_CONTENT': '[0-2]?[0-9]|3[01]'
                            }
                        },
                        '1_CONTENT': '(?:[\\\\/:.\\-])',
                        '2_month': {
                            '0_val': {
                                '0_CONTENT': '0?[1-9]|1[0-2]'
                            }
                        },
                        '3_CONTENT': '(?:[\\\\/:.\\-])',
                        '4_year': {
                            '0_val': {
                                '0_CONTENT': '[12]\\d{3}|[012]\\d'
                            }
                        }
                    },
                    '3_CONTENT': '|',
                    '4_v2': {
                        '0_day': {
                            '0_iter': {
                                '0_CONTENT': '[ \\t]*',
                                '1_opt1': {
                                    '0_CONTENT': '^|d[ií]as?|el|los|del?|(?= )'
                                },
                                '2_CONTENT': ' *',
                                '3_val': {
                                    '0_num': {
                                        '0_CONTENT': '[0-3]?[0-9]'
                                    },
                                    '1_CONTENT': '|',
                                    '2_text': {
                                        '0_CONTENT': '(?:uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|trece|catorce|quince|dieci|vei?nt[ei]?|trei?ntai?)(?:>uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve)?'
                                    }
                                },
                                '4_CONTENT': ' *',
                                '5_opt2': {
                                    '0_CONTENT': ', *y|[\\,y]|(?= )'
                                },
                                '6_CONTENT': '(?= *)'
                            },
                            '1_CONTENT': '*'
                        },
                        '1_month': {
                            '0_cond1': {
                                '0_CONTENT': 'mes(?:es)? *(?:de)? *'
                            },
                            '1_CONTENT': '?',
                            '2_iter': {
                                '0_CONTENT': '[ \\t]*',
                                '1_opt1': {
                                    '0_CONTENT': '^|e[nl]|del?|(?= )'
                                },
                                '2_CONTENT': ' *',
                                '3_val': {
                                    '0_text': {
                                        '0_CONTENT': '(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|sep?tiembre|octubre|noviembre|diciembre)'
                                    }
                                },
                                '4_CONTENT': ' *',
                                '5_opt2': {
                                    '0_CONTENT': ', *y|[\\,y]|(?= )|\\.|$'
                                },
                                '6_CONTENT': '(?= *)'
                            },
                            '3_CONTENT': '+',
                            '4_cond2': {
                                '0_CONTENT': 'de este a[nñ]o'
                            },
                            '5_CONTENT': '?'
                        },
                        '2_year': {
                            '0_iter': {
                                '0_CONTENT': '[ \\t]*',
                                '1_opt1': {
                                    '0_CONTENT': 'el|en|del?|(?= )'
                                },
                                '2_CONTENT': ' *',
                                '3_val': {
                                    '0_max': {
                                        '0_CONTENT': '[1-2]\\.?[0-9]{3}'
                                    },
                                    '1_CONTENT': '|',
                                    '2_min': {
                                        '0_CONTENT': '[129][0-9](?=[ .,]|$)'
                                    }
                                },
                                '4_CONTENT': ' *',
                                '5_opt2': {
                                    '0_CONTENT': ', *y|[\\,y]|(?= )|(?=.)|\\.|$'
                                },
                                '6_CONTENT': '(?= *)'
                            },
                            '1_CONTENT': '*'
                        },
                        '3_CONTENT': '(?= *)'
                    },
                    '5_CONTENT': '|',
                    '8_v4': {
                        '0_year': {
                            '0_cond1': {
                                '0_CONTENT': 'a[nñ]os?'
                            },
                            '1_CONTENT': '?',
                            '2_iter': {
                                '0_CONTENT': '[ \\t]*',
                                '1_opt1': {
                                    '0_CONTENT': '^|, *y|[,y]| '
                                },
                                '2_CONTENT': ' *',
                                '3_val': {
                                    '0_max': {
                                        '0_CONTENT': '[1-2]\\.?[0-9]{3}'
                                    },
                                    '1_CONTENT': '|',
                                    '2_min': {
                                        '0_CONTENT': '[129][0-9]'
                                    }
                                },
                                '4_CONTENT': ' *',
                                '5_opt2': {
                                    '0_CONTENT': '(?=, *y)|(?=[\\,y])|(?= )|$'
                                },
                                '6_CONTENT': '(?= *)'
                            },
                            '3_CONTENT': '+',
                            '4_cond2': {
                                '0_CONTENT': ' *(?:(?: *[a-zA-Z]+ *){0,6})?a[nñ]os?'
                            },
                            '5_CONTENT': '?'
                        }
                    },
                    '9_CONTENT': ')',
                    '10_vz': {
                        '0_time': {
                            '0_CONTENT': ',? *(?:sobre)? *',
                            '1_opt1': {
                                '0_CONTENT': 'a? *las'
                            },
                            '2_CONTENT': '? *',
                            '3_val': {
                                '0_CONTENT': '\\d{1,2}[:,]\\d{1,2} *(?:h|horas)?'
                            },
                            '4_CONTENT': ' *(?:sobre)? *',
                            '5_opt2': {
                                '0_CONTENT': 'del|$'
                            },
                            '6_CONTENT': '?'
                        }
                    },
                    '11_CONTENT': '?'
                }
        result =self.regex_generator.generate_regex_with_dict(dict_regex_ner)
        return result


    def get_dictionaries(self):
        return self._dict_completo_fechas_es
