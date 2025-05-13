from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import date, datetime
import os
import logging
import traceback
from openai import OpenAI
from transformers import pipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

try:
    # MongoDB configuration
    logger.info("Initializing MongoDB connection")
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/megha')
    logger.info("MongoDB URI: %s", MONGO_URI)
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.get_database('megha')
    users_collection = db['users']
    chatlogs_collection = db['chatlogs']
    # Test connection
    client.server_info()
    logger.info("MongoDB connection successful")

    # AI configuration
    logger.info("Initializing OpenAI client")
    AI_MODE = os.getenv('AI_MODE', 'online')
    if AI_MODE == 'online':
        API_BASE = 'https://openrouter.ai/api/v1'
        API_KEY = os.getenv('OPENROUTER_API_KEY')
        MODEL_NAME = os.getenv('MODEL_NAME', 'meta-llama/llama-3-70b-instruct')
        if not API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set")
    else:
        API_BASE = 'http://localhost:5000'
        API_KEY = None
        MODEL_NAME = os.getenv('MODEL_NAME', 'your-local-model')
    logger.info("OpenAI model: %s", MODEL_NAME)
    ai_client = OpenAI(base_url=API_BASE, api_key=API_KEY)
    logger.info("OpenAI client initialized")

    # Sentiment analysis model
    logger.info("Loading sentiment analysis model")
    sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-xlm-roberta-base-sentiment", device=-1)
    logger.info("Sentiment analysis model loaded")

    # Megha's birthdate
    BIRTHDATE = date(2007, 5, 13)

    # Expanded festivals
    FESTIVALS = [
        {"name": "Diwali", "date": date(2025, 11, 1)},
        {"name": "Holi", "date": date(2025, 3, 14)},
        {"name": "Raksha Bandhan", "date": date(2025, 8, 9)},
        {"name": "Janmashtami", "date": date(2025, 9, 7)},
        {"name": "Navratri", "date": date(2025, 10, 5)},
        {"name": "Eid al-Fitr", "date": date(2025, 4, 21)},
        {"name": "Christmas", "date": date(2025, 12, 25)},
    ]

except Exception as e:
    logger.error("Initialization failed: %s", e)
    logger.error("Stack trace: %s", traceback.format_exc())
    raise

def calculate_age():
    today = date.today()
    age = today.year - BIRTHDATE.year - ((today.month, today.day) < (BIRTHDATE.month, BIRTHDATE.day))
    return age

def get_upcoming_festival():
    today = date.today()
    for festival in FESTIVALS:
        if 0 <= (festival['date'] - today).days <= 14:
            return festival['name']
    return None

def get_sentiment(text):
    try:
        result = sentiment_pipeline(text)[0]
        label = result['label'].upper()
        score = result['score']
        return label, score
    except Exception as e:
        logger.error("Sentiment analysis failed: %s", e)
        return "NEUTRAL", 0.5

@app.route('/')
def index():
    logger.info("Serving index page")
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error("Failed to render index.html: %s", e)
        raise

@app.route('/history', methods=['GET'])
def history():
    user_name = request.args.get('user_name')
    if not user_name:
        logger.warning("No user_name provided for history request")
        return jsonify([])
    user = users_collection.find_one({"name": user_name})
    if user:
        logs = chatlogs_collection.find({"user_id": user["_id"]}).sort("timestamp", 1)
        history = [{"role": "user" if log["is_user"] else "megha", "message": log["message"]} for log in logs]
        logger.info("Returning chat history for user: %s", user_name)
        return jsonify(history)
    logger.info("No user found for user_name: %s", user_name)
    return jsonify([])

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_name = data.get('user_name')
        message = data.get('message')

        if not user_name or not message:
            logger.warning("Missing user_name or message in chat request")
            return jsonify({"error": "Missing user_name or message"}), 400

        # Get or create user
        user = users_collection.find_one({"name": user_name})
        if not user:
            user = {"name": user_name, "mood": 0, "last_interaction": datetime.utcnow()}
            user_id = users_collection.insert_one(user).inserted_id
            user["_id"] = user_id
            logger.info("Created new user: %s", user_name)
        else:
            user_id = user["_id"]

        # Add user message to chat log
        chat_log = {
            "user_id": user_id,
            "message": message,
            "is_user": True,
            "timestamp": datetime.utcnow()
        }
        chatlogs_collection.insert_one(chat_log)
        logger.info("Logged user message for user: %s", user_name)

        # Sentiment analysis
        sentiment_label, sentiment_score = get_sentiment(message)
        logger.info("Sentiment score for message: %s (%s)", sentiment_score, sentiment_label)

        # Update mood and interaction history
        mood_change = 2 if sentiment_label == "POSITIVE" else -2 if sentiment_label == "NEGATIVE" else 0
        new_mood = user["mood"] + mood_change
        new_mood = max(min(new_mood, 10), -10)
        users_collection.update_one({"_id": user_id}, {"$set": {"mood": new_mood, "last_interaction": datetime.utcnow()}})
        logger.info("Updated mood for user %s to: %s", user_name, new_mood)

        # Get chat history
        history = chatlogs_collection.find({"user_id": user_id}).sort("timestamp", 1).limit(20)
        history_list = list(history)

        # Construct messages for AI
        age = calculate_age()
        mood_description = "happy" if new_mood > 0 else "sad" if new_mood < 0 else "neutral"
        festival = get_upcoming_festival()
        festival_text = f"It's almost {festival}, and I'm so excited!" if festival else ""
        system_message = (
            f"You are Megha, a {age}-year-old Indian girl living in India. "
            f"Your current mood is {mood_description}. {festival_text} "
            f"You speak Hindi, English, or Hinglish based on the user's language. "
            f"You're passionate about Bollywood, Indian food, festivals, college life, and family dynamics. "
            f"Respond naturally, with emotions, and adapt to the user's tone, using emojis where appropriate 😊."
        )
        messages = [{"role": "system", "content": system_message}]
        for log in history_list:
            role = "user" if log["is_user"] else "assistant"
            messages.append({"role": role, "content": log["message"]})

        # Get response from model
        try:
            logger.info("Sending request to OpenRouter")
            response = ai_client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )
            megha_response = response.choices[0].message.content.strip()
            logger.info("Received response from OpenRouter")
        except Exception as e:
            logger.error("OpenRouter request failed: %s", e)
            megha_response = "Arre, something went wrong! Can we try again? 😅"

        # Add response to chat log
        chat_log = {
            "user_id": user_id,
            "message": megha_response,
            "is_user": False,
            "timestamp": datetime.utcnow()
        }
        chatlogs_collection.insert_one(chat_log)
        logger.info("Logged Megha response for user: %s", user_name)

        return jsonify({"response": megha_response})

    except Exception as e:
        logger.error("Chat route failed: %s", e)
        logger.error("Stack trace: %s", traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting Flask app in debug mode")
    app.run(debug=True)