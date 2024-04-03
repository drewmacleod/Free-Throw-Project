import re
# make time into time_seconds column and make integers
def time_into_seconds(time):
    time_list = time.split(':')
    seconds = (int(time_list[0]) * 60) + int(time_list[1])
    return seconds

# Gets score difference from game
def score_difference(score):
    score_list = score.split('-')
    score_list[0] = score_list[0].strip()
    score_list[1] = score_list[1].strip()
    return abs(int(score_list[0]) - int(score_list[1]))

def fix_player_syntax(player):
    player = re.sub(r'[^\w\s]+','', player)
    player = player.lower()
    return player

def get_free_throw_stats(player):
	player.shot_made = player.shot_made - 211
	return player