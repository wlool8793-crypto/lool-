import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import requests
import pandas as pd
import numpy as np
from urllib.parse import urljoin, quote
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import feedparser
import yfinance as yf
from app.services.cache_service import cache_service
from app.core.config import settings
from app.integrations.external_apis import external_api_manager, APIProvider
import logging

logger = logging.getLogger(__name__)


class WebServiceType(Enum):
    SEARCH_ENGINE = "search_engine"
    NEWS_AGGREGATOR = "news_aggregator"
    WEATHER_SERVICE = "weather_service"
    FINANCIAL_DATA = "financial_data"
    STOCK_MARKET = "stock_market"
    CRYPTOCURRENCY = "cryptocurrency"
    REAL_ESTATE = "real_estate"
    JOB_BOARD = "job_board"
    E_COMMERCE = "e_commerce"
    SOCIAL_MEDIA = "social_media"
    MAPPING_SERVICE = "mapping_service"
    TRANSLATION_SERVICE = "translation_service"
    EMAIL_SERVICE = "email_service"
    CALENDAR_SERVICE = "calendar_service"
    STORAGE_SERVICE = "storage_service"
    DATABASE_SERVICE = "database_service"


class SearchEngine:
    """Advanced search engine integration"""

    def __init__(self):
        self.search_engines = {
            "google": {
                "base_url": "https://www.googleapis.com/customsearch/v1",
                "requires_key": True,
                "results_per_page": 10
            },
            "bing": {
                "base_url": "https://api.bing.microsoft.com/v7.0/search",
                "requires_key": True,
                "results_per_page": 10
            },
            "duckduckgo": {
                "base_url": "https://api.duckduckgo.com",
                "requires_key": False,
                "results_per_page": 10
            }
        }

    async def search(
        self,
        query: str,
        engine: str = "google",
        num_results: int = 10,
        search_type: str = "web",
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform web search"""
        try:
            if engine not in self.search_engines:
                return {
                    "success": False,
                    "error": f"Unsupported search engine: {engine}"
                }

            engine_config = self.search_engines[engine]

            if engine == "google":
                return await self._search_google(query, num_results, search_type, filters)
            elif engine == "bing":
                return await self._search_bing(query, num_results, search_type, filters)
            elif engine == "duckduckgo":
                return await self._search_duckduckgo(query, num_results, search_type, filters)
            else:
                return {
                    "success": False,
                    "error": f"Search engine {engine} not implemented"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Search error: {str(e)}"
            }

    async def _search_google(self, query: str, num_results: int, search_type: str, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Google Custom Search"""
        if not settings.GOOGLE_API_KEY or not settings.GOOGLE_CSE_ID:
            return {
                "success": False,
                "error": "Google API key and Custom Search Engine ID required"
            }

        params = {
            "key": settings.GOOGLE_API_KEY,
            "cx": settings.GOOGLE_CSE_ID,
            "q": query,
            "num": min(num_results, 10)
        }

        # Apply filters
        if filters:
            if filters.get("site_search"):
                params["siteSearch"] = filters["site_search"]
            if filters.get("date_restrict"):
                params["dateRestrict"] = filters["date_restrict"]

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.googleapis.com/customsearch/v1",
                params=params,
                timeout=30
            ) as response:
                result = await response.json()

                if "error" in result:
                    return {
                        "success": False,
                        "error": result["error"]["message"]
                    }

                items = result.get("items", [])
                search_results = []

                for item in items:
                    search_results.append({
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "snippet": item.get("snippet"),
                        "display_link": item.get("displayLink"),
                        "formatted_url": item.get("formattedUrl"),
                        "pagemap": item.get("pagemap", {})
                    })

                return {
                    "success": True,
                    "query": query,
                    "search_engine": "google",
                    "total_results": result.get("searchInformation", {}).get("totalResults", 0),
                    "search_time": result.get("searchInformation", {}).get("searchTime", 0),
                    "results": search_results
                }

    async def _search_bing(self, query: str, num_results: int, search_type: str, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Bing Search API"""
        if not settings.BING_API_KEY:
            return {
                "success": False,
                "error": "Bing API key required"
            }

        headers = {
            "Ocp-Apim-Subscription-Key": settings.BING_API_KEY
        }

        params = {
            "q": query,
            "count": min(num_results, 50),
            "mkt": "en-US"
        }

        # Apply filters
        if filters:
            if filters.get("site_search"):
                params["q"] += f" site:{filters['site_search']}"
            if filters.get("freshness"):
                params["freshness"] = filters["freshness"]

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.bing.microsoft.com/v7.0/search",
                headers=headers,
                params=params,
                timeout=30
            ) as response:
                result = await response.json()

                if "error" in result:
                    return {
                        "success": False,
                        "error": result["error"]["message"]
                    }

                web_pages = result.get("webPages", {}).get("value", [])
                search_results = []

                for item in web_pages:
                    search_results.append({
                        "title": item.get("name"),
                        "link": item.get("url"),
                        "snippet": item.get("snippet"),
                        "display_link": item.get("displayUrl"),
                        "date_last_crawled": item.get("dateLastCrawled"),
                        "deep_links": item.get("deepLinks", [])
                    })

                return {
                    "success": True,
                    "query": query,
                    "search_engine": "bing",
                    "total_estimated_matches": result.get("webPages", {}).get("totalEstimatedMatches", 0),
                    "results": search_results
                }

    async def _search_duckduckgo(self, query: str, num_results: int, search_type: str, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """DuckDuckGo Search (no API key required)"""
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.duckduckgo.com",
                params=params,
                timeout=30
            ) as response:
                result = await response.json()

                related_topics = result.get("RelatedTopics", [])
                search_results = []

                for topic in related_topics[:num_results]:
                    if "Text" in topic and "FirstURL" in topic:
                        search_results.append({
                            "title": topic.get("Text", "").split(" - ")[0],
                            "link": topic.get("FirstURL"),
                            "snippet": topic.get("Text", ""),
                            "icon_url": topic.get("Icon", {}).get("URL")
                        })

                return {
                    "success": True,
                    "query": query,
                    "search_engine": "duckduckgo",
                    "results": search_results
                }


class NewsAggregator:
    """News aggregation from multiple sources"""

    def __init__(self):
        self.news_sources = {
            "newsapi": {
                "base_url": "https://newsapi.org/v2",
                "requires_key": True
            },
            "rss_feeds": {
                "feeds": [
                    "https://rss.cnn.com/rss/edition.rss",
                    "https://feeds.bbci.co.uk/news/rss.xml",
                    "https://rss.reuters.com/reuters/topNews",
                    "https://feeds.npr.org/1001/rss.xml"
                ]
            },
            "google_news": {
                "base_url": "https://news.google.com/rss"
            }
        }

    async def get_news(
        self,
        query: Optional[str] = None,
        sources: Optional[List[str]] = None,
        category: Optional[str] = None,
        language: str = "en",
        max_results: int = 10,
        sort_by: str = "publishedAt"
    ) -> Dict[str, Any]:
        """Get news articles"""
        try:
            if settings.NEWS_API_KEY:
                return await self._get_news_newsapi(query, sources, category, language, max_results, sort_by)
            else:
                return await self._get_news_rss(query, max_results)

        except Exception as e:
            return {
                "success": False,
                "error": f"News aggregation error: {str(e)}"
            }

    async def _get_news_newsapi(self, query: Optional[str], sources: Optional[List[str]], category: Optional[str], language: str, max_results: int, sort_by: str) -> Dict[str, Any]:
        """Get news from NewsAPI"""
        params = {
            "apiKey": settings.NEWS_API_KEY,
            "language": language,
            "pageSize": min(max_results, 100),
            "sortBy": sort_by
        }

        if query:
            params["q"] = query
            endpoint = "/everything"
        elif category:
            params["category"] = category
            endpoint = "/top-headlines"
        else:
            endpoint = "/top-headlines"

        if sources:
            params["sources"] = ",".join(sources)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://newsapi.org/v2{endpoint}",
                params=params,
                timeout=30
            ) as response:
                result = await response.json()

                if result.get("status") != "ok":
                    return {
                        "success": False,
                        "error": result.get("message", "Unknown error")
                    }

                articles = result.get("articles", [])
                news_items = []

                for article in articles:
                    news_items.append({
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "content": article.get("content"),
                        "author": article.get("author"),
                        "source": article.get("source", {}).get("name"),
                        "published_at": article.get("publishedAt"),
                        "url": article.get("url"),
                        "url_to_image": article.get("urlToImage")
                    })

                return {
                    "success": True,
                    "source": "newsapi",
                    "total_results": result.get("totalResults", 0),
                    "articles": news_items
                }

    async def _get_news_rss(self, query: Optional[str], max_results: int) -> Dict[str, Any]:
        """Get news from RSS feeds"""
        news_items = []

        for feed_url in self.news_sources["rss_feeds"]["feeds"]:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(feed_url, timeout=30) as response:
                        feed_content = await response.text()
                        feed = feedparser.parse(feed_content)

                        for entry in feed.entries[:max_results // len(self.news_sources["rss_feeds"]["feeds"])]:
                            # Filter by query if provided
                            if query:
                                title = entry.get("title", "").lower()
                                summary = entry.get("summary", "").lower()
                                if query.lower() not in title and query.lower() not in summary:
                                    continue

                            news_item = {
                                "title": entry.get("title"),
                                "description": entry.get("summary"),
                                "link": entry.get("link"),
                                "published_at": entry.get("published"),
                                "source": feed.get("feed", {}).get("title"),
                                "author": entry.get("author")
                            }

                            # Extract image from content if available
                            if "media_thumbnail" in entry:
                                news_item["url_to_image"] = entry["media_thumbnail"][0]["url"]
                            elif "enclosures" in entry:
                                for enclosure in entry["enclosures"]:
                                    if enclosure.get("type", "").startswith("image/"):
                                        news_item["url_to_image"] = enclosure.get("href")
                                        break

                            news_items.append(news_item)

            except Exception as e:
                logger.error(f"Error fetching RSS feed {feed_url}: {e}")
                continue

        # Sort by publish date
        news_items.sort(key=lambda x: x.get("published_at", ""), reverse=True)

        return {
            "success": True,
            "source": "rss_feeds",
            "total_results": len(news_items),
            "articles": news_items[:max_results]
        }


class WeatherService:
    """Weather information service"""

    def __init__(self):
        self.weather_providers = {
            "openweather": {
                "base_url": "https://api.openweathermap.org/data/2.5",
                "requires_key": True
            },
            "weatherapi": {
                "base_url": "https://api.weatherapi.com/v1",
                "requires_key": True
            }
        }

    async def get_current_weather(
        self,
        location: str,
        units: str = "metric",
        provider: str = "openweather"
    ) -> Dict[str, Any]:
        """Get current weather for location"""
        try:
            if provider == "openweather":
                return await self._get_weather_openweather(location, units)
            elif provider == "weatherapi":
                return await self._get_weather_weatherapi(location, units)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported weather provider: {provider}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Weather service error: {str(e)}"
            }

    async def _get_weather_openweather(self, location: str, units: str) -> Dict[str, Any]:
        """Get weather from OpenWeatherMap"""
        if not settings.OPENWEATHER_API_KEY:
            return {
                "success": False,
                "error": "OpenWeather API key required"
            }

        params = {
            "q": location,
            "appid": settings.OPENWEATHER_API_KEY,
            "units": units
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params=params,
                timeout=30
            ) as response:
                result = await response.json()

                if result.get("cod") != 200:
                    return {
                        "success": False,
                        "error": result.get("message", "Unknown error")
                    }

                main = result.get("main", {})
                weather = result.get("weather", [{}])[0]
                wind = result.get("wind", {})

                return {
                    "success": True,
                    "provider": "openweather",
                    "location": {
                        "name": result.get("name"),
                        "country": result.get("sys", {}).get("country"),
                        "coordinates": result.get("coord", {})
                    },
                    "weather": {
                        "main": weather.get("main"),
                        "description": weather.get("description"),
                        "icon": weather.get("icon")
                    },
                    "temperature": {
                        "current": main.get("temp"),
                        "feels_like": main.get("feels_like"),
                        "min": main.get("temp_min"),
                        "max": main.get("temp_max"),
                        "humidity": main.get("humidity"),
                        "pressure": main.get("pressure")
                    },
                    "wind": {
                        "speed": wind.get("speed"),
                        "direction": wind.get("deg")
                    },
                    "visibility": result.get("visibility"),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def _get_weather_weatherapi(self, location: str, units: str) -> Dict[str, Any]:
        """Get weather from WeatherAPI"""
        if not settings.WEATHERAPI_KEY:
            return {
                "success": False,
                "error": "WeatherAPI key required"
            }

        # Convert units
        unit_map = {"metric": "m", "imperial": "f"}
        api_units = unit_map.get(units, "m")

        params = {
            "key": settings.WEATHERAPI_KEY,
            "q": location,
            "aqi": "no"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.weatherapi.com/v1/current.json",
                params=params,
                timeout=30
            ) as response:
                result = await response.json()

                if "error" in result:
                    return {
                        "success": False,
                        "error": result["error"]["message"]
                    }

                current = result.get("current", {})
                location_data = result.get("location", {})

                return {
                    "success": True,
                    "provider": "weatherapi",
                    "location": {
                        "name": location_data.get("name"),
                        "region": location_data.get("region"),
                        "country": location_data.get("country"),
                        "coordinates": {
                            "lat": location_data.get("lat"),
                            "lon": location_data.get("lon")
                        }
                    },
                    "weather": {
                        "main": current.get("condition", {}).get("text"),
                        "icon": current.get("condition", {}).get("icon")
                    },
                    "temperature": {
                        "current": current.get("temp_c") if units == "metric" else current.get("temp_f"),
                        "feels_like": current.get("feelslike_c") if units == "metric" else current.get("feelslike_f"),
                        "humidity": current.get("humidity"),
                        "pressure": current.get("pressure_mb"),
                        "uv_index": current.get("uv")
                    },
                    "wind": {
                        "speed": current.get("wind_kph") if units == "metric" else current.get("wind_mph"),
                        "direction": current.get("wind_degree")
                    },
                    "visibility": current.get("vis_km") if units == "metric" else current.get("vis_miles"),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def get_forecast(
        self,
        location: str,
        days: int = 5,
        units: str = "metric",
        provider: str = "openweather"
    ) -> Dict[str, Any]:
        """Get weather forecast"""
        try:
            if provider == "openweather":
                return await self._get_forecast_openweather(location, days, units)
            else:
                return {
                    "success": False,
                    "error": f"Forecast not supported for provider: {provider}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Weather forecast error: {str(e)}"
            }

    async def _get_forecast_openweather(self, location: str, days: int, units: str) -> Dict[str, Any]:
        """Get forecast from OpenWeatherMap"""
        if not settings.OPENWEATHER_API_KEY:
            return {
                "success": False,
                "error": "OpenWeather API key required"
            }

        params = {
            "q": location,
            "appid": settings.OPENWEATHER_API_KEY,
            "units": units,
            "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.openweathermap.org/data/2.5/forecast",
                params=params,
                timeout=30
            ) as response:
                result = await response.json()

                if result.get("cod") != "200":
                    return {
                        "success": False,
                        "error": result.get("message", "Unknown error")
                    }

                forecasts = []
                for item in result.get("list", []):
                    forecasts.append({
                        "datetime": item.get("dt_txt"),
                        "temperature": item.get("main", {}).get("temp"),
                        "description": item.get("weather", [{}])[0].get("description"),
                        "humidity": item.get("main", {}).get("humidity"),
                        "wind_speed": item.get("wind", {}).get("speed"),
                        "pop": item.get("pop", 0)  # Probability of precipitation
                    })

                return {
                    "success": True,
                    "provider": "openweather",
                    "location": {
                        "name": result.get("city", {}).get("name"),
                        "country": result.get("city", {}).get("country")
                    },
                    "forecast": forecasts,
                    "timestamp": datetime.utcnow().isoformat()
                }


class FinancialDataService:
    """Financial data and stock market service"""

    def __init__(self):
        self.data_sources = {
            "yfinance": {
                "enabled": True,
                "requires_key": False
            },
            "alpha_vantage": {
                "enabled": bool(settings.ALPHA_VANTAGE_API_KEY),
                "requires_key": True
            },
            "coinbase": {
                "enabled": bool(settings.COINBASE_API_KEY),
                "requires_key": True
            }
        }

    async def get_stock_price(
        self,
        symbol: str,
        period: str = "1d",
        interval: str = "1m"
    ) -> Dict[str, Any]:
        """Get stock price data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                return {
                    "success": False,
                    "error": f"No data found for symbol: {symbol}"
                }

            # Convert to list of dictionaries
            price_data = []
            for timestamp, row in hist.iterrows():
                price_data.append({
                    "timestamp": timestamp.isoformat(),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"])
                })

            # Get current price info
            info = ticker.info
            current_price = hist["Close"].iloc[-1] if not hist.empty else None

            return {
                "success": True,
                "symbol": symbol,
                "current_price": current_price,
                "company_info": {
                    "name": info.get("longName"),
                    "sector": info.get("sector"),
                    "industry": info.get("industry"),
                    "market_cap": info.get("marketCap"),
                    "description": info.get("longBusinessSummary")
                },
                "price_data": price_data,
                "period": period,
                "interval": interval
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Stock price error: {str(e)}"
            }

    async def get_crypto_prices(self, symbols: List[str]) -> Dict[str, Any]:
        """Get cryptocurrency prices"""
        try:
            crypto_data = {}

            for symbol in symbols:
                try:
                    # Add USD suffix if not present
                    crypto_symbol = f"{symbol}-USD" if not symbol.endswith("-USD") else symbol
                    ticker = yf.Ticker(crypto_symbol)
                    hist = ticker.history(period="1d")

                    if not hist.empty:
                        current_price = hist["Close"].iloc[-1]
                        crypto_data[symbol] = {
                            "price": float(current_price),
                            "change": float(hist["Close"].pct_change().iloc[-1] * 100) if len(hist) > 1 else 0,
                            "volume": int(hist["Volume"].iloc[-1]),
                            "market_cap": ticker.info.get("marketCap"),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        crypto_data[symbol] = {
                            "error": f"No data found for {symbol}"
                        }

                except Exception as e:
                    crypto_data[symbol] = {
                        "error": str(e)
                    }

            return {
                "success": True,
                "crypto_data": crypto_data,
                "symbols": symbols,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Crypto prices error: {str(e)}"
            }

    async def get_market_summary(self) -> Dict[str, Any]:
        """Get market summary for major indices"""
        try:
            indices = {
                "^GSPC": "S&P 500",
                "^DJI": "Dow Jones",
                "^IXIC": "NASDAQ",
                "^VIX": "VIX Volatility Index"
            }

            market_data = {}

            for symbol, name in indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d")

                    if not hist.empty:
                        current_price = hist["Close"].iloc[-1]
                        previous_close = hist["Close"].iloc[0] if len(hist) > 1 else current_price
                        change = ((current_price - previous_close) / previous_close) * 100

                        market_data[symbol] = {
                            "name": name,
                            "price": float(current_price),
                            "change": float(change),
                            "volume": int(hist["Volume"].iloc[-1]) if "Volume" in hist.columns else 0
                        }

                except Exception as e:
                    market_data[symbol] = {
                        "name": name,
                        "error": str(e)
                    }

            return {
                "success": True,
                "market_data": market_data,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Market summary error: {str(e)}"
            }


class WebServiceManager:
    """Comprehensive web service manager"""

    def __init__(self):
        self.search_engine = SearchEngine()
        self.news_aggregator = NewsAggregator()
        self.weather_service = WeatherService()
        self.financial_service = FinancialDataService()

    async def search_web(
        self,
        query: str,
        engine: str = "google",
        num_results: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search the web"""
        return await self.search_engine.search(query, engine, num_results, "web", filters)

    async def get_news(
        self,
        query: Optional[str] = None,
        sources: Optional[List[str]] = None,
        category: Optional[str] = None,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """Get news articles"""
        return await self.news_aggregator.get_news(query, sources, category, "en", max_results)

    async def get_weather(
        self,
        location: str,
        units: str = "metric",
        forecast_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get weather information"""
        if forecast_days:
            return await self.weather_service.get_forecast(location, forecast_days, units)
        else:
            return await self.weather_service.get_current_weather(location, units)

    async def get_stock_data(
        self,
        symbol: str,
        period: str = "1d",
        interval: str = "1m"
    ) -> Dict[str, Any]:
        """Get stock market data"""
        return await self.financial_service.get_stock_price(symbol, period, interval)

    async def get_crypto_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Get cryptocurrency data"""
        return await self.financial_service.get_crypto_prices(symbols)

    async def get_market_summary(self) -> Dict[str, Any]:
        """Get market summary"""
        return await self.financial_service.get_market_summary()

    async def web_scrape(
        self,
        url: str,
        extraction_type: str = "content",
        selectors: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Scrape web content"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status != 200:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {response.reason}"
                        }

                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')

                    if extraction_type == "content":
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()

                        title = soup.find('title')
                        title_text = title.get_text() if title else "No title"

                        # Extract main content
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
                            body = soup.find('body')
                            main_content = body.get_text(strip=True) if body else ""

                        return {
                            "success": True,
                            "url": url,
                            "title": title_text,
                            "content": main_content[:5000],  # Limit content length
                            "word_count": len(main_content.split())
                        }

                    elif extraction_type == "links":
                        links = []
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            if href.startswith('http'):
                                links.append({
                                    "url": href,
                                    "text": link.get_text(strip=True),
                                    "title": link.get('title', '')
                                })

                        return {
                            "success": True,
                            "url": url,
                            "links": links[:50]  # Limit to first 50 links
                        }

                    elif extraction_type == "structured" and selectors:
                        extracted_data = {}
                        for field, selector in selectors.items():
                            elements = soup.select(selector)
                            if elements:
                                if len(elements) == 1:
                                    extracted_data[field] = elements[0].get_text(strip=True)
                                else:
                                    extracted_data[field] = [elem.get_text(strip=True) for elem in elements]

                        return {
                            "success": True,
                            "url": url,
                            "extracted_data": extracted_data
                        }

                    else:
                        return {
                            "success": False,
                            "error": f"Unsupported extraction type: {extraction_type}"
                        }

        except Exception as e:
            return {
                "success": False,
                "error": f"Web scraping error: {str(e)}"
            }

    def get_available_services(self) -> List[Dict[str, Any]]:
        """Get list of available web services"""
        return [
            {
                "name": "web_search",
                "description": "Search the web using multiple search engines",
                "engines": ["google", "bing", "duckduckgo"]
            },
            {
                "name": "news_aggregation",
                "description": "Aggregate news from multiple sources",
                "sources": ["newsapi", "rss_feeds"]
            },
            {
                "name": "weather_service",
                "description": "Get weather information and forecasts",
                "providers": ["openweather", "weatherapi"]
            },
            {
                "name": "financial_data",
                "description": "Get stock market and financial data",
                "sources": ["yfinance", "alpha_vantage", "coinbase"]
            },
            {
                "name": "web_scraping",
                "description": "Scrape and extract data from websites",
                "extraction_types": ["content", "links", "structured"]
            }
        ]


# Global instance
web_service_manager = WebServiceManager()