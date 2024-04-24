import string
import re
from py_stringmatching.similarity_measure.overlap_coefficient \
    import OverlapCoefficient
from collections import Counter
from py_stringmatching.similarity_measure.cosine import Cosine


def split_arguments(text):
    return re.split('\t|\n', text.lower())


def filter_numbers_and_empty_cases(list_arguments):
    additional_pattern = re.compile('itt_\d+')
    return [element for element in list(set(list_arguments))
            if len(element) > 3
            and element[1] != '_'
            and not additional_pattern.match(element)
            ]


def remove_punctuations(text):
    # text = text.strip('\"')
    text = text.replace('(', '') \
        .replace(')', '') \
        .replace('"', '') \
        .replace('?', '') \
        .replace('.', '') \
        .replace(',', '') \
        .replace('!', '')
    text.translate(str.maketrans('', '', string.punctuation))
    return text


def word_frequency(text):
    return Counter(text.lower().split())


def compare_counts(dict1, dict2):
    # returns the words present in the first but not the second dictionary
    non_shared_words = {word: dict1[word]
                        for word in dict1
                        if word not in dict2
                        }
    common_words_different_count = {word: dict1[word] - dict2[word]
                                    for word in dict1
                                    if word in dict2
                                    and dict1[word] > dict2[word]
                                    }
    non_shared_words.update(common_words_different_count)
    return non_shared_words


def counter_to_list(dict_counter, word_lenght):
    list_words = []
    for word in dict_counter:
        # add only long words to the list
        if len(word) > word_lenght:
            for repeat in range(dict_counter[word]):
                list_words.append(word)
    return list_words


def overlap_similarity_index(modified_counter, original_counter,
                            role='bot', to_be_compared_word_length=2):
    # OverlapCoefficient does not care about number of instances
    # of a word; it just cares about its presence;
    # it computes the number of similar words divided by the
    # minimum length of either sets.
    # So I expanded the counter to engage all the words 
    # (to include all the instances)
    # in this version it only care about the words longer than
    # to_be_compared_word_length which is 2 by default
    modified_list = \
        counter_to_list(modified_counter, to_be_compared_word_length)
    original_list = \
        counter_to_list(original_counter, to_be_compared_word_length)

    oc = OverlapCoefficient()
    overlap_index = oc.get_raw_score(modified_list, original_list)
    # OverlapCoefficient normalized by dividing the overlap by the
    # length of the shorter list;
    # However, I want to divide it by the length of the modified list
    # for the wizards. Because mostly the have added a few words to
    #  the original arguments; thus the modified arguments become longer than
    # the original ones. However in the case of bots, they may have generated a 
    # very long part and added to the original argument. It would be wiser to keep
    # the denominator the length of the shorter argument; otherwise the overlap may
    # become too small
    if role == 'wizard':
        size_modified_arg = len(modified_list)
        size_original_arg = len(original_list)
        if size_modified_arg > size_original_arg:
            return overlap_index * size_original_arg / size_modified_arg

    return overlap_index


def cosine_similarity_index \
    (modified_counter, original_counter, to_be_compared_word_length=3):
    # Cosine similarity measures the number of common words didvided by
    # the square root of the multiplication of the length of two sets
    # it only takes the words longer than
    # to_be_compared_word_length into account
    modified_list = \
        counter_to_list(modified_counter, to_be_compared_word_length)
    original_list = \
        counter_to_list(original_counter, to_be_compared_word_length)

    cs = Cosine()
    cosine_index = cs.get_raw_score(modified_list, original_list)

    return cosine_index


def find_original_argument \
    (modified_arg_counts, original_args_counts, \
        base_line_similarity, to_be_compared_word_length=3):
    # search for the original message in the pool of that topic!
    for idx, argument_counts in \
            enumerate(original_args_counts):
        search_overlap = cosine_similarity_index(
            modified_arg_counts, argument_counts, \
                to_be_compared_word_length)
        if search_overlap >= base_line_similarity:
            found_original_count = argument_counts
            base_line_similarity = search_overlap
            idx_original_arg = idx
    return idx_original_arg, base_line_similarity, found_original_count

