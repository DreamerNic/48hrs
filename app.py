import logging
import copy
import json
import random
import time
from slack_bolt import App
from slack_sdk.web import WebClient
from question_former import QuestionMaker
from game_master import GameMaster

app = App(ignoring_self_events_enabled=False)
bot_id = ""
game_master = GameMaster([])
question_ids_by_channel = {} #key: channel_id, value: dict of question_prompts by their timestamp
current_question_id = 0

def create_and_send_question(channel: str, client: WebClient):
    players = update_player_list(channel, client)

    todays_question = QuestionMaker(channel,players)

    message = todays_question.get_message_payload()
    response = client.chat_postMessage(**message)

    todays_question.timestamp = response["ts"]

    if channel not in question_ids_by_channel:
        question_ids_by_channel[channel] = {}

    question_id = todays_question.timestamp #only unique identifier the api returns
    question_ids_by_channel[channel][question_id] = todays_question

    global current_question_id
    current_question_id = question_id

    queue_next_question(channel, client)

#when we schedule future messages they do not have a ts (basically message ID yet.
#This function will take that message and add it to our question ID's by channel dict.
def link_message(ts: str, channel_id: str, client: WebClient):
    global question_ids_by_channel

    current_question_id = ts

    if channel_id not in question_ids_by_channel:
        question_ids_by_channel[channel_id] = {}

    question_ids_by_channel[channel_id][ts] = copy.deepcopy(question_ids_by_channel[channel_id][0])
    question_ids_by_channel[channel_id][ts].timestamp = ts

    queue_next_question(channel_id, client)
    print("linking message")
    return


def queue_next_question(channel_id: str, client: WebClient):
    global next_question
    players = update_player_list(channel_id, client)

    schedule_time = int(time.time()) + 60

    question_ids_by_channel[channel_id][0] = QuestionMaker(channel_id, players)

    message = question_ids_by_channel[channel_id][0].get_schedule_message(schedule_time)
    response = client.chat_scheduleMessage(**message)

def send_player_score_message(player: str, channel: str, client: WebClient):
    message = game_master.get_player_score_message(player, channel)
    client.chat_postEphemeral(**message)

def send_leaderboard_message(channel: str, client: WebClient):
    message = game_master.get_leaderboard_message(channel)
    client.chat_postMessage(**message)


@app.event("reaction_added")
def handle_x_emoji_reaction(event, client):
    user_id = event.get("user")
    reaction = event.get("reaction")
    channel_id = event.get("item", {}).get("channel")
    question_id = event.get("item", {}).get("ts")

    if channel_id not in question_ids_by_channel or question_id not in question_ids_by_channel[channel_id]:
        return

    if reaction != "heavy_multiplication_x":
        game_master.increase_score(user_id, 1)
        return

    question = question_ids_by_channel[channel_id][question_id]
    if (question.user_id == user_id):
        question.reroll_player()

        # Get the new message payload
        message = question.get_message_payload()

        # Post the updated message in Slack
        updated_message = client.chat_update(**message)

        if (question.completed):
            current_question_id = None


# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@app.event("message")
def message(event, client):
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")
    ts = event.get("ts")
    global bot_id
    global question_ids_by_channel
    if text and text.lower() == "tinytalk":
        create_and_send_question(channel_id, client)

    if text and text.lower() == "score":
        send_player_score_message(user_id, channel_id, client)

    if text and text.lower() == "leader":
        send_leaderboard_message(channel_id, client)

    print(f"user is {user_id} bot id is{bot_id}")

    if(user_id == bot_id and ts not in question_ids_by_channel[channel_id]):
        print(ts)
        link_message(ts, channel_id, client)

    game_master.increase_score(user_id, 1)

def update_player_list(channel_id: str, client: WebClient):
    global game_master
    global bot_id
    players = []
    for page in client.conversations_members(channel=channel_id):
        players = players + page['members']

    bot_id = get_bot_id(client)
    if bot_id in players: players.remove(bot_id)

    if game_master is None:
        game_master = GameMaster(players)
    else:
        game_master.update_players(players)
    return players

def get_bot_id(client):
    test_response = client.auth_test()
    return test_response['user_id']

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.start(3000)
