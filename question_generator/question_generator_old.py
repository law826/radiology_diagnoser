from nltk import word_tokenize, wordpunct_tokenize, RegexpChunkParser, RegexpParser
from nltk.chunk.regexp import ChunkRule
import nltk
import string

#tokens = wordpunct_tokenize('The differential diagnosis of COP includes bronchiolalveolar cell carcinoma, lymphoma, vasculitis, sarcoidosis, chronic eosinophilic pneumonia, and infectious pneumonia.')
#tokens = wordpunct_tokenize('AIP is a rapidly progressive form of interstitial pneumonia characterized histologically by hyaline membranes within the alveoli and diffuse, active interstitial fibrosis indistinguishable from the histoligcal pattern found in acute respiratory distress syndrome caused by sepsis and shock')
tokens = wordpunct_tokenize('Ground glass opacities are present in about 60 percent of cases.')

tagged = nltk.pos_tag(tokens)

sentences = ['The differential diagnosis of COP includes bronchiolalveolar cell carcinoma, lymphoma, vasculitis, sarcoidosis, chronic eosinophilic pneumonia, and infectious pneumonia.',
            'AIP is a rapidly progressive form of interstitial pneumonia characterized histologically by hyaline membranes within the alveoli and diffuse, active interstitial fibrosis indistinguishable from the histoligcal pattern found in acute respiratory distress syndrome caused by sepsis and shock',
            'Ground glass opacities are present in about 60 percent of cases.',
            'The term AIP is reserved for diffuse alveolar damage of unknown origin.',
            'Patients with AIP present with respiratory failure developing over days or weeks.',
            'Air bronchograms, with mild cylindric bronchial dilatation, are common.',
            'The upper lung refers to the upper one third of the lung, which includes the majority of the upper lobes and the uppermost portion of the superior segments of the lower lobes.'
]
#chunks = nltk.ne_chunk(tagged)

def verb_split(tagged):
    """
    Simple splitting of sentence based on first verb found.
    """
    try:
        first_verb_index = next(i for i, pair in enumerate(tagged) if (pair[1] == 'VBZ' or pair[1] == 'VBP'))
        first_verb_index
        question_list = [pair[0] for pair in tagged[:first_verb_index+1]]
        question_list.append('what?')
        question_string = ''.join([('' if c in string.punctuation else ' ')+c for c in question_list]).strip()
        answer_list = [pair[0] for pair in tagged[first_verb_index+1:]]
        answer_string = ''.join([('' if c in string.punctuation else ' ')+c for c in answer_list]).strip()
        return question_string, answer_string
    except:
        pass
   
def VBD_question(tagged):
    """
    Tries to leverage prepositions to generation questions.
    """
    try:
        first_verb_index = next(i for i, pair in enumerate(tagged) if (pair[1] == 'VBZ' or pair[1] == 'VBP'))
        subject_phrase = [pair[0] for pair in tagged[:first_verb_index+1]]
        phrase_dict = {'VBDP': 'VBDP: {<VBD|VBP|VBN><RB|JJ>*<IN>}'}
        vbdp_fragments = []
        for i, (key, phrase) in enumerate(phrase_dict.items()):
            cp = RegexpParser(phrase)
            if i==0:
                result = cp.parse(tagged)
            else:
                result = cp.parse(result)

        for i, item in enumerate(result):
            if type(item) is nltk.Tree:
                fragment = [pair[0] for pair in item]
                if item.node == 'VBDP':
                    vbdp_fragments.append((fragment, i))

        qa_list = []
        for vbdp, index in vbdp_fragments:
            question_list = subject_phrase + vbdp
            question_list.append('what?')
            question_string = ''.join([('' if c in string.punctuation else ' ')+c for c in question_list]).strip()
            sentence_remainder = result[index+1:]
            sentence_remainder_treeless = []
            for tree_or_tuple in sentence_remainder:
                try: 
                    tree_or_tuple.leaves()
                    for leaf in tree_or_tuple.leaves():
                        sentence_remainder_treeless.append(leaf)
                except AttributeError:
                    sentence_remainder_treeless.append(tree_or_tuple)


            answer_list = [pair[0] for pair in sentence_remainder_treeless]
            answer_string = ''.join([('' if c in string.punctuation else ' ')+c for c in answer_list]).strip()

            qa_list.append((question_string, answer_string))

        return qa_list
    except:
        """
        If not verb recognized above, simply split sentence based on prepositions.
        """
        prep_indices = [i for i, pair in enumerate(tagged) if pair[1] == 'IN']
        qa_list = []
        for prep_index in prep_indices:
            question_list = [pair[0] for pair in tagged[:prep_index+1]]
            question_list.append('what?')
            question_string = ''.join([('' if c in string.punctuation else ' ')+c for c in question_list]).strip()
            answer_list = [pair[0] for pair in tagged[prep_index+1:]]
            answer_string = ''.join([('' if c in string.punctuation else ' ')+c for c in answer_list]).strip()
            qa_list.append((question_string, answer_string))
        return qa_list

sentence_list = []
for sentence in sentences[6:7]:
    tokens = wordpunct_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    qa_list = []
    functions = [verb_split, VBD_question]
    for function in functions:
        partial_qa_list = function(tagged)
        qa_list.append(partial_qa_list)
    sentence_list.append(qa_list)
import pdb; pdb.set_trace()