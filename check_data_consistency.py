import json
import pandas as pd

with open('argubot_final_exp.json', 'r') as f:
    final_dialogues = json.load(f)


topics = ['vegan', 'vaccine', 'brexit']
count_all_from_prolific = 0
ids = []
is_in_final_ids = []
for topic in topics:
    f_name = topic + '_chat_data.csv'
    with open(f_name, 'r') as f:
        prolific_df = pd.read_csv(f)
    id_list_topic = list(prolific_df['ResponseId'])
    ids.append(id_list_topic)
    count_all_from_prolific += len(id_list_topic)
    for id in id_list_topic:
        # check if they exist in final_dialogues
        for conversation in final_dialogues:
            for message in conversation['messages']:
                # check one message sent by particitipant for sender id
                if message['role'] == 'participant':
                    if message['sender'] == id:
                        is_in_final_ids.append(id)
                        break

print(f"Number of all participants in prolific: {count_all_from_prolific}\n"
      f"Number of participants in final_data: {len(final_dialogues)}\n"
      f"Number of participants in prolific who are also in final data: {len(is_in_final_ids)}")