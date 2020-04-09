import timeit

from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
import re
from models.regex.regex_generator import RegexGenerator
from models.regex.parameters import Parameters

# =============================================================================
# DICCIONARIOS FECHAS [COMPLETO]
# =============================================================================

class RegexModel:

	def __init__(self, parameters):
		self._parameters = parameters

	def execute_pre_process(self, corpus):
		splitted_sentences = list()

		t1 = timeit.default_timer()
		sentences = self._nltk_tokenizer(corpus)
		t2 = timeit.default_timer()
		print(f"Time for NLTK tokenizer: {t2 - t1}")

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
		corpus_string = ' '.join(splitted_sentences)

		return corpus_string

	def _nltk_tokenizer(self, document):
		abbreviation = ['sra', 'dª', 'dña', 'sras', 'sres', 'sr', 'excmos', 'excmo', 'excma', 'excmas', 'ilma', 'ilmas',
						'ilmo', 'ilmos', 'ilma', 'ilmas', 'art', 'arts', 'núm', 'cp', 'c.p', 's.l', 'rcud', 'rcuds',
						'rec']

		punkt_param = PunktParameters()

		punkt_param.abbrev_types = set(abbreviation)
		sentence_splitter = PunktSentenceTokenizer(punkt_param)
		text = document
		sentences = sentence_splitter.tokenize(text)

		return sentences

	@staticmethod
	def _aux_v2_join_groups_pre_post(match):
		result = dict()
		dict_match = {k: v for k, v in match.groupdict().items() if v}
		version = [k for k in dict_match if (("vz" not in k) and ("va" not in k))][0]

		dict_all_selected = {
			k: v for k, v in match.groupdict().items()
			if version == k.split("_")[0] or ("va" == k.split("_")[0] and v) or ("vz" == k.split("_")[0] and v)
		}
		list_selected = list(dict_all_selected.keys())

		# Se asigna el valor de v_[az] al v* que se haya detectado
		# El v_[az] puede estar antes y/o despues
		if list(dict_match.keys())[0] == "va":
			# Se agrega antes de la v* que haga match
			dict_match[version] = dict_match["va"] + dict_match[version]
			del dict_match["va"]

		if list(dict_match.keys())[-1][:2] == "vz":
			# Se agrega despues de la v*
			dict_match[version] += dict_match["vz"]
			del dict_match["vz"]

		for k, v in dict_match.items():
			# result[version+k[2:]] = v
			if (("vz" in k) or ("va" in k)):
				result[version + k[2:]] = (match.group(k), match.start(k), match.end(k))
			else:
				result[k] = (match.group(k), match.start(k), match.end(k))

		return result, list_selected, version

	@staticmethod
	def _aux_v2_generate_dict_with_list(list_keys):
		def aux_recursive_list(str_key, dict_keys_groups):
			x = str_key.split('_')[0]
			if x in list(dict_keys_groups.keys()):
				dict_keys_groups[x] = aux_recursive_list(str_key[len(x) + 1:], dict_keys_groups[x])
			else:
				dict_keys_groups[x] = dict()

			return dict_keys_groups

		dict_keys_groups = dict()
		for i in range(len(list_keys)):
			dict_keys_groups = aux_recursive_list(list_keys[i], dict_keys_groups)

		return dict_keys_groups

	@staticmethod
	def _aux_v2_generate_dict_with_dict(dict_groups):
		def aux_recursive_dict(str_key, tuple_value, dict_keys_match):
			x = str_key.split('_')[0]
			if x in list(dict_keys_match.keys()):
				dict_keys_match[x] = aux_recursive_dict(str_key[len(x) + 1:], tuple_value, dict_keys_match[x])
			else:
				dict_keys_match[x] = {"MATCH": tuple_value}  # dict()

			return dict_keys_match

		dict_keys_match = dict()
		for k, v in dict_groups.items():
			dict_keys_match = aux_recursive_dict(k, v, dict_keys_match)

		return dict_keys_match

	def _aux_v2_find_regex(self, match):
		# TODO: Que elimine los cond1 y cond2 si los hay
		# Genero el nuevo diccionario metiendo las subentidades del global(va|vz) al que haya encontrado (v1,v2,v3...)
		# dict_groups = (string_match, start_pos, end_pos)
		dict_match_groups, list_keys_selected, version = self._aux_v2_join_groups_pre_post(match)

		# Genero el esqueleto de todos los posibles grupos de la version que haya encontrado
		dict_keys_selected = self._aux_v2_generate_dict_with_list(list_keys_selected)[version]
		# Genero con el diccionario un diccionario escalonado, con estructura JSON
		dict_keys_match = self._aux_v2_generate_dict_with_dict(dict_match_groups)[version]

		ents_sel = list(dict_keys_selected.keys())
		ents_match = list(dict_keys_match.keys())
		# print(ents_sel, ents_match)

		entities = {"entity_str": match, "entity": dict()}
		for i in range(len(ents_match)):
			if ents_match[i] in ents_sel:  # Puede que haya que quitar este if
				ent = ents_match[i]
				entities["entity"][ent] = dict_keys_match[ent]["MATCH"]
				aux_cond1 = ("", 0, 0)
				aux_cond2 = ("", 0, 0)
				aux_opt1 = ("", 0, 0)
				aux_opt2 = ("", 0, 0)

				# Si esta entidad tiene condiciones inicial y/o final
				if "cond1" in list(dict_keys_selected[ent].keys()):
					if "cond1" in list(dict_keys_match[ent].keys()):
						aux_cond1 = dict_keys_match[ent]["cond1"]["MATCH"]
					else:
						# Se pone a None para despues decartar el match si no tiene las condiciones
						aux_cond1 = None

				if "cond2" in list(dict_keys_selected[ent].keys()):
					if "cond2" in list(dict_keys_match[ent].keys()):
						aux_cond2 = dict_keys_match[ent]["cond2"]["MATCH"]
					else:
						# Se pone a None para despues decartar el match si no tiene las condiciones
						aux_cond2 = None

				# Comprueba si existen las condiciones en esa sub_entidad y esta sola
				if not aux_cond1 and not aux_cond2:
					if (len(ents_match) - 1) < 2:
						del entities["entity"]
						break

				flag_iter = False
				if "iter" in list(dict_keys_match[ent].keys()):
					flag_iter = True
					ent_dict_match = dict_keys_match[ent]["iter"]
				# ent_dict_selected = dict_keys_selected[ent]["iter"]
				else:
					ent_dict_match = dict_keys_match[ent]
				# ent_dict_selected = dict_keys_selected[ent]

				if "opt1" in list(ent_dict_match.keys()):
					aux_opt1 = ent_dict_match["opt1"]["MATCH"]
				if "opt2" in list(ent_dict_match.keys()):
					aux_opt2 = ent_dict_match["opt2"]["MATCH"]

				if "val" in ent_dict_match:
					# Esta parte esta bien pero hay que elaborarla mas
					# En vez de num, tiene que comprobar el tipo que tenga
					# t = tipo
					# if "num" in list(ent_dict_match["val"].keys()):
					#     if ent_dict_match["val"]["num"]["MATCH"][0] == " ":
					#         if len(entities["entity"].keys()) == 1:
					#             del entities["entity"]
					#             return entities
					# else:
					#     if (len(ents_match) - 1) < 2:
					#         del entities["entity"]
					#         return entities

					# capturar valor de val y quitar espacios de iter
					# iter: _12_
					# val: 12

					# aux_sel = aux_dict_selected["val"].keys()
					# aux_match = aux_dict_match["val"].keys()
					# t = set(aux_sel).intersection(set(aux_match)).pop()

					# Si esta entidad tiene condiciones inicial y final
					# Si esta sub_entidad ha hecho match de las condiciones
					# if aux_cond1 or aux_cond2:
					if not aux_cond1:
						aux_cond1 = ("", 0, 0)
					if not aux_cond2:
						aux_cond2 = ("", 0, 0)

					result = entities["entity"][ent]  # dict_keys_match[ent]["iter"]["val"][t]["MATCH"]
					offset_s = len(aux_cond1[0])  # len(aux_opt1)
					offset_e = len(result[0]) - (len(aux_opt2[0]) + len(aux_cond2[0]))

					if flag_iter:
						entities["entity"][ent] = (
						result[0][offset_s:offset_e], result[1] + offset_s, result[1] + offset_e)
					else:
						entities["entity"][ent] = ent_dict_match["val"]["MATCH"]

				# Si no tiene iter quiere decir que tiene la forma de v1_ent_[]
				else:
					if aux_cond1 or aux_cond2:
						del entities["entity"]
						return entities

					entities["entity"][ent] = ent_dict_match["MATCH"]

		return entities

	def execute_core_algorithm(self, corpus):
		# Get dictionaries
		complete_dict = self._parameters.get_dictionaries()
		matches = re.finditer(complete_dict, corpus, re.MULTILINE | re.IGNORECASE)

		results = list()
		for match in matches:
			result_match = self._aux_v2_find_regex(match)
			if "entity" in list(result_match.keys()):
				# print("Indices:", result_match["entity_str"].span())
				result_indices = result_match["entity_str"].span()
				print("Original:", result_match["entity_str"].group())

				results.append(result_indices)
		return results



def main_regex():

	f = open("../../documents/STS_175_2020.txt", "r", encoding="utf8")
	file = f.read()

	parameters = Parameters()
	# Orquestation
	regex_model = RegexModel(parameters=parameters)

	corpus_preprocessed = regex_model.execute_pre_process(file)

	t1 = timeit.default_timer()
	result_regex = regex_model.execute_core_algorithm(corpus_preprocessed)
	t2 = timeit.default_timer()
	print(f"Total time for regex algorithm {t2-t1}")
	print(result_regex)

	if result_regex is not None:
		for i in result_regex:
			print(i)


if __name__ == '__main__':
	main_regex()
