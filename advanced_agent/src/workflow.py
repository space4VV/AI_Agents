import logging
from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from src.firecrawl import FirecrawlService
from src.models import CompanyAnalysis, CompanyInfo, ResearchState
from src.prompts import DeveloperToolsPrompts

logger = logging.getLogger(__name__)


class ResearchWorkflow:
    """
    Workflow for conducting research on developer tools and technologies.
    This workflow uses a state graph to manage the research process, including tool extraction,
    company analysis, and providing recommendations based on the research findings.
    It integrates with the Firecrawl service to search and scrape company information,
    and uses an LLM to analyze the data and generate recommendations.
    """

    def __init__(self):

        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        self.firecrawl_service = FirecrawlService()
        self.prompts = DeveloperToolsPrompts()
        self.research_workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Build the state graph for the research workflow.
        This defines the steps involved in the research process, including tool extraction,
        company analysis, and generating recommendations.
        """
        graph = StateGraph(ResearchState)

        graph.add_node(
            "extract_tools",
            self._extract_tools_step,
        )

        graph.add_node(
            "research_companies",
            self._research_companies_step,
        )
        graph.add_node(
            "analyze_companies",
            self._anayze_step,
        )
        graph.set_entry_point("extract_tools")
        graph.add_edge(
            "extract_tools",
            "research_companies",
        )
        graph.add_edge(
            "research_companies",
            "analyze_companies",
        )
        graph.add_edge(
            "analyze_companies",
            END,
        )

        return graph.compile()

    def _extract_tools_step(self, state: ResearchState) -> Dict:
        """
        Step to extract tools from articles based on the research query.
        Args:
            state (ResearchState): Current state of the research workflow.
        Returns:
            Dict: Updated dictionary with extracted tools.
        """
        logger.info(f"Extracting articles for query: {state.query}")
        article_query = f"Finding the best alternatives to: {state.query}"
        search_results = self.firecrawl_service.search_companies(
            article_query, num_results=3
        )
        all_content = ""
        for result in search_results.data:
            url = result.get("url", "")
            scraped = self.firecrawl_service.scrape_company_pages(url)
            if scraped:
                all_content += scraped.markdown[:1500] + "\n\n"

        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(
                content=self.prompts.tool_extraction_user(state.query, all_content)
            ),
        ]

        try:
            response = self.llm.invoke(messages)
            tool_names = [
                name.strip()
                for name in response.content.strip().split("\n")
                if name.strip()
            ]
            logger.info(f"Extracted tools: {', '.join(tool_names[:5])}")
            return {"extracted_tools": tool_names}
        except Exception as e:
            logger.error(f"Error during tool extraction: {e}")
            state.extracted_tools = []
            return {"extracted_tools": []}

    def _analyze_companies_step(
        self, company_name: str, content: str
    ) -> CompanyAnalysis:
        """
        Step to analyze a company based on its content.
        Args:
            company_name (str): Name of the company to analyze.
            content (str): Content to analyze for the company.
        Returns:
            CompanyAnalysis: Analysis of the company.
        """
        structred_llm = self.llm.with_structured_output(CompanyAnalysis)
        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(
                content=self.prompts.tool_analysis_user(company_name, content)
            ),
        ]
        try:
            analysis = structred_llm.invoke(messages)
            logger.info(f"Analyzed company: {company_name}")
            return analysis
        except Exception as e:
            logger.error(f"Error during company analysis for {company_name}: {e}")
            return CompanyAnalysis(
                pricing_model="Unknown",
                is_open_source=None,
                tech_stack=[],
                description="Failed to analyze company",
                api_available=None,
                language_support=[],
                integration_capabilities=[],
            )

    def _research_companies_step(self, state: ResearchState) -> Dict[str, Any]:
        """
        Step to research companies based on the extracted tools.
        Args:
            state (ResearchState): Current state of the research workflow.
        Returns:
            Dict[str, Any]: Updated state with researched companies.
        """
        extracted_tools = getattr(state, "extracted_tools", [])
        if not extracted_tools:
            logger.warning("No tools extracted for analysis.")
            search_results = self.firecrawl_service.search_companies(
                state.query, num_results=3
            )
            tool_names = [
                result.get("metadata", "").get("title", "unknown")
                for result in search_results.data
                if result.get("metadata")
            ]
        else:
            tool_names = extracted_tools[:4]
        logger.info(f"Researching companies for tools: {', '.join(tool_names)}")
        companies = []
        for tool_name in tool_names:
            tool_search_results = self.firecrawl_service.search_companies(
                tool_name + "official site", num_results=1
            )
            if tool_search_results:
                url = tool_search_results.data[0].get("url", "")
                company = CompanyInfo(
                    name=tool_name,
                    description=tool_search_results.data[0].get("markdown", ""),
                    website=url,
                    tech_stack=[],
                    competitors=[],
                )

                scraped_content = self.firecrawl_service.scrape_company_pages(url)
                if scraped_content:
                    content = scraped_content.markdown
                    analysis = self._analyze_companies_step(company.name, content)
                    company.pricing_model = analysis.pricing_model
                    company.is_open_source = analysis.is_open_source
                    company.tech_stack = analysis.tech_stack
                    company.description = analysis.description
                    company.api_available = analysis.api_available
                    company.language_support = analysis.language_support
                    company.integration_capabilities = analysis.integration_capabilities
                companies.append(company)
        logger.info(f"Researched {len(companies)} companies.")
        return {"companies": companies}

    def _anayze_step(self, state: ResearchState) -> Dict[str, Any]:
        """
        Step to analyze the research findings and generate recommendations.
        Args:
            state (ResearchState): Current state of the research workflow.
        Returns:
            Dict[str, Any]: Updated state with analysis and recommendations.
        """
        logger.info("Generating recommendations based on research findings.")
        if not state.companies:
            logger.warning("No companies available for analysis.")
            return {"analysis": "No companies found for analysis."}

        company_data = ", ".join(
            [
                company.model_dump_json()
                for company in state.companies
                if company.tech_stack and company.description
            ]
        )
        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(
                content=self.prompts.recommendations_user(state.query, company_data)
            ),
        ]
        response = self.llm.invoke(messages)
        return {"analysis": response.content}

    def run(self, query: str) -> ResearchState:
        """
        Run the research workflow with the given query.
        Args:
            query (str): The research query to start the workflow.
        Returns:
            ResearchState: Final state of the research workflow after completion.
        """
        initial_state = ResearchState(query=query)
        final_state = self.research_workflow.invoke(initial_state)
        return ResearchState(**final_state)
