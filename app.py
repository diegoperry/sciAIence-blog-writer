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
        agents = AppAgents()
        tasks = AppTasks()

        researcher_agent = agents.researcher_agent()
        writer_agent = agents.writer_agent()
        quality_agent = agents.quality_agent()

        research_task = tasks.research_task(
            researcher_agent,
            self.topic,
            self.complexity,
            self.interests,
        )

        write_task = tasks.write_task(
            writer_agent,
            self.topic,
            self.complexity,
            self.interests,
        )

        check_task = tasks.check_task(
            quality_agent,
            self.topic,
            self.complexity,
            self.interests,
        )

        rewrite_task = tasks.rewrite_task(
            quality_agent,
            self.topic,
            self.complexity,
            self.interests,
        )

        crew = Crew(
            agents=[
                researcher_agent, writer_agent, quality_agent
            ],
            tasks=[research_task, write_task, check_task,rewrite_task],
            verbose=True

        )

        result = crew.kickoff()
        self.output_placeholder.markdown(result)

        return result


if __name__ == "__main__":
    st.header("⚛️ SciAIence Blog Writer")

    st.subheader("🤖 Let a team of specialized AI agents research and write your scientific blog!",
                 divider="rainbow", anchor=False)

    import datetime

    today = datetime.datetime.now().date()
    next_year = today.year + 1
    jan_16_next_year = datetime.date(next_year, 1, 10)

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