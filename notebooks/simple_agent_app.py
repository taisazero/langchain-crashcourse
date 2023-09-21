from chainlit.config import config
import chainlit as cl
from langchain.memory import SimpleMemory, ConversationSummaryBufferMemory, CombinedMemory
from langchain.agents import AgentExecutor
from langchain.agents.initialize import initialize_agent
from langchain.agents import load_tools
from chainlit import on_message, on_chat_start
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentType

#TODO: load environment variables from your .env file
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

@cl.on_chat_start
async def start():
    # TODO: initialize LLM (we use ChatOpenAI because we'll later define a `chat` agent)
    # BEGIN Writing
    llm = ChatOpenAI(
        temperature= 0,
        model_name='gpt-3.5-turbo',
        max_tokens= 500,
    )
    #TODO: create a memory, load tools, and initialize an agent with the type `CHAT_CONVERSATIONAL_REACT_DESCRIPTION`
    # Tip: Set `return_messages` to `True` in the memory so that the agent returns the messages it generates
    conversational_memory = ConversationSummaryBufferMemory(
        llm=llm,
        input_key='input',
        memory_key='chat_history',
        max_token_limit=250,
        return_messages=True,
        human_prefix="User",
        ai_prefix="Assistant"
    )
    tools = load_tools(['llm-math', 'terminal', 'python_repl', 'serpapi'], llm=llm)
    # initialize agent
    # Hint: There is a parameter that allows you to set the maximum number of iterations, 
        # this is useful to limit the number of messages the agent generates and hence $ spent on OAI credits.
    # Hint: CHAT_CONVERSATIONAL_REACT_DESCRIPTION needs the memory to return its messages.
    # Hint: How could you enable the agent to adapt to parsing issues it encounters?
    agent = initialize_agent(
        llm=llm,
        memory=conversational_memory,
        tools=tools,
        verbose=True,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, 
        handle_parsing_errors=True,
        max_iterations=3,
    )
    # END Writing
    # create agentexecutor
    cl.user_session.set("agent", agent)

@cl.on_message
async def on_message(message):
    agent = cl.user_session.get("agent")
    response = await cl.make_async(agent.run)(
        input=message, callbacks=[cl.LangchainCallbackHandler()]
    )
    await cl.Message(content=response).send()
