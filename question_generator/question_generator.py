import nltk

text = nltk.word_tokenize('The differential diagnosis of COP includes bronchoalveolar cell carcinoma, lymphoma, and vasculitis.')
text = nltk.word_tokenize('AIP is a rapidly progressive form of interstitial pneumonia characterized histologically by hyaline membranes within the alveoli and diffuse, active interstitial ﬁbrosis indistinguishable from the histologic pattern found in acute respiratory distress syndrome caused by sepsis and shock.')


def simple_verb_parse(text):
	pos = nltk.pos_tag(text)
	first_verb_index = next(i for i, x in enumerate(pos) if x[1] == 'VBZ')
	question_list = [x[0] for x in pos[0:first_verb_index+1]]
	question_list.append('what?')
	question_string = ' '.join(question_list)


	answer_list = [x[0] for x in pos[first_verb_index+1:]]
	answer_string = ' '.join(answer_list)

	print 'Question: %s' %question_string
	print 'Answer: %s' %answer_string

simple_verb_parse(text)