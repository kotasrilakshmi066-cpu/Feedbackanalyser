from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, AgentType
from tools import classify_feedback_by_theme, get_sentiment_score

llm = Ollama(model="llama3")

tools = [
    classify_feedback_by_theme,
    get_sentiment_score
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)