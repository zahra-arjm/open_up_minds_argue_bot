import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# adding jitter where needed
def rand_jitter(arr, scale=.02):
    stdev = scale * (max(arr) - min(arr))
    return arr + np.random.randn(len(arr)) * stdev
# load participant ids for non-responsives
participants_ids_dict = pd.read_json('participants_responsiveness_ids.json', lines=True)
experiments = ['wizards',  'model', 'final']

# create empty figures to keep all experiments in one axes
fig1, hist_count_messages = plt.subplots()
fig2, hist_frequency_receptive_messages = plt.subplots()
fig3, receptive_vs_stanley_scores = plt.subplots(2, 1, figsize=(8, 12))
fig4, receptive_vs_rating = plt.subplots()
fig5, acknowledge_hedging_vs_receptiveness = plt.subplots(2, 3)
fig5.canvas.manager.full_screen_toggle() # toggle fullscreen mode
fig6, halo_effect_scatter = plt.subplots()

df_merged = pd.DataFrame()
for idx_exp, experiment in enumerate(experiments):
  f_name = experiment + '_df.csv'
  df = pd.read_csv(f_name)
  df.set_index('id', inplace=True)
  # in the final experiment everyone only answered "after" questions
  if experiment != 'final':
    # Only keep conversations who answered at least on question ('before' and 'after')
    df = df.loc[participants_ids_dict[experiment][0]['responsives'],:]

  # Calculate average changes in opinions for the opposite group. 
  # In the case of "no vote" in brexit group, 
  # both the change in opinion in both groups will be added.

  # split doers/non-doers/no votes
  doers_ids = df[ \
    (df['doer or not'] == 'yes') \
    | (df['doer or not'] == 'Yes') \
    | (df['doer or not'] == 'leave (for brexit)') \
    | (df['doer or not'] == 'Leave (For brexit)') \
        ].index
  nondoers_ids = df[ \
    (df['doer or not'] == 'against (remain)') \
    | (df['doer or not'] == 'no') \
    | (df['doer or not'] == 'No') \
    | (df['doer or not'] == 'remain (against brexit)') \
    | (df['doer or not'] == 'Remain (Against brexit)') \
        ].index
  # no votes
  non_action_ids = df.loc[(~df.index.isin(doers_ids)) & (~df.index.isin(nondoers_ids))].index

  # split questions into "before"/"after" and "doers"/"nondoers"
  after_cols = df.columns[df.columns.str.endswith('after')]
  before_cols = df.columns[df.columns.str.endswith('before')]
  doers_cols = df.columns[df.columns.str.startswith('doers')]
  nondoers_cols = df.columns[df.columns.str.startswith('non-doers')]

  for id in df.index:
    sum_movement = 0
    count_questions = 0
    if id in doers_ids:
      opp_before = nondoers_cols.intersection(before_cols)
      opp_after = nondoers_cols.intersection(after_cols)
    elif id in nondoers_ids:
      opp_before = doers_cols.intersection(before_cols)
      opp_after = doers_cols.intersection(after_cols)
    else:
      opp_before = before_cols
      opp_after = after_cols

    for idx, before_col in enumerate(opp_before):
      # if participants had answered to both "before" and "after" questions
      if (experiment == 'final' \
      or ((df.loc[id, before_col] > 0) \
      & (df.loc[id, opp_after[idx]] > 0))):
        count_questions += 1
      
        opinion_before = df.loc[id, before_col]
        opinion_after = df.loc[id, opp_after[idx]]
        # make before opinion 0 for final experiment; because participants were not
        # supposed to answer "before" questions
        if experiment == 'final':
          opinion_before = 0
        # reverse scoring for the question about 'good reasons'
        if 'good_reasons' in before_col:
          sum_movement = sum_movement + \
              opinion_after - \
              opinion_before
        else:
          sum_movement = sum_movement - \
              opinion_after + \
              opinion_before
    # since in final experiment they did not answer "before" questions
    # and most questions are negative for the "opposing group" I changed the sign
    # so the more favorable their opinion, it will be a higher value
    if experiment == 'final':
        sum_movement = -sum_movement
    df.loc[id, 'average_movement'] = sum_movement / count_questions
  # Calculate the participants opinion about their interaction with the wizards/bots.
  positive_cols = ['Enjoyable', 'Engaging', 'Natural', 'Clear', 'Persuasive']
  negative_cols = ['Confusing', 'Frustrating', 'Too_Complicated', 'Boring']
  engagement_qs = ['Enjoyable', 'Engaging', 'Natural', 'Confusing', 'Frustrating']
  content_qs = ['Clear', 'Persuasive', 'Too_Complicated', 'Boring']
  # add two columns for models and final experiments
  if experiment != 'wizards':
    positive_cols += ['Consistent', 'Knowledgable']
    content_qs += ['Consistent', 'Knowledgable']
  # the participants in wizards and model experiments either answered to all 
  # the questions about the survey or none of them
  # I reverse coded the negative columns and averaged all the sum
  # then centered the result around 4 to make it symmetric
  df['engagement_rating'] = \
    (df.loc[:, list(set(engagement_qs) & set(positive_cols))].sum(axis=1) \
    + 8 * len(set(engagement_qs) & set(negative_cols)) \
    - df.loc[:, list(set(engagement_qs) & set(negative_cols))].sum(axis=1)) \
    / (len(engagement_qs)) \
    - 4
  df['content_rating'] = \
    (df.loc[:, list(set(content_qs) & set(positive_cols))].sum(axis=1) \
    + 8 * len(set(content_qs) & set(negative_cols)) \
    - df.loc[:, list(set(content_qs) & set(negative_cols))].sum(axis=1)) \
    / (len(content_qs)) \
    - 4
  # number of conversations with negative ratings
  print(f"In {experiment} experiment\n"
        f"out of {len(df)} conversations\n"
        f"Number of negatively rated engagements: "
        f"{(df['engagement_rating'] < 0).sum()}\n"
        f"Number of negatively rated chat contents: "
        f"{(df['content_rating'] < 0).sum()}\n"
        f"Number of negation used: {(df['count_negations'] > 0).sum()}\n"
        f"Number of conversations with at least one receptive messages: " 
        f"{(df['count_receptive_msgs'] > 0).sum()} "
        f"({((df['count_receptive_msgs'] > 0).sum()) / len(df):.0%})\n"
        f"Number of conversations with at least one acknowledgement/hedging: " 
        f"{((df['count_acknowlegements'] > 0) | df['count_hedgings'] > 0).sum()} "
        f"({(((df['count_acknowlegements'] > 0) | df['count_hedgings'] > 0).sum()) / len(df):.0%})\n"
        f"Frequency of using acknowledgement/hedgings in conversations: "
        f"{((df['count_acknowlegements'] + df['count_hedgings']) / df['count_woz_or_bot_messages']).mean(): .2f}")
  ## visualize the data
  # Distribution of number of messages
  receptive_msg_frequency = df['count_receptive_msgs'] / \
                            df['count_woz_or_bot_messages']
  hist_count_messages.hist(df['count_woz_or_bot_messages'],
                    alpha=.5, label=f"{experiment} experiment")
  hist_frequency_receptive_messages.hist(receptive_msg_frequency,
                                          alpha=.5, 
                                          label=f"{experiment} experiment",
                                          bins=np.arange(-.05, 1.05, .05))
  receptive_vs_rating.scatter(rand_jitter(receptive_msg_frequency, scale=.05), \
                              df['engagement_rating'],
                              alpha=.5, 
                              label=f"{experiment} experiment")
  # plot "average_movement" or stanley scores in two differnt plots 
  # for final and the other two experiments. Because in final experiment
  # there were no movement; the score is just for "after" questions
  # about the opposite group
  if experiment == 'final':
    receptive_vs_stanley_scores[0].scatter(rand_jitter(receptive_msg_frequency), \
                                      df['average_movement'],
                                      alpha=.5, 
                                      label=f"{experiment} experiment",
                                      color='g')
  else:
    receptive_vs_stanley_scores[1].scatter(rand_jitter(receptive_msg_frequency), \
                                      df['average_movement'],
                                      alpha=.5, 
                                      label=f"{experiment} experiment")
  # check if acknowledgement is related to engagement
  df['if_include_acknowledge'] = df['count_acknowlegements'] > 0
  df['if_include_acknowledge_or_hedging'] = \
    (df['count_acknowlegements'] + df['count_hedgings']) > 0
  df['experiment'] = experiment
  # merge df with df_merged
  df_merged = pd.concat([df_merged, df])

