"""
Gamification service for reward/points engine
Implements badges, levels, and point systems to encourage safe driving
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
import json

class GamificationService:
    """
    Service for managing driver gamification features
    """
    
    def __init__(self):
        self.point_values = {
            'safe_trip': 100,
            'smooth_acceleration': 10,
            'smooth_braking': 10,
            'speed_compliance': 15,
            'phone_free_trip': 50,
            'night_driving_bonus': 25,
            'highway_safety': 20,
            'eco_driving': 30
        }
        
        self.badges = {
            'safe_driver': {'points_required': 1000, 'description': 'Complete 10 safe trips'},
            'speed_demon_reformed': {'points_required': 500, 'description': 'Improve speed compliance'},
            'smooth_operator': {'points_required': 750, 'description': 'Master smooth driving'},
            'phone_free_champion': {'points_required': 1200, 'description': '30 days phone-free driving'},
            'eco_warrior': {'points_required': 800, 'description': 'Excel at eco-friendly driving'},
            'night_owl': {'points_required': 600, 'description': 'Safe night driving expert'},
            'highway_hero': {'points_required': 900, 'description': 'Highway safety master'},
            'consistency_king': {'points_required': 2000, 'description': '60 days of consistent safe driving'}
        }
        
        self.levels = {
            1: {'name': 'Learner', 'points_required': 0},
            2: {'name': 'Careful Driver', 'points_required': 500},
            3: {'name': 'Safe Driver', 'points_required': 1500},
            4: {'name': 'Expert Driver', 'points_required': 3000},
            5: {'name': 'Master Driver', 'points_required': 5000},
            6: {'name': 'Legendary Driver', 'points_required': 10000}
        }
    
    def calculate_trip_points(self, trip_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate points earned for a specific trip
        """
        points_breakdown = {}
        total_points = 0
        
        # Base points for completing a trip safely
        if trip_data.get('behavior_score', 0) >= 80:
            points_breakdown['safe_trip'] = self.point_values['safe_trip']
            total_points += self.point_values['safe_trip']
        
        # Smooth acceleration bonus
        if trip_data.get('harsh_acceleration_count', 10) <= 2:
            points_breakdown['smooth_acceleration'] = self.point_values['smooth_acceleration']
            total_points += self.point_values['smooth_acceleration']
        
        # Smooth braking bonus
        if trip_data.get('harsh_braking_count', 10) <= 2:
            points_breakdown['smooth_braking'] = self.point_values['smooth_braking']
            total_points += self.point_values['smooth_braking']
        
        # Speed compliance bonus
        if trip_data.get('speed_violations', 5) == 0:
            points_breakdown['speed_compliance'] = self.point_values['speed_compliance']
            total_points += self.point_values['speed_compliance']
        
        # Phone-free driving bonus
        if trip_data.get('phone_usage_duration', 300) == 0:
            points_breakdown['phone_free_trip'] = self.point_values['phone_free_trip']
            total_points += self.point_values['phone_free_trip']
        
        # Night driving bonus (if applicable)
        if trip_data.get('is_night_trip', False) and trip_data.get('behavior_score', 0) >= 85:
            points_breakdown['night_driving_bonus'] = self.point_values['night_driving_bonus']
            total_points += self.point_values['night_driving_bonus']
        
        # Highway safety bonus
        if trip_data.get('highway_percentage', 0) > 50 and trip_data.get('behavior_score', 0) >= 85:
            points_breakdown['highway_safety'] = self.point_values['highway_safety']
            total_points += self.point_values['highway_safety']
        
        # Eco-driving bonus
        if trip_data.get('fuel_efficiency_score', 0) >= 80:
            points_breakdown['eco_driving'] = self.point_values['eco_driving']
            total_points += self.point_values['eco_driving']
        
        return {
            'total_points': total_points,
            'points_breakdown': points_breakdown,
            'multipliers_applied': self._get_active_multipliers(trip_data)
        }
    
    def check_badge_eligibility(self, driver_stats: Dict[str, Any]) -> List[str]:
        """
        Check which badges a driver is eligible for
        """
        eligible_badges = []
        total_points = driver_stats.get('total_points', 0)
        
        for badge_name, badge_info in self.badges.items():
            if total_points >= badge_info['points_required']:
                # Additional specific criteria for some badges
                if badge_name == 'safe_driver' and driver_stats.get('safe_trips', 0) >= 10:
                    eligible_badges.append(badge_name)
                elif badge_name == 'phone_free_champion' and driver_stats.get('phone_free_days', 0) >= 30:
                    eligible_badges.append(badge_name)
                elif badge_name == 'consistency_king' and driver_stats.get('consistent_days', 0) >= 60:
                    eligible_badges.append(badge_name)
                elif badge_name not in ['safe_driver', 'phone_free_champion', 'consistency_king']:
                    eligible_badges.append(badge_name)
        
        return eligible_badges
    
    def calculate_driver_level(self, total_points: int) -> Dict[str, Any]:
        """
        Calculate driver level based on total points
        """
        current_level = 1
        for level, info in self.levels.items():
            if total_points >= info['points_required']:
                current_level = level
            else:
                break
        
        next_level = current_level + 1 if current_level < max(self.levels.keys()) else current_level
        points_to_next = self.levels[next_level]['points_required'] - total_points if next_level > current_level else 0
        
        return {
            'current_level': current_level,
            'level_name': self.levels[current_level]['name'],
            'next_level': next_level,
            'points_to_next_level': points_to_next,
            'progress_percentage': (total_points / self.levels[next_level]['points_required'] * 100) if next_level > current_level else 100
        }
    
    def _get_active_multipliers(self, trip_data: Dict[str, Any]) -> List[str]:
        """
        Get any active point multipliers for special events or achievements
        """
        multipliers = []
        
        # Weekend challenge multiplier
        if trip_data.get('is_weekend', False):
            multipliers.append('weekend_challenge_2x')
        
        # Perfect week multiplier
        if trip_data.get('perfect_week_streak', 0) > 0:
            multipliers.append('perfect_week_bonus')
        
        # New driver encouragement
        if trip_data.get('total_trips', 100) < 10:
            multipliers.append('new_driver_bonus')
        
        return multipliers
    
    def generate_leaderboard(self, driver_data: List[Dict[str, Any]], timeframe: str = 'monthly') -> List[Dict[str, Any]]:
        """
        Generate leaderboard for specified timeframe
        """
        # Sort drivers by points in descending order
        sorted_drivers = sorted(driver_data, key=lambda x: x.get('points', 0), reverse=True)
        
        leaderboard = []
        for i, driver in enumerate(sorted_drivers[:10]):  # Top 10
            leaderboard.append({
                'rank': i + 1,
                'driver_id': driver['driver_id'],
                'driver_name': driver.get('name', f"Driver {driver['driver_id']}"),
                'points': driver.get('points', 0),
                'level': self.calculate_driver_level(driver.get('points', 0))['level_name'],
                'badges_count': len(driver.get('badges', [])),
                'safe_trips': driver.get('safe_trips', 0)
            })
        
        return leaderboard
    
    def get_personalized_challenges(self, driver_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate personalized challenges based on driver performance
        """
        challenges = []
        
        # Speed improvement challenge
        if driver_stats.get('speed_compliance_rate', 100) < 90:
            challenges.append({
                'id': 'speed_improvement',
                'title': 'Speed Master Challenge',
                'description': 'Complete 5 trips with perfect speed compliance',
                'reward_points': 200,
                'deadline': (datetime.now() + timedelta(days=7)).isoformat(),
                'progress': 0,
                'target': 5
            })
        
        # Phone-free challenge
        if driver_stats.get('phone_usage_rate', 0) > 10:
            challenges.append({
                'id': 'phone_free',
                'title': 'Hands-Free Hero',
                'description': 'Complete 7 consecutive phone-free trips',
                'reward_points': 350,
                'deadline': (datetime.now() + timedelta(days=10)).isoformat(),
                'progress': 0,
                'target': 7
            })
        
        # Smooth driving challenge
        if driver_stats.get('smooth_driving_score', 100) < 85:
            challenges.append({
                'id': 'smooth_driving',
                'title': 'Smooth Operator',
                'description': 'Achieve 90+ smooth driving score for 3 trips',
                'reward_points': 150,
                'deadline': (datetime.now() + timedelta(days=5)).isoformat(),
                'progress': 0,
                'target': 3
            })
        
        return challenges
