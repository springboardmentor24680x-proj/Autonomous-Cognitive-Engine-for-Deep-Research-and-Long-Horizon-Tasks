import streamlit as st
from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.models.groq import Groq

# -----------------------
# Streamlit App Setup
# -----------------------
st.title("AI Startup Trend Analysis Agent 📈")
st.caption(
    "Get the latest trend analysis and startup opportunities based on your topic of interest in a click!"
)

topic = st.text_input("Enter the area of interest for your Startup:")
groq_api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

if st.button("Generate Analysis"):
    if not groq_api_key:
        st.warning("Please enter your Groq API key.")
    elif not topic.strip():
        st.warning("Please enter a topic of interest.")
    else:
        with st.spinner("Processing your request..."):
            try:
                # -----------------------
                # Initialize Groq WITH model
                # -----------------------
                # Initialize Groq (NO model argument)
                groq_model = Groq(api_key=groq_api_key)
 

                # -----------------------
                # Agent 1: News Collector
                # -----------------------
                news_collector = Agent(
                    name="News Collector",
                    role="Collects recent news articles on the given topic",
                    tools=[DuckDuckGoTools()],
                    model=groq_model,
                    instructions=["Gather latest articles on the topic"],
                    markdown=True,
                )

                # -----------------------
                # Agent 2: Summary Writer
                # -----------------------
                summary_writer = Agent(
                    name="Summary Writer",
                    role="Summarizes collected news articles",
                    tools=[Newspaper4kTools(
                        enable_read_article=True,
                        include_summary=True
                    )],
                    model=groq_model,
                    instructions=["Provide concise summaries of the articles"],
                    markdown=True,
                )

                # -----------------------
                # Agent 3: Trend Analyzer
                # -----------------------
                trend_analyzer = Agent(
                    name="Trend Analyzer",
                    role="Analyzes trends from summaries",
                    model=groq_model,
                    instructions=[
                        "Identify emerging trends, market gaps, and startup opportunities"
                    ],
                    markdown=True,
                )

                # -----------------------
                # Execute workflow
                # -----------------------
                news_response: RunOutput = news_collector.run(
                    f"Collect recent news on {topic}"
                )
                articles = news_response.content

                summary_response: RunOutput = summary_writer.run(
                    f"Summarize the following articles:\n{articles}"
                )
                summaries = summary_response.content

                trend_response: RunOutput = trend_analyzer.run(
                    f"Analyze trends from the following summaries:\n{summaries}"
                )
                analysis = trend_response.content

                # -----------------------
                # Display results
                # -----------------------
                st.subheader("Trend Analysis and Potential Startup Opportunities")
                st.write(analysis)

            except Exception as e:
                st.error(f"An error occurred: {e}")

else:
    st.info("Enter the topic and API key, then click 'Generate Analysis'.")
