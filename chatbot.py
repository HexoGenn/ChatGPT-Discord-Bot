import os
import discord
import time
import asyncio
import random
from chatrequest import get_response
import re

MESSAGE_LIMIT = 40
TIME_LIMIT = 2 * 60 * 60
DEPTH_LIMIT = 6
CHAR_LIMIT = 150
bot_reply_speed = 10

admin_user_ids = [
    '577114211671343114', '1017808758124052621', '1159810149268078702', '960935093562658927', '462121395002802186'
]

allowed_channels = [
    '838844411726135346', '1182787402557829241', '1182787391069630596',
    '1182787378407014400', '1182787364075098243', '1182111957415890954',
    '879067848683687946', '1182746485041930240', '1182746502242775130',
    '1182770239998537848', '1182770546073669682', '1182770916070015026',
    '1200128721600909352','1144248857451053056','1200846983125016636',
    '1191551797391802448'
]


def read_last_message_time(user_id):
  try:
    with open(f"cooldowns/{user_id}_last_message_time.txt", "r") as file:
      data = file.read().split(',')
      return [float(data[0]),float(data[1])]
  except FileNotFoundError:
    return [0, 0]


def write_last_message_time(user_id, last_time, count):
  with open(f"cooldowns/{user_id}_last_message_time.txt", "w") as file:
    file.write(f"{last_time},{count}")


async def temp_message(message, content, reaction):
  if reaction != None:
    await message.add_reaction(reaction)
  error_message = await message.channel.send(content)
  await asyncio.sleep(5)
  await error_message.delete()


# New cache for message references
message_reference_cache = {}

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True


