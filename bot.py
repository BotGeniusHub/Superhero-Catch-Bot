import requests
from pyrogram import Client, filters, idle
from pymongo import MongoClient

TOKEN = '6206599982:AAECqgU3Os4kTjSuS_Zz-zcM7JZHWdvbI10'
API_TOKEN = '803115424842504'
MONGO_CONNECTION_STRING = 'mongodb+srv://sonu55:sonu55@cluster0.vqztrvk.mongodb.net/?retryWrites=true&w=majority'

api_id = '16743442'
api_hash = '12bbd720f4097ba7713c5e40a11dfd2a'

app = Client(
    "my_bot",
    bot_token=TOKEN,
    api_id=api_id,
    api_hash=api_hash
)

message_count = 0

def spawn_character(client, message):
    global message_count
    message_count += 1

    if message_count % 10 == 0:
        character_id = get_random_character_id()
        response = requests.get(f'https://superheroapi.com/api/{API_TOKEN}/{character_id}')

        if response.status_code == 200:
            character_data = response.json()

            character_name = character_data['name']
            character_image = character_data['image']['url']
            character_ability = character_data['powerstats']['intelligence']

            sent_message = client.send_photo(
                chat_id=message.chat.id,
                photo=character_image,
                caption=f"A new Character {character_name} appeared! Type /protect name to collect them!"
            )

            save_character_info(character_name, character_image, character_ability, character_id, message.chat.id, message.from_user.id, message_id)
        else:
            print("Failed to fetch a character from the Superhero API.")

def save_character_info(character_name, character_image, character_ability, character_id, chat_id, user_id, message_id):
    client = MongoClient(MONGO_CONNECTION_STRING)
    db = client['my_bot_db']
    collection = db['character_info']

    info = {
        'character_name': character_name,
        'character_image': character_image,
        'character_ability': character_ability,
        'character_id': character_id,
        'chat_id': chat_id,
        'user_id': user_id,
        'message_id': message_id
    }

    collection.insert_one(info)

# Rest of the code remains the same

@app.on_message(filters.group & filters.command("protecc"))
def handle_protect_command(client, message):
    protected_characters = get_protected_characters(message.chat.id)

    if protected_characters:
        reply = "Protected Characters:\n\n"
        for character in protected_characters:
            reply += f" {character['character_name']} (Ability: {character['character_ability']})\n"

        client.send_message(
            chat_id=message.chat.id,
            text=reply
        )
    else:
        client.send_message(
            chat_id=message.chat.id,
            text="No protected characters found in this chat."
        )

@app.on_message(filters.private & filters.command("collection"))
def handle_collection_command(client, message):
    protected_characters = get_protected_characters_by_user(message.from_user.id)

    if protected_characters:
        reply = "Your Protected Characters:\n\n"
        for character in protected_characters:
            reply += f"- {character['character_name']} (Ability: {character['character_ability']})\n"

        client.send_message(
            chat_id=message.chat.id,
            text=reply
        )
    else:
        client.send_message(
            chat_id=message.chat.id,
            text="You have no protected characters in your collection."
        )

def get_random_character_id():
    import random
    return random.randint(1, 731)

def get_protected_characters(chat_id):
    client = MongoClient(MONGO_CONNECTION_STRING)
    db = client['my_bot_db']
    collection = db['character_info']

    protected_characters = collection.find({'chat_id': chat_id})
    return protected_characters

def get_protected_characters_by_user(user_id):
    client = MongoClient(MONGO_CONNECTION_STRING)
    db = client['my_bot_db']
    collection = db['character_info']

    protected_characters = collection.find({'user_id': user_id})
    return protected_characters

@app.on_message(filters.group)
def handle_group_message(client, message):
    spawn_character(client, message)

app.run()
idle()
