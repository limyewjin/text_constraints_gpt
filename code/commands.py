import datetime
import dateparser
import http.client
import json
import os

from dotenv import load_dotenv
load_dotenv()

import api
import code
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
        return "GetCommandError", "Invalid JSON"
    # All other errors, return "Error: + error message"
    except Exception as e:
        return "GetCommandError", str(e)


def execute_command(command_name, arguments):
    try:
        if command_name == "memory_add":
            return commit_memory(arguments["string"])
        elif command_name == "memory_del":
            return delete_memory(arguments["key"])
        elif command_name == "memory_ovr":
            return overwrite_memory(arguments["key"], arguments["string"])
        elif command_name == "code_add":
            return add_code(arguments["key"], arguments["description"], arguments["args"], arguments["code"])
        elif command_name == "code_execute":
            return execute_code(arguments["key"], arguments["args"])
        elif command_name == "search":
            return search_serper(arguments["query"])
        elif command_name == "browse_website":
            return browse_website(arguments["url"])
        elif command_name == "scrape":
            return scrape(arguments["url"])
        elif command_name == "website_summary":
            return website_summary(arguments["url"])
        elif command_name == "get_text_summary":
            return get_text_summary(arguments["text"], arguments["hint"])
        elif command_name == "get_calendar":
            return get_calendar(arguments["user"])
        elif command_name == "get_dow":
            return get_dow(arguments["date"])
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


def add_code(key, description, args, code_str):
    if not isinstance(args, dict):
        return f"args: {args_str} is not a python dict"

    present = key in mem.code_memory
    mem.code_memory[key] = {
            'description': description,
            'args': args,
            'code': code_str}
    return f"Overwritten code {key}" if present else f'Added code {key}'


def execute_code(key, args):
    if key not in mem.code_memory:
        return f"{key} not found in code memory."

    if not isinstance(args, dict):
        return f"args: {args_str} is not a python dict"

    code_item = mem.code_memory[key]

    vars = args
    vars["args"] = args
    return code.execute_python_code(code_item["code"], vars)


def get_calendar(user):
    return """[
    {
        "event": "vacation",
        "datestart": "04-20-23",
        "dateend": "04-21-23"
    },
    {
        "event": "flight to Denver",
        "datestart": "04-18-23",
        "dateend": "04-18-23"
    },
    {
        "event": "flight to NYC",
        "datestart": "04-27-23",
        "dateend": "04-28-23",
    },
    {
        "event": "vacation",
        "datestart": "05-01-23",
        "dateend": "05-03-23",
    }
]"""

def get_dow(date_string):
    date_object = dateparser.parse(date_string)
    day_of_week = date_object.strftime("%A")
    return day_of_week

def search_serper(query, api_key=os.environ["SERPER_API_KEY"]):
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
      "q": query
    })
    headers = {
      'X-API-KEY': api_key,
      'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")


def scrape(url):
    return commands_text.scrape(url)

def browse_website(url):
    summary = website_summary(url)
    links = get_hyperlinks(url)

    # Limit links to 5
    if len(links) > 5:
        links = links[:5]

    result = f"""Website Content Summary: {summary}\n\nLinks: {links}"""

    return result


def get_hyperlinks(url):
    link_list = commands_text.scrape_links(url)
    return link_list


def website_summary(url):
    text = commands_text.scrape_text(url)
    summary = commands_text.summarize_text(text, "details about the content and not about the site or business")
    return """ "Result" : """ + summary


def get_datetime():
    return "Current date and time: " + \
        datetime.datetime.now().strftime("%Y-%m-%d %A %H:%M:%S")


def get_text_summary(text, hint=None):
    summary = commands_text.summarize_text(text, hint, is_website=False)
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
