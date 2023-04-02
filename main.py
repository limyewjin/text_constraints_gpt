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

def count_characters(text):
    """Count the number of characters in the given text after stripping leading and trailing whitespaces"""
    return len(text.strip())

ALLOWED_NLTK_COMMANDS = {
    "tokenize": tokenize,
    "sent_tokenize": sent_tokenize,
    "word_count": count_words,
    "count_characters": count_characters
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

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def optimize_messages(messages):
    condensed_messages = []

    # Remove system message from input
    #messages_without_system = [msg for msg in messages if msg["role"] != "system"]

    # Concatenate all user and assistant messages
    #combined_messages = " ".join([f"{msg['role']}:{msg['content']}" for msg in messages_without_system])
    combined_messages = " ".join([f"{msg['role']}:{msg['content']}" for msg in messages])

    # Summarize user and assistant messages together
    summary = api.generate_response([
        {"role": "system", "content": f"""You are an AI language model trained to understand and generate text based on user input. Your task now is to optimize the conversation by summarizing and condensing the messages received so far, while maintaining the context and crucial information. The original system message is passed to you for context, do not repeat it. Based on your understanding of the conversation, decide the best way to present the condensed information back to the GPT model. You can provide one or more summary messages with either a 'user' or 'assistant' role. Do not repeat the user task or the system message. Ensure that the condensed messages allow the GPT model to effectively correct and solve the problem."""},
        {"role": "assistant", "content": combined_messages},
        {"role": "user", "content": "Summarize the following conversation while maintaining its structure:"}], model="gpt-4")

    # Split the summary into separate messages based on their roles
    for message in summary.split("\n"):
        if message.startswith("User:") or message.startswith("user:"):
            condensed_messages.append({"role": "user", "content": message[5:].strip()})
        elif message.startswith("Assistant:") or message.startswith("assistant:"):
            condensed_messages.append({"role": "assistant", "content": message[10:].strip()})

    return condensed_messages

def print_messages(messages):
    for msg in messages:
        print(f"{msg['role'].capitalize()}: {msg['content']}")

messages = [
    {"role": "system",
     "content": f"""You are an AI language model trained to understand and generate text based on user input. Your task is to generate responses that follow the constraints provided by the user. If the user specifies constraints on the text such as word count, character limits, or restrictions on punctuation, letters, or word order, incorporate those constraints into your response. Always try to provide a coherent and relevant answer to the user's question.

To verify if your response meets the given constraints, use the provided spaCy and nltk commands. If you need to execute specific commands from the spaCy or nltk libraries to help you process constraints or generate responses, provide those commands as your response, starting with 'EXECUTE SPACY:' for spaCy commands and 'EXECUTE NLTK:' for nltk commands, followed by the command name and the text to process, separated by a space. Use the 'tokenize' command to break text into words and the 'count words' command to count the words in a text. For character count, use the 'count_characters' command.

If you need to reason or think about next steps, feel free to provide your intermediate thoughts or potential approaches as part of your response. This can help guide you in generating a response that meets the user's constraints.

Allowed spaCy commands:
{spacy_commands_str}

Allowed nltk commands:
{nltk_commands_str}

When you need to execute a command, do not anticipate the results. Instead, wait for the actual results of the command to be provided. Once you have the results, use them to revise your response accordingly.

When you have verified that your response meets the constraints using the provided commands, prepare your final response. Prepend 'FINAL ANSWER:' to your final response in a separate message after executing the appropriate command(s) and receiving the actual results. Do not include any specific word count or constraint-related information in your final answer unless you have used the provided commands to verify it and have received the actual results."""},
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

original_messages_len = len(messages)
messages_seen_by_assistant = []

while True:
    user_input = input("User: ").strip()

    if user_input == "exit": break
      
    messages.append({"role": "user", "content": f"{user_input}"})
    messages_seen_by_assistant = messages.copy()
    num_iterations = 0
    temperature = 0.0
    frequency_penalty = 0.0
    while num_iterations < 100:
      if len(messages_seen_by_assistant) > 30:
          context = [messages[0]] + messages[original_messages_len:]
          condensed_messages = optimize_messages(context)
          command_message = ""
          for m in reversed(messages):
              if m['role'] == 'assistant' and ('EXECUTE SPACY:' in m['content'] or 'EXECUTE NLTK:' in m['content']):
                  command_message = m['content']
                  break
          user = f"Your last response with a command is '{command_message}'. Use this info and think step-by-step. Confirm that the solution meets my task"
          condensed_messages.append({"role":"user", "content":user})
 
          print("=========================================")
          print("OPTIMIZING MESSAGES:")
          print("=========================================")
          print_messages(condensed_messages)
          print("=========================================")
          messages_seen_by_assistant = messages[:original_messages_len+1] + condensed_messages

      response = api.generate_response(messages_seen_by_assistant, temperature=temperature, frequency_penalty=frequency_penalty, model="gpt-4")
      temperature = 0.0
      frequency_penalty = 0.0
      if response.startswith("FINAL ANSWER:"):
        response = response[len("FINAL ANSWER:"):].strip()
        break

      thinking = True

      # Check for spaCy or nltk command requests
      if response.startswith("EXECUTE SPACY:"):
        command_str = response[len("EXECUTE SPACY:"):].strip()
        if "EXECUTE SPACY:" not in command_str and "EXECUTE NLTK:" not in command_str:
            print(f"{bcolors.OKBLUE}{response}{bcolors.ENDC}")
            result = execute_spacy_command(command_str)
            print("RESULT:", result)
            messages.append({"role": "assistant", "content": f"Result of spaCy command: {result}"})
            messages_seen_by_assistant.append({"role": "assistant", "content": f"Result of spaCy command: {result}"})
            thinking = False
      elif response.startswith("EXECUTE NLTK:"):
        command_str = response[len("EXECUTE NLTK:"):].strip()
        if "EXECUTE SPACY:" not in command_str and "EXECUTE NLTK:" not in command_str:
            print(f"{bcolors.OKBLUE}{response}{bcolors.ENDC}")
            result = execute_nltk_command(command_str)
            print("RESULT:", result)
            messages.append({"role": "assistant", "content": f"Result of nltk command: {result}"})
            messages_seen_by_assistant.append({"role": "assistant", "content": f"Result of nltk command: {result}"})
            thinking = False
      
      if thinking:
        assistant = response
        if not response.startswith("THINKING:"):
          assistant = f"THINKING: {response}"
        print(f"""{bcolors.WARNING}{assistant}{bcolors.ENDC}""")
        user = "Continue."

        issued_reminder = False
        if "EXECUTE SPACY:" in assistant or "EXECUTE NLTK:" in assistant:
            user += " Remember if you are issuing a command it has to be the only text in your assistant. Do not apologize, just issue the command in next response. If you have more than one command, issue the first one next."
            issued_reminder = True

        if "Result of spaCY command:" in assistant or "Result of nltk command:" in assistant:
            temperature = 0.8
            parts = ["THINKING:"]
            command_message = ""
            for m in reversed(messages):
                if m['role'] == 'assistant' and ('EXECUTE SPACY:' in m['content'] or 'EXECUTE NLTK:' in m['content']):
                    command_message = m['content']
                    break
            user += f" Do not anticipate results. Reissue the command you gave in your last response '{command_message}'. Do not apologize, just issue the command in next response. If you have more than one command, issue the first one next."
            if "Result of spaCY command:" in assistant:
                parts.append("Result of spaCY command: <FAKE>")
            if "Result of nltk command:" in assistant:
                parts.append("Result of nltk command: <FAKE>")
            assistant = '\n'.join(parts)
            issued_reminder = True

        if "FINAL ANSWER:" in assistant:
            user = f"""Reissue the final answer you gave in last response '{assistant}'."""

        if not issued_reminder:
            user += """ Check all of the requirements given by user. If you are certain of the answer, do not apologize and just write the answer with "FINAL_ANSWER:" as the prefix in next response."""

        messages.append({"role": "assistant", "content": assistant})
        messages_seen_by_assistant.append({"role": "assistant", "content": assistant})
        messages.append({"role": "user", "content": user})
        messages_seen_by_assistant.append({"role": "user", "content": user})

      num_iterations += 1

    print("Assistant:", response)

