import requests
from pyrogram import Client, Filters, idle
from pymongo import MongoClient

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
API_TOKEN = '803115424842504'
MONGO_CONNECTION_STRING = 'mongodb+srv://sonu55:sonu55@cluster0.vqztrvk.mongodb.net/?retryWrites=true&w=majority'

def spawn_character(client, message):
    # Check if the message count is a multiple of 10
    if message.message_id % 10 == 0:
        # Fetch a random Marvel character from the Superhero API
        response = requests.get('https://superheroapi.com/api/{0}/RANDOM_ID'.format(API_TOKEN))

        if response.status_code == 200:
            character_data = response.json()

            character_name = character_data['name']
            character_image = character_data['image']['url']

            # Send the encounter message with the character name and image
            message = client.send_photo(
                chat_id=message.chat.id,
                photo=character_image,
                caption=f"A wild {character_name} appeared! Protect them!"
            )

            # Save the character information and user info in MongoDB
            save_character_info(character_name, character_image, message.chat.id, message.from_user.id)
        else:
            print("Failed to fetch a character from the Superhero API.")

def save_character_info(character_name, character_image, chat_id, user_id):
    client = MongoClient(MONGO_CONNECTION_STRING)
    db = client['my_bot_db']
    collection = db['character_info']

    info = {
        'character_name': character_name,
        'character_image': character_image,
        'chat_id': chat_id,
        'user_id': user_id
    }

    collection.insert_one(info)

def main():
    app = Client("my_bot", bot_token=TOKEN)

    @app.on_message(Filters.group & Filters.command("protecc"))
    def handle_protect_command(client, message):
        # Retrieve the protected characters for the current chat from MongoDB
        protected_characters = get_protected_characters(message.chat.id)

        if protected_characters:
            reply = "Protected Characters:\n\n"
            for character in protected_characters:
                reply += f"- {character}\n"

            client.send_message(
                chat_id=message.chat.id,
                text=reply
            )
        else:
            client.send_message(
                chat_id=message.chat.id,
                text="No protected characters found in this chat."
            )

    def get_protected_characters(chat_id):
        client = MongoClient(MONGO_CONNECTION_STRING)
        db = client['my_bot_db']
        collection = db['character_info']

        protected_characters = collection.distinct('character_name', {'chat_id': chat_id})
        return protected_characters

    @app.on_message(Filters.group)
    def handle_group_message(client, message):
        spawn_character(client, message)

app.run()
idle() 

