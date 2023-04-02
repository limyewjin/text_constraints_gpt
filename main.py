import api
import os
from dotenv import load_dotenv

import spacy
import nltk
import string

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
    tokenizer = nltk.TweetTokenizer()
    words = [x for i in nltk.sent_tokenize(text) for x in tokenizer.tokenize(i) if x not in string.punctuation]
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

Before providing your final response, make sure to use the provided spaCy and nltk commands to verify that your response meets the given constraints. If you need to execute specific commands from the spaCy or nltk libraries to help you process constraints or generate responses, provide those commands as your response, starting with 'EXECUTE SPACY:' for spaCy commands and 'EXECUTE NLTK:' for nltk commands, followed by the command name and the text to process, separated by a space. Use the 'tokenize' command to break text into words and the 'word_count' command to count the words in a text.

If you need to reason or think about next steps, feel free to provide your intermediate thoughts or potential approaches as part of your response. This can help guide you in generating a response that meets the user's constraints.

Allowed spaCy commands:
{spacy_commands_str}

Allowed nltk commands:
{nltk_commands_str}

Only after verifying that your response meets the constraints using the provided commands, prepare your final response. Prepend 'FINAL ANSWER:' to your final response in a separate message after executing the appropriate command(s). Do not include any specific word count or constraint-related information in your final answer unless you have used the provided commands to verify it."""},
    {"role": "user",
     "content": "write a poem about spring using 12 words"},
    {"role": "assistant",
     "content": "EXECUTE NLTK: word_count Spring brings about new life, Flowers bloom, birds sing, Warm sunshine, new beginnings."},
    {"role": "assistant",
     "content": "Result of nltk command: 13"},
    {"role": "assistant",
     "content": 'The user requested 12 words but the number of words in "Spring brings about new life, Flowers bloom, birds sing, Warm sunshine, new beginnings." is 13. I need to remove a word to make it 12 words.'},
    {"role": "assistant",
     "content": "EXECUTE NLTK: word_count Spring brings new life, Flowers bloom, birds sing, Warm sunshine, new beginnings."},
    {"role": "assistant",
     "content": "Result of nltk command: 12"},
    {"role": "assistant",
     "content": "FINAL ANSWER: Spring brings new life, Flowers bloom, birds sing, Warm sunshine, new beginnings."},
]

while True:
    user_input = input("User: ").strip()

    if user_input == "exit": break
      
    messages.append({"role": "user", "content": f"{user_input}"})
    num_iterations = 0
    while num_iterations < 10:
      response = api.generate_response(messages, model="gpt-4")
      if response.startswith("FINAL ANSWER:"):
        response = response[len("FINAL ANSWER:"):].strip()
        break

      # Check for spaCy or nltk command requests
      if response.startswith("EXECUTE SPACY:"):
        print(response)
        command_str = response[len("EXECUTE SPACY:"):].strip()
        result = execute_spacy_command(command_str)
        print("RESULT:", result)
        messages.append({"role": "assistant", "content": f"Result of spaCy command: {result}"})
      elif response.startswith("EXECUTE NLTK:"):
        print(response)
        command_str = response[len("EXECUTE NLTK:"):].strip()
        result = execute_nltk_command(command_str)
        print("RESULT:", result)
        messages.append({"role": "assistant", "content": f"Result of nltk command: {result}"})
      else:
        print("THINKING:", response)
        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": "Please revise your response based on the constraints."})

      num_iterations += 1

    print("Assistant:", response)