def extract_acknowlegements(text):
    pattern_pool = [
        'I see',
        'I do see',
        'I can see your point',
        'good point',
        'important point',
        'valid point',
        'interesting point',
        'great point',
        'excellent point'
        'I like your point',
        'fair',  # fair point
        'good reasons',
        'good question',
        'good idea',
        'great idea',
        'I totally accept',
        'I completely accept',
        'I accept',
        'I agree',
        'I largey agree',
        'I completely agree',
        'I definitely agree',
        'I totally agree',
        'Absolutely agree',
        'Agree there',
        'true',
        'exactly',
        'interesting response',
        'interesting position',
        'interesting question',
        'yes',
        'you are right',
        "you're right",
        'you are absolutely right',
        'you are correct',
        "you're correct",
        # 'you mean',
        # 'fair point',
        'I know what you mean',
        'exactly',
        'interesting perspective',
        ]

    for pattern in (pattern_pool):
        if re.search(pattern.lower(), text.lower()):
            return [pattern]
    # search for "yes" at the start of the message
    if text.lower().startswith('yes'):
        return ['yes']
    
    return []


def extract_hedging(text):
    pattern_pool = [
        'maybe',
        'perhaps',
        "it's possible",
        'it is possible',
        'it could be possible',
        'could it be possible',
        'it could be said'
        "it might be",
        # "it could be argued",
        # 'it could also be argued',
        'be argued',  # also count "couldn't it be argued"
        'people could',
        'some think',
        'some say',
        'some believe',
        'some argue',
        'some vegans argue',
        'would say',  # some/so many/people would say
        'would think',
        'would beleive',
        'would argue',  # some/people/many
        'might say',
        'might argue',
        'might think',
        'might believe',
        'may say',
        'may argue',
        'may think',
        'may believe',
        # 'some people feel',
        # 'some people doubt',
        # 'some people say',
        # 'some people think',
        # 'some people argue',
        # 'some people believe',
        # 'some people are concerned',
        'many people',
        'some people',
        'others argue',
        'others believe',
        'others think',
        'others say',
        'some have said that',
        # 'some people might argue',
        # "some people might believe",
        # 'some might argue',
        # 'some may argue',
        # 'some may believe',
        # 'some might believe',
        # 'some may say'
        # # 'some would say',
        # 'some might say',
        # 'some might think',
        # 'some may think',
        # 'some would think',
        ]

    for pattern in (pattern_pool):
        if re.search(pattern.lower(), text.lower()):
            return [pattern]
    return []


def extract_negation(text):
    pattern_pool = [
        'no but',
        'no, but',
        'not at all',
        "I don't think",
        'untrue',
        'That is not true',
        "That's not true",
        'not at all',
        ]
    for pattern in (pattern_pool):
        if re.search(pattern.lower(), text.lower()):
            return [pattern]

    # search for "no" at the start of the message
    if text.lower().startswith('no'):
        return ['no']

    return []


# search for patterns in modified arguments which have some add-ons!
# if they exist in modified argument,
# check if they are not part of the original argument
def patterns_in_added_text(modified_argument, original_argument):
    acknowlege_expressions_in_moidified = \
        extract_acknowlegements(modified_argument)
    if len(acknowlege_expressions_in_moidified) > 0:
        acknowlege_expressions_in_original = \
            extract_acknowlegements(original_argument)
    acknowlege_in_added_text = \
        [pattern for pattern
            in acknowlege_expressions_in_moidified
            if pattern not in acknowlege_expressions_in_original]

    hedgig_expressions_in_moidified = \
        extract_hedging(modified_argument)
    if len(hedgig_expressions_in_moidified) > 0:
        hedgig_expressions_in_original = \
            extract_hedging(original_argument)
    hedging_in_added_text = \
        [pattern for pattern in hedgig_expressions_in_moidified
            if pattern not in hedgig_expressions_in_original]

    negation_in_moidified = extract_negation(modified_argument)
    if len(negation_in_moidified) > 0:
        negation_in_original = extract_negation(original_argument)
    negation_in_added_text = \
        [pattern for pattern in negation_in_moidified
            if pattern not in negation_in_original]

    return acknowlege_in_added_text, hedging_in_added_text, \
        negation_in_added_text


def get_the_new_key(question, topic):
    if topic == 'brexit':
        nondoer_pattern = 'Remain'
    else:
        nondoer_pattern = 'NOT'

    list_partial_keys = [
        'doers_good_reasons',
        'doers_Unintelligent',
        'doers_Irrational',
        'doers_Ignorant',
        'doers_Unethical',
        'doers_Immoral',
        'doers_of_bad_moral_character',
        # 'non-doers_good_reasons',
        # 'non-doers_Unintelligent',
        # 'non-doers_Irrational',
        # 'non-doers_Ignorant',
        # 'non-doers_Unethical',
        # 'non-doers_Immoral',
        # 'non-doers_of_bad_moral_character'
    ]

    for tag in list_partial_keys:
        parts = tag.split('_')
        if (nondoer_pattern in question
                and parts[-1] in question):
            return 'non-' + tag + '_before', 'non-' + tag + '_after'
        elif parts[-1] in question:
            return tag + '_before', tag + '_after'
    return False
