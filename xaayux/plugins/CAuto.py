from .. import client, DELAY
from telethon import events, types, Button
from telethon.tl.types import PeerChannel, PeerChat, PeerUser 
import logging 
import time
import asyncio
import random
from xaayux.config import channel_ids, messages, DELAY

sent_messages = {}
last_sent_message_ids = {}
logging.basicConfig(level=logging.INFO)


@client.on(events.NewMessage(outgoing=True)) 
async def store_message_ids(event):
    channel_id = event.to_id
    message_id = event.message.id

    # Check the type of the entity
    if isinstance(channel_id, int): # If it's a user ID
        channel_id = channel_id 
    elif isinstance(channel_id, PeerChannel): # If it's a channel
        channel_id = channel_id.channel_id
    elif isinstance(channel_id, PeerChat): # If it's a chat
        channel_id = channel_id.chat_id
    elif isinstance(channel_id, PeerUser): # If it's a user, skip storing message
        return

    if channel_id not in sent_messages:
        sent_messages[channel_id] = []
    sent_messages[channel_id].append(message_id)

@client.on(events.NewMessage(outgoing=True, pattern='!clearall'))
async def clear_all_messages(event):
    for channel_id, message_ids in sent_messages.items():
        try:
            await client.delete_messages(channel_id, message_ids)
            time.sleep(1) 
        except Exception as e:
            print(f"Error deleting messages in channel {channel_id}: {e}")

    await event.respond('All messages deleted successfully.')
#°=======================
@client.on(events.NewMessage(outgoing=True, pattern='!setlink'))
async def handle_set_link(event):
    new_link = event.text.split(' ')[1] # Get the new link from the message
    global link # Access the global variable
    link = new_link
    await event.respond("Link updated successfully!")


@client.on(events.NewMessage(outgoing=True, pattern='!acstop'))
async def handle_cancel(event):
    await event.respond('📄 Stopped Auto Message Sending...\n⚙️Mode: Loop/Auto')
    global send_task
    send_task.cancel()

@client.on(events.NewMessage(outgoing=True, pattern='!acsend'))
async def handle_start(event):
    await event.respond("📄Started  Auto Message Sending...\n⚙️Mode: Loop/Auto")
    global send_task
    send_task = asyncio.create_task(send_messages())

# ===================================


@client.on(events.NewMessage(outgoing=True, pattern='!csend'))
async def handle_start(event):
    await event.respond("📄Started Message Sending...\n⚙️Mode: Single ")
    parts = link.split('/')
    username = parts[-2]
    message_id = int(parts[-1])

    entity = await client.get_entity(username)
    message = await client.get_messages(entity, ids=message_id)

    # Send messages to all channels and track previous message IDs
    for channel_id in channel_ids:
        try:
            # Get the previous message ID for this channel (if any)
            previous_message_id = last_sent_message_ids.get(channel_id)

            if message.media:
                sent_message = await client.send_file(channel_id, message.media, caption=message.text)
            else:
                sent_message = await client.send_message(channel_id, message.text, forward=False)

            # Delete the previous message if it exists
            if previous_message_id is not None:
                try:
                    await client.delete_messages(channel_id, [previous_message_id])
                    time.sleep(1) # Wait before updating the message ID
                except Exception as e:
                    print(f"Error deleting previous message in channel {channel_id}: {e}")

            # Update the message ID in the dictionary AFTER deleting the previous one
            last_sent_message_ids[channel_id] = sent_message.id 
            time.sleep(1) # Wait for a short delay before moving to the next channel
        except Exception as e:
            print(f"Error sending message to channel {channel_id}: {e}")
            
#---------------------------------------
async def forward_message(link):
    # Extract the channel username and message ID from the link
    parts = link.split('/')
    username = parts[-2]
    message_id = int(parts[-1])
    
    entity = await client.get_entity(username)
    
    message = await client.get_messages(entity, ids=message_id)
    
    if message.media:
        # Send the media message without any forwarding information to all channels
        for channel_id in channel_ids:
            await client.send_file(channel_id, message.media, caption=message.text)
    else:
        # Send the text-only message without any forwarding information to all channels
        for channel_id in channel_ids:
            await client.send_message(channel_id, message.text, forward=False)
            
