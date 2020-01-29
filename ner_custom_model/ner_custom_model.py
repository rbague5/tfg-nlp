import timeit


class NerCustomModel:

	def custom_model(self, corpus):
		pass


def main_custom_model(corpus):
	print("|--------------------------------|")
	print("| STARTING NER WITH CUSTOM MODEL |")
	print("|--------------------------------|")

	# Orquestation
	ner_custom_model = NerCustomModel()

	dates_custom_model = list()

	# VARIABLES OF TIME MANAGEMENT
	t_custom_model = 0

	t1 = timeit.default_timer()
	result_custom_model = ner_custom_model.custom_model(corpus)
	t2 = timeit.default_timer()
	t_custom_model += (t2 - t1)

	if result_custom_model is not None:
		dates_custom_model += result_custom_model


if __name__ == '__main__':
	main_custom_model()