# add columns  for categorizing number of acknowledgments and also its frequency
df_merged.insert(3, 'Number of Acknowledgements',
                 pd.cut(df_merged['count_acknowlegements'],
                  bins=[0,1,2,3,10],
                  right=False,
                  labels=['zero', 'one', 'two', 'three or more']))
data_for_cut = df_merged['count_acknowlegements'] / df_merged['count_woz_or_bot_messages']
df_merged.insert(4, 'Frequency of Acknowledgements',
                 pd.cut(data_for_cut,
                  bins=[0,.1,.2,.3,1.01],
                  right=False,
                  labels=['zero', '.1', '.2', '.3 or more']))
# add columns  for categorizing sum of acknowledgments and hedging and also their frequency
data_for_cut = df_merged['count_acknowlegements'] + df_merged['count_hedgings']
df_merged.insert(6, 'Number of Acknowledgements and Hedgings',
                 pd.cut(df_merged['count_acknowlegements'],
                  bins=[0,1,2,3,10],
                  right=False,
                  labels=['zero', 'one', 'two', 'three or more']))
data_for_cut = data_for_cut / df_merged['count_woz_or_bot_messages']
df_merged.insert(7, 'Frequency of Acknowledgements and Hedgings',
                 pd.cut(data_for_cut,
                  bins=[0,.1,.2,.3,1.01],
                  right=False,
                  labels=['zero', '.1', '.2', '.3 or more']))
