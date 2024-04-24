import json
import functions as my_funcs


with open('argubot_final_exp.json', 'r') as f_exp, \
     open('arguments_frequency.json', 'r') as arg_freq, \
     open('original_arguments_modified.json', 'r') as args, \
     open('wizards_dialogues.json', 'r') as first_exp, \
     open('models_dialogues.json', 'r') as models:
    final_dialogues = json.load(f_exp)
    argument_frequencies = json.load(arg_freq)
    original_arguments = json.load(args)
    model_dialogues = json.load(models)
    wizards_dialogues = json.load(first_exp)

# length of to be compared words for finding the most related
# original argument. Based on trial and error for different experiments.
# it is 3 by defualt and the defualt is used for model and final dialogues
to_be_compared_word_length_wizards = 4

# analyze wizard's data
for idx_conversation, conversation in enumerate(wizards_dialogues):
    topic = conversation['topic']
    for idx_message, message in enumerate(conversation['messages']):
        if ('original_argument' not in message
                or 'modified_argument' not in message):
            continue
        if (message['original_argument'] != ""
                and message['role'] == 'woz'):
            original_count = my_funcs.word_frequency(
                my_funcs.remove_punctuations(
                    message['original_argument']
                    )
                    )
            modified_count = my_funcs.word_frequency(
                my_funcs.remove_punctuations(
                    message['modified_argument']
                    )
                    )
            found_original_count = original_count
            # find the actual original argments
            similarity = my_funcs.cosine_similarity_index(
                modified_count, original_count, \
                to_be_compared_word_length_wizards
                )
            max_similarity = similarity
            message['found_original_argument'] = \
                message['original_argument']
            if similarity < .5:
                idx_original_arg, max_similarity, found_original_count = \
                    my_funcs.find_original_argument(modified_count, \
                        argument_frequencies[topic], \
                        max_similarity, \
                        to_be_compared_word_length_wizards
                        )

                message['found_original_argument'] = \
                    original_arguments[topic][idx_original_arg]

            overlap = my_funcs.overlap_similarity_index(
                modified_count, found_original_count, role='wizard')
            # if overlap is smaller than .23 we are almost sure that
            # the wizard have not used the original argument
            if overlap < .23:
                message['found_original_argument'] = ''

            # if there were differences between original and
            # modified argument
            if overlap != 1:
                message['added_acknowledge'], message['added_hedging'], \
                    message['added_negation'] = \
                    my_funcs.patterns_in_added_text(
                        message['modified_argument'],
                        message['found_original_argument']
                        )

# analyze model_dialogues
for idx_conversation, conversation in enumerate(model_dialogues):
    topic = conversation['topic']
    for idx_message, message in enumerate(conversation['messages']):
        if ('original_argument' not in message
                or 'modified_argument' not in message):
            continue
        if (message['original_argument'] != ""
                and message['model'] == 'argubot'):
            original_count = my_funcs.word_frequency(
                my_funcs.remove_punctuations(
                    message['original_argument']
                    )
                    )
            modified_count = my_funcs.word_frequency(
                my_funcs.remove_punctuations(
                    message['modified_argument']
                    )
                    )
            found_original_count = original_count
            # find the actual original argments
            similarity = my_funcs.cosine_similarity_index(
                modified_count, original_count
                )
            max_similarity = similarity
            message['found_original_argument'] = \
                message['original_argument']
            if similarity < .5:
                # search for the original message in the pool of that topic!
                idx_original_arg, max_similarity, found_original_count = \
                    my_funcs.find_original_argument(modified_count, \
                        argument_frequencies[topic], \
                        max_similarity
                        )

                message['found_original_argument'] = \
                    original_arguments[topic][idx_original_arg]

            overlap = my_funcs.overlap_similarity_index(
                modified_count, found_original_count)
            # because of the nature of bot's args (sometimes much generated text
            # sometimes the exact original argument) I used the average of two 
            # similarity indices
            average_similarity = (overlap + max_similarity) / 2
            if average_similarity < .45:
                message['found_original_argument'] = ''
            # if there were differences between original and
            # modified argument
            if overlap != 1:
                message['added_acknowledge'], message['added_hedging'], \
                    message['added_negation'] = \
                    my_funcs.patterns_in_added_text(
                        message['modified_argument'],
                        message['found_original_argument']
                        )


for idx_conversation, conversation in enumerate(final_dialogues):
    topic = conversation['topic']
    for idx_message, message in enumerate(conversation['messages']):
        if ('original_argument' not in message
                or 'modified_argument' not in message):
            continue
        if (message['original_argument'] != ""
                and message['role'] == 'chatbot'):
            original_count = my_funcs.word_frequency(
                my_funcs.remove_punctuations(
                    message['original_argument']
                    )
                    )
            modified_count = my_funcs.word_frequency(
                my_funcs.remove_punctuations(
                    message['modified_argument']
                    )
                    )
            found_original_count = original_count
            # find the actual original argments
            similarity = my_funcs.cosine_similarity_index(
                modified_count, original_count
                )
            max_similarity = similarity
            message['found_original_argument'] = \
                message['original_argument']
            if similarity < .5:
                # search for the original message in the pool of that topic!
                idx_original_arg, max_similarity, found_original_count = \
                    my_funcs.find_original_argument(modified_count, \
                        argument_frequencies[topic], \
                        max_similarity
                        )

                message['found_original_argument'] = \
                    original_arguments[topic][idx_original_arg]

            overlap = my_funcs.overlap_similarity_index(
                modified_count, found_original_count)
            # because of the nature of bot's args (sometimes much generated text
            # sometimes the exact original argument) I used the average of two 
            # similarity indices
            average_similarity = (overlap + max_similarity) / 2
            if average_similarity < .497:
                message['found_original_argument'] = ''
            # if there were differences between original and
            # modified argument
            if overlap != 1:
                message['added_acknowledge'], message['added_hedging'], \
                    message['added_negation'] = \
                    my_funcs.patterns_in_added_text(
                        message['modified_argument'],
                        message['found_original_argument']
                        )

# save updated conversations
with open('wizards_dialogues_updated.json', 'w') as w, \
     open('model_dialogues_updated.json', 'w') as m, \
     open('final_dialogues_updated.json', 'w') as f:
    w.write(json.dumps(wizards_dialogues))
    m.write(json.dumps(model_dialogues))
    f.write(json.dumps(final_dialogues))