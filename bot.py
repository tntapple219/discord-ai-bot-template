import os
from dotenv import load_dotenv
from openai import OpenAI
import discord
from discord.ext import commands
import random # Used for randomly selecting API keys
import asyncio # Used for asynchronous delays

# --- Environment Variable Loading and API Key Setup ---
load_dotenv()

# Load all API Keys from .env, split by comma into a list
# This is our 'raw' key pool, used for resetting the available keys
OPEN_ROUTER_API_KEYS_RAW = os.getenv("OPEN_ROUTER_API_KEYS")
if OPEN_ROUTER_API_KEYS_RAW:
    ALL_API_KEYS = [key.strip() for key in OPEN_ROUTER_API_KEYS_RAW.split(',')]
else:
    ALL_API_KEYS = [] # If no keys are set, provide an empty list

# This is our 'currently available' key pool, from which invalid keys will be dynamically removed
# Note: This will be initialized once before on_ready or the first chat command execution
current_api_keys = list(ALL_API_KEYS) # Use list() for a shallow copy to avoid modifying the original list

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN") # Renamed for clarity, often "DISCORD_BOT_TOKEN" is used
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "google/gemma-3-27b-it:free") # Load model name, with a default
SYSTEM_PROMPT = os.getenv("AI_SYSTEM_PROMPT") # Load the system prompt from .env
# New: Load the API base URL, with OpenRouter's URL as a default
AI_API_BASE_URL = os.getenv("AI_API_BASE_URL", "https://openrouter.ai/api/v1") 


# Validate essential environment variables
if not DISCORD_TOKEN:
    print("Error: DISCORD_BOT_TOKEN not found in .env. Please set it. (╥_╥)")
    exit() # Exit if no Discord token

if not SYSTEM_PROMPT:
    print("Warning: AI_SYSTEM_PROMPT not found in .env. Using a generic system prompt. ( •́ ₃ •̀ )")
    # Fallback to a generic system prompt if none is provided in .env
    SYSTEM_PROMPT = "You are a helpful AI assistant."

# --- Helper Function: Reset Available API Keys ---
def reset_api_keys():
    global current_api_keys
    current_api_keys = list(ALL_API_KEYS) # Reload all keys
    if current_api_keys:
        print("API Key pool has been reset! (｡•̀ᴗ-)✧")
    else:
        print("Warning: Attempted to reset API Key pool, but no keys are configured in .env. (｡•́︿•̀｡)")


# --- User-specific Conversation History Data ---
user_histories = {}
MAX_HISTORY_TURNS = 20 # Max 20 conversation turns (excluding System message)

# Discord bot setup
intents = discord.Intents.all()
intents.message_content = True # Required for reading message content
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    """Event that fires when the bot is ready and connected to Discord."""
    print(f"{bot.user} has connected to Discord! (✿◕‿◕)")
    # Ensure current_api_keys is initialized before the first command is run
    if not current_api_keys and ALL_API_KEYS:
        reset_api_keys()
    
    try:
        await bot.tree.sync() # Sync slash commands
        print("Slash commands synced!")
    except Exception as e:
        print(f"Failed to sync commands: {e} (╥_╥)")


@bot.tree.command(name="chat", description="Ask the AI a question!")
async def chat(ctx, message:str):
    """Handles the AI chat command, managing history and API key rotation."""
    user_id = ctx.user.id
    await ctx.response.defer(thinking=True) # Display "Bot is thinking..."

    # Initialize history for the user if it doesn't exist, starting with the system prompt
    if user_id not in user_histories:
        user_histories[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    history = user_histories[user_id]

    # Add user's message to history
    history.append({"role": "user", "content": message})

    # Limit history length (keep system message, so total length is MAX_HISTORY_TURNS + 1)
    # If it exceeds, remove the oldest conversation turn (index 1 is the first user message of a turn)
    if len(history) > MAX_HISTORY_TURNS + 1:
        history.pop(1)

    # --- AI Call and Automatic Key Switching Logic ---
    ai_response_content = "Oops! All AI Keys are used up, or the model could not respond to your request. (⊃д⊂) Please try again later." # Default error message
    
    # Max retries is the number of keys, to prevent infinite loops
    max_api_retries = len(ALL_API_KEYS)
    current_retries = 0

    # Ensure current_api_keys has content, especially if all keys failed and were cleared
    if not current_api_keys and ALL_API_KEYS:
        reset_api_keys()

    while current_retries < max_api_retries:
        if not current_api_keys: # If the current key pool is empty
            print("All available API keys have failed. Resetting key pool!")
            reset_api_keys()
            
            if not current_api_keys: # If still empty after reset, truly no keys configured
                ai_response_content = "Oops! No OpenAI API Keys found or configured. Please contact the bot owner! (｡•́︿•̀｡)"
                break # Exit loop, as no keys are available
            
            await asyncio.sleep(1) # Add a small delay to let the system breathe (๑´ㅂ`๑)

        selected_api_key = random.choice(current_api_keys) # Randomly select a key from the available pool
        print(f"Attempting with Key (partial): {selected_api_key[:8]}... ({len(current_api_keys)} keys remaining)")

        try:
            # Initialize OpenAI client with the selected key and base_url (now from .env)
            client_ai_dynamic = OpenAI(
                api_key=selected_api_key,
                base_url=AI_API_BASE_URL # Use the base URL from .env
            )
            
            response = await client_ai_dynamic.chat.completions.create( # Use await here
                model=AI_MODEL_NAME, # Use the model name from .env
                messages=history,
            )
            ai_response_content = response.choices[0].message.content
            
            break # Success! Exit the loop
            
        except Exception as e:
            print(f"API call failed with Key (partial): {selected_api_key[:8]}... Error: {e}")
            
            # If this key failed, remove it from the current available key pool!
            if selected_api_key in current_api_keys:
                current_api_keys.remove(selected_api_key)
                print(f"Removed invalid Key (partial): {selected_api_key[:8]}... ({len(current_api_keys)} keys remaining)")
            
            current_retries += 1 # Increment retry count
            await asyncio.sleep(0.5) # Wait a bit after failure before trying the next key

    # --- Respond to user and update history ---
    await ctx.followup.send(f"{ai_response_content}")
    
    # Only add to history if AI provided an actual response (not an error message)
    if not ai_response_content.startswith("Oops!"): # Check for the specific error message prefix
        history.append({"role": "assistant", "content": ai_response_content})
        # Re-limit history length (ensure length is within bounds after assistant's response)
        if len(history) > MAX_HISTORY_TURNS + 1:
            history.pop(1)


@bot.tree.command()
async def reset(ctx):
    """Resets your personal conversation history with the bot."""
    user_id = ctx.user.id
    # Clear history, only keeping the System message (loaded from .env)
    user_histories[user_id] = [
        {"role": "system", "content": SYSTEM_PROMPT} # Load system prompt from .env here as well
    ]
    await ctx.response.send_message("Your memory has been cleared! ( •̀ ω •́ )✧")

bot.run(DISCORD_TOKEN)
