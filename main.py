import os
from dotenv import load_dotenv
import asyncio
from pyrogram import Client, filters
import json
import re

emote_table_file = "emote_table"

def findWholeWord(w):
    escaped_word = re.escape(w)
    pattern = r'(^|\s)' + escaped_word + r'($|\s)'
    return re.compile(pattern).search


load_dotenv()
creds = {}
emote_table = dict()

with open(emote_table_file, 'r') as f:
    if os.path.getsize(emote_table_file) > 0:
        emote_table = json.load(f)

creds['admin'] = os.getenv('admin')
if creds['admin']:
    my_list = creds['admin'].split(',')

creds['bot_token'] = os.getenv('bot_token')
creds['api_hash'] = os.getenv('api_hash')
creds['api_id'] = os.getenv('api_id')

app = Client("my_account")

@app.on_message(filters.group & filters.text)
async def my_handler(client, message):
    for pattern, file_id in emote_table.items():
        if(findWholeWord(pattern)(message.text)):
            await client.send_sticker(
                chat_id=message.chat.id,
                sticker=file_id,
                reply_to_message_id=message.id
            )

@app.on_message(filters.sticker & filters.private)
async def sticker_handler(client, message):
    await message.reply(message.sticker.file_id)

@app.on_message(filters.command("add"))
async def add_emote(client, message):
    if not (str(message.chat.id) in creds['admin']):
        await message.reply("Permission denied: You are not an admin", quote=True)
        return
    
    _, alias, file_id = message.text.split()

    emote_table[alias] = file_id
    with open(emote_table_file, "w") as f:
        json.dump(emote_table, f)
    print(f"Added alias {alias} to {file_id}")
    await message.reply(f"Added alias {alias} to {file_id}", quote=True)


try:
    app.run()
finally:
    with open(emote_table_file, "w") as f:
        json.dump(emote_table, f)