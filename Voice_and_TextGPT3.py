import openai
import pyttsx3
import speech_recognition as sr
import time
import shutil
import os

# Set OpenAI API key goes here
openai.api_key = "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"

# Initialize the text-to-speech engine
engine = pyttsx3.init()

def transcribe_audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except:
        print('Skipping unknown error')

def generate_response(prompt, conversation_history=[]):
    prompt_with_history = '\n'.join(conversation_history + [prompt])
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_with_history,
        max_tokens=4000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response["choices"][0]["text"]

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def save_conversation(prompt, response):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = os.path.join("conversations", f"conversation_{timestamp}.txt")
    with open(filename, "w") as file:
        file.write("Prompt: {}\n".format(prompt))
        file.write("Response: {}\n".format(response))
    print("Conversation saved: {}".format(filename))

def save_memory(memory):
    with open("memory.txt", "a") as file:
        file.write('\n'.join(memory) + '\n')

def load_memory():
    if not os.path.exists("memory.txt"):
        return []
    with open("memory.txt", "r") as file:
        return file.read().splitlines()

def main():
    # Create "conversations" directory if it doesn't exist
    conversations_dir = "conversations"
    if not os.path.exists(conversations_dir):
        os.makedirs(conversations_dir)

    conversation_history = []

    # Create "audio_inputs" directory if it doesn't exist
    audio_inputs_dir = "audio_inputs"
    if not os.path.exists(audio_inputs_dir):
        os.makedirs(audio_inputs_dir)

    while True:
        # Wait for user to choose input method
        print("Select input method:")
        print("1. Audio")
        print("2. Text")
        choice = input("Enter your choice (1 or 2): ")

        if choice == "1":
            try:
                # Record Audio
                filename = "input.wav"
                print("Say your question...")
                with sr.Microphone() as source:
                    recognizer = sr.Recognizer()
                    source.pause_threshold = 1
                    audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
                    with open(filename, "wb") as f:
                        f.write(audio.get_wav_data())
                # Transcribe audio to text
                text = transcribe_audio_to_text(filename)
                if text:
                    print(f"You said: {text}")

                    # Generate Response using GPT-3
                    response = generate_response(text, conversation_history)
                    print(f"GPT-3 says: {response}")

                    # Read response using text to-speech
                    speak_text(response)
                    # Create a copy of the input.wav file and move it to "audio_inputs" directory
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    new_filename = os.path.join(audio_inputs_dir, f"input_{timestamp}.wav")
                    shutil.copyfile(filename, new_filename)
                    print(f"Copy of input.wav created: {new_filename}")

                    # Save conversation to a text file
                    save_conversation(text, response)

                    # Update conversation history
                    conversation_history.append('\n' + "Prompt: " + text)
                    conversation_history.append("GPT: " + response + '\n')

                    # Save conversation history to memory
                    save_memory(conversation_history)

            except Exception as e:
                print("An error occurred: {}".format(e))
        
        elif choice == "2":
            # Input using text
            prompt = input("Enter your question: ")

            # Generate Response using GPT-3
            response = generate_response(prompt, conversation_history)
            print(f"GPT-3 says: {response}")

            # Read response using text-to-speech
            speak_text(response)

            # Save conversation to a text file
            save_conversation(prompt, response)

            # Update conversation history
            conversation_history.append('\n' + "Prompt: " + prompt)
            conversation_history.append("GPT: " + response + '\n')

            # Save conversation history to memory
            save_memory(conversation_history)

        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()    
