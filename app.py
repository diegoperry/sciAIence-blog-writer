from crewai import Crew
from app_agents import AppAgents, StreamToExpander
from app_tasks import AppTasks
import streamlit as st
import datetime
import sys

st.set_page_config(page_icon="✈️", layout="wide")


def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


class MyCrew:

    def __init__(self, topic, complexity, interests):
        self.topic = topic
        self.complexity = complexity
        self.interests = interests
        self.output_placeholder = st.empty()

    def run(self):
        agents = AppAgents()  # Instantiate agents
        tasks = AppTasks()  # Instantiate tasks

        # Define the agents
        researcher_agent = agents.researcher_agent()
        writer_agent = agents.writer_agent()
        quality_agent = agents.quality_agent()

        # Define the tasks
        research_task = tasks.research_task(
            researcher_agent,
            self.topic,
            self.interests,
            self.complexity,
        )

        write_task = tasks.write_task(
            writer_agent,
            self.topic,
            self.interests,
            self.complexity,
        )

        check_task = tasks.check_task(
            quality_agent,
            self.topic,
            self.interests,
            self.complexity,
        )

        rewrite_task = tasks.rewrite_task(
            writer_agent,  # Use writer_agent for rewriting
            self.topic,
            self.interests,
            self.complexity,
        )

        # Define the crew with the agents and tasks
        crew = Crew(
            agents=[researcher_agent, writer_agent, quality_agent],
            tasks=[research_task, write_task, check_task, rewrite_task],
            verbose=True
        )

        # Kick off the crew process and get the result
        result = crew.kickoff()

        # Debugging: Print the result to inspect its structure
        print("DEBUG: Result Structure:", result)

        # Attempt to parse the result based on its structure
        try:
            # If result is a dictionary with 'tasks', access the output of the last task
            if isinstance(result, dict) and 'tasks' in result:
                final_output = result['tasks'][-1]['output']
            # If result is a list, access the output of the last element
            elif isinstance(result, list):
                final_output = result[-1]['output']
            # If result is a string, use it directly
            elif isinstance(result, str):
                final_output = result
            else:
                final_output = "Unexpected result format"
        except Exception as e:
            print("DEBUG: Error accessing final output:", e)
            final_output = "Error processing the result"

        # Display the final output
        self.output_placeholder.markdown(final_output)
        return final_output


if __name__ == "__main__":
    st.header("⚛️ SciAIence Blog Writer")

    st.subheader("🤖 Let a team of specialized AI agents research and write your scientific blog!",
                 divider="rainbow", anchor=False)



    with st.sidebar:
        st.header("👇 Enter your blog details")
        with st.form("my_form"):
            topic = st.text_area(
                "What is the topic of your scientific blog?", placeholder="How String Theory Proposes Multiple Dimensions Beyond Our Perception.")
            complexity = st.text_input(
                "What level of complexity do you want your blog post to be?", placeholder="Simple, easy to understand")

            interests = st.text_area("What discoveries, scientists or experiments do you want to highlight?",
                                     placeholder="The role of the Large Hadron Collider in providing evidence for string theory's predictions.")

            submitted = st.form_submit_button("Submit")

        st.divider()

        st.sidebar.info("Built with CrewAI and Streamlit by Diego Perry", icon="🔭")

if submitted:
    with st.status("🤖 **Agents at work...**", state="running", expanded=True) as status:
        with st.container(height=500, border=False):
            sys.stdout = StreamToExpander(st)
            MyCrew = MyCrew(topic, complexity, interests)
            result = MyCrew.run()
        status.update(label="✅ Blog Ready!",
                      state="complete", expanded=False)

    st.subheader("Here is your blog", anchor=False, divider="rainbow")
    st.markdown(result)