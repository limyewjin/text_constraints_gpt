import api
import os
from dotenv import load_dotenv

messages = [
    {"role": "system",
     "content": """You are an AI language model trained to understand and generate text based on user input. Your task is to generate responses that follow the constraints provided by the user. If the user specifies constraints on the text such as word count, character limits, or restrictions on punctuation, letters, or word order, incorporate those constraints into your response. Always try to provide a coherent and relevant answer to the user's question. If you are confident that your response meets the given constraints, prepend 'FINAL ANSWER:' to your response. Otherwise, the conversation will continue, and you will be asked to revise your response."""},
    ]

while True:
    user_input = input("User: ").strip()

    if user_input == "exit": break
      
    messages.append({"role": "user", "content": f"{user_input}"})
    num_iterations = 0
    while num_iterations < 5:
      response = api.generate_response(messages)
      if response.startswith("FINAL ANSWER:"):
        return response_text[len("FINAL ANSWER:"):].strip()

      # Add the assistant's response to the conversation and ask for a revision
      messages.append({"role": "assistant", "content": response_text})
      messages.append({"role": "user", "content": "Please revise your response based on the constraints."})
    print("Assistant:", response)

