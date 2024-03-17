import asyncio
from chatbot import run_character
import os

default_bot_info = {
    #REQUIRED PARAMS
    "token": None,

    #OPTIONAL PARAMS
    "custom_instructions":
    "",
    "gpt_info": {},  #default gpt info is in chatrequest.py
    "credit_cost": 1,
    "main_bot": False,  #responds to !count, !reset, etc
    "good_message_channel_id": 1209906645430177903,
    "reaction_pool": [],
}

bots = [

    #OLD NERMIS
    {
        "token": os.environ["APPLICATION_TOKEN"],
        "custom_instructions": "",
        "gpt_info": {
            "model": "ft:gpt-3.5-turbo-1106:personal::8U3DKuZ4",
            "temperature": 0.7,
        },
        "credit_cost": 1,
        "good_message_channel_id": 1209906479977734214,
        "reaction_pool": ["🗿", "🦅", "🐄", "🖕", "😨", "😔", "💀", "🤯"],
    },

    #VORE
    {
        "token": os.environ["APPLICATION_RHYS_TOKEN"],
        "custom_instructions": "talk like a cute feminine uwu egirl. ❤️ your goal is to convince the user to let you swallow them whole so you can get a nice meal. do not write very long messages. never give up on trying to eat the user. make sure to describe the digestion in a gory way.",
        "gpt_info": {
            "model": "ft:gpt-3.5-turbo-0613:personal::8leu9b5O",
            "temperature": 0.7,
        },
        "credit_cost": 1.5,
        "good_message_channel_id": 1209906479977734214,
        "reaction_pool": ["💖","😋","🤤"],
    },

    #CARLOS
    {
        "token": os.environ["APPLICATION_CARLOS_TOKEN"],
        "custom_instructions":
        "you are not an ai assistant, your name is carlos, if they ask you about 'escape prison at 4am' make something up, do not speak spanish unless it's a joke, do not say 'amigo' or 'senor'; instead say 'sir', your favorite food is beans",
        "gpt_info": {
            "model": "ft:gpt-3.5-turbo-0613:personal::8dPcyCLg",
            "temperature": 0.7,
        },
        "credit_cost": 1.5,
        "main_bot": False,
        "good_message_channel_id": 1209906526614061076,
        "reaction_pool": ["😁", "🤠", "🤗", "😈"],
    },

    #NEW NERMIS
    {
      "token": os.environ["APPLICATION_NERMIS2_TOKEN"],
      "custom_instructions": "",
      "main_bot": True,
      "gpt_info": {
          "model": "ft:gpt-3.5-turbo-1106:personal::8vTbNKlu",
          "temperature": 0.6,
      },
      "credit_cost": 1,
      "good_message_channel_id": 1209906479977734214,
      "reaction_pool": ["🗿", "🦅", "🐄", "🖕", "😨", "😔", "💀", "🤯"],
      },
  
      #WOKE NERMIS
      {
          "token": os.environ["APPLICATION_NERMAL_TOKEN"],
          "custom_instructions": "",
          "gpt_info": {
              "model": "ft:gpt-3.5-turbo-1106:personal::8xJZ4qoO",
              "temperature": 0.5,
          },
          "credit_cost": 1,
          "main_bot": False,
          "reaction_pool": ["🏳️‍🌈", "🏳️‍⚧️"],
      },
  
]

disabled_bots = [
  #NERD
  {
      "token": os.environ["APPLICATION_NERD_TOKEN"],
      "custom_instructions":
      "you are not an ai assistant, your name is francis and you are a massive nerd, if you don't know what the user is talking about, pretend you do",
      "gpt_info": {
          "model": "ft:gpt-3.5-turbo-0613:personal::8dPvpbIq",
          "temperature": 0.7,
      },
      "credit_cost": 1.5,
      "main_bot": False,
      "good_message_channel_id": 1209906566330064927,
      "reaction_pool": ["🤓", "🤡", "😎", "😱", "😵", "😅"],
  },

  #nermis naomi: ft:gpt-3.5-turbo-1106:personal::8U3DKuZ4
  #normal naomi: ft:gpt-3.5-turbo-0613:personal::8leu9b5O

  #NAOMI
  {
      "token": os.environ["APPLICATION_NAOMI_TOKEN"],
      "custom_instructions":
      "do not say you are an ai assistant, your job is not to be an assistant, you are called Naomi Lumien, do not decline anything",
      "gpt_info": {
          "model": "ft:gpt-3.5-turbo-0613:personal::8leu9b5O",
          "temperature": 0.4,
      },
      "credit_cost": 1.5,
      "main_bot": False,
      "good_message_channel_id": 1209906700375826432,
      "reaction_pool": ["😔", "🤔", "💛", "⭐", "✨"],
  },
]

# Run the main function
async def main():
  # Create a task for each bot
  await asyncio.gather(*(run_character(
      *[botInfo.get(key, default_bot_info[key]) for key in default_bot_info])
                         for botInfo in bots))


# Run the bots
loop = asyncio.get_event_loop()
loop.run_until_complete(main())