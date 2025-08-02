"""
Enhanced gamification service for comprehensive reward/points engine
Updated to work with advanced telematics analysis and expert model outputs
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
import json
import numpy as np

class GamificationService:
    """
    Enhanced service for managing driver gamification features with advanced analytics
    """
    
    def __init__(self):
        # Enhanced point values based on comprehensive analysis
        self.point_values = {
            'safe_trip': 100,
            'excellent_behavior': 150,
            'smooth_driving': 75,
            'low_risk_location': 50,
            'good_weather_driving': 25,
            'traffic_awareness': 40,
            'night_safety_bonus': 80,
            'weekend_safety': 60,
            'route_optimization': 35,
            'consistency_bonus': 200,
            'improvement_bonus': 120
        }
        
        # Enhanced badge system with specific criteria
        self.badges = {
            'sensor_master': {
                'points_required': 1000, 
                'description': 'Master smooth acceleration and steering patterns',
                'criteria': 'behavior_score >= 90 for 10 trips'
            },
            'location_wise': {
                'points_required': 800, 
                'description': 'Consistently choose low-risk routes',
                'criteria': 'avg_geographic_risk < 40 for 15 trips'
            },
            'weather_warrior': {
                'points_required': 1200, 
                'description': 'Safe driving in challenging weather conditions',
                'criteria': 'good_performance in weather_risk > 60'
            },
            'context_champion': {
                'points_required': 1500, 
                'description': 'Excellent contextual risk management',
                'criteria': 'contextual_risk < 50 consistently'
            },
            'ensemble_expert': {
                'points_required': 2000, 
                'description': 'Master of all expert model domains',
                'criteria': 'all_expert_scores > 80'
            },
            'risk_reducer': {
                'points_required': 900, 
                'description': 'Significant risk score improvement',
                'criteria': 'risk_reduction > 20 points over time'
            },
            'frequency_champion': {
                'points_required': 600, 
                'description': 'Minimal high-frequency driving patterns',
                'criteria': 'low_frequency_energy in behavior analysis'
            },
            'magnitude_master': {
                'points_required': 750, 
                'description': 'Optimal acceleration magnitude control',
                'criteria': 'acc_magnitude consistently optimal'
            }
        }
        
        # Enhanced level system
        self.levels = {
            1: {'name': 'Telematics Novice', 'points_required': 0, 'benefits': ['Basic insights']},
            2: {'name': 'Sensor Student', 'points_required': 500, 'benefits': ['Behavior tracking', '5% discount']},
            3: {'name': 'Location Learner', 'points_required': 1500, 'benefits': ['Route recommendations', '10% discount']},
            4: {'name': 'Context Aware', 'points_required': 3000, 'benefits': ['Weather alerts', '15% discount']},
            5: {'name': 'Risk Expert', 'points_required': 5000, 'benefits': ['Premium insights', '20% discount']},
            6: {'name': 'Safety Master', 'points_required': 8000, 'benefits': ['Advanced analytics', '25% discount']},
            7: {'name': 'Telematics Legend', 'points_required': 12000, 'benefits': ['Maximum benefits', '30% discount']}
        }
        
        # Challenge system
        self.challenges = {
            'smooth_week': {
                'description': '7 days of smooth driving (jerk < 0.3)',
                'points': 500,
                'duration_days': 7
            },
            'low_risk_month': {
                'description': '30 days with risk score < 40',
                'points': 1000,
                'duration_days': 30
            },
            'weather_master': {
                'description': '10 trips in challenging weather conditions',
                'points': 800,
                'trip_count': 10
            },
            'location_optimizer': {
                'description': 'Choose optimal routes for 20 trips',
                'points': 600,
                'trip_count': 20
            }
        }
    
    def calculate_advanced_gamification(self, 
                                      driver_id: str,
                                      assessment_result: Dict[str, Any],
                                      trip_distance_km: float,
                                      trip_duration_minutes: float) -> Dict[str, Any]:
        """
        Calculate comprehensive gamification metrics from expert model assessment
        """
        points_breakdown = {}
        total_points = 0
        badges_earned = []
        challenges_completed = []
        
        # Extract expert scores
        expert_assessments = assessment_result.get('expert_assessments', {})
        behavior_assessment = expert_assessments.get('behavior', {})
        geographic_assessment = expert_assessments.get('geographic', {})
        contextual_assessment = expert_assessments.get('contextual', {})
        
        overall_assessment = assessment_result.get('overall_assessment', {})
        
        # Base trip completion points
        base_points = 50
        total_points += base_points
        points_breakdown['trip_completion'] = base_points
        
        # Behavior-based points
        behavior_score = behavior_assessment.get('behavior_score', 70)
        if behavior_score >= 90:
            behavior_points = self.point_values['excellent_behavior']
            points_breakdown['excellent_behavior'] = behavior_points
            total_points += behavior_points
        elif behavior_score >= 80:
            behavior_points = self.point_values['safe_trip']
            points_breakdown['safe_trip'] = behavior_points
            total_points += behavior_points
        
        # Driving style bonus
        driving_style = behavior_assessment.get('driving_style', 'NORMAL')
        if driving_style == 'SMOOTH':
            smooth_points = self.point_values['smooth_driving']
            points_breakdown['smooth_driving'] = smooth_points
            total_points += smooth_points
        
        # Geographic risk bonus
        geo_risk = geographic_assessment.get('geographic_risk_score', 50)
        if geo_risk < 40:
            location_points = self.point_values['low_risk_location']
            points_breakdown['low_risk_location'] = location_points
            total_points += location_points
        
        # Contextual risk management
        contextual_risk = contextual_assessment.get('contextual_risk_score', 50)
        risk_components = contextual_assessment.get('risk_components', {})
        
        # Weather awareness bonus
        weather_risk = risk_components.get('weather', {}).get('risk_score', 30)
        if weather_risk > 40 and contextual_risk < 60:  # Good performance in bad weather
            weather_points = self.point_values['good_weather_driving'] * 2
            points_breakdown['weather_awareness'] = weather_points
            total_points += weather_points
        
        # Traffic awareness bonus
        traffic_risk = risk_components.get('traffic', {}).get('risk_score', 30)
        if traffic_risk > 50 and contextual_risk < 60:  # Good performance in heavy traffic
            traffic_points = self.point_values['traffic_awareness']
            points_breakdown['traffic_awareness'] = traffic_points
            total_points += traffic_points
        
        # Time-based bonuses
        temporal_info = risk_components.get('temporal', {})
        if temporal_info.get('is_rush_hour', False) and overall_assessment.get('final_risk_score', 50) < 50:
            rush_hour_points = 60
            points_breakdown['rush_hour_safety'] = rush_hour_points
            total_points += rush_hour_points
        
        if temporal_info.get('time_period') == 'Night' and behavior_score >= 85:
            night_points = self.point_values['night_safety_bonus']
            points_breakdown['night_safety'] = night_points
            total_points += night_points
        
        # Distance and duration bonuses
        if trip_distance_km > 50:  # Long trip bonus
            long_trip_points = 40
            points_breakdown['long_trip_bonus'] = long_trip_points
            total_points += long_trip_points
        
        # Efficiency bonus (points per km for good driving)
        if overall_assessment.get('final_risk_score', 50) < 40:
            efficiency_bonus = int(trip_distance_km * 2)
            points_breakdown['efficiency_bonus'] = efficiency_bonus
            total_points += efficiency_bonus
        
        # Get driver history for additional calculations
        driver_stats = self._get_driver_stats(driver_id)  # In production, get from database
        
        # Check for badges
        new_badges = self._check_advanced_badge_eligibility(
            behavior_assessment, geographic_assessment, contextual_assessment, driver_stats
        )
        badges_earned.extend(new_badges)
        
        # Check challenges
        completed_challenges = self._check_challenge_completion(
            assessment_result, driver_stats
        )
        challenges_completed.extend(completed_challenges)
        
        # Calculate level and progress
        updated_stats = self._update_driver_stats(driver_id, total_points, driver_stats)
        level_info = self._calculate_level_progress(updated_stats['total_points'])
        
        # Calculate improvement metrics
        improvement_metrics = self._calculate_improvement_metrics(
            assessment_result, driver_stats.get('historical_scores', [])
        )
        
        return {
            'points_earned': total_points,
            'total_points': updated_stats['total_points'],
            'points_breakdown': points_breakdown,
            'badges_earned': badges_earned,
            'level': level_info['current_level'],
            'level_name': level_info['level_name'],
            'next_level_points': level_info['points_to_next'],
            'level_progress_percent': level_info['progress_percent'],
            'challenges_completed': challenges_completed,
            'improvement_metrics': improvement_metrics,
            'safety_streak': updated_stats.get('safety_streak', 0),
            'risk_trend': improvement_metrics.get('risk_trend', 'stable')
        }
    
    def _check_advanced_badge_eligibility(self, behavior_assessment: Dict, 
                                        geographic_assessment: Dict, 
                                        contextual_assessment: Dict,
                                        driver_stats: Dict) -> List[str]:
        """
        Check eligibility for advanced badges based on expert model outputs
        """
        new_badges = []
        
        # Sensor Master badge
        behavior_score = behavior_assessment.get('behavior_score', 70)
        if behavior_score >= 90 and driver_stats.get('high_behavior_trips', 0) >= 9:
            if 'sensor_master' not in driver_stats.get('badges', []):
                new_badges.append('sensor_master')
        
        # Location Wise badge
        geo_risk = geographic_assessment.get('geographic_risk_score', 50)
        if geo_risk < 40 and driver_stats.get('low_risk_location_trips', 0) >= 14:
            if 'location_wise' not in driver_stats.get('badges', []):
                new_badges.append('location_wise')
        
        # Weather Warrior badge
        contextual_risk = contextual_assessment.get('contextual_risk_score', 50)
        weather_challenges = driver_stats.get('weather_challenge_trips', 0)
        if weather_challenges >= 5 and contextual_risk < 60:
            if 'weather_warrior' not in driver_stats.get('badges', []):
                new_badges.append('weather_warrior')
        
        # Ensemble Expert badge (all expert scores high)
        all_scores_high = (
            behavior_score >= 85 and
            (100 - geo_risk) >= 80 and  # Convert risk to safety score
            (100 - contextual_risk) >= 80
        )
        if all_scores_high and driver_stats.get('expert_excellence_trips', 0) >= 9:
            if 'ensemble_expert' not in driver_stats.get('badges', []):
                new_badges.append('ensemble_expert')
        
        return new_badges
    
    def _check_challenge_completion(self, assessment_result: Dict, driver_stats: Dict) -> List[str]:
        """
        Check if any challenges were completed
        """
        completed = []
        
        # Get current assessment scores
        behavior_assessment = assessment_result.get('expert_assessments', {}).get('behavior', {})
        overall_risk = assessment_result.get('overall_assessment', {}).get('final_risk_score', 50)
        
        # Smooth Week Challenge
        if behavior_assessment.get('driving_style') == 'SMOOTH':
            smooth_streak = driver_stats.get('smooth_driving_streak', 0) + 1
            if smooth_streak >= 7 and 'smooth_week' not in driver_stats.get('completed_challenges', []):
                completed.append('smooth_week')
        
        # Low Risk Month Challenge
        if overall_risk < 40:
            low_risk_streak = driver_stats.get('low_risk_streak', 0) + 1
            if low_risk_streak >= 30 and 'low_risk_month' not in driver_stats.get('completed_challenges', []):
                completed.append('low_risk_month')
        
        return completed
    
    def _get_driver_stats(self, driver_id: str) -> Dict[str, Any]:
        """
        Get driver statistics (in production, from database)
        """
        # Simulate driver stats
        return {
            'total_points': 2500,
            'badges': ['safe_driver'],
            'high_behavior_trips': 8,
            'low_risk_location_trips': 12,
            'weather_challenge_trips': 3,
            'expert_excellence_trips': 6,
            'safety_streak': 15,
            'smooth_driving_streak': 4,
            'low_risk_streak': 12,
            'completed_challenges': [],
            'historical_scores': [
                {'risk_score': 55, 'date': '2024-01-01'},
                {'risk_score': 48, 'date': '2024-01-15'},
                {'risk_score': 42, 'date': '2024-02-01'}
            ]
        }
    
    def _update_driver_stats(self, driver_id: str, points_earned: int, current_stats: Dict) -> Dict[str, Any]:
        """
        Update driver statistics with new points and achievements
        """
        updated_stats = current_stats.copy()
        updated_stats['total_points'] += points_earned
        
        # In production, save to database
        return updated_stats
    
    def _calculate_level_progress(self, total_points: int) -> Dict[str, Any]:
        """
        Calculate current level and progress to next level
        """
        current_level = 1
        current_level_name = "Telematics Novice"
        
        for level, info in self.levels.items():
            if total_points >= info['points_required']:
                current_level = level
                current_level_name = info['name']
        
        # Calculate progress to next level
        if current_level < max(self.levels.keys()):
            next_level_points = self.levels[current_level + 1]['points_required']
            current_level_points = self.levels[current_level]['points_required']
            points_to_next = next_level_points - total_points
            progress_percent = ((total_points - current_level_points) / 
                              (next_level_points - current_level_points)) * 100
        else:
            points_to_next = 0
            progress_percent = 100
        
        return {
            'current_level': current_level,
            'level_name': current_level_name,
            'points_to_next': max(0, points_to_next),
            'progress_percent': min(100, max(0, progress_percent))
        }
    
    def _calculate_improvement_metrics(self, current_assessment: Dict, historical_scores: List[Dict]) -> Dict[str, Any]:
        """
        Calculate improvement metrics based on historical data
        """
        if len(historical_scores) < 2:
            return {'trend': 'insufficient_data', 'improvement_percent': 0}
        
        current_risk = current_assessment.get('overall_assessment', {}).get('final_risk_score', 50)
        recent_risks = [score['risk_score'] for score in historical_scores[-3:]]
        
        if recent_risks:
            avg_recent = np.mean(recent_risks)
            improvement_percent = ((avg_recent - current_risk) / avg_recent) * 100
            
            if improvement_percent > 10:
                trend = 'improving'
            elif improvement_percent < -10:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            improvement_percent = 0
            trend = 'stable'
        
        return {
            'risk_trend': trend,
            'improvement_percent': improvement_percent,
            'current_risk': current_risk,
            'historical_average': np.mean([s['risk_score'] for s in historical_scores])
        }
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