async def run_character(token,custom_instructions,gpt_info,credit_cost,main_bot,good_message_channel_id,reaction_pool):

  client = discord.Client(intents=intents)

  async def get_message_chain(message, depth, is_dm):

    messages = []

    is_dm = False #always use reply chain cuz it's better

    if not is_dm:
      #if not a DM, get the reply chain
      max_depth = depth

      current_message = message
      while current_message and depth > 0:
        if current_message.author != client.user:
          message_info = f"{current_message.content}"
        else:
          message_info = current_message.content

        words = message_info.split()
        filtered_words = []

        discord_ping_pattern = r"<@!?\d+>"  # Regex pattern to match Discord pings

        filtered_words = [word for word in words if not re.match(discord_ping_pattern, word)]
              
        message_info = " ".join(filtered_words)
        message_info = message_info.replace("\n", r"\n")
        
        messages.append({
            "role":
            "user" if current_message.author != client.user else "assistant",
            "content": message_info,
        })

        if current_message.reference:
          ref_message_id = current_message.reference.message_id
          cur_message_id = current_message.id
          if str(cur_message_id) in message_reference_cache:
            current_message = message_reference_cache[str(cur_message_id)]
          else:
            current_message = await current_message.channel.fetch_message(
                ref_message_id)
            message_reference_cache[str(cur_message_id)] = current_message
        else:
          current_message = None

        depth -= 1

      return messages[::-1], str(max_depth - depth)
    elif is_dm:
      #if the bot is in a dm, get the message history
      past_messages = [
          message async for message in message.channel.history(limit=depth)
      ]
      for past_message in past_messages:
        if past_message.author != client.user:
          message_info = f"{past_message.content}"  # has support for adder users name and stuff but it causes ai hallucinations
        else:
          message_info = past_message.content
        messages.append({
            "role":
            "user" if past_message.author != client.user else "assistant",
            "content":
            message_info
        })
      return messages, str(len(past_messages))

  @client.event
  async def on_ready():
    print(f'We have logged in as {client.user}',end="\n\n")
    await client.change_presence(activity=discord.Game(
        name="https://discord.gg/DbrqH8cRwb"))

  @client.event
  async def on_raw_reaction_add(payload):
      # Get the channel and message where the reaction was added
      channel = client.get_channel(payload.channel_id)
      message = await channel.fetch_message(payload.message_id)
      user = await client.fetch_user(payload.user_id)

      # Define the reaction type
      type = "👍 GOOD" if str(payload.emoji) == "👍" else (None if str(payload.emoji) == "👎" else None)

      # Check if the reaction is to a bot's message and is a thumbs up or thumbs down
      if message.author.id == client.user.id and not user.bot and type and user.id == 960935093562658927:
          channel = client.get_channel(good_message_channel_id)
          if channel:
              messages, _ = await get_message_chain(message, 15, isinstance(channel, discord.DMChannel))
              await channel.send(f"{type}\n```json\n{str(messages)}```")
             
              with open(f"good_examples/{good_message_channel_id}.jsonl", "a") as file:
                file.write(str(messages) + "\n")
  
  @client.event
  async def on_message(message):

    if message.author == client.user:
      return

    USER_MSG_LIMIT = MESSAGE_LIMIT
    USER_DEPTH_LIMIT = DEPTH_LIMIT

    DM = isinstance(message.channel, discord.DMChannel)

    bot = message.author.bot

    if bot and message.channel.id != 1191551797391802448:
      return

    premium = False
    admin = str(message.author.id) in admin_user_ids

    if not DM:
      premium = (admin) or (bot) or (1182782686058790932 in [
          role.id for role in message.author.roles
      ]) or (1181417001915273297 in [role.id for role in message.author.roles])

    if premium:
      USER_MSG_LIMIT *= 4
      if bot:
        USER_DEPTH_LIMIT = 8
      else:
        USER_DEPTH_LIMIT = 20

    if main_bot:
      if message.content.startswith('!count'):
        count = read_last_message_time(message.author.id)[1]
        await temp_message(
            message, f"you have used {count}/{USER_MSG_LIMIT} of your credits\nit costs 1 credit for a short response",
            "✔️")
        return
      elif message.content.startswith('!print'):
        print(message.content,end="\n\n")
        return

      elif message.content.startswith('!arguespeed'):
        arguespeed = float(message.content.split(' ')[1])
        await temp_message(
        message, f"set bot reply speed to {bot_reply_speed}",
        "✔️")
        
      elif message.content.startswith('!repeat'):

        if client.user.mentioned_in(message):
          return

        if not admin:
          await temp_message(message, "u cant use this idiot", "❌")
          return

        await message.channel.send(message.content[8:])

      elif message.content.startswith('!reset'):

        if not admin:
          await temp_message(message, "u cant use this idiot", "❌")
          return

        user_id_to_remove_limit = message.content.split(' ')[1]
        try:
          user_id_to_remove_limit = int(user_id_to_remove_limit)
          write_last_message_time(user_id_to_remove_limit, 0, 0)
          await temp_message(
              message,
              f"message limit removed for user with ID {user_id_to_remove_limit}",
              "✔️")
          return

        except:
          await temp_message(message, "invalid user id", "❌")
          return

    #if DM and not admin:
      #await temp_message(message,
                         #"go talk to nermis in the server cuz its dead fr",
                         #"❌")
      #return

    if client.user.mentioned_in(message):

      error_checks = {
          "rate_limit": {
              "check":
              lambda message: time.time() - read_last_message_time(
                  message.author.id)[0] < TIME_LIMIT and
              read_last_message_time(message.author.id)[1]+credit_cost > USER_MSG_LIMIT,
              "message":
              f"sry there's a limit of {USER_MSG_LIMIT} credits every {TIME_LIMIT/60/60:.0f} hours to protect rhys bank account\n**NOTE::** if you have the 'extra messages' role, it will work in the official server, not dms"
          },
          "length_limit": {
              "check": lambda message: len(message.content) > CHAR_LIMIT,
              "message": f"too long message bro max is {CHAR_LIMIT} characters"
          },
          "channel_limit": {
              "check":
              lambda message:
              (not DM) and str(message.channel.id) not in allowed_channels,
              "message":
              "i dont work here idiot\n*but if u want me to work here, ask rhysrhysrhysrhysrhys on discord*"
          },
      }

      if (str(message.author.id) not in admin_user_ids) and not (bot):
        for error_type, error_info in error_checks.items():
          if error_info["check"](message):
            print(error_info["message"],end="\n\n")
            await temp_message(message, error_info["message"], "❌")
            return

      processing_message = "None"

      async def statusMessage(msg):

        nonlocal processing_message

        if (not bot):
          if processing_message == "None":
            processing_message = await message.reply(msg)
          else:
            if msg == "[DELETE]":
              await processing_message.delete()
              processing_message = "None"
            else:
              await processing_message.edit(content=msg)

      msg_time_info = read_last_message_time(message.author.id)
      last_message_time, message_count = msg_time_info[0], msg_time_info[1]
      limit_message = None

      if time.time() - last_message_time > TIME_LIMIT:
        limit_message = await message.reply(f"oh err btw\nthe limit for you is {USER_MSG_LIMIT} credits every {TIME_LIMIT/60/60:.0f} hours\n\nu can type !count to check what u got left lol\n\n**react with a thumbs up to creative and good responses so that the bots will get better**")
        message_count = 0
        last_message_time = time.time()

      write_last_message_time(message.author.id, last_message_time,
                              message_count + credit_cost)

      try:

        await statusMessage(
            "reading replies... (this may take a while for long reply-chains)")

        messages, replyamt = await get_message_chain(message, USER_DEPTH_LIMIT,
                                                     DM)
        messages.insert(0, {"role": "system", "content": custom_instructions})

        await statusMessage("generating message...")

        response = ""
        tries = 0

        debug_info = {}

        gpt_info["messages"] = messages

        debug_info["reply_amt"] = replyamt

        #slow down automatic chats
        if bot:
          await asyncio.sleep(bot_reply_speed)

        while (response == "") and tries < 3:
          response = get_response(gpt_info,debug_info)
          tries += 1
          await statusMessage(f"attempt #{tries}...")
        if response == "":
          response = "the generator responded with an empty message"
      except Exception as e:
        print("⚠ error: " + str(e),end="\n\n")
        response = "the generator had an error try again sry"

      await statusMessage("[DELETE]")

      #replace instances of ":trollface:" in the message with "<:trollface:1183171666264735754>"
      response = response.replace(":trollface:",
                                  "<:trollface:1183241939869515776>")
      response = response.replace(":trolled:",
                                  "<:trolled:1210061016151629875>")
      response = response.replace(":approvalcat:",
                                  "<:approvalcat:1183172114208010260>")

      #stop people using the bot to ping other bots or everyone
      message.content = message.content.replace("@", "")

      if limit_message:
        await limit_message.delete()

      if (not DM):
        response = await message.reply(content=response)
      else:
        response = await message.channel.send(content=response)

      #await response.add_reaction("👍")
      #await response.add_reaction("👎")

      async def remove_bot_reactions_after_delay(message, delay):
          await asyncio.sleep(delay)
          try:
              # Check if the bot's user has reacted with the specified emoji and remove it
              bot_user = message.guild.me
              await message.remove_reaction("👍", bot_user)
              await message.remove_reaction("👎", bot_user)
          except:
              pass  # Reaction was already removed

      asyncio.create_task(remove_bot_reactions_after_delay(response, 10))

      if (random.randint(1, 3) == 1) and (len(reaction_pool) > 0):
        await message.add_reaction(
            random.choice(reaction_pool))
    elif DM:
      await temp_message(message,
       "ping the bot or reply to him lol",
       "❌")
  
  await client.start(token)
