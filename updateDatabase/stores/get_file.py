import json
import os
module_dir = os.path.dirname(__file__)

def get_games_as_csv():
    gamesmen_file_path = os.path.join(module_dir, 'gamesmen_links.json')
    with open(gamesmen_file_path) as file:
        games = json.loads(file.read())
    write_game_titles_to_csv(games)

def write_game_titles_to_csv(games):
    titles = ",".join([game['title'] for game in games])
    outfile = os.path.join(module_dir, 'gamesmen_title_list.csv')
    with open(outfile, "w") as file:
        file.write(titles)
