import os
from dotenv import load_dotenv
import asyncio
from pyrogram import Client, filters, types
import json
import re

emote_table_file = "emote_table"

class Search:

    def __init__(self, dict: dict) -> None:
        self._dict = dict

    def find_emote(self, w: str):
        if any([ord('а') <= ord(i) <= ord('я') for i in w]):
            w = self.ru_to_en_keyboard(w)

        result = []     
        for key, value in self._dict.items():
            if w.lower() in key.lower():
                result.append(value)
        return sorted(result, key=lambda x: len(x))

    # https://github.com/nawinds/inline-stickers-search-bot/blob/master/modules/search.py
    @staticmethod
    def ru_to_en_keyboard(text: str) -> str:
        layout = dict(zip(map(ord, '''йцукенгшщзхъфывапролджэячсмитьбю.ёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё'''),
                          '''qwertyuiop[]asdfghjkl;'zxcvbnm,./`QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~'''))
        return text.translate(layout)

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

@app.on_message(filters.command("menu"))
async def menu_handler(client, message):
    bs = '\n'
    await message.reply(f"{bs.join([pattern for pattern, _ in emote_table.items()])}", quote=False)

@app.on_inline_query()
async def inline_query(client, inline_query):
    print(inline_query.query)
    search = Search(emote_table)
    result = [types.InlineQueryResultCachedSticker(sticker_file_id=file_id) for file_id in search.find_emote(w=inline_query.query)[:50]]
    
    await inline_query.answer(
        results=result,
        is_gallery=True
    )

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
    print("Starting ... ")
    app.run()
finally:
    print("Exiting ...")
    with open(emote_table_file, "w") as f:
        json.dump(emote_table, f)   