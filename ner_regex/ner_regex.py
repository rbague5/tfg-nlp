import timeit


class NerRegex:

	def regex(self, corpus):
		pass


def main_regex(corpus):
	print("|-------------------------|")
	print("| STARTING NER WITH REGEX |")
	print("|-------------------------|")

	# Orquestation
	ner_regex = NerRegex()

	dates_regex = list()

	# VARIABLES OF TIME MANAGEMENT
	t_regex = 0

	t1 = timeit.default_timer()
	result_regex = ner_regex.regex(corpus)
	t2 = timeit.default_timer()
	t_regex += (t2 - t1)

	if result_regex is not None:
		dates_regex += result_regex


if __name__ == '__main__':

	main_regex()
