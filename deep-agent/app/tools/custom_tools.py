import asyncio
import json
import uuid
import re
import aiohttp
import requests
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from app.services.cache_service import cache_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ToolType(Enum):
    WEB_SCRAPER = "web_scraper"
    API_CLIENT = "api_client"
    DATA_ANALYZER = "data_analyzer"
    IMAGE_PROCESSOR = "image_processor"
    EMAIL_CLIENT = "email_client"
    CALENDAR_CLIENT = "calendar_client"
    SOCIAL_MEDIA = "social_media"
    CLOUD_STORAGE = "cloud_storage"
    BLOCKCHAIN = "blockchain"
    AI_SERVICES = "ai_services"


@dataclass
class ToolResult:
    """Custom tool result data structure"""
    success: bool
    result: Any
    tool_name: str
    execution_time: float
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class WebScraperTool:
    """Advanced web scraping tool with multiple extraction strategies"""

    def __init__(self):
        self.session = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    async def scrape_url(
        self,
        url: str,
        extraction_type: str = "content",
        selectors: Optional[Dict[str, str]] = None,
        max_pages: int = 1
    ) -> ToolResult:
        """Scrape content from a URL"""
        start_time = datetime.utcnow()

        try:
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)

            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    return ToolResult(
                        success=False,
                        result=None,
                        tool_name="web_scraper",
                        execution_time=(datetime.utcnow() - start_time).total_seconds(),
                        error=f"HTTP {response.status}: {response.reason}"
                    )

                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')

                if extraction_type == "content":
                    result = self._extract_main_content(soup)
                elif extraction_type == "structured":
                    result = self._extract_structured_data(soup, selectors)
                elif extraction_type == "links":
                    result = self._extract_links(soup, url)
                elif extraction_type == "images":
                    result = self._extract_images(soup, url)
                elif extraction_type == "forms":
                    result = self._extract_forms(soup)
                else:
                    result = self._extract_main_content(soup)

                return ToolResult(
                    success=True,
                    result=result,
                    tool_name="web_scraper",
                    execution_time=(datetime.utcnow() - start_time).total_seconds(),
                    metadata={
                        "url": url,
                        "extraction_type": extraction_type,
                        "content_length": len(content)
                    }
                )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                tool_name="web_scraper",
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                error=str(e)
            )

    def _extract_main_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract main content from webpage"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract title
        title = soup.find('title')
        title_text = title.get_text() if title else "No title"

        # Extract main content (try common content containers)
        content_selectors = [
            'article', 'main', '.content', '#content', '.post', '.article',
            '[role="main"]', '.main-content', '#main'
        ]

        main_content = None
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                main_content = element.get_text(strip=True)
                break

        if not main_content:
            # Fallback to body content
            body = soup.find('body')
            main_content = body.get_text(strip=True) if body else ""

        # Extract metadata
        meta_description = soup.find('meta', attrs={'name': 'description'})
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})

        return {
            "title": title_text,
            "content": main_content[:5000],  # Limit content length
            "description": meta_description.get('content', '') if meta_description else '',
            "keywords": meta_keywords.get('content', '') if meta_keywords else '',
            "word_count": len(main_content.split()),
            "extracted_at": datetime.utcnow().isoformat()
        }

    def _extract_structured_data(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract structured data using CSS selectors"""
        result = {}

        for field, selector in selectors.items():
            elements = soup.select(selector)
            if elements:
                if len(elements) == 1:
                    result[field] = elements[0].get_text(strip=True)
                else:
                    result[field] = [elem.get_text(strip=True) for elem in elements]

        return result

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links from webpage"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http'):
                url = href
            elif href.startswith('/'):
                url = urljoin(base_url, href)
            else:
                continue

            links.append({
                "url": url,
                "text": link.get_text(strip=True),
                "title": link.get('title', '')
            })

        return links[:50]  # Limit to first 50 links

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract images from webpage"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            if src.startswith('http'):
                url = src
            elif src.startswith('/'):
                url = urljoin(base_url, src)
            else:
                continue

            images.append({
                "url": url,
                "alt": img.get('alt', ''),
                "title": img.get('title', '')
            })

        return images[:30]  # Limit to first 30 images

    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract forms from webpage"""
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                "action": form.get('action', ''),
                "method": form.get('method', 'GET').upper(),
                "fields": []
            }

            for input_field in form.find_all(['input', 'select', 'textarea']):
                field_data = {
                    "name": input_field.get('name', ''),
                    "type": input_field.get('type', 'text'),
                    "required": input_field.has_attr('required')
                }

                if input_field.name == 'select':
                    options = [opt.get('value', opt.get_text()) for opt in input_field.find_all('option')]
                    field_data["options"] = options

                form_data["fields"].append(field_data)

            forms.append(form_data)

        return forms


