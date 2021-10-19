import random

class QuestionMaker:

    WELCOME_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                ":Socks: IT'S SOCK TIME!!! :Socks:"
            )
        }
    }

    DONE_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                ":Socks: Question Complete!!! :Socks:"
            )
        }
    }

    DIVIDER_BLOCK = {"type": "divider"}

    CATEGORIES = [
    "Ask a Question :Question: Reply with a question for your team", 
    "Videos :Clapper: Reply with a link to a video/song you enjoy", 
    "This or That! Reply with two topics represented by emojis and let the team vote",
    ]

    def __init__(self, channel, players):
        self.channel = channel
        self.players = players
        self.user_id = random.choice(self.players)
        self.username = "TinyTalk"
        self.icon_emoji = ":robot_face:"
        self.timestamp = ""
        self.completed = False
        self.scheduled = False

    def get_message_payload(self):
        if self.completed:
            return {
                "ts": self.timestamp,
                "channel": self.channel,
                "username": self.username,
                "icon_emoji": self.icon_emoji,
                "blocks": [
                    self.DONE_BLOCK,
                ],
            }
        else:
            return {
                "ts": self.timestamp,
                "channel": self.channel,
                "username": self.username,
                "icon_emoji": self.icon_emoji,
                "blocks": [
                    self.WELCOME_BLOCK,
                    self.DIVIDER_BLOCK,
                    *self._get_user_block(),
                    *self._get_info_block(),
                ],
            }

    def get_schedule_message(self, time):
        return {
            "channel": self.channel,
            "username": self.username,
            "post_at": time,
            "text": "ok",
            "blocks": [
                self.WELCOME_BLOCK,
                self.DIVIDER_BLOCK,
                *self._get_user_block(),
                *self._get_info_block(),
            ],
        }

    def reroll_player(self):
        #remove current player as they have opted out
        self.players.remove(self.user_id)
        
        if not self.players:
            self.completed = True
            return
        # reroll selected player
        self.user_id = random.choice(self.players)

    def is_completed(self):
        return self.completed

    def _get_user_block(self):
        text = (
            f"<@{self.user_id}> You have been chosen to win today's :Socks:"
        )
        return self._get_task_block(text)

    def _get_info_block(self):
        text = (
            f"The category is {random.choice(self.CATEGORIES)} or react with :x: to opt out"
        )
        return self._get_task_block(text)

    @staticmethod
    def _get_task_block(text):
        return [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
        ]

