import os
import time
from dotenv import load_dotenv

import api


def create_chat_message(role, content):
    """
    Create a chat message with the given role and content.
    Args:
    role (str): The role of the message sender, e.g., "system", "user", or "assistant".
    content (str): The content of the message.
    Returns:
    dict: A dictionary containing the role and content of the message.
    """
    return {"role": role, "content": content}


def optimize_messages(messages):
    condensed_messages = []

    combined_messages = " ".join([f"{msg['role']}:{msg['content']}" for msg in messages])

    # Summarize user and assistant messages together
    summary = api.generate_response([
        {"role": "system", "content": f"""You are an AI language model trained to understand and generate text based on user input. Your task now is to optimize the conversation by summarizing and condensing the messages received so far, while maintaining the context and crucial information. The original system message is passed to you for context, do not repeat it. Based on your understanding of the conversation, provide a summary message from 'user' role that allows the GPT model to effectively solve the problem."""},
        {"role": "assistant", "content": combined_messages},
        {"role": "user", "content": "Summarize the following conversation while maintaining its structure."}],
        model="gpt-4")

    # Split the summary into separate messages based on their roles
    for message in summary.split("\n"):
        if message.startswith("User:") or message.startswith("user:"):
            condensed_messages.append({"role": "user", "content": message[5:].strip()})
        elif message.startswith("Assistant:") or message.startswith("assistant:"):
            condensed_messages.append({"role": "assistant", "content": message[10:].strip()})

    return condensed_messages


def chat_with_ai(
        prompt,
        user_input,
        full_message_history,
        permanent_memory,
        token_limit,
        debug=False):
    while True:
        current_context = [
                create_chat_message("system", prompt),
                create_chat_message("system", f"Permanent memory: {permanent_memory}")]

        num_current_context_tokens = sum(len(msg["content"].split()) for msg in current_context) + len(prompt.split())
        num_full_message_history_tokens = sum(len(msg["content"].split()) for msg in full_message_history)

        if num_current_context_tokens + num_full_message_history_tokens > token_limit / 2:
            # Optimize the messages using the `optimize_messages` function
            condensed_messages = optimize_messages(full_message_history[:-2])
            current_context.extend(condensed_messages + full_message_history[-2:])
        else:
            current_context.extend(full_message_history)

        current_context.extend([create_chat_message("user", user_input)])

        # Debug print the current context
        if debug:
            print("------------ CONTEXT SENT TO AI ---------------")
            for message in current_context:
                # Skip printing the prompt
                if message["role"] == "system" and message["content"] == prompt:
                    continue
                print(f"{message['role'].capitalize()}: {message['content']}")
            print("----------- END OF CONTEXT ----------------")

        assistant_reply = api.generate_response(current_context, model="gpt-4")

        # Update full message history
        full_message_history.append(
                create_chat_message("user", user_input))
        full_message_history.append(
                create_chat_message("assistant", assistant_reply))
        return assistant_reply
