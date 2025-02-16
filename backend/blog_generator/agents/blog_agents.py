# backend/blog_generator/agents/blog_agents.py

from crewai import Agent, Task, Crew
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import BaseTool
from bs4 import BeautifulSoup
import requests
from typing import Optional, List, Dict, Any, Union, Type
from pydantic import BaseModel, Field
import json
import graphviz
from io import BytesIO
import base64
from langchain.tools import Tool

# Input models for tools
class SearchInput(BaseModel):
    """Input for search tool"""
    query: str = Field(description="The search query to run")

class ScraperInput(BaseModel):
    """Input for scraper tool"""
    url: str = Field(description="The URL to scrape")

class DiagramInput(BaseModel):
    """Input for diagram tool"""
    content_type: str = Field(description="Type of diagram to generate")
    description: str = Field(description="Description of the diagram")

# Tool implementations
class WebSearchTool(BaseTool):
    name: str = "Web Search"
    description: str = "Search for content across the internet"
    args_schema: Type[BaseModel] = SearchInput
    search_engine: DuckDuckGoSearchRun = Field(default_factory=DuckDuckGoSearchRun)

    def __init__(self, **data):
        super().__init__(**data)
        self.search_engine = DuckDuckGoSearchRun()

    def _run(self, query: str) -> str:
        """Run web search with proper error handling"""
        try:
            return self.search_engine.run(query)
        except Exception as e:
            return f"Error performing search: {str(e)}"

class WebScraperTool(BaseTool):
    name: str = "Web Scraper"
    description: str = "Scrape content from websites"
    args_schema: Type[BaseModel] = ScraperInput

    def __init__(self, **data):
        super().__init__(**data)

    def _run(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for script in soup(["script", "style"]):
                script.decompose()
                
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:5000]
        except Exception as e:
            return f"Error scraping {url}: {str(e)}"

class DiagramGenerator(BaseTool):
    name: str = "Diagram Generator"
    description: str = "Generate technical diagrams in Mermaid format"
    args_schema: Type[BaseModel] = DiagramInput

    def __init__(self, **data):
        super().__init__(**data)

    def _run(self, content_type: str, description: str = "System diagram") -> Dict[str, str]:
        """Run the diagram generator with parameters"""
        return self.create_diagram(content_type, description)

    @staticmethod
    def create_diagram(diagram_type: str, description: str) -> Dict[str, str]:
        """Generate diagram and return structured output"""
        try:
            if diagram_type.lower() in ["diagram", "architecture"]:
                diagram = """graph TB
                    Client[Client] --> LB[Load Balancer]
                    subgraph Backend
                        LB --> API1[API Server 1]
                        LB --> API2[API Server 2]
                        API1 --> DB[(Database)]
                        API2 --> DB
                        API1 --> Cache[(Cache)]
                        API2 --> Cache
                    end"""
            
            elif diagram_type.lower() == "flowchart":
                diagram = """graph TD
                    A[Start] --> B[Process]
                    B --> C{Decision}
                    C -->|Yes| D[Action 1]
                    C -->|No| E[Action 2]
                    D --> F[End]
                    E --> F"""
            
            elif diagram_type.lower() == "sequence":
                diagram = """sequenceDiagram
                    participant U as User
                    participant S as System
                    participant DB as Database
                    U->>S: Request Data
                    S->>DB: Query
                    DB-->>S: Results
                    S-->>U: Response"""
            
            elif diagram_type.lower() == "retnet":
                diagram = """graph TB
                    subgraph RetNet Architecture
                        Input[Input] --> Embed[Embedding Layer]
                        Embed --> RetUnit[Retention Unit]
                        RetUnit --> MultiHead[Multi-Head Attention]
                        MultiHead --> FFN[Feed Forward Network]
                        FFN --> Out[Output Layer]
                    end
                    subgraph Retention Unit
                        State[State] --> Update[Update]
                        Update --> Decay[Decay]
                        Decay --> NewState[New State]
                    end"""
            
            else:
                raise ValueError(f"Unsupported diagram type: {diagram_type}")

            return {
                'markdown': f"```mermaid\n{diagram}\n```",
                'description': description,
                'placement': 'To be determined based on content flow'
            }
            
        except Exception as e:
            return {
                'error': f"Error generating diagram: {str(e)}",
                'markdown': None,
                'description': description
            }

