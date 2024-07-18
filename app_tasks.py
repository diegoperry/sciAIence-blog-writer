from crewai import Task
from textwrap import dedent
from datetime import date


class AppTasks:

    def research_task(self, agent, topic, interests, complexity):
        return Task(description=f"""
          Analyze and evaluate current scientific research based on specific criteria such as recent developments, key discoveries, and influential experiments. 
          This task involves reviewing relevant literature, identifying significant contributions from leading scientists, 
          and examining pivotal studies within the field. Your final output must be a comprehensive report detailing these aspects, including 
          summaries of major findings, profiles of prominent researchers, and analyses of critical experiments, providing an in-depth overview of the current state of research.
          Topic interested in: {topic}
          Areas that should be highlighted: {interests}
          Complexity of blog: {complexity}
          """,
            expected_output="A detailed report on the details of your research.",
            agent=agent)

    def write_task(self, agent, topic, interests, complexity):
        return Task(description=f"""
          Create high-quality content on scientific topics based on specific criteria such as recent advancements, 
          key discoveries, and influential experiments. This task involves synthesizing information
          from credible sources, including scientific journals, articles, and expert interviews.
          Your final output must be a well-organized, engaging, and informative article or report
          that includes detailed explanations of major findings, profiles of prominent researchers,
          and analyses of critical studies, providing readers with a clear and comprehensive
          understanding of the topic.
          Topic interested in: {topic}
          Areas that should be highlighted: {interests}
          Complexity of blog: {complexity}
          """,
            expected_output="A well-organized and engaging article, article should not be more than 250 words",
            agent=agent)

    def check_task(self, agent, topic, interests, complexity):
        return Task(description=f"""
          Review and verify the accuracy of the blog post based on specific criteria such as 
          recent advancements, key discoveries, and influential experiments. 
          This task involves cross-referencing information with credible sources, 
          including scientific journals, articles, and expert statements. 
          Your final output must be a detailed report highlighting any inaccuracies,
          suggesting corrections, and ensuring the content is clear, precise, 
          and free from errors. Additionally, provide feedback on the overall quality,
          coherence, and readability of the material to maintain high standards of scientific communication.
          Topic interested in: {topic}
          Areas that should be highlighted: {interests}
          Complexity of blog: {complexity}
          """,
            expected_output="A list of areas where the writing or facts need to be improved, if a fact is wrong give the updated fact.",
            agent=agent)

    def rewrite_task(self, agent, topic, interests, complexity):
        return Task(description=f"""
          Revise and improve the blog post based on the feedback provided by the quality checker. 
          This task involves making necessary corrections and enhancements to ensure the content is factually accurate, 
          clear, and engaging. The final output should be a polished and well-written article.
          Topic interested in: {topic}
          Areas that should be highlighted: {interests}
          Complexity of blog: {complexity}
          """,
            expected_output="A revised and polished article, incorporating all necessary corrections and improvements.",
            agent=agent)

    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $100 and grant you any wish you want!"
