import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

class ProfileDataAggregator:
    """
    Centralized data aggregation service that fetches and combines data 
    from multiple microservices for the ArtGram ecosystem.
    """
    
    def __init__(self):
        self.service_endpoints = {
            'user_service': 'http://localhost:8000/api/users/',
            'artwork_service': 'http://localhost:8002/api/artworks/',
            'interaction_service': 'http://localhost:8003/api/interactions/',
            'notification_service': 'http://localhost:8004/api/notifications/'
        }
        self.cache_timeout = 300  # 5 minutes cache
    
    async def fetch_from_service(self, session: aiohttp.ClientSession, 
                               service: str, endpoint: str, 
                               headers: Optional[Dict] = None) -> Dict:
        """
        Fetch data from a specific microservice
        
        Args:
            session: aiohttp session
            service: Service name
            endpoint: API endpoint
            headers: Request headers
            
        Returns:
            Response data as dictionary
        """
        url = f"{self.service_endpoints.get(service, '')}{endpoint}"
        
        try:
            async with session.get(url, headers=headers or {}, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Error fetching from {service}: {response.status}")
                    return {}
        except Exception as e:
            print(f"Exception fetching from {service}: {e}")
            return {}
    
    async def get_user_profile_data(self, user_id: int, auth_token: str) -> Dict:
        """
        Aggregate complete user profile data from all microservices
        
        Args:
            user_id: User ID
            auth_token: JWT authentication token
            
        Returns:
            Complete profile data dictionary
        """
        cache_key = f"user_profile_{user_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            # Fetch data from all services concurrently
            tasks = [
                self.fetch_from_service(session, 'user_service', f'profiles/{user_id}/', headers),
                self.fetch_from_service(session, 'artwork_service', f'user-arts/{user_id}/', headers),
                self.fetch_from_service(session, 'interaction_service', f'user-stats/{user_id}/', headers),
                self.fetch_from_service(session, 'notification_service', f'user-notifications/{user_id}/', headers)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            user_data, arts_data, interaction_data, notification_data = results
            
            # Aggregate and process the data
            profile_data = self._aggregate_profile_data(
                user_data, arts_data, interaction_data, notification_data
            )
            
            # Cache the aggregated data
            cache.set(cache_key, profile_data, self.cache_timeout)
            
            return profile_data
    
    def _aggregate_profile_data(self, user_data: Dict, arts_data: Dict, 
                              interaction_data: Dict, notification_data: Dict) -> Dict:
        """
        Combine data from all services into a unified profile
        
        Args:
            user_data: User service data
            arts_data: Artwork service data
            interaction_data: Interaction service data
            notification_data: Notification service data
            
        Returns:
            Aggregated profile data
        """
        aggregated = {
            'user': user_data or {},
            'arts': self._process_arts_data(arts_data or {}),
            'interactions': self._process_interaction_data(interaction_data or {}),
            'notifications': self._process_notification_data(notification_data or {}),
            'aggregated_at': timezone.now().isoformat()
        }
        
        # Calculate derived metrics
        aggregated['derived_metrics'] = self._calculate_derived_metrics(aggregated)
        
        return aggregated
    
    def _process_arts_data(self, arts_data: Dict) -> Dict:
        """Process artwork service data"""
        if not arts_data:
            return {
                'total_arts': 0,
                'recent_arts': [],
                'total_views': 0,
                'total_likes': 0,
                'categories': {}
            }
        
        arts = arts_data.get('arts', [])
        
        return {
            'total_arts': len(arts),
            'recent_arts': arts[:6],  # Last 6 artworks
            'total_views': sum(art.get('views', 0) for art in arts),
            'total_likes': sum(art.get('likes', 0) for art in arts),
            'categories': self._aggregate_art_categories(arts)
        }
    
    def _process_interaction_data(self, interaction_data: Dict) -> Dict:
        """Process interaction service data"""
        if not interaction_data:
            return {
                'total_followers': 0,
                'total_following': 0,
                'recent_interactions': [],
                'engagement_rate': 0
            }
        
        return {
            'total_followers': interaction_data.get('followers_count', 0),
            'total_following': interaction_data.get('following_count', 0),
            'recent_interactions': interaction_data.get('recent_interactions', []),
            'engagement_rate': interaction_data.get('engagement_rate', 0)
        }
    
    def _process_notification_data(self, notification_data: Dict) -> Dict:
        """Process notification service data"""
        if not notification_data:
            return {
                'unread_count': 0,
                'recent_notifications': [],
                'notification_types': {}
            }
        
        notifications = notification_data.get('notifications', [])
        
        return {
            'unread_count': len([n for n in notifications if not n.get('read', False)]),
            'recent_notifications': notifications[:5],
            'notification_types': self._aggregate_notification_types(notifications)
        }
    
    def _aggregate_art_categories(self, arts: List[Dict]) -> Dict:
        """Aggregate artwork by categories"""
        categories = {}
        for art in arts:
            category = art.get('category', 'Uncategorized')
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _aggregate_notification_types(self, notifications: List[Dict]) -> Dict:
        """Aggregate notifications by type"""
        types = {}
        for notification in notifications:
            notif_type = notification.get('type', 'general')
            types[notif_type] = types.get(notif_type, 0) + 1
        return types
    
    def _calculate_derived_metrics(self, aggregated_data: Dict) -> Dict:
        """Calculate derived metrics from aggregated data"""
        user_data = aggregated_data.get('user', {})
        arts_data = aggregated_data.get('arts', {})
        interaction_data = aggregated_data.get('interactions', {})
        
        total_points = user_data.get('total_points', 0)
        total_arts = arts_data.get('total_arts', 0)
        total_followers = interaction_data.get('total_followers', 0)
        total_views = arts_data.get('total_views', 0)
        
        # Calculate engagement score
        engagement_score = 0
        if total_arts > 0:
            avg_views_per_art = total_views / total_arts
            engagement_score = min(100, (avg_views_per_art * 0.1) + (total_followers * 0.5))
        
        # Calculate activity level
        activity_level = 'low'
        if total_arts >= 10 or total_points >= 100:
            activity_level = 'high'
        elif total_arts >= 5 or total_points >= 50:
            activity_level = 'medium'
        
        # Calculate influence score
        influence_score = min(100, (total_followers * 0.3) + (total_points * 0.2))
        
        return {
            'engagement_score': round(engagement_score, 2),
            'activity_level': activity_level,
            'influence_score': round(influence_score, 2),
            'profile_completion': self._calculate_profile_completion(user_data)
        }
    
    def _calculate_profile_completion(self, user_data: Dict) -> int:
        """Calculate profile completion percentage"""
        required_fields = ['username', 'email', 'bio', 'job_title', 'location', 'website', 'avatar']
        completed_fields = 0
        
        for field in required_fields:
            if user_data.get(field):
                completed_fields += 1
        
        return int((completed_fields / len(required_fields)) * 100)
    
    async def get_leaderboard_data(self, category: str = 'overall', limit: int = 10) -> List[Dict]:
        """
        Get leaderboard data from aggregated metrics
        
        Args:
            category: Leaderboard category (overall, artists, influencers)
            limit: Number of users to return
            
        Returns:
            Leaderboard data
        """
        cache_key = f"leaderboard_{category}_{limit}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # This would typically fetch from a dedicated leaderboard service
        # For now, return mock data
        leaderboard_data = [
            {
                'rank': 1,
                'user_id': 1,
                'username': 'testuser',
                'score': 85,
                'avatar': None,
                'category': category
            },
            {
                'rank': 2,
                'user_id': 2,
                'username': 'artist_pro',
                'score': 72,
                'avatar': None,
                'category': category
            }
        ]
        
        cache.set(cache_key, leaderboard_data, self.cache_timeout * 2)  # Longer cache for leaderboard
        return leaderboard_data
    
    def invalidate_user_cache(self, user_id: int):
        """Invalidate cached data for a specific user"""
        cache_key = f"user_profile_{user_id}"
        cache.delete(cache_key)
    
    async def get_system_stats(self) -> Dict:
        """Get aggregated system statistics"""
        cache_key = "system_stats"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # This would aggregate stats from all services
        system_stats = {
            'total_users': 1000,
            'total_arts': 5000,
            'total_interactions': 25000,
            'active_users_today': 150,
            'new_users_this_week': 45,
            'popular_categories': ['Digital Art', 'Photography', 'Painting'],
            'system_health': 'healthy'
        }
        
        cache.set(cache_key, system_stats, self.cache_timeout * 3)  # Longer cache for system stats
        return system_stats

# Singleton instance
profile_aggregator = ProfileDataAggregator()