class DataAnalyzerTool:
    """Advanced data analysis tool with statistical capabilities"""

    def __init__(self):
        self.supported_formats = ['csv', 'json', 'excel', 'parquet']

    async def analyze_data(
        self,
        data: Union[str, List[Dict], pd.DataFrame],
        analysis_type: str = "summary"
    ) -> ToolResult:
        """Analyze data with various statistical methods"""
        start_time = datetime.utcnow()

        try:
            # Convert input to DataFrame
            if isinstance(data, str):
                if data.startswith('['):  # JSON array
                    df = pd.read_json(data)
                else:
                    # Assume CSV format
                    from io import StringIO
                    df = pd.read_csv(StringIO(data))
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, pd.DataFrame):
                df = data
            else:
                raise ValueError("Unsupported data format")

            # Perform analysis
            if analysis_type == "summary":
                result = self._generate_summary(df)
            elif analysis_type == "statistics":
                result = self._generate_statistics(df)
            elif analysis_type == "correlation":
                result = self._generate_correlation(df)
            elif analysis_type == "visualization":
                result = self._generate_visualization_data(df)
            else:
                result = self._generate_summary(df)

            return ToolResult(
                success=True,
                result=result,
                tool_name="data_analyzer",
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                metadata={
                    "analysis_type": analysis_type,
                    "rows": len(df),
                    "columns": len(df.columns)
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                tool_name="data_analyzer",
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                error=str(e)
            )

    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data summary"""
        summary = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "sample_data": df.head(5).to_dict('records')
        }

        # Add summary statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary["numeric_summary"] = df[numeric_cols].describe().to_dict()

        return summary

    def _generate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate detailed statistics"""
        stats = {}

        # Numeric statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            stats["numeric"] = {}
            for col in numeric_cols:
                stats["numeric"][col] = {
                    "mean": df[col].mean(),
                    "median": df[col].median(),
                    "std": df[col].std(),
                    "min": df[col].min(),
                    "max": df[col].max(),
                    "quartiles": df[col].quantile([0.25, 0.5, 0.75]).to_dict()
                }

        # Categorical statistics
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            stats["categorical"] = {}
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                stats["categorical"][col] = {
                    "unique_count": df[col].nunique(),
                    "most_common": value_counts.head(10).to_dict(),
                    "value_counts": value_counts.to_dict()
                }

        return stats

    def _generate_correlation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate correlation analysis"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return {"error": "Need at least 2 numeric columns for correlation analysis"}

        correlation_matrix = df[numeric_cols].corr()

        # Find strong correlations
        strong_correlations = []
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i < j:  # Avoid duplicates
                    corr_value = correlation_matrix.loc[col1, col2]
                    if abs(corr_value) > 0.5:  # Strong correlation threshold
                        strong_correlations.append({
                            "variable1": col1,
                            "variable2": col2,
                            "correlation": corr_value
                        })

        return {
            "correlation_matrix": correlation_matrix.to_dict(),
            "strong_correlations": sorted(strong_correlations, key=lambda x: abs(x["correlation"]), reverse=True)
        }

    def _generate_visualization_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data ready for visualization"""
        viz_data = {}

        # Histogram data for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].nunique() > 1:
                hist_data = df[col].value_counts(bins=20).sort_index()
                viz_data[f"{col}_histogram"] = {
                    "values": hist_data.values.tolist(),
                    "bins": [(left + right) / 2 for left, right in zip(hist_data.index.left, hist_data.index.right)],
                    "counts": hist_data.values.tolist()
                }

        # Bar chart data for categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].nunique() <= 20:  # Only for columns with reasonable unique values
                value_counts = df[col].value_counts().head(10)
                viz_data[f"{col}_bar"] = {
                    "categories": value_counts.index.tolist(),
                    "values": value_counts.values.tolist()
                }

        return viz_data


class EmailClientTool:
    """Email client tool for sending and managing emails"""

    def __init__(self):
        self.smtp_config = None
        self.imap_config = None

    def configure_smtp(self, host: str, port: int, username: str, password: str, use_tls: bool = True):
        """Configure SMTP settings"""
        self.smtp_config = {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "use_tls": use_tls
        }

    async def send_email(
        self,
        to: Union[str, List[str]],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> ToolResult:
        """Send an email"""
        start_time = datetime.utcnow()

        try:
            if not self.smtp_config:
                return ToolResult(
                    success=False,
                    result=None,
                    tool_name="email_client",
                    execution_time=(datetime.utcnow() - start_time).total_seconds(),
                    error="SMTP not configured"
                )

            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.base import MIMEBase
            from email import encoders

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['username']
            msg['To'] = ', '.join([to] if isinstance(to, str) else to)
            msg['Subject'] = subject

            # Add body
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # Add attachments
            if attachments:
                for attachment_path in attachments:
                    with open(attachment_path, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {attachment_path.split("/")[-1]}'
                        )
                        msg.attach(part)

            # Send email
            with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                if self.smtp_config['use_tls']:
                    server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)

            return ToolResult(
                success=True,
                result={
                    "message": "Email sent successfully",
                    "to": to,
                    "subject": subject,
                    "attachments_count": len(attachments) if attachments else 0
                },
                tool_name="email_client",
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                tool_name="email_client",
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                error=str(e)
            )


class APIClientTool:
    """Generic API client tool for REST APIs"""

    def __init__(self):
        self.session = None
        self.base_url = ""
        self.default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Deep-Agent/1.0"
        }

    def configure(self, base_url: str, api_key: Optional[str] = None, headers: Optional[Dict[str, str]] = None):
        """Configure API client"""
        self.base_url = base_url.rstrip('/')
        if api_key:
            self.default_headers["Authorization"] = f"Bearer {api_key}"
        if headers:
            self.default_headers.update(headers)

    async def make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> ToolResult:
        """Make HTTP request to API"""
        start_time = datetime.utcnow()

        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            # Prepare request
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            request_headers = {**self.default_headers, **(headers or {})}

            async with self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                timeout=30
            ) as response:

                response_data = await response.text()

                try:
                    # Try to parse as JSON
                    json_response = json.loads(response_data)
                except json.JSONDecodeError:
                    json_response = response_data

                return ToolResult(
                    success=response.status < 400,
                    result={
                        "status_code": response.status,
                        "data": json_response,
                        "headers": dict(response.headers)
                    },
                    tool_name="api_client",
                    execution_time=(datetime.utcnow() - start_time).total_seconds(),
                    metadata={
                        "method": method,
                        "url": url,
                        "params": params,
                        "data_size": len(response_data)
                    }
                )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                tool_name="api_client",
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                error=str(e)
            )

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> ToolResult:
        """Make GET request"""
        return await self.make_request("GET", endpoint, params=params)

    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> ToolResult:
        """Make POST request"""
        return await self.make_request("POST", endpoint, data=data)

    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> ToolResult:
        """Make PUT request"""
        return await self.make_request("PUT", endpoint, data=data)

    async def delete(self, endpoint: str) -> ToolResult:
        """Make DELETE request"""
        return await self.make_request("DELETE", endpoint)


class CustomToolManager:
    """Manager for custom tools"""

    def __init__(self):
        self.tools = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize all custom tools"""
        self.tools["web_scraper"] = WebScraperTool()
        self.tools["data_analyzer"] = DataAnalyzerTool()
        self.tools["email_client"] = EmailClientTool()
        self.tools["api_client"] = APIClientTool()

    def get_tool(self, tool_name: str) -> Optional[Any]:
        """Get a tool instance"""
        return self.tools.get(tool_name)

    async def execute_tool(
        self,
        tool_name: str,
        method: str,
        *args,
        **kwargs
    ) -> ToolResult:
        """Execute a tool method"""
        tool = self.tools.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                result=None,
                tool_name=tool_name,
                execution_time=0,
                error=f"Tool '{tool_name}' not found"
            )

        try:
            if hasattr(tool, method):
                method_func = getattr(tool, method)
                if asyncio.iscoroutinefunction(method_func):
                    result = await method_func(*args, **kwargs)
                else:
                    result = method_func(*args, **kwargs)
                return result
            else:
                return ToolResult(
                    success=False,
                    result=None,
                    tool_name=tool_name,
                    execution_time=0,
                    error=f"Method '{method}' not found on tool '{tool_name}'"
                )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                tool_name=tool_name,
                execution_time=0,
                error=str(e)
            )

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        tools_info = []
        for tool_name, tool_instance in self.tools.items():
            methods = [method for method in dir(tool_instance) if not method.startswith('_') and callable(getattr(tool_instance, method))]
            tools_info.append({
                "name": tool_name,
                "class": tool_instance.__class__.__name__,
                "methods": methods
            })
        return tools_info


# Global instance
custom_tool_manager = CustomToolManager()