import speech_recognition as sr
import google.generativeai as genai
from elevenlabs.client import ElevenLabs  # imports the ElevenLabs class we use to connect to their API
from elevenlabs import play               # separate function just for playing the audio out loud
import time
 
GEMINI_API_KEY     = ""
ELEVENLABS_API_KEY = ""
 
# Gemini setup (old SDK but still works)
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash-lite")

# ElevenLabs setup (NEW SDK 방식)
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


# -------------------------
# START GAME
# -------------------------
def start_adventure():
    print("\n" + "=" * 55)
    print("  🧙 Welcome to the AI Dungeon Master Adventure! 🧙")
    print("=" * 55)

    hero_name = input("\n⚔️  What is your hero's name? → ").strip()
    if hero_name == "":
        hero_name = "Brave Hero"

    print("\n🗺️  Choose your adventure theme:")
    print("   1. Fantasy")
    print("   2. Pirate")
    print("   3. Space")
    print("   4. Haunted")

    theme_choice = input("\n   Type a number (1-4) → ").strip()

    themes = {
        "1": "fantasy",
        "2": "pirate",
        "3": "space",
        "4": "haunted house"
    }

    theme = themes.get(theme_choice, "fantasy")

    print(f"\n✅ Great! Prepare yourself, {hero_name}!")
    print(f"   Your {theme} adventure begins...\n")

    return {
        "hero_name": hero_name,
        "theme": theme,
        "health": 100,
        "inventory": ["torch", "small dagger"],
        "story_history": []
    }


# -------------------------
# SPEECH INPUT
# -------------------------
def listen_to_player():
    recognizer = sr.Recognizer()

    print("\n🎤 Speak your action...")

    with sr.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic, duration=1)

        try:
            audio = recognizer.listen(mic, timeout=8)
            text = recognizer.recognize_google(audio)
            print(f"   You said: {text}")
            return text

        except:
            return ""


# -------------------------
# GEMINI STORY GENERATION
# -------------------------
def ask_dungeon_master(player_action, game_state):

    memory = "\n".join(game_state["story_history"][-4:]) if game_state["story_history"] else "Start of adventure."

    prompt = f"""
You are a Dungeon Master in a {game_state['theme']} world.

Hero: {game_state['hero_name']}
Health: {game_state['health']}
Inventory: {game_state['inventory']}

History:
{memory}

Player action: {player_action}

Write 3-4 exciting sentences and continue the story.
"""

    response = gemini_model.generate_content(prompt)
    return response.text


# -------------------------
# FIXED ELEVENLABS (THIS IS THE IMPORTANT FIX)
# -------------------------
def narrate(message):
    print("\n🧙 Dungeon Master says:\n")
    print(message)

    try:
        audio = client.text_to_speech.convert(
            text=message,
            voice_id="JBFqnCBsd6RMkjVDRZzb",  # George voice
            model_id="eleven_multilingual_v2"
        )

        play(audio)

    except Exception as e:
        print(f"\n[Voice error: {e}]")


# -------------------------
# UPDATE GAME STATE
# -------------------------
def update_game_state(story_text, game_state):
    game_state["story_history"].append(story_text)
    return game_state


# -------------------------
# GAME LOOP
# -------------------------
def play_game():

    game_state = start_adventure()

    opening = gemini_model.generate_content(
        f"Start a {game_state['theme']} adventure for {game_state['hero_name']}."
    ).text

    narrate(opening)
    game_state["story_history"].append(opening)

    while True:

        action = listen_to_player()

        if action == "":
            print("No input detected.")
            continue

        if "quit" in action.lower():
            break

        story = ask_dungeon_master(action, game_state)
        game_state = update_game_state(story, game_state)
        narrate(story)

        if game_state["health"] <= 0:
            print("Game Over")
            break


if __name__ == "__main__":
    play_game()