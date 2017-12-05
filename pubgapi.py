import json
import time
import requests
from timeit import default_timer as timer

class PUBGAPI:
    """Object that returns the API"""
    def __init__(self, api_key, pubg_season):
        self.pubg_season = pubg_season
        self.api_key = api_key
        self.platform = 'pc'
        self.api_link = "https://api.pubgtracker.com/v2/profile/pc/"
        self.api_steam = "https://api.pubgtracker.com/v2/search/steam?steamId="
        self.headers = {
            'content-type': "application/json",
            'trn-api-key': api_key,
        }


class PLAYER:

    def __init__(self, PUBGAPI, player_name, player_region, player_mode, player_first_person):
        self.error = ""
        self.api = PUBGAPI
        self.mode = self.get_mode(player_mode, player_first_person)
        if self.mode == "error":
            self.error = "mode"
            return
        self.verified_region = self.verify_region(player_region)
        if self.verified_region == 'error':
            self.error = 'region'
            return
        self.data = self.get_profile_json(player_name,player_region,self.mode,)
        if self.data == "error":
            self.error = "api"
            return

        self.rating = self.get_player_rating(self.verified_region)
        self.total_kills = self.get_player_total_kills(self.verified_region)
        self.kdr = self.get_player_kdr(self.verified_region)
        self.kills_per_game = self.get_kills_per_game(self.verified_region)
        self.wins_this_season = self.get_wins_this_season(self.verified_region)
        self.rounds_played = self.get_rounds_played(self.verified_region)
        self.most_kills = self.get_most_kills(self.verified_region)
        self.longest_kill = self.get_longest_kill(self.verified_region)
        self.average_damage_per_game = self.get_avg_damage_per_game(self.verified_region)

        if self.rating is 'None':
            self.data = 'error'
            self.error = 'unknown error'
            return

    def get_profile_json(self, player_name, player_region, mode):
        url = self.api.api_link + player_name + '?region=' + player_region + '&mode=' + mode + "&season=" + self.api.pubg_season
        response = requests.request("GET", url, headers=self.api.headers)

        if "Error updating" in response.text:
            print("error in pubg api")
            return "error"
        data = json.loads(response.text)
        return data

    def get_player_total_kills(self,player_region):
        return self.filter_stat('Kills', self.data, player_region)

    def get_player_rating(self,player_region):
        return self.filter_stat('Rating', self.data, player_region)

    def get_player_kdr(self,player_region):
        return self.filter_stat('K/D Ratio', self.data, player_region)

    def get_kills_per_game(self,player_region):
        return self.filter_stat('Kills Pg', self.data, player_region)

    def get_wins_this_season(self,player_region):
        return self.filter_stat('Wins', self.data, player_region)

    def get_rounds_played(self,player_region):
        return self.filter_stat('Rounds Played', self.data, player_region)

    def get_most_kills(self,player_region):
        return self.filter_stat('Round Most Kills', self.data, player_region)

    def get_longest_kill(self,player_region):
        return self.filter_stat('Longest Kill', self.data, player_region)

    def get_avg_damage_per_game(self, player_region):
        return self.filter_stat('Avg Dmg per match', self.data, player_region)

    def filter_stat(self, stat, response, region):
        for stat_current in response['stats']:
            if stat_current['region'] == region and stat_current['season'] == self.api.pubg_season:
                for datas in stat_current['stats']:
                    if datas['label'] == stat:
                        return datas['value']

    @staticmethod
    def verify_region(region):
        if region == 'na':
            return 'na'
        elif region == 'eu':
            return 'eu'
        elif region == 'sa':
            return 'sa'
        elif region == 'as':
            return 'as'
        elif region == 'krjp':
            return 'krjp'
        elif region == 'sea':
            return 'sea'
        elif region == 'oc':
            return 'oc'
        elif region == 'agg':
            return 'agg'
        else:
            return 'error'

    @staticmethod
    def get_mode(player_mode, player_first_person):
        if player_mode == 'solo' and player_first_person == 'tpp':
            return 'solo'
        elif player_mode == 'solo' and player_first_person == 'fpp':
            return 'solo-fpp'
        elif player_mode == 'duo' and player_first_person == 'tpp':
            return 'duo'
        elif player_mode == 'duo' and player_first_person == 'fpp':
            return 'duo-fpp'
        elif player_mode == 'squad' and player_first_person == 'tpp':
            return 'squad'
        elif player_mode == 'squad' and player_first_person == 'fpp':
            return 'squad-fpp'
        else:
            return "error"
