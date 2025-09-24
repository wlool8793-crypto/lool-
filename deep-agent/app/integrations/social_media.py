"""
Social Media Platform Integrations for LangGraph Deep Web Agent

This module provides comprehensive integrations with social media platforms
including Twitter, Facebook, Instagram, LinkedIn, TikTok, and others.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import asyncpg
import redis.asyncio as redis
from urllib.parse import urlencode, quote

from app.core.config import settings
from app.database.redis import RedisManager
from app.tools.ai_services import AIServiceManager
from app.integrations.external_apis import ExternalAPIManager

logger = logging.getLogger(__name__)

class SocialPlatform(Enum):
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    REDDIT = "reddit"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    SLACK = "slack"

@dataclass
class SocialPost:
    """Represents a social media post"""
    id: str
    platform: SocialPlatform
    content: str
    author: str
    author_id: str
    timestamp: datetime
    likes: int = 0
    shares: int = 0
    comments: int = 0
    url: str = ""
    media_urls: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    sentiment: float = 0.0
    engagement_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SocialUser:
    """Represents a social media user"""
    id: str
    platform: SocialPlatform
    username: str
    display_name: str
    bio: str = ""
    followers: int = 0
    following: int = 0
    posts: int = 0
    verified: bool = False
    profile_image: str = ""
    join_date: Optional[datetime] = None
    location: str = ""
    website: str = ""
    engagement_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SocialMetrics:
    """Social media engagement metrics"""
    platform: SocialPlatform
    date: datetime
    followers: int
    following: int
    posts: int
    likes: int
    shares: int
    comments: int
    impressions: int
    reach: int
    engagement_rate: float
    sentiment_score: float
    top_hashtags: List[str]
    top_mentions: List[str]

class SocialMediaManager:
    """Manages social media platform integrations"""

    def __init__(self):
        self.redis_manager = RedisManager()
        self.api_manager = ExternalAPIManager()
        self.ai_service = AIServiceManager()

        # Platform configurations
        self.platform_configs = self._load_platform_configs()

        # API clients for each platform
        self.api_clients = {}
        self._initialize_api_clients()

        # Rate limiting
        self.rate_limits = {}
        self._initialize_rate_limits()

    def _load_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load platform configurations"""
        return {
            "twitter": {
                "api_base": "https://api.twitter.com/2",
                "oauth_base": "https://twitter.com/i/oauth2/authorize",
                "token_url": "https://api.twitter.com/2/oauth2/token",
                "scopes": ["tweet.read", "tweet.write", "users.read", "follow.read", "follow.write"],
                "version": "2"
            },
            "facebook": {
                "api_base": "https://graph.facebook.com/v18.0",
                "oauth_base": "https://www.facebook.com/v18.0/dialog/oauth",
                "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
                "scopes": ["public_profile", "pages_read_engagement", "pages_manage_posts"],
                "version": "18.0"
            },
            "instagram": {
                "api_base": "https://graph.instagram.com",
                "oauth_base": "https://api.instagram.com/oauth/authorize",
                "token_url": "https://api.instagram.com/oauth/access_token",
                "scopes": ["user_profile", "user_media", "instagram_content"],
                "version": "latest"
            },
            "linkedin": {
                "api_base": "https://api.linkedin.com/v2",
                "oauth_base": "https://www.linkedin.com/oauth/v2/authorization",
                "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
                "scopes": ["r_liteprofile", "r_emailaddress", "w_member_social"],
                "version": "2"
            },
            "youtube": {
                "api_base": "https://www.googleapis.com/youtube/v3",
                "oauth_base": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "scopes": ["https://www.googleapis.com/auth/youtube.readonly"],
                "version": "3"
            },
            "reddit": {
                "api_base": "https://oauth.reddit.com",
                "oauth_base": "https://www.reddit.com/api/v1/authorize",
                "token_url": "https://www.reddit.com/api/v1/access_token",
                "scopes": ["identity", "read", "submit"],
                "version": "1"
            }
        }

    def _initialize_api_clients(self):
        """Initialize API clients for each platform"""
        try:
            # Twitter client
            if settings.TWITTER_API_KEY and settings.TWITTER_API_SECRET:
                self.api_clients['twitter'] = self._create_twitter_client()

            # Facebook client
            if settings.FACEBOOK_APP_ID and settings.FACEBOOK_APP_SECRET:
                self.api_clients['facebook'] = self._create_facebook_client()

            # Instagram client
            if settings.INSTAGRAM_CLIENT_ID and settings.INSTAGRAM_CLIENT_SECRET:
                self.api_clients['instagram'] = self._create_instagram_client()

            # LinkedIn client
            if settings.LINKEDIN_CLIENT_ID and settings.LINKEDIN_CLIENT_SECRET:
                self.api_clients['linkedin'] = self._create_linkedin_client()

            # YouTube client
            if settings.YOUTUBE_API_KEY:
                self.api_clients['youtube'] = self._create_youtube_client()

            # Reddit client
            if settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET:
                self.api_clients['reddit'] = self._create_reddit_client()

        except Exception as e:
            logger.error(f"Error initializing API clients: {e}")

    def _create_twitter_client(self) -> Dict[str, Any]:
        """Create Twitter API client"""
        return {
            'api_key': settings.TWITTER_API_KEY,
            'api_secret': settings.TWITTER_API_SECRET,
            'bearer_token': settings.TWITTER_BEARER_TOKEN,
            'access_token': settings.TWITTER_ACCESS_TOKEN,
            'access_token_secret': settings.TWITTER_ACCESS_TOKEN_SECRET
        }

    def _create_facebook_client(self) -> Dict[str, Any]:
        """Create Facebook API client"""
        return {
            'app_id': settings.FACEBOOK_APP_ID,
            'app_secret': settings.FACEBOOK_APP_SECRET,
            'access_token': settings.FACEBOOK_ACCESS_TOKEN
        }

    def _create_instagram_client(self) -> Dict[str, Any]:
        """Create Instagram API client"""
        return {
            'client_id': settings.INSTAGRAM_CLIENT_ID,
            'client_secret': settings.INSTAGRAM_CLIENT_SECRET,
            'access_token': settings.INSTAGRAM_ACCESS_TOKEN
        }

    def _create_linkedin_client(self) -> Dict[str, Any]:
        """Create LinkedIn API client"""
        return {
            'client_id': settings.LINKEDIN_CLIENT_ID,
            'client_secret': settings.LINKEDIN_CLIENT_SECRET,
            'access_token': settings.LINKEDIN_ACCESS_TOKEN
        }

    def _create_youtube_client(self) -> Dict[str, Any]:
        """Create YouTube API client"""
        return {
            'api_key': settings.YOUTUBE_API_KEY,
            'access_token': settings.YOUTUBE_ACCESS_TOKEN
        }

    def _create_reddit_client(self) -> Dict[str, Any]:
        """Create Reddit API client"""
        return {
            'client_id': settings.REDDIT_CLIENT_ID,
            'client_secret': settings.REDDIT_CLIENT_SECRET,
            'access_token': settings.REDDIT_ACCESS_TOKEN,
            'user_agent': 'DeepAgent/1.0'
        }

    def _initialize_rate_limits(self):
        """Initialize rate limiting for each platform"""
        self.rate_limits = {
            "twitter": {
                "requests_per_15min": 300,
                "window_seconds": 900
            },
            "facebook": {
                "requests_per_hour": 200,
                "window_seconds": 3600
            },
            "instagram": {
                "requests_per_hour": 200,
                "window_seconds": 3600
            },
            "linkedin": {
                "requests_per_hour": 100,
                "window_seconds": 3600
            },
            "youtube": {
                "requests_per_100sec": 100,
                "window_seconds": 100
            },
            "reddit": {
                "requests_per_minute": 60,
                "window_seconds": 60
            }
        }

    async def authenticate_platform(self, platform: SocialPlatform,
                                  auth_code: str = None,
                                  client_id: str = None,
                                  client_secret: str = None) -> Dict[str, Any]:
        """Authenticate with social media platform"""
        auth_result = {
            'success': False,
            'access_token': None,
            'refresh_token': None,
            'expires_in': 0,
            'error': None
        }

        try:
            platform_config = self.platform_configs.get(platform.value)
            if not platform_config:
                raise Exception(f"Platform {platform.value} not supported")

            if platform == SocialPlatform.TWITTER:
                auth_result = await self._authenticate_twitter(auth_code, client_id, client_secret)
            elif platform == SocialPlatform.FACEBOOK:
                auth_result = await self._authenticate_facebook(auth_code, client_id, client_secret)
            elif platform == SocialPlatform.INSTAGRAM:
                auth_result = await self._authenticate_instagram(auth_code, client_id, client_secret)
            elif platform == SocialPlatform.LINKEDIN:
                auth_result = await self._authenticate_linkedin(auth_code, client_id, client_secret)
            elif platform == SocialPlatform.YOUTUBE:
                auth_result = await self._authenticate_youtube(auth_code, client_id, client_secret)
            elif platform == SocialPlatform.REDDIT:
                auth_result = await self._authenticate_reddit(auth_code, client_id, client_secret)

        except Exception as e:
            logger.error(f"Error authenticating with {platform.value}: {e}")
            auth_result['error'] = str(e)

        return auth_result

    async def _authenticate_twitter(self, auth_code: str, client_id: str, client_secret: str) -> Dict[str, Any]:
        """Authenticate with Twitter"""
        auth_result = {
            'success': False,
            'access_token': None,
            'refresh_token': None,
            'expires_in': 0,
            'error': None
        }

        try:
            if 'twitter' not in self.api_clients:
                raise Exception("Twitter client not configured")

            # Exchange authorization code for access token
            client = self.api_clients['twitter']

            auth_data = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': settings.TWITTER_REDIRECT_URI,
                'client_id': client_id,
                'code_verifier': 'challenge'  # Should be stored during OAuth flow
            }

            auth_string = f"{client_id}:{client_secret}"
            import base64
            encoded_auth = base64.b64encode(auth_string.encode()).decode()

            headers = {
                'Authorization': f'Basic {encoded_auth}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.platform_configs['twitter']['token_url'],
                    data=auth_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        auth_result['success'] = True
                        auth_result['access_token'] = token_data.get('access_token')
                        auth_result['refresh_token'] = token_data.get('refresh_token')
                        auth_result['expires_in'] = token_data.get('expires_in', 7200)
                    else:
                        error_data = await response.text()
                        auth_result['error'] = f"Twitter auth failed: {error_data}"

        except Exception as e:
            logger.error(f"Error authenticating with Twitter: {e}")
            auth_result['error'] = str(e)

        return auth_result

    async def _authenticate_facebook(self, auth_code: str, client_id: str, client_secret: str) -> Dict[str, Any]:
        """Authenticate with Facebook"""
        # Placeholder implementation
        return {'success': False, 'error': 'Facebook authentication not implemented'}

    async def _authenticate_instagram(self, auth_code: str, client_id: str, client_secret: str) -> Dict[str, Any]:
        """Authenticate with Instagram"""
        # Placeholder implementation
        return {'success': False, 'error': 'Instagram authentication not implemented'}

    async def _authenticate_linkedin(self, auth_code: str, client_id: str, client_secret: str) -> Dict[str, Any]:
        """Authenticate with LinkedIn"""
        # Placeholder implementation
        return {'success': False, 'error': 'LinkedIn authentication not implemented'}

    async def _authenticate_youtube(self, auth_code: str, client_id: str, client_secret: str) -> Dict[str, Any]:
        """Authenticate with YouTube"""
        # Placeholder implementation
        return {'success': False, 'error': 'YouTube authentication not implemented'}

    async def _authenticate_reddit(self, auth_code: str, client_id: str, client_secret: str) -> Dict[str, Any]:
        """Authenticate with Reddit"""
        # Placeholder implementation
        return {'success': False, 'error': 'Reddit authentication not implemented'}

    async def get_user_profile(self, platform: SocialPlatform, user_id: str) -> Optional[SocialUser]:
        """Get user profile from social platform"""
        try:
            if platform == SocialPlatform.TWITTER:
                return await self._get_twitter_user(user_id)
            elif platform == SocialPlatform.FACEBOOK:
                return await self._get_facebook_user(user_id)
            elif platform == SocialPlatform.INSTAGRAM:
                return await self._get_instagram_user(user_id)
            elif platform == SocialPlatform.LINKEDIN:
                return await self._get_linkedin_user(user_id)
            elif platform == SocialPlatform.YOUTUBE:
                return await self._get_youtube_user(user_id)
            elif platform == SocialPlatform.REDDIT:
                return await self._get_reddit_user(user_id)

        except Exception as e:
            logger.error(f"Error getting user profile from {platform.value}: {e}")
            return None

    async def _get_twitter_user(self, user_id: str) -> Optional[SocialUser]:
        """Get Twitter user profile"""
        try:
            if 'twitter' not in self.api_clients:
                return None

            client = self.api_clients['twitter']
            url = f"{self.platform_configs['twitter']['api_base']}/users/{user_id}"

            headers = {
                'Authorization': f'Bearer {client["bearer_token"]}',
                'Content-Type': 'application/json'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        user = SocialUser(
                            id=user_data['data']['id'],
                            platform=SocialPlatform.TWITTER,
                            username=user_data['data']['username'],
                            display_name=user_data['data']['name'],
                            bio=user_data['data'].get('description', ''),
                            followers=user_data['data']['public_metrics']['followers_count'],
                            following=user_data['data']['public_metrics']['following_count'],
                            posts=user_data['data']['public_metrics']['tweet_count'],
                            verified=user_data['data']['verified'],
                            profile_image=user_data['data'].get('profile_image_url', ''),
                            join_date=datetime.strptime(user_data['data']['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                            location=user_data['data'].get('location', ''),
                            website=user_data['data'].get('url', ''),
                            metadata={
                                'protected': user_data['data']['protected'],
                                'public_metrics': user_data['data']['public_metrics']
                            }
                        )

                        # Calculate engagement rate
                        if user.followers > 0:
                            total_engagement = user.posts * 2  # Average engagement per post
                            user.engagement_rate = (total_engagement / user.followers) * 100

                        return user

        except Exception as e:
            logger.error(f"Error getting Twitter user {user_id}: {e}")

        return None

    async def _get_facebook_user(self, user_id: str) -> Optional[SocialUser]:
        """Get Facebook user profile"""
        # Placeholder implementation
        return None

    async def _get_instagram_user(self, user_id: str) -> Optional[SocialUser]:
        """Get Instagram user profile"""
        # Placeholder implementation
        return None

    async def _get_linkedin_user(self, user_id: str) -> Optional[SocialUser]:
        """Get LinkedIn user profile"""
        # Placeholder implementation
        return None

    async def _get_youtube_user(self, user_id: str) -> Optional[SocialUser]:
        """Get YouTube user profile"""
        # Placeholder implementation
        return None

    async def _get_reddit_user(self, user_id: str) -> Optional[SocialUser]:
        """Get Reddit user profile"""
        # Placeholder implementation
        return None

    async def get_user_posts(self, platform: SocialPlatform, user_id: str,
                           limit: int = 10, cursor: str = None) -> List[SocialPost]:
        """Get user posts from social platform"""
        posts = []

        try:
            if platform == SocialPlatform.TWITTER:
                posts = await self._get_twitter_posts(user_id, limit, cursor)
            elif platform == SocialPlatform.FACEBOOK:
                posts = await self._get_facebook_posts(user_id, limit, cursor)
            elif platform == SocialPlatform.INSTAGRAM:
                posts = await self._get_instagram_posts(user_id, limit, cursor)
            elif platform == SocialPlatform.LINKEDIN:
                posts = await self._get_linkedin_posts(user_id, limit, cursor)
            elif platform == SocialPlatform.YOUTUBE:
                posts = await self._get_youtube_posts(user_id, limit, cursor)
            elif platform == SocialPlatform.REDDIT:
                posts = await self._get_reddit_posts(user_id, limit, cursor)

        except Exception as e:
            logger.error(f"Error getting posts from {platform.value}: {e}")

        return posts

    async def _get_twitter_posts(self, user_id: str, limit: int, cursor: str) -> List[SocialPost]:
        """Get Twitter user posts"""
        posts = []

        try:
            if 'twitter' not in self.api_clients:
                return posts

            client = self.api_clients['twitter']
            url = f"{self.platform_configs['twitter']['api_base']}/users/{user_id}/tweets"

            params = {
                'max_results': min(limit, 100),
                'tweet.fields': 'created_at,public_metrics,context_annotations,entities',
                'expansions': 'author_id,attachments.media_keys',
                'user.fields': 'name,username,verified,profile_image_url'
            }

            if cursor:
                params['pagination_token'] = cursor

            headers = {
                'Authorization': f'Bearer {client["bearer_token"]}',
                'Content-Type': 'application/json'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract includes
                        includes = data.get('includes', {})
                        users = {user['id']: user for user in includes.get('users', [])}
                        media = {media['media_key']: media for media in includes.get('media', [])}

                        # Process tweets
                        for tweet_data in data.get('data', []):
                            post = SocialPost(
                                id=tweet_data['id'],
                                platform=SocialPlatform.TWITTER,
                                content=tweet_data['text'],
                                author=users.get(tweet_data['author_id'], {}).get('username', ''),
                                author_id=tweet_data['author_id'],
                                timestamp=datetime.strptime(tweet_data['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                                likes=tweet_data['public_metrics']['like_count'],
                                shares=tweet_data['public_metrics']['retweet_count'],
                                comments=tweet_data['public_metrics']['reply_count'],
                                url=f"https://twitter.com/{users.get(tweet_data['author_id'], {}).get('username', '')}/status/{tweet_data['id']}",
                                hashtags=self._extract_hashtags(tweet_data.get('entities', {}).get('hashtags', [])),
                                mentions=self._extract_mentions(tweet_data.get('entities', {}).get('mentions', [])),
                                metadata={
                                    'quote_count': tweet_data['public_metrics']['quote_count'],
                                    'context_annotations': tweet_data.get('context_annotations', []),
                                    'entities': tweet_data.get('entities', {})
                                }
                            )

                            # Calculate engagement rate
                            total_engagement = post.likes + post.shares + post.comments
                            user_info = users.get(tweet_data['author_id'], {})
                            followers = user_info.get('public_metrics', {}).get('followers_count', 1)
                            post.engagement_rate = (total_engagement / followers) * 100 if followers > 0 else 0

                            # Analyze sentiment
                            post.sentiment = await self._analyze_sentiment(post.content)

                            posts.append(post)

        except Exception as e:
            logger.error(f"Error getting Twitter posts for {user_id}: {e}")

        return posts

    def _extract_hashtags(self, hashtag_entities: List[Dict[str, Any]]) -> List[str]:
        """Extract hashtags from Twitter entities"""
        return [tag['tag'] for tag in hashtag_entities]

    def _extract_mentions(self, mention_entities: List[Dict[str, Any]]) -> List[str]:
        """Extract mentions from Twitter entities"""
        return [mention['username'] for mention in mention_entities]

    async def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text using AI service"""
        try:
            sentiment_result = await self.ai_service.analyze_sentiment(text)
            return sentiment_result.get('score', 0.0)
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0.0

    async def _get_facebook_posts(self, user_id: str, limit: int, cursor: str) -> List[SocialPost]:
        """Get Facebook user posts"""
        # Placeholder implementation
        return []

    async def _get_instagram_posts(self, user_id: str, limit: int, cursor: str) -> List[SocialPost]:
        """Get Instagram user posts"""
        # Placeholder implementation
        return []

    async def _get_linkedin_posts(self, user_id: str, limit: int, cursor: str) -> List[SocialPost]:
        """Get LinkedIn user posts"""
        # Placeholder implementation
        return []

    async def _get_youtube_posts(self, user_id: str, limit: int, cursor: str) -> List[SocialPost]:
        """Get YouTube user videos"""
        # Placeholder implementation
        return []

    async def _get_reddit_posts(self, user_id: str, limit: int, cursor: str) -> List[SocialPost]:
        """Get Reddit user posts"""
        # Placeholder implementation
        return []

    async def search_posts(self, platform: SocialPlatform, query: str,
                         limit: int = 10, filters: Dict[str, Any] = None) -> List[SocialPost]:
        """Search for posts on social platform"""
        posts = []

        try:
            if platform == SocialPlatform.TWITTER:
                posts = await self._search_twitter_posts(query, limit, filters)
            elif platform == SocialPlatform.FACEBOOK:
                posts = await self._search_facebook_posts(query, limit, filters)
            elif platform == SocialPlatform.INSTAGRAM:
                posts = await self._search_instagram_posts(query, limit, filters)
            elif platform == SocialPlatform.LINKEDIN:
                posts = await self._search_linkedin_posts(query, limit, filters)
            elif platform == SocialPlatform.YOUTUBE:
                posts = await self._search_youtube_posts(query, limit, filters)
            elif platform == SocialPlatform.REDDIT:
                posts = await self._search_reddit_posts(query, limit, filters)

        except Exception as e:
            logger.error(f"Error searching posts on {platform.value}: {e}")

        return posts

    async def _search_twitter_posts(self, query: str, limit: int, filters: Dict[str, Any]) -> List[SocialPost]:
        """Search Twitter posts"""
        posts = []

        try:
            if 'twitter' not in self.api_clients:
                return posts

            client = self.api_clients['twitter']
            url = f"{self.platform_configs['twitter']['api_base']}/tweets/search/recent"

            # Build query with filters
            search_query = query
            if filters:
                if filters.get('hashtags'):
                    search_query += " " + " ".join([f"#{tag}" for tag in filters['hashtags']])
                if filters.get('mentions'):
                    search_query += " " + " ".join([f"@{mention}" for mention in filters['mentions']])
                if filters.get('from_user'):
                    search_query += f" from:{filters['from_user']}"
                if filters.get('date_from'):
                    search_query += f" since:{filters['date_from']}"
                if filters.get('date_to'):
                    search_query += f" until:{filters['date_to']}"

            params = {
                'query': search_query,
                'max_results': min(limit, 100),
                'tweet.fields': 'created_at,public_metrics,context_annotations,entities',
                'expansions': 'author_id,attachments.media_keys',
                'user.fields': 'name,username,verified,profile_image_url'
            }

            headers = {
                'Authorization': f'Bearer {client["bearer_token"]}',
                'Content-Type': 'application/json'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract includes
                        includes = data.get('includes', {})
                        users = {user['id']: user for user in includes.get('users', [])}
                        media = {media['media_key']: media for media in includes.get('media', [])}

                        # Process tweets
                        for tweet_data in data.get('data', []):
                            post = SocialPost(
                                id=tweet_data['id'],
                                platform=SocialPlatform.TWITTER,
                                content=tweet_data['text'],
                                author=users.get(tweet_data['author_id'], {}).get('username', ''),
                                author_id=tweet_data['author_id'],
                                timestamp=datetime.strptime(tweet_data['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                                likes=tweet_data['public_metrics']['like_count'],
                                shares=tweet_data['public_metrics']['retweet_count'],
                                comments=tweet_data['public_metrics']['reply_count'],
                                url=f"https://twitter.com/{users.get(tweet_data['author_id'], {}).get('username', '')}/status/{tweet_data['id']}",
                                hashtags=self._extract_hashtags(tweet_data.get('entities', {}).get('hashtags', [])),
                                mentions=self._extract_mentions(tweet_data.get('entities', {}).get('mentions', [])),
                                metadata={
                                    'quote_count': tweet_data['public_metrics']['quote_count'],
                                    'context_annotations': tweet_data.get('context_annotations', []),
                                    'entities': tweet_data.get('entities', {})
                                }
                            )

                            # Calculate engagement rate
                            total_engagement = post.likes + post.shares + post.comments
                            user_info = users.get(tweet_data['author_id'], {})
                            followers = user_info.get('public_metrics', {}).get('followers_count', 1)
                            post.engagement_rate = (total_engagement / followers) * 100 if followers > 0 else 0

                            # Analyze sentiment
                            post.sentiment = await self._analyze_sentiment(post.content)

                            posts.append(post)

        except Exception as e:
            logger.error(f"Error searching Twitter posts: {e}")

        return posts

    async def _search_facebook_posts(self, query: str, limit: int, filters: Dict[str, Any]) -> List[SocialPost]:
        """Search Facebook posts"""
        # Placeholder implementation
        return []

    async def _search_instagram_posts(self, query: str, limit: int, filters: Dict[str, Any]) -> List[SocialPost]:
        """Search Instagram posts"""
        # Placeholder implementation
        return []

    async def _search_linkedin_posts(self, query: str, limit: int, filters: Dict[str, Any]) -> List[SocialPost]:
        """Search LinkedIn posts"""
        # Placeholder implementation
        return []

    async def _search_youtube_posts(self, query: str, limit: int, filters: Dict[str, Any]) -> List[SocialPost]:
        """Search YouTube videos"""
        # Placeholder implementation
        return []

    async def _search_reddit_posts(self, query: str, limit: int, filters: Dict[str, Any]) -> List[SocialPost]:
        """Search Reddit posts"""
        # Placeholder implementation
        return []

    async def create_post(self, platform: SocialPlatform, content: str,
                        media_urls: List[str] = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a post on social platform"""
        post_result = {
            'success': False,
            'post_id': None,
            'post_url': None,
            'error': None
        }

        try:
            if platform == SocialPlatform.TWITTER:
                post_result = await self._create_twitter_post(content, media_urls, metadata)
            elif platform == SocialPlatform.FACEBOOK:
                post_result = await self._create_facebook_post(content, media_urls, metadata)
            elif platform == SocialPlatform.INSTAGRAM:
                post_result = await self._create_instagram_post(content, media_urls, metadata)
            elif platform == SocialPlatform.LINKEDIN:
                post_result = await self._create_linkedin_post(content, media_urls, metadata)
            elif platform == SocialPlatform.YOUTUBE:
                post_result = await self._create_youtube_post(content, media_urls, metadata)
            elif platform == SocialPlatform.REDDIT:
                post_result = await self._create_reddit_post(content, media_urls, metadata)

        except Exception as e:
            logger.error(f"Error creating post on {platform.value}: {e}")
            post_result['error'] = str(e)

        return post_result

    async def _create_twitter_post(self, content: str, media_urls: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create Twitter post"""
        post_result = {
            'success': False,
            'post_id': None,
            'post_url': None,
            'error': None
        }

        try:
            if 'twitter' not in self.api_clients:
                raise Exception("Twitter client not configured")

            client = self.api_clients['twitter']
            url = f"{self.platform_configs['twitter']['api_base']}/tweets"

            # Upload media if provided
            media_ids = []
            if media_urls:
                for media_url in media_urls:
                    media_id = await self._upload_twitter_media(media_url)
                    if media_id:
                        media_ids.append(media_id)

            # Create tweet
            tweet_data = {
                'text': content
            }

            if media_ids:
                tweet_data['media'] = {'media_ids': media_ids}

            headers = {
                'Authorization': f'Bearer {client["bearer_token"]}',
                'Content-Type': 'application/json'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=tweet_data, headers=headers) as response:
                    if response.status == 201:
                        response_data = await response.json()
                        post_result['success'] = True
                        post_result['post_id'] = response_data['data']['id']
                        post_result['post_url'] = f"https://twitter.com/i/web/status/{response_data['data']['id']}"
                    else:
                        error_data = await response.text()
                        post_result['error'] = f"Twitter post creation failed: {error_data}"

        except Exception as e:
            logger.error(f"Error creating Twitter post: {e}")
            post_result['error'] = str(e)

        return post_result

    async def _upload_twitter_media(self, media_url: str) -> Optional[str]:
        """Upload media to Twitter"""
        try:
            if 'twitter' not in self.api_clients:
                return None

            client = self.api_clients['twitter']
            upload_url = "https://upload.twitter.com/1.1/media/upload.json"

            # Download media
            async with aiohttp.ClientSession() as session:
                async with session.get(media_url) as response:
                    if response.status == 200:
                        media_data = await response.read()

                        # Upload to Twitter
                        headers = {
                            'Authorization': f'Bearer {client["bearer_token"]}',
                            'Content-Type': 'application/octet-stream'
                        }

                        files = {'media': media_data}
                        async with session.post(upload_url, headers=headers, data=files) as upload_response:
                            if upload_response.status == 200:
                                upload_data = await upload_response.json()
                                return upload_data.get('media_id')

        except Exception as e:
            logger.error(f"Error uploading media to Twitter: {e}")

        return None

    async def _create_facebook_post(self, content: str, media_urls: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create Facebook post"""
        # Placeholder implementation
        return {'success': False, 'error': 'Facebook post creation not implemented'}

    async def _create_instagram_post(self, content: str, media_urls: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create Instagram post"""
        # Placeholder implementation
        return {'success': False, 'error': 'Instagram post creation not implemented'}

    async def _create_linkedin_post(self, content: str, media_urls: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create LinkedIn post"""
        # Placeholder implementation
        return {'success': False, 'error': 'LinkedIn post creation not implemented'}

    async def _create_youtube_post(self, content: str, media_urls: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create YouTube video"""
        # Placeholder implementation
        return {'success': False, 'error': 'YouTube video creation not implemented'}

    async def _create_reddit_post(self, content: str, media_urls: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create Reddit post"""
        # Placeholder implementation
        return {'success': False, 'error': 'Reddit post creation not implemented'}

    async def get_platform_metrics(self, platform: SocialPlatform, user_id: str,
                                 date_range: Dict[str, datetime]) -> SocialMetrics:
        """Get platform metrics for user"""
        try:
            # Get user posts
            posts = await self.get_user_posts(platform, user_id, limit=100)

            if not posts:
                return SocialMetrics(
                    platform=platform,
                    date=datetime.now(),
                    followers=0,
                    following=0,
                    posts=0,
                    likes=0,
                    shares=0,
                    comments=0,
                    impressions=0,
                    reach=0,
                    engagement_rate=0.0,
                    sentiment_score=0.0,
                    top_hashtags=[],
                    top_mentions=[]
                )

            # Calculate metrics
            total_likes = sum(post.likes for post in posts)
            total_shares = sum(post.shares for post in posts)
            total_comments = sum(post.comments for post in posts)

            # Get user info for followers/following
            user = await self.get_user_profile(platform, user_id)
            followers = user.followers if user else 0
            following = user.following if user else 0

            # Calculate engagement rate
            total_engagement = total_likes + total_shares + total_comments
            engagement_rate = (total_engagement / followers) * 100 if followers > 0 else 0

            # Calculate sentiment score
            sentiment_score = sum(post.sentiment for post in posts) / len(posts) if posts else 0

            # Extract top hashtags and mentions
            all_hashtags = []
            all_mentions = []
            for post in posts:
                all_hashtags.extend(post.hashtags)
                all_mentions.extend(post.mentions)

            from collections import Counter
            top_hashtags = [tag for tag, _ in Counter(all_hashtags).most_common(10)]
            top_mentions = [mention for mention, _ in Counter(all_mentions).most_common(10)]

            return SocialMetrics(
                platform=platform,
                date=datetime.now(),
                followers=followers,
                following=following,
                posts=len(posts),
                likes=total_likes,
                shares=total_shares,
                comments=total_comments,
                impressions=0,  # Would need platform-specific API
                reach=0,  # Would need platform-specific API
                engagement_rate=engagement_rate,
                sentiment_score=sentiment_score,
                top_hashtags=top_hashtags,
                top_mentions=top_mentions
            )

        except Exception as e:
            logger.error(f"Error getting platform metrics for {platform.value}: {e}")
            return SocialMetrics(
                platform=platform,
                date=datetime.now(),
                followers=0,
                following=0,
                posts=0,
                likes=0,
                shares=0,
                comments=0,
                impressions=0,
                reach=0,
                engagement_rate=0.0,
                sentiment_score=0.0,
                top_hashtags=[],
                top_mentions=[]
            )

    async def analyze_social_performance(self, platform: SocialPlatform,
                                      user_id: str, date_range: Dict[str, datetime]) -> Dict[str, Any]:
        """Analyze social media performance"""
        analysis_result = {
            'platform': platform.value,
            'user_id': user_id,
            'metrics': {},
            'trends': {},
            'recommendations': [],
            'best_performing_posts': [],
            'audience_insights': {}
        }

        try:
            # Get metrics
            metrics = await self.get_platform_metrics(platform, user_id, date_range)
            analysis_result['metrics'] = {
                'followers': metrics.followers,
                'following': metrics.following,
                'posts': metrics.posts,
                'total_engagement': metrics.likes + metrics.shares + metrics.comments,
                'engagement_rate': metrics.engagement_rate,
                'sentiment_score': metrics.sentiment_score,
                'top_hashtags': metrics.top_hashtags,
                'top_mentions': metrics.top_mentions
            }

            # Get user posts for detailed analysis
            posts = await self.get_user_posts(platform, user_id, limit=50)

            if posts:
                # Find best performing posts
                sorted_posts = sorted(posts, key=lambda p: p.engagement_rate, reverse=True)
                analysis_result['best_performing_posts'] = sorted_posts[:5]

                # Analyze trends
                analysis_result['trends'] = await self._analyze_post_trends(posts)

                # Generate recommendations
                analysis_result['recommendations'] = await self._generate_social_recommendations(posts, metrics)

                # Audience insights
                analysis_result['audience_insights'] = await self._analyze_audience_insights(posts)

        except Exception as e:
            logger.error(f"Error analyzing social performance: {e}")

        return analysis_result

    async def _analyze_post_trends(self, posts: List[SocialPost]) -> Dict[str, Any]:
        """Analyze posting trends"""
        trends = {
            'posting_times': {},
            'content_types': {},
            'engagement_patterns': {},
            'sentiment_trends': {}
        }

        try:
            # Posting time analysis
            for post in posts:
                hour = post.timestamp.hour
                if hour not in trends['posting_times']:
                    trends['posting_times'][hour] = []
                trends['posting_times'][hour].append(post.engagement_rate)

            # Calculate average engagement by hour
            for hour, rates in trends['posting_times'].items():
                trends['posting_times'][hour] = sum(rates) / len(rates)

            # Content type analysis
            for post in posts:
                has_media = len(post.media_urls) > 0
                content_type = 'media' if has_media else 'text'
                if content_type not in trends['content_types']:
                    trends['content_types'][content_type] = []
                trends['content_types'][content_type].append(post.engagement_rate)

            # Calculate average engagement by content type
            for content_type, rates in trends['content_types'].items():
                trends['content_types'][content_type] = sum(rates) / len(rates)

            # Sentiment trends
            for post in posts:
                sentiment_category = 'positive' if post.sentiment > 0.2 else 'negative' if post.sentiment < -0.2 else 'neutral'
                if sentiment_category not in trends['sentiment_trends']:
                    trends['sentiment_trends'][sentiment_category] = []
                trends['sentiment_trends'][sentiment_category].append(post.engagement_rate)

            # Calculate average engagement by sentiment
            for sentiment, rates in trends['sentiment_trends'].items():
                trends['sentiment_trends'][sentiment] = sum(rates) / len(rates)

        except Exception as e:
            logger.error(f"Error analyzing post trends: {e}")

        return trends

    async def _generate_social_recommendations(self, posts: List[SocialPost], metrics: SocialMetrics) -> List[str]:
        """Generate social media recommendations"""
        recommendations = []

        try:
            # Analyze posting frequency
            if len(posts) < 10:
                recommendations.append("Consider posting more frequently to increase engagement")

            # Analyze engagement rate
            if metrics.engagement_rate < 1.0:
                recommendations.append("Low engagement rate detected. Try using more visuals or asking questions")

            # Analyze sentiment
            if metrics.sentiment_score < -0.1:
                recommendations.append("Negative sentiment detected. Consider more positive content")

            # Analyze hashtag usage
            if len(metrics.top_hashtags) < 3:
                recommendations.append("Use more relevant hashtags to increase discoverability")

            # Analyze posting times
            if posts:
                best_hour = max(range(24), key=lambda h: sum(1 for p in posts if p.timestamp.hour == h))
                recommendations.append(f"Your audience is most active at {best_hour}:00. Consider posting at this time")

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")

        return recommendations

    async def _analyze_audience_insights(self, posts: List[SocialPost]) -> Dict[str, Any]:
        """Analyze audience insights"""
        insights = {
            'total_audience': 0,
            'active_followers': 0,
            'engagement_distribution': {},
            'geographic_distribution': {},
            'interests': []
        }

        try:
            if not posts:
                return insights

            # Calculate total audience reach
            unique_authors = set(post.author_id for post in posts)
            insights['total_audience'] = len(unique_authors)

            # Calculate active followers (those who engage)
            engaged_users = set()
            for post in posts:
                if post.likes > 0 or post.shares > 0 or post.comments > 0:
                    engaged_users.add(post.author_id)
            insights['active_followers'] = len(engaged_users)

            # Engagement distribution
            engagement_rates = [post.engagement_rate for post in posts]
            insights['engagement_distribution'] = {
                'low': sum(1 for rate in engagement_rates if rate < 1.0),
                'medium': sum(1 for rate in engagement_rates if 1.0 <= rate < 5.0),
                'high': sum(1 for rate in engagement_rates if rate >= 5.0)
            }

            # Extract interests from hashtags and mentions
            all_hashtags = []
            for post in posts:
                all_hashtags.extend(post.hashtags)

            from collections import Counter
            insights['interests'] = [tag for tag, _ in Counter(all_hashtags).most_common(10)]

        except Exception as e:
            logger.error(f"Error analyzing audience insights: {e}")

        return insights