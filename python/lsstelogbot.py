import os
import time
import yaml
from slackclient import SlackClient
from ECLAPI import ECLConnection, ECLEntry
import sys

# bot's ID as an environment variable
#BOT_ID = os.environ.get("BOT_ID")

# constants
#AT_BOT = "<@" + BOT_ID + ">"
GET_COMMAND = "/get"
CATEGORY_COMMAND = "/cat"
TAG_COMMAND = "/tag"
CATLIST_COMMAND = "/listcat"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def find_username(slack_client, id):
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find author of this post 
        users = api_call.get('members')
        for user in users:
            if 'id' in user and user.get('id') == id:
                return user['name']
    return None

def extract_command_param(text, command):
    try:
        splitLowerText = text.lower().split()
        splitText = text.split()
        param = splitText[splitLowerText.index(command) + 1]
    except Exception:
        return None, text
    else:
        return param, text.replace(command + " " + param, "").strip()
    


def handle_command(slack_client, command, channel, user, conn):
    """
        Receives messages directed at the bot and determines if they
        are valid. Either an entry is retrieved from the eLog or
        a new entry is posted.
    """
    try:
        if command.lower().startswith(GET_COMMAND):
            entry = int(command.split(GET_COMMAND)[1].strip())
            response = conn.get(entry)
        elif command.lower().startswith(CATLIST_COMMAND):
            response = conn.category_list()
        else: # Assume this is a post
            category, post = extract_command_param(command, CATEGORY_COMMAND)
            if category is None:
                err = "Posting to eLog requires a category indicated by " \
                      + "/cat [categoryName]"
                slack_client.api_call("chat.postMessage", channel=channel,
                          text=err, as_user=True)
                return        

            # Find the user name
            author = find_username(slack_client, user)

            # Extract the category
            #category, post = extract_command_param(command, CATEGORY_COMMAND)
            #splitCommand = command.split()
            #category = splitCommand[splitCommand.index(CATEGORY_COMMAND) + 1]
            #post = command.replace(CATEGORY_COMMAND + " " + category, " ").strip()

            tags = []
            tag, post = extract_command_param(post, TAG_COMMAND)
            if tag is not None:
                tags.append(tag)

            e = ECLEntry(category=category,
                     tags = tags,
                     formname='Slack entry',
                     text=post,
                     preformatted=False)

            if author is not None:
                e.setValue(name="Author", value=author)

            response = conn.post(e)
 
        slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
    except Exception:
        return


def parse_slack_output(slack_rtm_output, AT_BOT):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip(), \
                       output['channel'], output['user']
    return None, None, None


if __name__ == "__main__":

    config = yaml.load(open('elog.conf', 'r'))
    SLACK_BOT_TOKEN = config.get('SLACK_BOT_TOKEN')
    xmluser = config.get('XML_USER')
    xmlpassword = config.get('XML_PASSWORD')
    elogUrl = config.get('ELOG_URL')
    elogUrl1 = config.get('ELOG_URL1')
    elogUrl2 = config.get('ELOG_URL2')
    BOT_ID = config.get('BOT_ID')
    AT_BOT = "<@" + BOT_ID + ">"

    slack_client = SlackClient(SLACK_BOT_TOKEN)

    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    conn = ECLConnection(elogUrl1, xmluser, xmlpassword) # elog connection

    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel, user = parse_slack_output(slack_client.rtm_read(), AT_BOT)
            if command and channel and conn:
                handle_command(slack_client, command, channel, user, conn)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
