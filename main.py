import discord
from discord.ext import commands
import config
import re
import asyncio
import random
import requests
from utility import Utils
import time
import sys
import codecs

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)

bot = commands.Bot(command_prefix="!", self_bot=True)
sleeping = config.sleep

global count
count = 2

global spamming_active
spamming_active = True

global removing
removing = True


def click_button(guild_id, channel_id, message_id, button_custom_id, user_id, session_id, application_id):
    url = f"https://discord.com/api/v10/interactions"
    headers = {
        "Authorization": f"Bot YOUR_BOT_TOKEN",
        "Content-Type": "application/json"
    }
    payload = {
        "type": 2,  # Type 2 corresponds to a button interaction
        "token": "YOUR_INTERACTION_TOKEN",  # This is obtained from the original message containing the button
        "member": {
            "user": {
                "id": user_id  # User ID of the bot or the user simulating the click
            },
            "session_id": session_id,
            "deaf": False,
            "mute": False,
        },
        "guild_id": str(guild_id),
        "channel_id": str(channel_id),
        "message_id": str(message_id),
        "data": {
            "component_type": 2,  # Type 2 represents buttons
            "custom_id": button_custom_id,  # The unique ID for the button
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


async def market_search(id,gender):
    global removing
    channel = bot.get_channel(config.ChannelId)
    if channel:
        removing = True
        if gender.lower() == 'male':
            await asyncio.sleep(random.randint(5, 10))
            await channel.send(f'<@716390085896962058> m s --n {id} --gender female --order price')
        else:
            await asyncio.sleep(random.randint(5, 10))
            await channel.send(f'<@716390085896962058> m s --n {id} --gender male --order price')



async def market_buy(listing_id):
    channel = bot.get_channel(config.ChannelId)
    if channel:
        await asyncio.sleep(random.randint(5, 10))
        await channel.send(f'<@716390085896962058> m b {listing_id}')


async def spam():
    global spamming_active
    while not sleeping:
        if spamming_active:
            channel = bot.get_channel(config.ChannelId)
            if channel:
                message_options = ["<@716390085896962058> breeding", "<@716390085896962058> breed", "<@716390085896962058> daycare"]
                await channel.send(random.choice(message_options))
            else:
                print("Channel not found. Please check the channel ID in the config.")
                break
        await asyncio.sleep(random.uniform(500, 600))
        # Reset spam if it was stopped
        if not spamming_active:
            await asyncio.sleep(random.uniform(1800, 2000))  # Wait before reactivating
            spamming_active = True

    

@bot.event
async def on_ready():
    print(f'\033[91mLOGGED IN AS {bot.user.name} ({bot.user.id})\033[0m')
    print(f'\033[91mSERVER STATUS: ONLINE\033[0m')
    print(f'\033[91mMade by Aman\033[0m')
    print(f'\033[91m------------------------------------------------------------------------------------------\033[0m')
    await spam()

@bot.event
async def on_message(msg: discord.Message):
    global count, spamming_active, removing
    channel = bot.get_channel(config.ChannelId)
    message = msg.content

    if msg.author.id == 716390085896962058 and msg.guild.id == config.GuildId:
        print(msg.content)

        for embed in msg.embeds:
            print(embed.title)
            if embed.description is not None:
                print(embed.description.encode('utf-8', 'ignore').decode('utf-8'))
            else:
                print("No description found in embed.")

            if 'Daycare' in embed.title:
                for field in embed.fields:
                    print(field)
                    if "Empty" in field.value:
                        removing = False
                        await asyncio.sleep(random.randint(5, 10))
                        await channel.send(f'<@716390085896962058> daycare add l')
                        await asyncio.sleep(random.randint(5, 10))
                        break
                    elif ("High compatibility" not in field.value) and ('@Pokétwo daycare eggs' not in field.value):
                        spamming_active = False
                        field_value = str(field.value)
                        match = re.search(r'`([^`]+)`', field_value)
                        if match:
                            extracted_value = match.group(1) 
                            await asyncio.sleep(random.randint(5, 10))
                            await channel.send(f'<@716390085896962058> daycare remove {extracted_value}')
                        else:
                            print("No match found")
                        
            if embed.description and "Pokétwo Marketplace" in embed.title:
                marketpattern = r"^`(\d+)`.*?•\s*[\d\.]+%\s*•\s*([\d,]+)\s*pc"
                matches = re.findall(marketpattern, embed.description, flags=re.MULTILINE)
                for listing_id, price in matches:
                    price_int = int(price.replace(",", ""))
                    if price_int < 500:
                        await market_buy(listing_id)
                        break  # Stop after the first valid match
                    else:
                        spamming_active = True

        if "No listings found" in message:
            spamming_active = True
            
        if "to the daycare for a deposit cost of" in message:
            await asyncio.sleep(random.randint(2, 5))
            pattern = r"<:_:\d+> Level \d+ ([\w\.'’\-]+(?:\s[\w\.'’\-]+)*)<:([a-z]+):"
            match = re.search(pattern, message)
            print(match)
            if match:
                name, gender = match.groups()
            
            if gender == 'male'or gender == 'female':
                spamming_active = False
                try:
                    # Find the 'Yes' button by label
                    target_button = None
                    for component in msg.components:
                        for button in component.children:
                            if button.label == 'Yes':
                                target_button = button
                                break
                        if target_button:
                            break

                    if target_button:
                        Utils.click_button(
                            token=config.token,
                            message_id=msg.id,
                            custom_id=target_button.custom_id,
                            channel_id=str(msg.channel.id),
                            guild_id=str(msg.guild.id),
                            application_id=str(msg.author.id),
                            session_id=Utils.generate_session_id(),
                            component_type=2  # 2 = Button component type
                        )
                except Exception as e:
                    print(f"Error clicking button: {e}")
                
                if count%2 == 0:
                    await market_search(name,gender)
                    count += 1
                else:
                    print("Spamming resumed")
                    spamming_active = True
                    count += 1
            else:
                pass

        if "from the daycare? All the progress will be lost" in message:
            await asyncio.sleep(random.randint(2, 5))
            try:
                # Find the 'Confirm' button by label
                target_button = None
                for component in msg.components:
                    for button in component.children:
                        if button.label == 'Confirm':
                            target_button = button
                            break
                    if target_button:
                        break

                if target_button:
                    Utils.click_button(
                        token=config.token,
                        message_id=msg.id,
                        custom_id=target_button.custom_id,
                        channel_id=str(msg.channel.id),
                        guild_id=str(msg.guild.id),
                        application_id=str(msg.author.id),
                        session_id=Utils.generate_session_id(),
                        component_type=2  # 2 = Button component type
                    )
            except Exception as e:
                print(f"Error clicking button: {e}")
            await channel.send(f'<@716390085896962058> daycare')
            spamming_active = True

        if "Are you sure you want to buy this" in message:
            await asyncio.sleep(random.randint(1, 2))
            try:
            # Find the 'Confirm' button by label
                target_button = None
                for component in msg.components:
                    for button in component.children:
                        if button.label == 'Confirm':
                            target_button = button
                            break
                    if target_button:
                        break

                if target_button:
                    Utils.click_button(
                        token=config.token,
                        message_id=msg.id,
                        custom_id=target_button.custom_id,
                        channel_id=str(msg.channel.id),
                        guild_id=str(msg.guild.id),
                        application_id=str(msg.author.id),
                        session_id=Utils.generate_session_id(),
                        component_type=2  # 2 = Button component type
                    )
            except Exception as e:
                print(f"Error clicking button: {e}")

            await asyncio.sleep(10)
            await channel.send(f'<@716390085896962058> daycare add l')




bot.run(config.token)
