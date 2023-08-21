"""here we define our agent class and their actions with tools
"""

from app.agents.tools import Tools
from langchain.agents import AgentType
from langchain.agents import AgentExecutor # will be used for custom agents
from langchain.agents import initialize_agent
from langchain.callbacks.base import BaseCallbackHandler
from typing import Dict, Union, Any, List
from langchain.schema import AgentAction
import streamlit as st
import time


class MyCustomHandlerOne(BaseCallbackHandler):
    
    def __init__(self):
        self.flag=True
    
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        # DUMMY OUTPUT for demo
        print(f"on_llm_start {serialized['name']}")


    def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        print(f"on_new_token {token}")

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when LLM errors."""

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> Any:
        print(f"on_chain_start {serialized['name']}")

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        print(f"on_tool_start {serialized['name']}")
        st.write(f"Identified tool {serialized['name']}")

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        print(f"on_agent_action {action}")

class ActionAgent():
		
    def __init__(self,llm):
        self.llm = llm
        self.agent = self.create_agent()

    def create_agent(self):    
        """
        Returns: AgentExecutor 
        
        AgnetType-> Zero-shot means the agent functions on the current action only — it has no memory.
                    ReAcT - Reasoning and Action steps, that LLM could cycle through
                    Enabling a multi-step process for identifying answers.
        """
        agent_executor = initialize_agent(self.fetch_tools(), self.llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,max_iterations=3)
        return agent_executor

    def fetch_tools(self):
        self.tools= Tools(self.llm).list_tools()
        return self.tools

    def run(self, input):
        handler1 = MyCustomHandlerOne()
        #return self.agent.run(input=input,callbacks=[handler1])
        return self.agent.run(input=input)