# Main Blog Crew Agent
class BlogCrewAgent:
    """Agent for generating blog content using CrewAI"""
    
    def __init__(self):
        self.tools = self.create_tools()
        
    def create_tools(self):
        """Create and initialize all required tools"""
        search_tool = WebSearchTool()
        scraper_tool = WebScraperTool()
        diagram_tool = DiagramGenerator()
        
        # Convert tools to CrewAI format
        return [
            Tool(
                name="Web Search",
                func=search_tool._run,
                description="Search for content across the internet"
            ),
            Tool(
                name="Web Scraper",
                func=scraper_tool._run,
                description="Scrape content from websites"
            ),
            Tool(
                name="Diagram Generator",
                func=diagram_tool._run,
                description="Generate technical diagrams in Mermaid format"
            )
        ]

    def create_agents(self, tools):
        """Create all required agents with proper tools"""
        researcher = Agent(
            role='Research Specialist',
            goal='Gather comprehensive information and identify topics needing visual aids',
            backstory="""Expert researcher skilled at finding information and identifying 
            where visuals would enhance understanding.""",
            tools=tools,
            verbose=True
        )

        image_curator = Agent(
            role='Image Curator',
            goal='Find and create appropriate visuals with proper metadata',
            backstory="""Visual content specialist who excels at finding relevant images 
            and creating technical diagrams. Ensures proper attribution and formatting.""",
            tools=tools,
            verbose=True
        )

        organizer = Agent(
            role='Content Organizer',
            goal='Organize research and visual content into a coherent structure',
            backstory="""Content strategist who excels at organizing information and 
            integrating visuals effectively.""",
            tools=tools,
            verbose=True
        )

        writer = Agent(
            role='Content Writer',
            goal='Create engaging blog content with properly integrated visuals',
            backstory="""Professional writer skilled at creating content that seamlessly 
            integrates text and visuals. Expert in markdown formatting.""",
            tools=tools,
            verbose=True
        )

        return [researcher, image_curator, organizer, writer]

    def create_tasks(self, agents, title: str, prompts: str):
        """Create all required tasks with proper agents"""
        return [
            Task(
                description=f"""Research {title} and identify key points needing visuals.
                Consider these aspects: {prompts}
                Create a list of topics where images or diagrams would be valuable.""",
                agent=agents[0],  # researcher
                expected_output="""A detailed research report containing:
                1. Key findings about the topic
                2. List of points that need visual representation
                3. Suggested types of visuals (images/diagrams)
                4. Relevant sources and references"""
            ),
            Task(
                description="""Find or generate appropriate visuals for identified topics.
                - For technical topics, create diagrams in Markdown format (MermaidJS).
                - Ensure all images include proper attribution information.
                - Recommend placement based on context in the blog.""",
                agent=agents[1],  # image_curator
                expected_output="""A structured JSON output including:
                {
                    "images": [
                        {
                            "type": "external" | "generated" | "diagram",
                            "markdown": "Generated diagram or image markdown",
                            "description": "Description of the visual",
                            "placement": "Section reference"
                        }
                    ]
                }"""
            ),
            Task(
                description="""Create a content outline integrating research and visuals.
                Use the structured image data to properly place visuals within the content.""",
                agent=agents[2],  # organizer
                expected_output="""A structured blog outline containing:
                1. Main sections and subsections
                2. Key points for each section
                3. Integrated visual placements
                4. Flow and transition notes"""
            ),
            Task(
                description="""Write the blog post in markdown format.
                Use the structured image and diagram data to properly integrate visuals.""",
                agent=agents[3],  # writer
                expected_output="""A complete blog post in markdown format including:
                1. Engaging title and introduction
                2. Well-structured content
                3. Properly integrated visuals
                4. Complete image credits section"""
            )
        ]

    def generate_blog(self, title: str, prompts: str) -> str:
        """Generate a blog post with the given title and prompts"""
        try:
            # Create agents with tools
            agents = self.create_agents(self.tools)
            
            # Create tasks
            tasks = self.create_tasks(agents, title, prompts)
            
            # Create and run crew
            crew = Crew(
                agents=agents,
                tasks=tasks,
                verbose=True
            )

            result = crew.kickoff()
            final_content = str(result)
            
            # Ensure image credits section exists
            if "## Image Credits" not in final_content:
                final_content = f"{final_content}\n\n## Image Credits\n"
            
            return final_content
            
        except Exception as e:
            raise Exception(f"Error in blog generation: {str(e)}")

# Test function
def test_tools():
    agent = BlogCrewAgent()
    tools = agent.create_tools()
    
    print("Testing Web Search...")
    search_tool = next(tool for tool in tools if isinstance(tool, WebSearchTool))
    result = search_tool._run("artificial intelligence latest developments")
    print(result[:200])
    
    print("\nTesting Diagram Generation...")
    diagram_tool = next(tool for tool in tools if isinstance(tool, DiagramGenerator))
    result = diagram_tool._run("architecture", "System Architecture")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_tools()