# checking for halo_effect_scatter effect of chat content and engagement
sns.scatterplot(ax=halo_effect_scatter,
                data=df_merged,
                x='content_rating',
                y='engagement_rating',
                hue='experiment',
                alpha=.5
                )
halo_effect_scatter.set_aspect('equal', adjustable='box')
halo_effect_scatter.set_xlabel('Content Rating')
halo_effect_scatter.set_ylabel('Engagement Rating')
sns.boxplot(ax=acknowledge_hedging_vs_receptiveness[0, 0],
            x=df_merged['if_include_acknowledge'],
            y=df_merged['engagement_rating'],
            hue=df_merged['experiment'])
sns.boxplot(ax=acknowledge_hedging_vs_receptiveness[0, 1],
            x=df_merged['Number of Acknowledgements'],
            y=df_merged['engagement_rating'],
            hue=df_merged['experiment'])
sns.boxplot(ax=acknowledge_hedging_vs_receptiveness[0, 2],
            x=df_merged['Frequency of Acknowledgements'],
            y=df_merged['engagement_rating'],
            hue=df_merged['experiment'])
sns.boxplot(ax=acknowledge_hedging_vs_receptiveness[1, 0],
            x=df_merged['if_include_acknowledge_or_hedging'],
            y=df_merged['engagement_rating'],
            hue=df_merged['experiment'])
sns.boxplot(ax=acknowledge_hedging_vs_receptiveness[1, 1],
            x=df_merged['Number of Acknowledgements and Hedgings'],
            y=df_merged['engagement_rating'],
            hue=df_merged['experiment'])
sns.boxplot(ax=acknowledge_hedging_vs_receptiveness[1, 2],
            x=df_merged['Frequency of Acknowledgements and Hedgings'],
            y=df_merged['engagement_rating'],
            hue=df_merged['experiment'])  
hist_count_messages.legend()
hist_count_messages.set_title("Histogram of the count of messages sent by wizards/bots")
hist_frequency_receptive_messages.legend()
hist_frequency_receptive_messages.set_title("Histogram of frequency of Receptive Messages")
receptive_vs_rating.legend()
receptive_vs_rating.set_title("Frequency of receptive messages vs. Engagement Rating")
receptive_vs_stanley_scores[0].legend()
receptive_vs_stanley_scores[0].set_title("Frequency of receptive messages vs. Stanley Scores")
receptive_vs_stanley_scores[1].legend()
receptive_vs_stanley_scores[1].set_title("Frequency of receptive messages vs. Average Movement")
acknowledge_hedging_vs_receptiveness[0, 0].set_xticklabels(
      ['Acknowledgement Absent', 'Acknowledgement Present'])
acknowledge_hedging_vs_receptiveness[1, 0].set_xticklabels(
      ['Acknowledgement/Hedging Absent', 'Acknowledgement/Hedging Present'])
for ax in acknowledge_hedging_vs_receptiveness.reshape(-1): 
  ax.set_ylabel("Engagement Rating")
  ax.legend()
plt.show()