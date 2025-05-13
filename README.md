Megha Chatbot
An emotionally intelligent, open-source chatbot simulating an 18-year-old Indian girl named Megha, created by Siddhartha Abhimanyu (@Elite_Sid).
Features

Emotional Intelligence: Understands user tone and adjusts mood and responses.
Memory: Remembers users and past conversations.
Cultural Awareness: Talks about Indian festivals, Bollywood, and college life.
Multilingual: Supports Hindi, English, and Hinglish.
Easy Deployment: One-click deployment on Heroku for non-coders.

Setup Instructions
Local Development

Clone the Repository:git clone https://github.com/yourusername/megha-chatbot.git
cd megha-chatbot


Install Dependencies:pip install -r requirements.txt


Install Polyglot Models:polyglot download sentiment2.hi sentiment2.en


Configure Environment Variables:
Copy .env.example to .env and edit:cp .env.example .env


For online mode:AI_MODE=online
OPENROUTER_API_KEY=your_api_key
MODEL_NAME=meta-llama/llama-3-70b-instruct


For local mode:
Set up text-generation-webui:git clone https://github.com







