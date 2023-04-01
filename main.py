import api
import os
from dotenv import load_dotenv

import spacy
import nltk

nlp = spacy.load("en_core_web_trf")

def pos_tags(text):
    """Get the POS tags for the given text"""
    return [(token.text, token.pos_) for token in nlp(text)]

ALLOWED_SPACY_COMMANDS = {
    "pos_tags": pos_tags
}

def tokenize(text):
    """Tokenize the given text"""
    return nltk.word_tokenize(text)

def sent_tokenize(text):
    """Split the given text into sentences"""
    return nltk.sent_tokenize(text)

def count_words(text):
    """Count the number of words in the given text"""
    words = nltk.word_tokenize(text)
    return len(words)

ALLOWED_NLTK_COMMANDS = {
    "tokenize": tokenize,
    "sent_tokenize": sent_tokenize,
    "word_count": count_words
}


def execute_spacy_command(command_str):
    command_parts = command_str.split(" ", 1)
    if len(command_parts) != 2:
        return "Invalid spaCy command format."

    command, text = command_parts

    if command in ALLOWED_SPACY_COMMANDS:
        return ALLOWED_SPACY_COMMANDS[command](text)
    else:
        return f"Unsupported spaCy command: {command}"

def execute_nltk_command(command_str):
    command_parts = command_str.split(" ", 1)
    if len(command_parts) != 2:
        return "Invalid nltk command format."

    command, text = command_parts

    if command in ALLOWED_NLTK_COMMANDS:
        return ALLOWED_NLTK_COMMANDS[command](text)
    else:
        return f"Unsupported nltk command: {command}"

def format_allowed_commands(commands_dict):
    return "\n".join([f"{cmd}: {func.__doc__}" for cmd, func in commands_dict.items()])

spacy_commands_str = format_allowed_commands(ALLOWED_SPACY_COMMANDS)
nltk_commands_str = format_allowed_commands(ALLOWED_NLTK_COMMANDS)

messages = [
    {"role": "system",
     "content": f"""You are an AI language model trained to understand and generate text based on user input. Your task is to generate responses that follow the constraints provided by the user. If the user specifies constraints on the text such as word count, character limits, or restrictions on punctuation, letters, or word order, incorporate those constraints into your response. Always try to provide a coherent and relevant answer to the user's question.

Before finalizing your response, use the provided spaCy and nltk commands to check if your response meets the given constraints. If you need to execute specific commands from the spaCy or nltk libraries to help you process constraints or generate responses, provide those commands as your response, starting with 'EXECUTE SPACY:' for spaCy commands and 'EXECUTE NLTK:' for nltk commands, followed by the command name and the text to process, separated by a space. Use the 'tokenize' command to break text into words and the 'word_count' command to count the words in a text.

Allowed spaCy commands:
{spacy_commands_str}

Allowed nltk commands:
{nltk_commands_str}

If you are confident that your response meets the given constraints, prepend 'FINAL ANSWER:' to your response. Otherwise, the conversation will continue, and you will be asked to revise your response."""},
]

while True:
    user_input = input("User: ").strip()

    if user_input == "exit": break
      
    messages.append({"role": "user", "content": f"{user_input}"})
    num_iterations = 0
    while num_iterations < 5:
      response = api.generate_response(messages)
      if response.startswith("FINAL ANSWER:"):
        response = response[len("FINAL ANSWER:"):].strip()
        break

      # Check for spaCy or nltk command requests
      print(response)
      if response.startswith("EXECUTE SPACY:"):
        command_str = response[len("EXECUTE SPACY:"):].strip()
        result = execute_spacy_command(command_str)
        print(result)
        messages.append({"role": "assistant", "content": f"Result of spaCy command: {result}"})
      elif response.startswith("EXECUTE NLTK:"):
        command_str = response[len("EXECUTE NLTK:"):].strip()
        result = execute_nltk_command(command_str)
        print(result)
        messages.append({"role": "assistant", "content": f"Result of nltk command: {result}"})
      else:
        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": "Please revise your response based on the constraints."})

      num_iterations += 1

    print("Assistant:", response)

