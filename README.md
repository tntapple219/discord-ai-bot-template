🤖 Discord AI Chatbot TemplateA highly customizable Discord AI chatbot template built with discord.py and openai (compatible with OpenAI-like APIs). This template features API key rotation for improved reliability and dynamic, per-user conversation history management with a configurable system prompt.✨ FeaturesDiscord Integration: Connects to your Discord server and responds to slash commands.AI Chat Functionality: Uses openai library to interact with various AI models (via OpenRouter.ai or other compatible APIs).API Key Rotation: Automatically switches to another API key if the current one fails, enhancing bot uptime and reliability.Per-User Conversation History: Maintains separate chat histories for each user, allowing for natural and continuous conversations.Configurable AI Personality: Easily define the AI's persona and instructions via an environment variable.Flexible API Endpoint: Switch between different OpenAI-compatible API services (like OpenRouter.ai, OpenAI's official API, etc.) by changing an environment variable.Command to Reset History: Users can clear their personal conversation history with a simple slash command.Secure Configuration: Utilizes .env files for managing sensitive information like tokens and API keys.🚀 Quick StartFollow these steps to get your AI chatbot up and running!1. PrerequisitesPython 3.8+: Make sure you have Python installed.Discord Bot Token: Create a new bot application on the Discord Developer Portal, enable Message Content Intent and Privileged Gateway Intents (under Bot -> Privileged Gateway Intents), and copy your bot token.OpenRouter.ai API Keys: Get your API keys from OpenRouter.ai or any other OpenAI-compatible API service.2. InstallationClone the repository (or download the bot.py file and create a .env file manually):git clone https://github.com/YOUR_GITHUB_USERNAME/discord-ai-bot-template.git
cd discord-ai-bot-template
(Remember to replace YOUR_GITHUB_USERNAME with tntapple219 once you upload it!)Install dependencies:pip install discord.py openai python-dotenv
3. ConfigurationCreate a .env file in the same directory as bot.py.Add your configuration to the .env file. Here's a template:# .env example
# Discord Bot Token (REQUIRED!)
DISCORD_BOT_TOKEN="YOUR_DISCORD_BOT_TOKEN_HERE"

# OpenRouter.ai API Keys (comma-separated if you have multiple)
# Get them from https://openrouter.ai/
OPEN_ROUTER_API_KEYS="sk-yourkey1,sk-yourkey2,sk-yourkey3" 

# AI Model Name (optional, defaults to google/gemma-3-27b-it:free)
# Check available models on OpenRouter.ai: https://openrouter.ai/docs#models
AI_MODEL_NAME="google/gemma-3-27b-it:free"

# The System Prompt / AI's Personality (REQUIRED for bot personality!)
# This sets the AI's core instructions and persona.
# Example: "You are a helpful AI assistant."
# Example: "You are a friendly, sarcastic chatbot who loves to make jokes."
AI_SYSTEM_PROMPT="You are a helpful and friendly AI assistant. Your goal is to provide useful information and and engage in pleasant conversation."

# AI API Base URL (optional, defaults to OpenRouter.ai's API URL)
# Use this if you want to connect to a different OpenAI-compatible API endpoint
# Example for OpenAI's official API: https://api.openai.com/v1
AI_API_BASE_URL="https://openrouter.ai/api/v1" 
Replace the placeholder values with your actual tokens and keys.4. Run the BotExecute the bot.py file:python bot.py
Your bot should now connect to Discord!⚡ UsageOnce the bot is online and slash commands are synced (this happens automatically when the bot starts), you can use the following commands in your Discord server:/chat <your_message>: Ask the AI a question and start a conversation./reset: Clear your personal conversation history with the bot.🤝 Contribution & FeedbackThis template is open-source and continuously evolving. Feel free to explore, modify, and use it for your projects. If you have any suggestions, bug reports, or ideas for improvement, don't hesitate to open an issue or submit a pull request on GitHub!📄 LicenseThis project is licensed under the MIT License - see the LICENSE file for details.
