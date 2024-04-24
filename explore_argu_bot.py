import json
import functions as my_funcs


with open('argubot_final_exp.json', 'r') as f_exp, \
     open('arguments_frequency.json', 'r') as arg_freq, \
     open('original_arguments_modified.json', 'r') as args, \
     open('models_dialogues.json', 'r') as models:
    final_dialogues = json.load(f_exp)
    argument_frequencies = json.load(arg_freq)
    original_arguments = json.load(args)
    models_dialogues = json.load(models)

# for idx_conversation, conversation in enumerate(models_dialogues):
#     topic = conversation['topic']
#     for idx_message, message in enumerate(conversation['messages']):
#         if ('original_argument' not in message
#                 or 'modified_argument' not in message):
#             continue
#         if (message['original_argument'] != ""
#                 and message['model'] == 'argubot'):
#             original_count = my_funcs.word_frequency(
#                 my_funcs.remove_punctuations(
#                     message['original_argument']
#                     )
#                     )
#             modified_count = my_funcs.word_frequency(
#                 my_funcs.remove_punctuations(
#                     message['modified_argument']
#                     )
#                     )
#             found_original_count = original_count
#             # find the actual original argments
#             similarity = my_funcs.cosine_similarity_index(
#                 modified_count, original_count
#                 )
#             max_similarity = similarity
#             message['found_original_argument'] = \
#                 message['original_argument']
#             if similarity < .5:
#                 # search for the original message in the pool of that topic!
                # idx_original_arg, max_similarity = \
                #     my_funcs.find_original_argument(modified_count, \
                #         argument_frequencies[topic], \
                #         max_similarity
                #         )

#                 message['found_original_argument'] = \
#                     original_arguments[topic][idx_original_arg]

#             overlap = my_funcs.overlap_similarity_index(
#                 modified_count, found_original_count)
#             # because of the nature of bot's args (sometimes much generated text
#             # sometimes the exact original argument) I used the average of two 
#             # similarity indices
#             average_similarity = (overlap + max_similarity) / 2
#             if average_similarity < .45:
#                 message['found_original_argument'] = ''
            
#             if average_similarity < .6 and average_similarity >= .45:
#                 print(message)

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
                idx_original_arg, max_similarity = \
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

            # # find second original arguments!
            # if average_similarity > .497 and average_similarity < .95:
            #     not_in_original_count = my_funcs.compare_counts(
            #         modified_count, found_original_count)
            #     if len(not_in_original_count) > 6:
            #         max_similarity = 0
            #         for idx, argument_count in \
            #                 enumerate(argument_frequencies[topic]):
            #             search_overlap = my_funcs.overlap_similarity_index(
            #                 not_in_original_count, argument_count, 
            #                 to_be_compared_word_length=3)
            #             if search_overlap >= max_similarity:
            #                 found_original_count = argument_count
            #                 max_similarity = search_overlap
            #                 idx_original_arg = idx
                    # if max_similarity > .6:
                    #     print(f"Modified argument: {message['modified_argument']}\nFound original: {message['found_original_argument']}\nSecond: {original_arguments[topic][idx_original_arg]}")
#             # if there were differences between original and
#             # modified argument
#             if overlap != 1:
#                 message['added_acknowledge'], message['added_hedging'], \
#                     message['added_negation'] = \
#                     my_funcs.patterns_in_added_text(
#                         message['modified_argument'],
#                         message['found_original_argument']
#                         )
