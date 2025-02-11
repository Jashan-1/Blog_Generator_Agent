# backend/blog_generator/agents/blog_agents.py

from crewai import Agent, Task, Crew
from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from bs4 import BeautifulSoup
import requests
from typing import Optional

class WebSearchTool:
    def __init__(self):
        self.search = DuckDuckGoSearchRun()

    def _run(self, query: str) -> str:
        return self.search.run(query)

class WebScraperTool:
    def _run(self, url: str) -> str:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            return text[:5000]  # Limit text length
        except Exception as e:
            return f"Error scraping {url}: {str(e)}"

class BlogCrewAgent:
    def __init__(self):
        self.search_tool = WebSearchTool()
        self.scraper_tool = WebScraperTool()

    def create_tools(self):
        return [
            Tool(
                name="Web Search",
                func=self.search_tool._run,
                description="Search for content across the internet using DuckDuckGo"
            ),
            Tool(
                name="Web Scraper",
                func=self.scraper_tool._run,
                description="Scrape content from websites"
            )
        ]

    def generate_blog(self, title: str, prompts: str) -> dict:
        # Create research agent
        researcher = Agent(
            role='Research Specialist',
            goal='Gather comprehensive information about the topic from multiple sources',
            backstory="""Expert researcher with years of experience in gathering and analyzing 
            information from various sources. Skilled at finding relevant and credible information.""",
            tools=self.create_tools(),
            verbose=True
        )

        # Create content organizer agent
        organizer = Agent(
            role='Content Organizer',
            goal='Organize research findings into a coherent structure',
            backstory="""Experienced content strategist who excels at organizing information 
            into clear, logical structures. Expert at creating content outlines.""",
            tools=self.create_tools(),
            verbose=True
        )

        # Create writer agent
        writer = Agent(
            role='Content Writer',
            goal='Create engaging and informative blog content in markdown format',
            backstory="""Professional blog writer with expertise in creating well-structured, 
            engaging content. Skilled at writing in markdown format and maintaining consistency.""",
            tools=self.create_tools(),
            verbose=True
        )

        # Create editor agent
        editor = Agent(
            role='Content Editor',
            goal='Polish and refine the blog content',
            backstory="""Experienced editor with attention to detail. Expert at improving 
            content clarity, flow, and ensuring proper markdown formatting.""",
            tools=self.create_tools(),
            verbose=True
        )

        # Create tasks with expected outputs
        research_task = Task(
            description=f"""Research thoroughly about {title}. 
            Consider these aspects: {prompts}
            Find relevant articles, studies, and expert opinions.
            Use the search tools to gather comprehensive information.""",
            agent=researcher,
            expected_output="""A comprehensive research summary including:
            - Key findings from multiple sources
            - Relevant statistics and data
            - Expert opinions and quotes
            - Current trends and developments"""
        )

        organize_task = Task(
            description="""Create a structured outline based on the research findings.
            Organize information logically and ensure good flow between sections.
            Prioritize the most relevant and engaging content.""",
            agent=organizer,
            expected_output="""A detailed blog outline including:
            - Main sections with headings
            - Key points for each section
            - Supporting information and examples
            - Logical flow and progression"""
        )

        writing_task = Task(
            description="""Write a comprehensive blog post in markdown format using the outline.
            Include proper headings, lists, and emphasis where appropriate.
            Add relevant quotes and citations from the research.
            Ensure the content is engaging and informative.""",
            agent=writer,
            expected_output="""A complete blog post in markdown format with:
            - Clear headings and subheadings
            - Well-structured paragraphs
            - Proper formatting (bold, italic, lists)
            - Citations and references
            - Engaging introduction and conclusion"""
        )

        editing_task = Task(
            description="""Review and polish the blog post.
            Ensure proper markdown formatting.
            Check for clarity, consistency, and flow.
            Verify all citations and references.
            Add meta description and tags if needed.""",
            agent=editor,
            expected_output="""A polished final draft with:
            - Corrected grammar and spelling
            - Consistent formatting
            - Improved flow and readability
            - Verified citations and links
            - SEO-friendly meta content"""
        )

        # Create and run crew
        crew = Crew(
            agents=[researcher, organizer, writer, editor],
            tasks=[research_task, organize_task, writing_task, editing_task],
            verbose=True
        )

        result = crew.kickoff()
        return result