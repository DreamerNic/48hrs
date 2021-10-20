import random

class QuestionMaker:

    DONE_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                ":Socks: The sock has returned to its drawer :Socks:"
            )
        }
    }

    DIVIDER_BLOCK = {"type": "divider"}

    CATEGORIES = [
    "a question :Question: Post a question for your team", 
    "a video :Clapper: Post a link to a video/song you enjoy", 
    "a choice :cat:/:dog: Post two emojis to represent topics to vote on",
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
                    #self.WELCOME_BLOCK,
                    *self._get_user_block(),
                    *self._get_info_block(),
                ],
            }

    def get_schedule_message(self, time):
        return {
            "channel": self.channel,
            "post_at": time,
            "text": "ok",
            "blocks": [
                #self.WELCOME_BLOCK,
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
            f":Socks: The sock drawer has opened and <@{self.user_id}> has been chosen :socks:"
        )
        return self._get_task_block(text)

    def _get_info_block(self):
        text = (
            f"This sock demands {random.choice(self.CATEGORIES)} \n\n react with :heavy_multiplication_x: to pass"
        )
        return self._get_task_block(text)

    @staticmethod
    def _get_task_block(text):
        return [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
        ]

