import pandas as pd
import json


experiments = ['wizards', 'model', 'final']

responsive_or_not_participants = {}

for experiment in experiments:
    responsive_or_not_participants[experiment] = {}
    f_name = experiment + '_df.csv'
    df = pd.read_csv(f_name)
    before_cols = df.columns[df.columns.str.endswith('before')]
    after_cols = df.columns[df.columns.str.endswith('after')]
    doer_nondoer_cols = df.columns[
        df.columns.str.startswith('doers') | \
        df.columns.str.startswith('non-doers')
        ]
    # responsive participants are the ones who have answered at lease one survey question
    # non-responive participants have answered none of the questions
    # non-responsive-after were the ones who did not answer any of the post conversation questions
    # non-responsive-before were the ones who did not answer any of the pre conversation questions
    responsives = []
    non_responsives = []
    non_responsives_after = []
    non_responsives_before = []

    for conversation_idx in range(len(df)):
        if (any(df.loc[conversation_idx, before_cols] > 0) &
            any(df.loc[conversation_idx, after_cols] > 0)):
            responsives.append(df.loc[conversation_idx, 'id'])
        # if they were not in the responsive group and has answered at least
        # one before-question (pre-survey), it means they have not answered
        # after-questions (post-survey) and vice versa
        elif any(df.loc[conversation_idx, before_cols] > 0):
            non_responsives_after.append(df.loc[conversation_idx, 'id'])
        elif any(df.loc[conversation_idx, after_cols] > 0):
            non_responsives_before.append(df.loc[conversation_idx, 'id'])
        else:
            non_responsives.append(df.loc[conversation_idx, 'id'])

    responsive_or_not_participants[experiment]['responsives'] = responsives
    responsive_or_not_participants[experiment]['non_responsives'] = non_responsives
    responsive_or_not_participants[experiment]['non_responsives_before'] = \
        non_responsives_before
    responsive_or_not_participants[experiment]['non_responsives_after'] = \
        non_responsives_after

with (open('participants_responsiveness_ids.json', 'w') as p):
    p.write(json.dumps(responsive_or_not_participants))