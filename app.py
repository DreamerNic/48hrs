import logging
import json
import random
from slack_bolt import App
from slack_sdk.web import WebClient
from question_former import QuestionMaker

app = App()
question_ids_by_channel = {} #key: channel_id, value: dict of question_prompts by their timestamp


def create_and_send_question(user_id: str, channel: str, client: WebClient):
    todays_question = QuestionMaker(channel,user_id)

    message = todays_question.get_message_payload()
    response = client.chat_postMessage(**message)

    todays_question.timestamp = response["ts"]

    if channel not in question_ids_by_channel:
        question_ids_by_channel[channel] = {}

    question_id = todays_question.timestamp #only unique identifier the api returns
    question_ids_by_channel[channel][question_id] = todays_question


@app.event("reaction_added")
def handle_x_emoji_reaction(event, client):
    user_id = event.get("user")
    reaction = event.get("reaction")
    channel_id = event.get("item", {}).get("channel")
    question_id = event.get("item", {}).get("ts")

    if channel_id not in question_ids_by_channel or question_id not in question_ids_by_channel[channel_id]:
        return

    if reaction != "x":
        return

    # Get the original tutorial sent.
    question = question_ids_by_channel[channel_id][question_id]

    players = []
    for page in client.conversations_members(channel=channel_id):
        players.append(page['members'])

    # remove bot and player that opted out
    players.remove(get_bot_id(client))
    players.remove(user_id)

    # reroll selected player
    question.user_id = random.choice(players)

    # Get the new message payload
    message = question.get_message_payload()

    # Post the updated message in Slack
    updated_message = client.chat_update(**message)


def get_bot_id(client):
    test_response = client.auth_test()
    return test_response['user_id']

# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@app.event("message")
def message(event, client):
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    if text and text.lower() == "socks":
        players = []
        for page in client.conversations_members(channel=channel_id):
            players= players + page['members']
        
        bot_id = get_bot_id(client)
        if bot_id in players: players.remove(get_bot_id(client))
        
        todays_player = random.choice(players)
        create_and_send_question(todays_player, channel_id, client)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.start(3000)
