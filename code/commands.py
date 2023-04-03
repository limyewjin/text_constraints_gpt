import datetime
import json

import api
import commands_text
import memory as mem

task_completed = False

def get_command(response):
    try:
        response_json = json.loads(response)
        command = response_json["command"]
        command_name = command["name"]
        arguments = command["args"]

        if not arguments:
            arguments = {}

        return command_name, arguments
    except json.decoder.JSONDecodeError:
        return "Error:", "Invalid JSON"
    # All other errors, return "Error: + error message"
    except Exception as e:
        return "Error:", str(e)


def execute_command(command_name, arguments):
    try:
        if command_name == "memory_add":
            return commit_memory(arguments["string"])
        elif command_name == "memory_del":
            return delete_memory(arguments["key"])
        elif command_name == "memory_ovr":
            return overwrite_memory(arguments["key"], arguments["string"])
        elif command_name == "get_text_summary":
            return get_text_summary(arguments["text"])
        elif command_name == "tokenize":
            return commands_text.tokenize(arguments["text"])
        elif command_name == "count_words":
            return commands_text.count_words(arguments["text"])
        elif command_name == "count_characters":
            return commands_text.count_characters(arguments["text"])
        elif command_name == "get_datetime":
            return get_datetime()
        elif command_name == "task_complete":
            return task_complete(arguments["final_answer"])
        else:
            return f"Unknown command {command_name}"
    # All errors, return "Error: + error message"
    except Exception as e:
        return "Error: " + str(e)


def get_datetime():
    return "Current date and time: " + \
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_text_summary(text):
    summary = commands_text.summarize_text(text)
    return """ "Result" : """ + summary


def commit_memory(string):
    _text = f"""Committing memory with string "{string}" """
    mem.permanent_memory.append(string)
    return _text


def delete_memory(key):
    if key >= 0 and key < len(mem.permanent_memory):
        _text = "Deleting memory with key " + str(key)
        del mem.permanent_memory[key]
        print(_text)
        return _text
    else:
        print("Invalid key, cannot delete memory.")
        return None


def overwrite_memory(key, string):
    if key >= 0 and key < len(mem.permanent_memory):
        _text = "Overwriting memory with key " + \
            str(key) + " and string " + string
        mem.permanent_memory[key] = string
        print(_text)
        return _text
    else:
        print("Invalid key, cannot overwrite memory.")
        return None


def task_complete(final_answer):
    global task_completed
    print(f"FINAL ANSWER: {final_answer}")
    task_completed = True
    return "Task Completed!"