async def send_messages():
    while True:
        await forward_message(link)
        
        await asyncio.sleep(DELAY)  # Send a message every 30 minutes 


#-------------------------

# -- Constants -- #
HELP = """
𝗔𝘂𝘁𝗼 𝗦𝗰𝗵𝗲𝗱𝘂𝗹𝗲𝗿 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀
!csend - Send Message To All Chnls.
!acsend - Send Message To All Chnls In Loop(Auto).
!acstop - Stop Auto Message Sending.
!alive - Check If Bot Is Alive
!about - About The Bot 
!help - Help Message
"""

ABOUT_TXT = """
᪥ Name: 𝗔𝘂𝘁𝗼 𝗦𝗰𝗵𝗲𝗱𝘂𝗹𝗲𝗿 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𝗕𝘆 @xAaYux • @LegendxTricks
᪥ Library: [Telethon](https://docs.telethon.dev/)
᪥ Language: Python 3 
᪥ Dev: [⏤‌ＫＡＲＴＩＫ𓆩♡𓆪™|🇮🇳](https://t.me/xAaYux)
"""

@client.on(events.NewMessage(pattern='@LegendxTricks'))
async def get_group_id(event):
    # Get the group ID
    group_id = event.chat_id
    
    # Save the group ID to saved messages
    await client.send_message('me', f'Saved Group ID:`{group_id}`')
      
@client.on(events.NewMessage(outgoing=True, pattern='!about'))
async def about(event):
    await event.edit(ABOUT_TXT, link_preview=False)


@client.on(events.NewMessage(outgoing=True, pattern='!help'))
async def help_me(event):
    await event.edit(HELP)


@client.on(events.NewMessage(outgoing=True, pattern='!alive'))
async def alive(event):
    txt = await event.edit("▢▢▢▢▢▢")
    await event.edit("▣▢▢▢▢▢")
    await event.edit("▣▣▢▢▢▢")
    await event.edit("▣▣▣▢▢▢")
    await event.edit("▣▣▣▣▢▢")
    await event.edit("▣▣▣▣▣▢")
    await event.edit("▣▣▣▣▣▣")
    
    await event.edit(f"𝗔𝘂𝘁𝗼")
    await event.edit(f"𝗔𝘂𝘁𝗼 𝗦𝗰𝗵𝗲𝗱𝘂𝗹𝗲𝗿")
    await event.edit(f"𝗔𝘂𝘁𝗼 𝗦𝗰𝗵𝗲𝗱𝘂𝗹𝗲𝗿 𝗨𝘀𝗲𝗿𝗯𝗼𝘁")
    await event.edit(f"𝗔𝘂𝘁𝗼 𝗦𝗰𝗵𝗲𝗱𝘂𝗹𝗲𝗿 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𝗜𝘀")
    await event.edit(f"𝗔𝘂𝘁𝗼 𝗦𝗰𝗵𝗲𝗱𝘂𝗹𝗲𝗿 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𝗜𝘀 𝗔𝗰𝘁𝗶𝘃𝗲.")
    await event.edit(f"𝗔𝘂𝘁𝗼 𝗦𝗰𝗵𝗲𝗱𝘂𝗹𝗲𝗿 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𝗜𝘀 𝗔𝗰𝘁𝗶𝘃𝗲.\n\n𝗗𝗲𝗮𝗹𝘆 𝗜𝘀 𝗦𝗲𝘁 𝗧𝗼 {DELAY}(𝗦𝗲𝗰𝗼𝗻𝗱𝘀).")
    await event.edit(f"𝗔𝘂𝘁𝗼 𝗦𝗰𝗵𝗲𝗱𝘂𝗹𝗲𝗿 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𝗜𝘀 𝗔𝗰𝘁𝗶𝘃𝗲.\n\n𝗗𝗲𝗮𝗹𝘆 𝗜𝘀 𝗦𝗲𝘁 𝗧𝗼 {DELAY}(𝗦𝗲𝗰𝗼𝗻𝗱𝘀).\n\n 💭 @LegendxTricks")


with client:
    client.run_until_disconnected()
