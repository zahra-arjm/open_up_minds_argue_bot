import string
import re
from collections import Counter
import json
import functions as my_funcs


with open('brexit_all.txt', 'r') as b, \
     open('vaccination_all.txt', 'r') as vac, \
     open('veganism_all.txt', 'r') as veg:
    brexit_args = b.read()
    vaccine_args = vac.read()
    veganism_args = veg.read()

brexit_args = my_funcs.split_arguments(brexit_args)
brexit_args = my_funcs.filter_numbers_and_empty_cases(brexit_args)

vaccine_args = my_funcs.split_arguments(vaccine_args)
vaccine_args = my_funcs.filter_numbers_and_empty_cases(vaccine_args)

veganism_args = my_funcs.split_arguments(veganism_args)
veganism_args = my_funcs.filter_numbers_and_empty_cases(veganism_args)

list_arguments_by_topic = []
list_frequency_words_in_args = []
dict_count_args = {}
dict_args = {}
for argument in brexit_args:
    list_arguments_by_topic.append(argument)
    list_frequency_words_in_args.append(
        my_funcs.word_frequency(
            my_funcs.remove_punctuations
            (argument)
            )
            )
dict_args['brexit'] = list_arguments_by_topic
dict_count_args['brexit'] = list_frequency_words_in_args

list_arguments_by_topic = []
list_frequency_words_in_args = []
for argument in veganism_args:
    list_arguments_by_topic.append(argument)
    list_frequency_words_in_args.append(
        my_funcs.word_frequency(
            my_funcs.remove_punctuations
            (argument)
            )
            )
dict_args['veganism'] = list_arguments_by_topic
dict_count_args['veganism'] = list_frequency_words_in_args

list_arguments_by_topic = []
list_frequency_words_in_args = []
for argument in vaccine_args:
    list_arguments_by_topic.append(argument)
    list_frequency_words_in_args.append(
        my_funcs.word_frequency(
            my_funcs.remove_punctuations
            (argument)
            )
            )
dict_args['vaccination'] = list_arguments_by_topic
dict_count_args['vaccination'] = list_frequency_words_in_args


with open('arguments_frequency.json', 'w') as f_freq, \
     open('original_arguments_modified.json', 'w') as f:
    f_freq.write(json.dumps(dict_count_args))
    f.write(json.dumps(dict_args))
