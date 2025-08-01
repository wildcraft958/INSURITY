"""
Expert 2: Geographic Risk Scoring Model
Analyzes location-based risk factors including accident history, road conditions
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

class GeoModel:
    """
    Geographic risk scoring model for location-based insurance assessment
    """
    
    def __init__(self):
        self.risk_zones = {}
        self.accident_history = {}
        self.weather_risk_factors = {}
    
    def calculate_zone_risk(self, latitude: float, longitude: float) -> float:
        """
        Calculate risk score based on geographic location
        """
        # Simplified risk calculation - replace with real data
        # Higher scores indicate higher risk
        
        # Urban vs rural classification
        urban_risk = self._classify_urban_rural(latitude, longitude)
        
        # Historical accident data for the area
        accident_risk = self._get_accident_risk(latitude, longitude)
        
        # Weather and road condition risks
        weather_risk = self._get_weather_risk(latitude, longitude)
        
        # Combine risk factors (weighted average)
        total_risk = (
            urban_risk * 0.4 +
            accident_risk * 0.4 +
            weather_risk * 0.2
        )
        
        return min(100, max(0, total_risk))
    
    def _classify_urban_rural(self, lat: float, lon: float) -> float:
        """
        Classify location as urban (higher risk) or rural (lower risk)
        """
        # Simplified classification - in reality, use proper geospatial data
        # Urban areas typically have higher accident rates
        return 65.0  # Default urban risk score
    
    def _get_accident_risk(self, lat: float, lon: float) -> float:
        """
        Get historical accident risk for the area
        """
        # In production, query accident database
        # Return risk score based on historical data
        return 50.0  # Default moderate risk
    
    def _get_weather_risk(self, lat: float, lon: float) -> float:
        """
        Get weather-related risk factors for the area
        """
        # Consider factors like:
        # - Precipitation frequency
        # - Snow/ice conditions
        # - Fog frequency
        # - Extreme weather events
        return 40.0  # Default moderate weather risk
    
    def get_route_risk_assessment(self, route_points: list) -> Dict[str, Any]:
        """
        Assess risk for an entire route
        """
        risk_scores = []
        high_risk_segments = []
        
        for i, point in enumerate(route_points):
            lat, lon = point['latitude'], point['longitude']
            risk = self.calculate_zone_risk(lat, lon)
            risk_scores.append(risk)
            
            if risk > 75:  # High risk threshold
                high_risk_segments.append({
                    'segment': i,
                    'risk_score': risk,
                    'coordinates': point
                })
        
        return {
            'average_risk': np.mean(risk_scores),
            'max_risk': max(risk_scores),
            'high_risk_segments': high_risk_segments,
            'total_segments': len(route_points)
        }
    
    def get_location_recommendations(self, risk_score: float) -> list:
        """
        Provide location-specific driving recommendations
        """
        recommendations = []
        
        if risk_score > 75:
            recommendations.extend([
                "Exercise extra caution in this high-risk area",
                "Reduce speed and increase following distance",
                "Avoid driving during peak accident hours if possible"
            ])
        elif risk_score > 50:
            recommendations.extend([
                "Be aware of moderate risk factors in this area",
                "Stay alert for local traffic patterns"
            ])
        else:
            recommendations.append("Generally safe area - maintain normal precautions")
        
        return recommendations
