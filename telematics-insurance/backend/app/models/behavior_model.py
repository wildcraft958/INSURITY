"""
Expert 1: Driver Behavior Scoring Model
Analyzes driving patterns, acceleration, braking, and speed behavior
"""
import numpy as np
import pandas as pd
from typing import Dict, Any

class BehaviorModel:
    """
    Driver behavior scoring model for telematics data
    """
    
    def __init__(self):
        self.model = None
        self.feature_columns = [
            'avg_speed', 'max_speed', 'speed_variance',
            'harsh_acceleration_count', 'harsh_braking_count',
            'cornering_score', 'phone_usage_duration',
            'night_driving_percentage', 'highway_percentage'
        ]
    
    def preprocess_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess telematics data for behavior scoring
        """
        processed = data.copy()
        
        # Calculate behavior metrics
        processed['speed_variance'] = processed['speed'].var()
        processed['harsh_acceleration_count'] = (processed['acceleration'] > 2.5).sum()
        processed['harsh_braking_count'] = (processed['acceleration'] < -2.5).sum()
        
        return processed[self.feature_columns]
    
    def score_behavior(self, features: Dict[str, Any]) -> float:
        """
        Calculate driver behavior score (0-100, higher is better)
        """
        # Simplified scoring logic - replace with trained model
        base_score = 100
        
        # Penalize risky behaviors
        if features.get('harsh_acceleration_count', 0) > 5:
            base_score -= 10
        if features.get('harsh_braking_count', 0) > 5:
            base_score -= 10
        if features.get('max_speed', 0) > 80:
            base_score -= 15
        if features.get('phone_usage_duration', 0) > 300:  # 5 minutes
            base_score -= 20
        
        return max(0, min(100, base_score))
    
    def get_recommendations(self, score: float) -> list:
        """
        Provide driving improvement recommendations
        """
        recommendations = []
        
        if score < 60:
            recommendations.extend([
                "Avoid harsh acceleration and braking",
                "Maintain safe following distances",
                "Reduce phone usage while driving"
            ])
        elif score < 80:
            recommendations.extend([
                "Monitor your speed in different zones",
                "Practice smooth acceleration and braking"
            ])
        else:
            recommendations.append("Great driving! Keep up the safe habits")
        
        return recommendations
