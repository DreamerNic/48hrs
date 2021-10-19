class GameMaster:

    SCORE_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                ":Socks: Check!"
            )
        }
    }
    LEADER_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                ":Socks: Current Leaders! :Socks:"
            )
        }
    }

    DIVIDER_BLOCK = {"type": "divider"}

    player_scores = {}

    def __init__(self, player_list):
        self.username = "TinyTalk"
        for player in player_list:
            self.player_scores[player] = 0
    
    def increase_score(self, player, score):
        if  player in self.player_scores:
            self.player_scores[player] += score

    def get_player_score(self, player):
        if player in self.player_scores:
            return self.player_scores[player]

    def update_players(self, player_list):
        for player in player_list:
            if player not in self.player_scores:
                self.player_scores[player] = 0

    def get_player_score_message(self, player, channel):
        return {
            "channel": channel,
            "username": self.username,
            "icon_emoji": ":Socks:",
            "user": player,
            "blocks": [
                self.SCORE_BLOCK,
                self.DIVIDER_BLOCK,
                *self._get_score_block(player),
            ],
        }

    def get_leaderboard_message(self, channel):
        return {
            "channel": channel,
            "username": self.username,
            "icon_emoji": ":Socks:",
            "blocks": [
                self.LEADER_BLOCK,
                self.DIVIDER_BLOCK,
                *self._get_leader_block(),
            ],
        }

    def _get_leader_block(self):
        sort_leader = sorted(self.player_scores.items(), key = lambda x:x[1], reverse = True)
        text = (
            f"""First Place: <@{sort_leader[0][0]}> WITH {sort_leader[0][1]} :Socks:
            Second Place: <@{sort_leader[1][0]}> WITH {sort_leader[1][1]} :Socks:"""
        )
        return self._get_task_block(text)
    
    def _get_score_block(self, player):
        text = (
            f"<@{player}> YOU HAVE {self.player_scores[player]} :Socks:"
        )
        return self._get_task_block(text)

    @staticmethod
    def _get_task_block(text):
        return [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
        ]