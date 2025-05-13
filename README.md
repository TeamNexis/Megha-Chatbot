Megha Chatbot
An emotionally intelligent, open-source chatbot simulating an 18-year-old Indian girl named Megha, created by Siddhartha Abhimanyu (@Elite_Sid).
Features

Emotional Intelligence: Uses transformer-based sentiment analysis for Hindi, English, and Hinglish.
Memory & Growth: Stores user data and chat history in MongoDB Atlas, tracks age and interactions.
Cultural Awareness: References Indian festivals, Bollywood, college life, and family dynamics.
Multilingual: Supports Hindi, English, and Hinglish with natural, emotional responses.
Future-Proof: Abstracted AI calls and environment variable-based configuration.
Free Deployment: Runs on Render’s free tier with MongoDB Atlas.

Prerequisites

A GitHub account for repository hosting.
A MongoDB Atlas account with a free M0 cluster.
An OpenRouter API key for AI responses.

Deployment on Render

Create a GitHub Repository:

Clone this repository or create a new one: git clone <your-repo-url>.
Add all files listed in the repository structure.
Push to GitHub: git add . && git commit -m "Initial commit" && git push origin main.


Set Up MongoDB Atlas:

Sign up at MongoDB Atlas.
Create an M0 cluster (free tier, 512 MB).
Add a database user (e.g., Luna with password Krishna).
Set Network Access to allow connections from anywhere (0.0.0.0/0) for testing.
Use the provided MongoDB URL: mongodb+srv://Luna:Krishna@luna.u6qymae.mongodb.net/megha?retryWrites=true&w=majority&appName=Luna.


Create a Render Account:

Sign up at Render using GitHub.


Deploy Web Service:

In Render Dashboard, click “New” > “Web Service”.
Connect your GitHub repository.
Configure:
Runtime: Docker.
Environment Variables:MONGO_URI=mongodb+srv://Luna:Krishna@luna.u6qymae.mongodb.net/megha?retryWrites=true&w=majority&appName=Luna
OPENROUTER_API_KEY=your_api_key
AI_MODE=online
MODEL_NAME=meta-llama/llama-3-70b-instruct
PYTHONUNBUFFERED=1


Replace your_api_key with a valid key from OpenRouter.


Select the free tier and deploy.


Verify Deployment:

Access the app at the Render-provided URL (e.g., https://your-app.onrender.com).
Test the chat interface: enter a username, send a message, and verify Megha responds (e.g., “Aaj main thoda low feel kar rahi hoon... 😔”).
Check Render logs for errors: go to Dashboard > Logs.


Verify MongoDB:

Log in to MongoDB Atlas.
Check users and chatlogs collections in the megha database.
Example documents:
users: {"_id": "...", "name": "testuser", "mood": 0, "last_interaction": "..."}
chatlogs: `{"





