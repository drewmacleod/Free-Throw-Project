# Github link to project: https://github.com/drewmacleod/Free-Throw-Project/tree/main/Free%20throws

import pandas as pd
import numpy as np
# Separate file that contains helper functions for cleaning up syntax
import free_throw_helpers as fth
import warnings
import matplotlib.pyplot as plt
import plotly.express as px
import matplotlib.ticker as mtick
from scipy.stats import ttest_ind

warnings.filterwarnings('ignore')
every_free_throw = pd.read_csv('data/free_throws.csv')
basketball_ref_url_16 = 'https://www.basketball-reference.com/leagues/NBA_2016_totals.html'
basketball_ref_url_15 = 'https://www.basketball-reference.com/leagues/NBA_2015_totals.html'
basketball_ref_url_14 = 'https://www.basketball-reference.com/leagues/NBA_2014_totals.html'
# Reads in seasons from 2013-2016
basketball_ref_stats_16 = pd.read_html(basketball_ref_url_16)
basketball_ref_stats_15 = pd.read_html(basketball_ref_url_15)
basketball_ref_stats_14 = pd.read_html(basketball_ref_url_14)
# Clean up html read in
basketball_ref_stats_16_df = basketball_ref_stats_16[0]
basketball_ref_stats_15_df = basketball_ref_stats_15[0]
basketball_ref_stats_14_df = basketball_ref_stats_14[0]

# If a player is traded midseason they have a row for each team and then a Total row. We only want Total row.
def drop_extra_rows_for_traded_player(df):
    player = ''
    for index,row in df.iterrows():
        if row['Tm'] == 'TOT':
            player = row['Player']
        elif player == row['Player']:
            row['Player'] = np.nan
    df = df[pd.notnull(df['Player'])]
    return df

basketball_ref_stats_14_df = drop_extra_rows_for_traded_player(basketball_ref_stats_14_df)
basketball_ref_stats_15_df = drop_extra_rows_for_traded_player(basketball_ref_stats_15_df)
basketball_ref_stats_16_df = drop_extra_rows_for_traded_player(basketball_ref_stats_16_df)

# Puts all 3 seasons freethrow numbers into fourth_quarter_ot_freethrows
seasons = ['2013 - 2014', '2014 - 2015', '2015 - 2016']
s = every_free_throw.season.isin(seasons)
fourth_quarter_ot_free_throws = every_free_throw[s]
# gets only 4th quarter/ OT free throws
fourth_quarter_ot_free_throws = fourth_quarter_ot_free_throws[fourth_quarter_ot_free_throws['period'] >= 4]
fourth_quarter_ot_free_throws['score_diff'] = fourth_quarter_ot_free_throws['score'].apply(fth.score_difference)
time_seconds = fourth_quarter_ot_free_throws['time'].apply(fth.time_into_seconds)
fourth_quarter_ot_free_throws['time_seconds'] = time_seconds
clutch_free_throws = fourth_quarter_ot_free_throws[(fourth_quarter_ot_free_throws['time_seconds'] <= 120) &
                                                 (fourth_quarter_ot_free_throws['score_diff'] <= 5)]
clutch_free_throws['player'] = clutch_free_throws['player'].apply(fth.fix_player_syntax)
clutch_ft_by_player = clutch_free_throws.groupby('player').shot_made.sum()
clutch_ft_by_player = clutch_ft_by_player.to_frame()
clutch_ft_by_player.columns = ['clutch_fts_made']
clutch_ft_by_player['clutch_fts_attempted'] = clutch_free_throws.groupby('player').shot_made.count()
clutch_ft_by_player['clutch_ft_decimal_percent'] = (clutch_ft_by_player['clutch_fts_made'] / clutch_ft_by_player['clutch_fts_attempted'])
clutch_ft_by_player['clutch_fts_attempted'].describe()

combined_14_15_seasons_stats = basketball_ref_stats_14_df.merge(basketball_ref_stats_15_df, on = 'Player', how='outer')
all_season_combined = combined_14_15_seasons_stats.merge(basketball_ref_stats_16_df, on ='Player', how='outer')
# drop header rows
all_season_combined = all_season_combined.drop(all_season_combined[all_season_combined['FTA_x'] == 'FTA'].index, )
all_season_combined = all_season_combined.fillna(0)

# make into integers instead of strings
all_season_combined['FTA_x'] = all_season_combined['FTA_x'].apply(lambda x: int(x))
all_season_combined['FTA_y'] = all_season_combined['FTA_y'].apply(lambda x: int(x))
all_season_combined['FTA'] = all_season_combined['FTA'].apply(lambda x: int(x))
# make into intgeres instead of strings
all_season_combined['FT_x'] = all_season_combined['FT_x'].apply(lambda x: int(x))
all_season_combined['FT_y'] = all_season_combined['FT_y'].apply(lambda x: int(x))
all_season_combined['FT'] = all_season_combined['FT'].apply(lambda x: int(x))

