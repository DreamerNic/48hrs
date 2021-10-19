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

    DIVIDER_BLOCK = {"type": "divider"}

    def __init__(self, channel, user_id):
        self.channel = channel
        self.user_id = user_id
        self.username = "TinyTalk"
        self.icon_emoji = ":robot_face"
        self.timestamp = ""
        self.reaction_task_completed = False
        self.pin_task_completed = False

    def get_message_payload(self):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [
                self.WELCOME_BLOCK,
                self.DIVIDER_BLOCK,
                *self._get_user_block(),
            ],
        }

    def _get_user_block(self):
        text = (
            f"<@{self.user_id}> YOU HAVE BEEN SELECTED"
        )
        return self._get_task_block(text)

    @staticmethod
    def _get_task_block(text):
        return [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
        ]

