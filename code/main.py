import colorama
import os
import json

import api
import chat
import commands
import memory as mem
import prompt_data


def print_to_console(
        title,
        title_color,
        content):
    print(f"{title_color}{title} {colorama.Style.RESET_ALL}{content}")


def print_assistant_thoughts(assistant_reply):
    try:
        # Parse and print Assistant response
        assistant_reply_json = json.loads(assistant_reply)

        assistant_thoughts = assistant_reply_json.get("thoughts")
        if assistant_thoughts:
            assistant_thoughts_text = assistant_thoughts.get("text")
            assistant_thoughts_reasoning = assistant_thoughts.get("reasoning")
            assistant_thoughts_plan = assistant_thoughts.get("plan")
            assistant_thoughts_criticism = assistant_thoughts.get("criticism")
            assistant_thoughts_speak = assistant_thoughts.get("speak")
        else:
            assistant_thoughts_text = None
            assistant_thoughts_reasoning = None
            assistant_thoughts_plan = None
            assistant_thoughts_criticism = None
            assistant_thoughts_speak = None

        print_to_console(
            f"THOUGHTS:",
            colorama.Fore.YELLOW,
            assistant_thoughts_text)
        print_to_console(
            "REASONING:",
            colorama.Fore.YELLOW,
            assistant_thoughts_reasoning)
        if assistant_thoughts_plan:
            print_to_console("PLAN:", colorama.Fore.YELLOW, "")
            # Split the input_string using the newline character and dash
            lines = assistant_thoughts_plan.split('\n')

            # Iterate through the lines and print each one with a bullet
            # point
            for line in lines:
                # Remove any "-" characters from the start of the line
                line = line.lstrip("- ")
                print_to_console("- ", colorama.Fore.GREEN, line.strip())
        print_to_console(
            "CRITICISM:",
            colorama.Fore.YELLOW,
            assistant_thoughts_criticism)
        print_to_console(
            "SPEAK:",
            colorama.Fore.YELLOW,
            assistant_thoughts_speak)
        print()

    except json.decoder.JSONDecodeError:
        print_to_console("Error: Invalid JSON\n", colorama.Fore.RED, assistant_reply)
    # All other errors, return "Error: + error message"
    except Exception as e:
        print_to_console("Error: \n", colorama.Fore.RED, str(e))


def construct_prompt():
    # Construct full prompt
    full_prompt = f"""You are an AI language model trained to understand and generate text based on user input. Your task is to generate responses that follow the constraints provided by the user. If the user specifies constraints on the text such as word count, character limits, or restrictions on punctuation, letters, or word order, incorporate those constraints into your response. Always try to provide a coherent and relevant answer to the user's question.

Your decisions must always be made independently without seeking user assistance. Play to your strengths as an LLM and pursue simple strategies.

To verify if your response meets the given constraints, use the provided commands. Remember to confirm that your final answer satisfies all requirements specified by the user."""
    prompt = prompt_data.load_prompt()
    full_prompt += f"\n\n{prompt}"
    return full_prompt

# initialize variables
prompt = construct_prompt()
full_message_history = []
token_limit = 6000
result = None

while True:
    user_input = input("User: ").strip()

    if user_input == "exit": break
      
    commands.task_completed = False
    num_iterations = 0
    while num_iterations < 50 and commands.task_completed == False:
        assistant_reply = chat.chat_with_ai(
                prompt,
                user_input,
                full_message_history,
                mem.permanent_memory,
                token_limit)
        print_assistant_thoughts(assistant_reply)

        # Get command name and arguments
        try:
            command_name, arguments = commands.get_command(assistant_reply)
        except Exception as e:
            print_to_console("Error: \n", colorama.Fore.RED, str(e))

        if command_name == "Error:" and arguments == "Invalid JSON":
            full_message_history.append(
                    chat.create_chat_message(
                        "system",
                        f"Invalid JSON response. Rewrite '{assistant_reply}' to be a valid JSON response."))
            print_to_console("SYSTEM: ", colorama.Fore.YELLOW, result)

            print()
            num_iterations += 1
            continue

        # Print command
        print_to_console(
            "NEXT ACTION: ",
            colorama.Fore.CYAN,
            f"COMMAND = {colorama.Fore.CYAN}{command_name}{colorama.Style.RESET_ALL}  ARGUMENTS = {colorama.Fore.CYAN}{arguments}{colorama.Style.RESET_ALL}")

        # Exectute command
        if command_name.lower() != "error":
            result = f"Command {command_name} returned: {commands.execute_command(command_name, arguments)}"
        else:
            result = f"Command {command_name} threw the following error: {arguments}"
        # Check if there's a result from the command append it to the message
        # history
        if result is not None:
            full_message_history.append(chat.create_chat_message("system", result))
            print_to_console("SYSTEM: ", colorama.Fore.YELLOW, result)
        else:
            full_message_history.append(
                chat.create_chat_message("system", "Unable to execute command"))
            print_to_console("SYSTEM: ", colorama.Fore.YELLOW, "Unable to execute command")

        print()
        num_iterations += 1