# make combined ft percentage for all 3 seasons
all_season_combined['total_ftm'] = all_season_combined['FT_x'] + all_season_combined['FT_y'] + all_season_combined['FT'] 
all_season_combined['total_fta'] = (all_season_combined['FTA_x'] + all_season_combined['FTA_y'] + all_season_combined['FTA'])
all_season_combined['total_ft%'] = (all_season_combined['total_ftm']) / (all_season_combined['total_fta'])

# normalize player name syntax for all seasons players
all_season_combined['Player'] = all_season_combined['Player'].apply(fth.fix_player_syntax)
clutch_ft_by_player = clutch_ft_by_player.reset_index()
# then merge clutch free throws onto that 3 season data frame 
clutch_and_total_combined = all_season_combined.merge(clutch_ft_by_player, left_on='Player', right_on='player')
# data frame with only clutch ft attempts > 75th percentile in attempts
sorted_clutch_and_total = clutch_and_total_combined[clutch_and_total_combined['clutch_fts_attempted'] >= 25]
# biggest changes positive or negative
sorted_clutch_and_total['ft_difference_in_clutch'] = sorted_clutch_and_total['clutch_ft_decimal_percent'] - sorted_clutch_and_total['total_ft%']
# biggest improvement in free throws
biggest_improvement_5 = sorted_clutch_and_total.sort_values('ft_difference_in_clutch', ascending=False).head(5)
# biggest regression in free throws
biggest_regression_5 = sorted_clutch_and_total.sort_values('ft_difference_in_clutch').head(5)
# best overall clutch percentage
best_overall_5 = sorted_clutch_and_total.sort_values('clutch_ft_decimal_percent', ascending = False).head(5)
# worst overall clutch percentage
worst_overall_5 = sorted_clutch_and_total.sort_values('clutch_ft_decimal_percent').head(5)
# set universal font settings for plots
plt.rcParams.update({'font.size': 8, 'font.weight': 'bold'})
# Creates chart showing comparison between overall free throws and in the clutch free throws.
# Optionally includes the difference vs the overall and clutch FT %'s'
def create_comparison_graph(df_original, chart_title, include_diff = False):
    df = df_original.copy()
    df['ft_difference_in_clutch'] = df['ft_difference_in_clutch'] * 100
    df['total_ft%'] = df['total_ft%'] * 100
    df['clutch_ft_decimal_percent'] = df['clutch_ft_decimal_percent'] * 100
    if include_diff:
        y_columns = ['ft_difference_in_clutch','total_ft%','clutch_ft_decimal_percent']
        y_labels = ['FT % Difference in Clutch', 'Total FT %', 'Clutch FT %']
        y_lim_min = min((df['ft_difference_in_clutch'].min() * 1.1), 0)
    else: 
        y_columns = ['total_ft%','clutch_ft_decimal_percent']
        y_labels = ['Total FT %', 'Clutch FT %']
        y_lim_min = 0        
    bar = df.plot(x = 'Player', y= y_columns, kind = 'bar',title = chart_title, ylim = (y_lim_min,110), alpha = 0.6)
    bar.set_ylabel('Free Throw %')
    bar.yaxis.set_major_formatter(mtick.PercentFormatter())
    for i in bar.patches:
        bar.annotate(str(round(i.get_height(), 1))+'%', xy=((i.get_x() - .035), (i.get_height() + 0.01)))
    bar.legend(loc='upper center', bbox_to_anchor=(0.7, 1.0),
          fancybox=True, labels= y_labels)
    return bar
# Create Charts for 4 different cases we'd be interested in looking at.
best_5_chart = create_comparison_graph(best_overall_5, 'Most Clutch Free Throw Shooters Average vs. Clutch Free Throw %')
worst_5_chart = create_comparison_graph(worst_overall_5, 'Least Clutch Free Throw Shooters Average vs. Clutch Free Throw %')
improved_5_chart = create_comparison_graph(biggest_improvement_5, 'Most Improved Free Throw Shooters in the Clutch', include_diff=True)
regressed_5_chart = create_comparison_graph(biggest_regression_5, 'Most Free Throw % Regression in the Clutch', include_diff=True)
plt.show()
# Remove the overlapping free throws from overall in order to properly test significance
clutch_and_total_combined['total_ftm_w_out_clutch'] = clutch_and_total_combined['total_ftm'] - clutch_and_total_combined['clutch_fts_made']
clutch_and_total_combined['total_fta_w_out_clutch'] = clutch_and_total_combined['total_fta'] - clutch_and_total_combined['clutch_fts_attempted']
clutch_and_total_combined['total_ft%_w_out_clutch'] = clutch_and_total_combined['total_ftm_w_out_clutch'] / clutch_and_total_combined['total_fta_w_out_clutch']
# Calculate Ttest Results and Print results and findings
print(ttest_ind(clutch_and_total_combined['clutch_ft_decimal_percent'], clutch_and_total_combined['total_ft%_w_out_clutch']))
print("P Value of 0.079 shows that there is a Statistically Signifcant difference at the 10 percent level (but not 5) where shooters perform worse at the free throw line in the Clutch vs. all other times")
