"""
An example module for a Python research software project.
"""

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

llama32_chat = ChatOllama(model="llama3.2", temperature=0)

# Create a message
msg = HumanMessage(content="Hello world", name="Dave")

# Message list
messages = [msg]

# Invoke the model with a list of messages 
result = llama32_chat.invoke(messages)

print(result)