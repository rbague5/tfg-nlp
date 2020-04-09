import pandas as pd
import re, os


class RegexGenerator:
    def __init__(self):
        pass

    def get_regex_from_dataset(self, file):
        current_path = os.path.dirname(os.path.realpath(__file__)) + "/"
        df = pd.read_csv(current_path + file, sep=';', encoding='utf-8')
        df_sort = df.copy()

        # Se ordenan por la longitud de Acronimo
        list_sort_long = df_sort.Acronimo.str.len().sort_values().index
        df_sort = df_sort.reindex(list_sort_long).reset_index()

        list_len = list(df.Acronimo.str.len().unique())
        list_len.sort()

        # Se ordena por la longitud y en alfabetico
        df_sort["long_Acronimo"] = df_sort["Acronimo"].str.len()
        df_sorted = df_sort.sort_values(by=['long_Acronimo', 'Acronimo'])[list(df.columns)].reset_index(drop=True)

        list_acronimos = list(
            df_sorted.loc[
                (~df_sorted["Tipo"].str.contains("jurisprudencia") &
                 df_sorted["Valido"].str.contains("si"))]["Acronimo"
            ].values

        )
        # Modificaciones x.lower, a�adir puntos entre medias, etc...
        list_acronimos = [x.lower() for x in list_acronimos]
        list_acronimos.remove("ref")

        dict_acronimos = self._transform_list_to_dict_tree(list_acronimos)
        dict_acronimos['count'] = 0

        return self._convert_tree_dict_to_regex(dict_acronimos)

        # TODO: A�adir para todas las abreviaciones '.' y '-' entre cada caracter

    # GENERACION DE REGEX MEDIANTE DICCIONARIOS DE LOS GRUPOS
    def generate_dict_with_regex(self, regex):
        """
        Convierte una regex en un diccionario anidado de regex, teniendo en cuenta los nombres de los grupos
        Siempre y cuando los grupos tengan la forma de "a_b_c", es decir el grupo a contiene a b y este a c
        Osea, que se separa mediante el _ para determinar si esta dentro o no y el cierre del parentesis
        :param regex:
        :return: String regex
        """
        def find_close_par(regex):
            """
            Encuentra la posicion de cierre del parentesis que se le pasa, no tiene que incluirse el parentesis
            de abertura en el parametro de entrada
            :param regex: Texto regex
            :return: Devuelve la posicion del parentesis de cierre
            """
            open_par = 0
            flag_no_count = False
            for i in range(len(regex)):
                # window = regex[i-4:4+i]
                if regex[i] == "[" and regex[i - 1] != "\\":
                    flag_no_count = True
                if regex[i] == "]" and regex[i - 1] != "\\":
                    flag_no_count = False

                if regex[i] == "(" and regex[i - 1] != "\\":
                    if not flag_no_count:
                        open_par += 1
                elif regex[i] == ")" and regex[i - 1] != "\\":
                    if not flag_no_count:
                        open_par -= 1

                if open_par == -1:
                    return i

            return -1

        dict_regex = dict()
        while len(regex) > 0:
            matches = list(re.finditer(r"\(\?P<v(?:\d{1,2}|[az]{1,2})(?:_\w+)*>", regex))
            if len(matches) != 0:
                match = matches[0]
                if regex[:match.span()[0]] != "":
                    dict_regex[str(len(dict_regex)) + "_" + "CONTENT"] = regex[:match.span()[0]]

                close_par = find_close_par(regex[match.span()[1]:]) + match.span()[1]
                next_regex = regex[match.span()[1]:close_par]
                group_name = match.group()[4:-1].split("_")[-1]
                dict_regex[str(len(dict_regex)) + "_" + group_name] = self.generate_dict_with_regex(next_regex)

                # Se le suma uno para quitar el parentesis de cierre del grupo
                regex = regex[close_par + 1:]

            else:
                if regex != "":
                    dict_regex[str(len(dict_regex)) + "_" + "CONTENT"] = regex
                break

        return dict_regex

    def generate_regex_with_dict(self, dict_aux, group_name=""):
        """
        "Funcion que genera un string regex mediante un diccionario, siendo las claves el nombre del grupo
        o CONTENT siendo el contenido que no pertenecea ningun grupo. Estan ambos precedidos de "NUM_", Siendo
        NUM un entero que determina la posicion o el orden en la regex, ya que los diccionarios son mutables,
        y el contendio puede cambiar de orden
        :param dict_aux:
        :param group_name:
        :return:
        """
        regex = ""
        # Obtener lista de las claves
        list_aux = list(dict_aux.keys())
        list_aux.sort(key=lambda x: int(x.split("_")[0]))

        for k in list_aux:
            if k.split("_")[1] != "CONTENT":
                # Se crea el grupo de la clase
                group_name_next = k.split("_")[1] if group_name == "" else group_name + "_" + k.split("_")[1]
                regex += r"(?P<" + group_name_next + r">"
                # print(group_name_next)
                if type(dict_aux[k]) == dict:
                    regex += self.generate_regex_with_dict(dict_aux[k], group_name_next)
                    regex += r")"
                else:
                    regex += dict_aux[k]
            else:
                regex += dict_aux[k]

        return regex

    @staticmethod
    def _transform_list_to_dict_tree(list_aux):
        """
        Funcion que transforma una lista de palabras en un diccionario en forma de arbol de caracters, por lo
        que palabras que empiecen con la misma letra se guardan en la misma clave
        :param list_aux: Lista con palabras
        :return: Diccionario en forma de arbol con todas las palabras indexadas por caracteres
        """
        def recursive_dict_acronim_generator(dict_aux, acronim):
            """
            Funcion auxiliar para realizar la funcion principal de forma recursiva
            :param dict_aux: Diccionario que se va almacenando
            :param acronim: Clave a guardar = "b"
            :return: Devuelve el Diccionario anidado
            """
            if len(acronim) == 0:
                return dict_aux

            if acronim[0] in (dict_aux.keys()):
                dict_aux[acronim[0]] = recursive_dict_acronim_generator(dict_aux[acronim[0]], acronim[1:])
            else:
                dict_aux[acronim[0]] = {'count': 0}
                dict_aux[acronim[0]] = recursive_dict_acronim_generator(dict_aux[acronim[0]], acronim[1:])

            #Compruebo que es la ultima letra del acronimo
            if len(acronim[1:]) == 0:
                # Si es la ultima entonces tengo que incrementar el count a 1
                dict_aux[acronim[0]]['count'] += 1

            return dict_aux

        dict_char = dict()
        for x in list_aux:
            dict_char = recursive_dict_acronim_generator(dict_char, x)

        return dict_char

    def _convert_tree_dict_to_regex(self, dict_to):  # , traze="-"):
        """
        Funcion que convierte un diccionario anidado de grupos a un string regex
        :param dict_to:
        :return:
        """
        def get_keys_with_same_dict(key_of_reference, dict_aux):
            def compare_dicts(dict_of_reference, dict_to_compare):
                for k in dict_of_reference:
                    if k in list(dict_to_compare.keys()):
                        if type(dict_of_reference[k]) == dict:
                            return compare_dicts(dict_of_reference[k], dict_to_compare[k])
                        else:
                            if dict_of_reference[k] != dict_to_compare[k]:
                                return False
                    else:
                        return False

                return True

            list_keys_same_dict = list()
            for k in dict_aux:
                if k != key_of_reference:
                    if type(dict_aux[k]) == type(dict_aux[key_of_reference]):
                        if len(dict_aux[k]) == len(dict_aux[key_of_reference]):
                            if compare_dicts(dict_aux[key_of_reference], dict_aux[k]):
                                list_keys_same_dict += [k]

            return list_keys_same_dict

        # Se pueden agregar nombres de grupo, si se a�ade otra key como 'name'
        # ya que los diccionarios son siempre por caracteres
        regex_pattern=""
        flag_parenthesis = False
        keys_with_same_dict = list()

        # 1� Condicion de varios elementos (?:|||)
        # 2� Condicion de elementos condicionales (?: )?
        if (len(dict_to) > 2 or dict_to['count'] > 0):
            # Elementos condicionales
            if len(list(dict_to.keys())) == 2:
                nested_key = [x for x in list(dict_to.keys()) if x != 'count'][0]
                # Si el caracter siguiente es unico, es decir, no tiene mas delante
                ## Se sabe si dentro solo hay un count
                # Entonces no se abre parentesis, osea tiene que ser la longitud superior a 1
                if len(dict_to[nested_key]) > 1:
                    flag_parenthesis = True
                    regex_pattern += "(?:"
            else:
                flag_parenthesis = True
                regex_pattern += "(?:" # += "(?P<"+dict_to['name']+">"

        i_key = 0
        list_keys_to_process = list(dict_to.keys())
        # print(traze,"LISTA DE KEYS",list_keys_to_process)
        for k in list_keys_to_process:
            flag_same_dict = False
            if k != 'count':
                i_key += 1
                # print(traze,"CLAVE", k)
                # AQUI INSERTAR NUEVA FORMA DE AGRUPAR CLAVES CON MISMO DICCIONARIO
                # LA FUNCION QUE COMPRUEBA SI SON IGUALES TIENE QUE SER RECURSIVA,
                # Y QUE SALGA EN CUANTO UNA CLAVE NO SEA IGUAL
                # MIRAR PRIMERO LA LONGITUD, DESPUES SI SON IGUALES
                keys_with_same_dict = get_keys_with_same_dict(k, dict_to)
                # LOS ESPACIOS NO SE DEBEN AGREGAR, PORQUE PUEDEN HABER MAS DE UNO SEGUIDO,
                # ESTO SE PUEDE QUITAR SI ANTES SE ASEGURA QUE LOS DATOS NO CONTIENEN MAS DE UN ESPACIO SEGUIDO
                #             if " " in keys_with_same_dict:
                #                 keys_with_same_dict.remove(" ")

                if len(keys_with_same_dict) > 0:
                    # print(traze, "HAY OTROS IGUALES")
                    flag_same_dict = True
                    regex_pattern += "["
                    for i in range(len(keys_with_same_dict)):
                        if keys_with_same_dict[i] in ['-', '^']:
                            regex_pattern += '\\' + keys_with_same_dict[i]
                        else:
                            regex_pattern += keys_with_same_dict[i]

                    # DEBE BORRAR EL RESTO DE CLAVES IGUALES
                    for key_to_remove in keys_with_same_dict:
                        # print(traze, keys_with_same_dict, key_to_remove, list_keys_to_process)
                        list_keys_to_process.remove(key_to_remove)

                if k in ['.']:
                    regex_pattern += '\\'

                regex_pattern += k

                if flag_same_dict:
                    regex_pattern += "]"

                if k == ' ':
                    regex_pattern +="+"

                if len(dict_to[k]) > 1:
                    regex_pattern += self._convert_tree_dict_to_regex(dict_to[k])  # , traze=traze+"-")
                    # Si hay un count > 0 entonces a�ade un ?
                    if dict_to[k]['count'] > 0:
                        regex_pattern += '?'

                if len(list_keys_to_process) > 2 and i_key < len(list_keys_to_process)-1:
                    regex_pattern += "|"

        if flag_parenthesis:
            regex_pattern += ")"

        return regex_pattern
