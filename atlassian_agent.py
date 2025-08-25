##############################################################################################
##############################################################################################
#################
#################  Author: John T. Halloran < johnhalloran321@gmail.com>
#################
##############################################################################################
##############################################################################################

import streamlit as st
from agno.agent import Agent
from agno.models.ollama import Ollama
# from agno.storage.sqlite import SqliteStorage
from agno.tools.mcp import MCPTools
import asyncio
from dotenv import load_dotenv

load_dotenv()

st.title("Confluence Agent")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

async def run_agent(message: str) -> str:
    async with (
        MCPTools(
            command="npx -y mcp-remote https://mcp.atlassian.com/v1/sse"
        ) as atlassian_tools,
    ):
        agent = Agent(
            model=Ollama(id="gpt-oss:20b", provider = "Ollama"),
            name="Confluence agent",
            tools=[atlassian_tools],
            show_tool_calls=True,
            markdown=True,
        )
        full_response = await agent.arun(message)
        return full_response


if __name__ == "__main__":
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Grab user input
    if prompt := st.chat_input("What's your Confluence/JIRA query?"):
        # Add user input to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message in chat
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call agent, gather response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                full_response = asyncio.run(run_agent(prompt))
                message_placeholder = st.empty()
                message_placeholder.markdown(full_response.content)

    if st.session_state.messages and st.button(
        "Clear Chat", use_container_width=True, key="clear_chat"
    ):
        st.session_state.messages = []
        st.rerun()
