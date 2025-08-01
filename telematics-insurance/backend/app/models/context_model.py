"""
Expert 3: Contextual Risk Scoring Model
Analyzes time-based, weather, and traffic context for risk assessment
"""
import numpy as np
import pandas as pd
from datetime import datetime, time
from typing import Dict, Any

class ContextModel:
    """
    Contextual risk scoring model for time, weather, and traffic analysis
    """
    
    def __init__(self):
        self.time_risk_factors = {
            'rush_hour_morning': (7, 9),
            'rush_hour_evening': (17, 19),
            'night_driving': (22, 6),
            'weekend_nights': 'weekend_night'
        }
    
    def calculate_temporal_risk(self, timestamp: datetime) -> float:
        """
        Calculate risk based on time of day and day of week
        """
        hour = timestamp.hour
        day_of_week = timestamp.weekday()  # 0=Monday, 6=Sunday
        
        risk_score = 30  # Base risk
        
        # Rush hour traffic increases risk
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            risk_score += 25
        
        # Night driving increases risk
        if hour >= 22 or hour <= 6:
            risk_score += 20
        
        # Weekend nights are particularly risky
        if day_of_week >= 5 and (hour >= 22 or hour <= 3):
            risk_score += 30
        
        # Friday evening rush is highest risk
        if day_of_week == 4 and 17 <= hour <= 20:
            risk_score += 15
        
        return min(100, max(0, risk_score))
    
    def calculate_weather_risk(self, weather_conditions: Dict[str, Any]) -> float:
        """
        Calculate risk based on weather conditions
        """
        base_risk = 20
        
        # Precipitation increases risk
        if weather_conditions.get('precipitation_mm', 0) > 0:
            base_risk += 25
        
        # Heavy rain significantly increases risk
        if weather_conditions.get('precipitation_mm', 0) > 10:
            base_risk += 25
        
        # Snow/ice conditions
        if weather_conditions.get('temperature_c', 20) < 0:
            base_risk += 30
        
        # Visibility issues
        if weather_conditions.get('visibility_km', 10) < 5:
            base_risk += 20
        
        # High winds
        if weather_conditions.get('wind_speed_kmh', 0) > 50:
            base_risk += 15
        
        return min(100, max(0, base_risk))
    
    def calculate_traffic_risk(self, traffic_data: Dict[str, Any]) -> float:
        """
        Calculate risk based on traffic conditions
        """
        base_risk = 25
        
        # Traffic density
        traffic_density = traffic_data.get('density', 'normal')
        if traffic_density == 'heavy':
            base_risk += 30
        elif traffic_density == 'moderate':
            base_risk += 15
        
        # Average speed vs speed limit
        avg_speed = traffic_data.get('average_speed_kmh', 50)
        speed_limit = traffic_data.get('speed_limit_kmh', 50)
        
        if avg_speed < speed_limit * 0.5:  # Slow traffic
            base_risk += 20
        elif avg_speed > speed_limit * 1.2:  # Fast traffic
            base_risk += 25
        
        # Accident reports in area
        active_incidents = traffic_data.get('active_incidents', 0)
        base_risk += min(20, active_incidents * 5)
        
        return min(100, max(0, base_risk))
    
    def get_comprehensive_context_score(self, 
                                      timestamp: datetime,
                                      weather: Dict[str, Any],
                                      traffic: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine all contextual factors for comprehensive risk assessment
        """
        temporal_risk = self.calculate_temporal_risk(timestamp)
        weather_risk = self.calculate_weather_risk(weather)
        traffic_risk = self.calculate_traffic_risk(traffic)
        
        # Weighted combination of risk factors
        combined_risk = (
            temporal_risk * 0.3 +
            weather_risk * 0.4 +
            traffic_risk * 0.3
        )
        
        return {
            'overall_risk': combined_risk,
            'temporal_risk': temporal_risk,
            'weather_risk': weather_risk,
            'traffic_risk': traffic_risk,
            'risk_category': self._categorize_risk(combined_risk)
        }
    
    def _categorize_risk(self, risk_score: float) -> str:
        """
        Categorize risk level for easier interpretation
        """
        if risk_score >= 75:
            return "High Risk"
        elif risk_score >= 50:
            return "Moderate Risk"
        elif risk_score >= 25:
            return "Low-Moderate Risk"
        else:
            return "Low Risk"
    
    def get_contextual_recommendations(self, context_score: Dict[str, Any]) -> list:
        """
        Provide context-specific driving recommendations
        """
        recommendations = []
        overall_risk = context_score['overall_risk']
        
        if context_score['weather_risk'] > 60:
            recommendations.extend([
                "Reduce speed due to weather conditions",
                "Increase following distance",
                "Use headlights and ensure good visibility"
            ])
        
        if context_score['traffic_risk'] > 60:
            recommendations.extend([
                "Be extra alert in heavy traffic",
                "Maintain safe following distance",
                "Watch for sudden lane changes"
            ])
        
        if context_score['temporal_risk'] > 60:
            recommendations.extend([
                "Exercise caution during high-risk time periods",
                "Consider alternative routes if possible",
                "Stay extra alert for impaired or aggressive drivers"
            ])
        
        if overall_risk < 30:
            recommendations.append("Good conditions for driving - maintain normal safety practices")
        
        return recommendations
