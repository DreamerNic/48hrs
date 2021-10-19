import logging
import json
import random
from slack_bolt import App
from slack_sdk.web import WebClient
from question_former import QuestionMaker

app = App()

question_prompts = {}

def start_question(user_id: str, channel: str, client: WebClient):
    today_question = QuestionMaker(channel,user_id)

    message = today_question.get_message_payload()

    response = client.chat_postMessage(**message)


    today_question.timestamp = response["ts"]

    if channel not in question_prompts:
        question_prompts[channel] = {}
    question_prompts[channel][user_id] = today_question



@app.event("reaction_added")
def update_emoji(event, client):
    channel_id = event.get("item", {}).get("channel")
    user_id = event.get("user")
    reaction = event.get("reaction")
    print(reaction)
    if channel_id not in question_prompts or reaction != "x":
        return

    # Get the original tutorial sent.
    question = question_prompts[channel_id][user_id]

    channel_members = []
    for page in client.conversations_members(channel=channel_id):
        channel_members = channel_members + page['members']

    question.user_id = random.choice(channel_members)

    # Get the new message payload
    message = question.get_message_payload()

    # Post the updated message in Slack
    updated_message = client.chat_update(**message)

# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@app.event("message")
def message(event, client):
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    if text and text.lower() == "socks":
        channel_members = []
        for page in client.conversations_members(channel=channel_id):
            channel_members = channel_members + page['members']
        print(channel_members)
        channel_members.remove(get_bot_id(client))
        print(channel_members)
        user_id = random.choice(channel_members)
        start_question(user_id, channel_id, client)
    if text and text.lower() == "zzsetup":
        set_bot_id(client)

def get_bot_id(client):
    test_response = client.auth_test()
    return test_response['user_id'] 

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.start(3000)
