import json
import pandas as pd
from functions import *
# import matplotlib.pyplot as plt

experiments = ['wizards', 'model', 'final']

for experiment in experiments:
    f_name = experiment + '_dialogues_updated.json'
    with open(f_name, 'r') as w:
        conversations = json.load(w)

    # initiate an empty dicts with needed keys;
    #  every row belongs to one conversation
    conversations_dict = {
        'id': [],
        'topic': [],
        'count_woz_or_bot_messages': [],
        'count_acknowlegements': [],
        'count_hedgings': [],
        'count_negations': [],
        'count_receptive_msgs': [],
        'age': [],
        'gender': [],
        'take_part_again': [],
        'recommend': [],
        'doer or not': [],
        'Enjoyable': [],
        'Engaging': [],
        'Natural': [],
        'Confusing': [],
        'Frustrating': [],
        'Clear': [],
        'Persuasive': [],
        'Too_Complicated': [],
        'Boring': [],
        'Consistent': [],
        'Knowledgable': [],
        'doers_good_reasons_before': [],
        'doers_good_reasons_after': [],
        'doers_Unintelligent_before': [],
        'doers_Unintelligent_after': [],
        'doers_Irrational_before': [],
        'doers_Irrational_after': [],
        'doers_Ignorant_before': [],
        'doers_Ignorant_after': [],
        'doers_Unethical_before': [],
        'doers_Unethical_after': [],
        'doers_Immoral_before': [],
        'doers_Immoral_after': [],
        'doers_of_bad_moral_character_before': [],
        'doers_of_bad_moral_character_after': [],
        'non-doers_good_reasons_before': [],
        'non-doers_good_reasons_after': [],                            
        'non-doers_Unintelligent_before': [],
        'non-doers_Unintelligent_after': [],
        'non-doers_Irrational_before': [],
        'non-doers_Irrational_after': [],
        'non-doers_Ignorant_before': [],
        'non-doers_Ignorant_after': [],
        'non-doers_Unethical_before': [],
        'non-doers_Unethical_after': [],
        'non-doers_Immoral_before': [],
        'non-doers_Immoral_after': [],
        'non-doers_of_bad_moral_character_before': [],
        'non-doers_of_bad_moral_character_after': [],
        }
    # remove keys for wizards' experiment
    if experiment == 'wizards':
        conversations_dict.pop('Consistent')
        conversations_dict.pop('Knowledgable')

    for conversation in conversations:
        count_acknowlegements = 0
        count_hedgings = 0
        count_negations = 0
        count_woz_or_bot_messages = 0
        count_receptive_msgs = 0
        for message in conversation['messages']:
            if not(message.keys() >= {'original_argument', 'modified_argument'}):
                continue
            if (message['original_argument'] != "" and
                ((experiment == 'wizards' and message['role'] == 'woz') or
                (experiment == 'model' and message['model'] == 'argubot') or
                (experiment == 'final' and message['role'] == 'chatbot'))):
                count_woz_or_bot_messages += 1
                if 'added_acknowledge' in message:
                    count_acknowlegements += len(message['added_acknowledge'])
                    count_hedgings += len(message['added_hedging'])
                    count_negations += len(message['added_negation'])
                    # check if the message had propertise of a
                    #  receptive conversation
                    if ((len(message['added_acknowledge']) > 0)
                        & (len(message['added_hedging']) > 0)
                        & (len(message['added_negation']) == 0)):
                        count_receptive_msgs += 1
        if count_woz_or_bot_messages == 0:
            continue        
        conversations_dict['id'].append(conversation['_id'])
        conversations_dict['topic'].append(conversation['topic'])
        conversations_dict['count_woz_or_bot_messages'].append(count_woz_or_bot_messages)
        conversations_dict['count_acknowlegements'].append(count_acknowlegements)
        conversations_dict['count_hedgings'].append(count_hedgings)
        conversations_dict['count_negations'].append(count_negations)
        conversations_dict['count_receptive_msgs'].append(count_receptive_msgs)
        for general_key in conversation['participant_info']:
            # if it is a demographic quesion
            if general_key in conversations_dict:
                conversations_dict[general_key].append(conversation['participant_info'][general_key])
            elif general_key in ['Engagement', 'Chat_Content']:
                for specific_key in conversation['participant_info'][general_key]:
                    conversations_dict[specific_key].append(conversation['participant_info'][general_key][specific_key])
            elif general_key == 'Questions':
                for question in conversation['participant_info'][general_key]:
                    modified_key_before, modified_key_after = get_the_new_key(question, conversation['topic'])
                    conversations_dict[modified_key_before].append(conversation['participant_info'][general_key][question]['before'])
                    conversations_dict[modified_key_after].append(conversation['participant_info'][general_key][question]['after'])
            elif (general_key in
                ['Have you had at least one dose of an approved Covid-19 vaccine?',
                    'Did you vote for (Leave) or against (Remain) Brexit in the 2016 UK referendum?',
                    'In the referendum on whether the UK should remain a member of the EU (BREXIT), how did you vote?',
                    'Are you a vegan?'
                    ]):
                conversations_dict['doer or not'].append(conversation['participant_info'][general_key])
            
        # check if any of the keys in wizard dict does not have any value;
        #  flag by -2
        for key in conversations_dict:
            if len(conversations_dict[key]) < len(conversations_dict['id']):
                conversations_dict[key].append(-2)
    
    df = pd.DataFrame.from_dict(conversations_dict)
    f_name = experiment + '_df.csv'
    df.to_csv(f_name, index=False)
