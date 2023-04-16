from colorama import Fore, Style
import json
import os
import readline

import api
import chat
import commands
import memory as mem
import prompt_data


def print_to_console(
        title,
        title_color,
        content):
    print(f"{title_color}{title} {Style.RESET_ALL}{content}")


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
            Fore.YELLOW,
            assistant_thoughts_text)
        print_to_console(
            "REASONING:",
            Fore.YELLOW,
            assistant_thoughts_reasoning)
        if assistant_thoughts_plan:
            print_to_console("PLAN:", Fore.YELLOW, "")
            # Split the input_string using the newline character and dash
            lines = assistant_thoughts_plan.split('\n')

            # Iterate through the lines and print each one with a bullet
            # point
            for line in lines:
                # Remove any "-" characters from the start of the line
                line = line.lstrip("- ")
                print_to_console("- ", Fore.GREEN, line.strip())
        print_to_console(
            "CRITICISM:",
            Fore.YELLOW,
            assistant_thoughts_criticism)
        print_to_console(
            "SPEAK:",
            Fore.YELLOW,
            assistant_thoughts_speak)
        print()

    except json.decoder.JSONDecodeError:
        print_to_console("Error: Invalid JSON\n", Fore.RED, assistant_reply)
    # All other errors, return "Error: + error message"
    except Exception as e:
        print_to_console("Error: \n", Fore.RED, str(e))


def construct_prompt():
    # Construct full prompt
    full_prompt = f"""You are an AI trained to understand and generate text based on user input. Your task is be a helpful assistant to the user, answering questions and fulfilling tasks such as to generate responses that follow the constraints provided by the user. Always try to provide a coherent and relevant answer to the user's question.

If there is a task or requirement which you are not capable of performing precisely, write and use Python code to perform the task, such as counting characters, getting the current date/time, or finding day of a week for a specific date. Python code execution returns stdout and stderr only so **print any output needed** in Python code.

Your decisions must always be made independently without seeking user assistance. Play to your strengths as an LLM and pursue simple strategies.

Remember to confirm that your final answer satisfies ALL requirements specified by the user. Use provided and generated commands to confirm requirements before responding with the final answer."""
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
      
    chat.reset()
    commands.task_completed = False
    num_iterations = 0
    while num_iterations < 50 and commands.task_completed == False:
        assistant_reply = chat.chat_with_ai(
                prompt,
                user_input if num_iterations == 0 else '',
                mem.permanent_memory,
                mem.code_memory,
                token_limit, True)
        print_assistant_thoughts(assistant_reply)

        # Get command name and arguments
        command_name = ""
        try:
            command_name, arguments = commands.get_command(assistant_reply)
            command_name = command_name.strip()
        except Exception as e:
            notes = "Error encountered while trying to parse response: {e}."
            chat.create_chat_message("user", notes)
            print_to_console("Error: \n", Fore.RED, str(e))

        if len(command_name) == 0 or command_name == "GetCommandError":
            nudge = ""
            if len(command_name) == 0:
                nudge = "Empty command name found. Specify a valid command."

            if command_name == "GetCommandError":
                if arguments == "'command'":
                    nudge = '"command" not found in response. It cannot be empty.'
                elif arguments == "'name'":
                    nudge = '"command" does not contain "name" and it cannot be empty.'
                elif arguments == "'args'":
                    nudge = '"command" does not contain "args".'
                elif arguments == "Invalid JSON":
                    nudge = "Invalid JSON response."
                    if '"command"' not in assistant_reply and '"thoughts"' not in assistant_reply:
                        nudge += ' "command" and "thoughts" not found in response.'
                    elif '"command"' not in assistant_reply:
                        nudge += ' "command" not found in response.'
                    elif '"thoughts"' not in assistant_reply:
                        nudge += ' "thoughts" not found in response.'

                    if '"command"' in assistant_reply and '"thoughts"' in assistant_reply:
                        if assistant_reply.count('"command"') > 1 and assistant_reply.count('"thoughts"') > 1:
                            nudge += ' Multiple "command" and "thoughts" found. Return just one set.'
                        else:
                            nudge += ' Extranous text found in response that makes response invalid JSON. Remove extra text and just return JSON response.'

                nudge += " Next response should follow RESPONSE FORMAT."

            chat.create_chat_message("user", nudge)
            print_to_console("SYSTEM: ", Fore.YELLOW, f"{command_name} {arguments}")
            print()
            num_iterations += 1
            continue
    
        # Print command
        print_to_console(
            "NEXT ACTION: ",
            Fore.CYAN,
            f"COMMAND = {Fore.CYAN}{command_name}{Style.RESET_ALL}  ARGUMENTS = {Fore.CYAN}{arguments}{Style.RESET_ALL}")

        # Exectute command
        command_result = commands.execute_command(command_name, arguments)
        result = f"Command {command_name} returned: {command_result}"

        if result is not None:
            if command_result == f"Unknown command {command_name}":
                nudge = f"{result}. Specify only valid commands."
                chat.create_chat_message("system", nudge)
            else:
                chat.create_chat_message("system", result)
            if len(result) > 100:
                print_to_console("SYSTEM: ", Fore.YELLOW, result[:100] + "...")
            else:
                print_to_console("SYSTEM: ", Fore.YELLOW, result)
        else:
            chat.create_chat_message("system", "Unable to execute command")
            print_to_console("SYSTEM: ", Fore.YELLOW, "Unable to execute command")

        print()
        num_iterations += 1
