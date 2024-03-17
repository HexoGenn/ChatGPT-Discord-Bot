from openai import OpenAI

client = OpenAI()

default_gpt_info = {

  #optional
  "model": "gpt-3.5-turbo-1106",
  "temperature": 1,
  "frequency_penalty": 0.6,
  "presence_penalty": 0.6,
  "max_length": 256,

  #required
  "messages": None
  
}

def get_response(gpt_info, debug_info):
  try:

    gpt_info = {**default_gpt_info, **gpt_info}

    response = client.chat.completions.create(model=gpt_info["model"],temperature=gpt_info["temperature"],messages=gpt_info["messages"],frequency_penalty=gpt_info["frequency_penalty"],presence_penalty=gpt_info["presence_penalty"])

    # Rest of the code remains the same
    input_tokens, output_tokens = response.usage.prompt_tokens, response.usage.completion_tokens
    input_cost = input_tokens * 0.001 / 1000
    output_cost = output_tokens * 0.002 / 1000
    gpt4_input_cost = input_tokens * 0.03 / 1000
    gpt4_output_cost = output_tokens * 0.06 / 1000
    total_cost = input_cost + output_cost
    print("\nResponse: " + response.choices[0].message.content)
    print("Reply Chain: " + debug_info["reply_amt"] + " Msgs")
    print(f"Cost: ${total_cost:.6f} ({output_tokens+input_tokens} Tokens)")
    print(f"1K Msgs Cost: ${total_cost*1000:.6f}")
    print(f"GPT-4 Would Cost: ${gpt4_input_cost+gpt4_output_cost:.6f}",end="\n\n")

    return response.choices[0].message.content
  except Exception as e:
    print(f"An error occurred: {e}")
    return "sorry your request can't be processed\nyour problem 🦅"
