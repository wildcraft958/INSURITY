"""
Expert 3: Contextual Risk Scoring Model
Analyzes temporal patterns, weather conditions, and traffic context for comprehensive risk assessment
Based on contextual analysis notebook findings
"""
import numpy as np
import pandas as pd
from datetime import datetime, time
from typing import Dict, Any, List
from sklearn.preprocessing import StandardScaler

class ContextModel:
    """
    Advanced contextual risk scoring model for comprehensive risk assessment
    Incorporates temporal, weather, and traffic analysis
    """
    
    def __init__(self):
        self.risk_thresholds = {
            'low': 30,
            'moderate': 60,
            'high': 80
        }
        
        # Risk factor weights based on analysis
        self.weights = {
            'temporal': 0.4,
            'weather': 0.35,
            'traffic': 0.25
        }
        
        # Temporal risk patterns from analysis
        self.temporal_patterns = {
            'rush_hour_morning': (7, 9, 25),
            'rush_hour_evening': (17, 19, 30),
            'night_driving': (22, 6, 35),
            'weekend_nights': (22, 3, 40),
            'friday_evening': (17, 20, 35)
        }
        
        # Weather risk factors
        self.weather_risk_factors = {
            'clear': 0,
            'rain': 25,
            'heavy_rain': 40,
            'snow': 45,
            'fog': 35,
            'ice': 50
        }
    
    def calculate_comprehensive_contextual_risk(self, 
                                              timestamp: datetime,
                                              weather_data: Dict[str, Any],
                                              traffic_data: Dict[str, Any],
                                              location_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive contextual risk score combining all factors
        """
        # Calculate individual risk components
        temporal_risk = self.calculate_temporal_risk(timestamp)
        weather_risk = self.calculate_weather_risk(weather_data)
        traffic_risk = self.calculate_traffic_risk(traffic_data)
        
        # Weighted combination
        combined_risk = (
            temporal_risk['risk_score'] * self.weights['temporal'] +
            weather_risk['risk_score'] * self.weights['weather'] +
            traffic_risk['risk_score'] * self.weights['traffic']
        )
        
        # Calculate risk interactions
        interaction_risk = self._calculate_risk_interactions(
            temporal_risk, weather_risk, traffic_risk, timestamp
        )
        
        # Final risk score with interactions
        final_risk = min(100, combined_risk + interaction_risk)
        
        return {
            'contextual_risk_score': final_risk,
            'risk_category': self._categorize_risk(final_risk),
            'risk_components': {
                'temporal': temporal_risk,
                'weather': weather_risk,
                'traffic': traffic_risk
            },
            'interaction_bonus': interaction_risk,
            'risk_factors': self._identify_primary_risk_factors(
                temporal_risk, weather_risk, traffic_risk
            )
        }
    
    def calculate_temporal_risk(self, timestamp: datetime) -> Dict[str, Any]:
        """
        Enhanced temporal risk calculation based on analysis patterns
        """
        hour = timestamp.hour
        day_of_week = timestamp.weekday()  # 0=Monday, 6=Sunday
        month = timestamp.month
        
        base_risk = 20
        risk_factors = []
        
        # Time period analysis
        time_period = self._get_time_period(hour)
        period_risks = {
            'Night': 25,
            'Morning': 15,
            'Afternoon': 10, 
            'Evening': 20
        }
        
        period_risk = period_risks.get(time_period, 15)
        base_risk += period_risk
        
        # Rush hour analysis
        if self._is_rush_hour(hour):
            rush_penalty = 25
            base_risk += rush_penalty
            risk_factors.append(f"Rush hour traffic (+{rush_penalty})")
        
        # Weekend analysis
        if self._is_weekend(day_of_week):
            if 22 <= hour <= 23 or 0 <= hour <= 3:
                weekend_penalty = 30
                base_risk += weekend_penalty
                risk_factors.append(f"Weekend night driving (+{weekend_penalty})")
            else:
                base_risk += 5  # General weekend risk
        
        # Special day patterns
        if day_of_week == 4:  # Friday
            if 17 <= hour <= 20:
                friday_penalty = 15
                base_risk += friday_penalty
                risk_factors.append(f"Friday evening (+{friday_penalty})")
        
        # Seasonal factors
        if month in [12, 1, 2]:  # Winter months
            base_risk += 10
            risk_factors.append("Winter season (+10)")
        
        return {
            'risk_score': min(100, base_risk),
            'time_period': time_period,
            'is_rush_hour': self._is_rush_hour(hour),
            'is_weekend': self._is_weekend(day_of_week),
            'risk_factors': risk_factors
        }
    
    def calculate_weather_risk(self, weather_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced weather risk calculation with multiple factors
        """
        base_risk = 15
        risk_factors = []
        
        # Precipitation analysis
        precipitation = weather_conditions.get('precipitation_mm', 0)
        if precipitation > 0:
            if precipitation <= 2:
                precip_risk = 15
                condition = "Light rain"
            elif precipitation <= 10:
                precip_risk = 25
                condition = "Moderate rain"
            else:
                precip_risk = 40
                condition = "Heavy rain"
            
            base_risk += precip_risk
            risk_factors.append(f"{condition} (+{precip_risk})")
        
        # Temperature analysis
        temperature = weather_conditions.get('temperature_c', 20)
        if temperature < 0:
            temp_risk = 30
            base_risk += temp_risk
            risk_factors.append(f"Freezing conditions (+{temp_risk})")
        elif temperature < 5:
            temp_risk = 15
            base_risk += temp_risk
            risk_factors.append(f"Cold conditions (+{temp_risk})")
        
        # Visibility analysis
        visibility = weather_conditions.get('visibility_km', 10)
        if visibility < 1:
            vis_risk = 40
            risk_factors.append(f"Very poor visibility (+{vis_risk})")
        elif visibility < 5:
            vis_risk = 25
            risk_factors.append(f"Poor visibility (+{vis_risk})")
        elif visibility < 10:
            vis_risk = 10
            risk_factors.append(f"Reduced visibility (+{vis_risk})")
        else:
            vis_risk = 0
        
        base_risk += vis_risk
        
        # Wind analysis
        wind_speed = weather_conditions.get('wind_speed_kmh', 0)
        if wind_speed > 50:
            wind_risk = 20
            base_risk += wind_risk
            risk_factors.append(f"High winds (+{wind_risk})")
        elif wind_speed > 30:
            wind_risk = 10
            base_risk += wind_risk
            risk_factors.append(f"Moderate winds (+{wind_risk})")
        
        # Weather condition type
        condition = weather_conditions.get('conditions', 'clear').lower()
        condition_risk = self.weather_risk_factors.get(condition, 0)
        if condition_risk > 0:
            base_risk += condition_risk
            risk_factors.append(f"{condition.title()} conditions (+{condition_risk})")
        
        return {
            'risk_score': min(100, base_risk),
            'precipitation_mm': precipitation,
            'temperature_c': temperature,
            'visibility_km': visibility,
            'wind_speed_kmh': wind_speed,
            'conditions': condition,
            'risk_factors': risk_factors
        }
    
    def calculate_traffic_risk(self, traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced traffic risk assessment with comprehensive factors
        """
        base_risk = 20
        risk_factors = []
        
        # Traffic density analysis
        density = traffic_data.get('density', 'moderate').lower()
        density_risks = {'light': 5, 'moderate': 15, 'heavy': 30, 'severe': 45}
        density_risk = density_risks.get(density, 15)
        base_risk += density_risk
        
        if density_risk > 15:
            risk_factors.append(f"{density.title()} traffic (+{density_risk})")
        
        # Speed analysis
        avg_speed = traffic_data.get('average_speed_kmh', 50)
        speed_limit = traffic_data.get('speed_limit_kmh', 50)
        
        if speed_limit > 0:
            speed_ratio = avg_speed / speed_limit
            
            if speed_ratio < 0.3:  # Very slow traffic
                speed_risk = 25
                risk_factors.append(f"Very slow traffic (+{speed_risk})")
            elif speed_ratio < 0.5:  # Slow traffic
                speed_risk = 15
                risk_factors.append(f"Slow traffic (+{speed_risk})")
            elif speed_ratio > 1.3:  # Fast traffic
                speed_risk = 20
                risk_factors.append(f"Fast traffic (+{speed_risk})")
            else:
                speed_risk = 0
            
            base_risk += speed_risk
        
        # Active incidents
        incidents = traffic_data.get('active_incidents', 0)
        if incidents > 0:
            incident_risk = min(30, incidents * 10)
            base_risk += incident_risk
            risk_factors.append(f"Active incidents (+{incident_risk})")
        
        # Construction zones
        construction = traffic_data.get('construction_zones', 0)
        if construction > 0:
            construction_risk = min(20, construction * 15)
            base_risk += construction_risk
            risk_factors.append(f"Construction zones (+{construction_risk})")
        
        return {
            'risk_score': min(100, base_risk),
            'density': density,
            'speed_ratio': avg_speed / max(speed_limit, 1),
            'incidents': incidents,
            'construction': construction,
            'risk_factors': risk_factors
        }
    
    def _calculate_risk_interactions(self, temporal: Dict, weather: Dict, 
                                   traffic: Dict, timestamp: datetime) -> float:
        """
        Calculate risk interactions between different factors
        """
        interaction_bonus = 0
        
        # Bad weather + night driving
        if weather['risk_score'] > 40 and temporal['time_period'] == 'Night':
            interaction_bonus += 15
        
        # Heavy traffic + bad weather
        if traffic['risk_score'] > 50 and weather['risk_score'] > 40:
            interaction_bonus += 10
        
        # Rush hour + bad weather
        if temporal['is_rush_hour'] and weather['risk_score'] > 30:
            interaction_bonus += 12
        
        # Weekend night + any other high risk factor
        if (temporal['is_weekend'] and temporal['time_period'] == 'Night' and
            (weather['risk_score'] > 30 or traffic['risk_score'] > 40)):
            interaction_bonus += 8
        
        return interaction_bonus
    
    def _get_time_period(self, hour: int) -> str:
        """Get time period classification"""
        if 0 <= hour < 6:
            return 'Night'
        elif 6 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 18:
            return 'Afternoon'
        else:
            return 'Evening'
    
    def _is_rush_hour(self, hour: int) -> bool:
        """Check if time is during rush hour"""
        return (7 <= hour <= 9) or (17 <= hour <= 19)
    
    def _is_weekend(self, day_of_week: int) -> bool:
        """Check if day is weekend (Saturday=5, Sunday=6)"""
        return day_of_week >= 5
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize overall risk level"""
        if risk_score < self.risk_thresholds['low']:
            return "Low Risk"
        elif risk_score < self.risk_thresholds['moderate']:
            return "Moderate Risk"
        elif risk_score < self.risk_thresholds['high']:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def _identify_primary_risk_factors(self, temporal: Dict, weather: Dict, traffic: Dict) -> List[str]:
        """Identify primary contributing risk factors"""
        all_factors = []
        all_factors.extend(temporal.get('risk_factors', []))
        all_factors.extend(weather.get('risk_factors', []))
        all_factors.extend(traffic.get('risk_factors', []))
        
        return all_factors
    
    def get_contextual_recommendations(self, risk_assessment: Dict[str, Any]) -> List[str]:
        """
        Provide contextual driving recommendations based on risk assessment
        """
        recommendations = []
        risk_score = risk_assessment['contextual_risk_score']
        risk_factors = risk_assessment['risk_factors']
        
        # General recommendations based on risk level
        if risk_score > 80:
            recommendations.extend([
                "Consider delaying non-essential trips",
                "Use extreme caution if driving is necessary",
                "Reduce speed significantly below normal",
                "Increase following distance substantially"
            ])
        elif risk_score > 60:
            recommendations.extend([
                "Exercise extra caution while driving",
                "Reduce speed and increase following distance",
                "Avoid aggressive maneuvers"
            ])
        elif risk_score > 40:
            recommendations.extend([
                "Stay alert to changing conditions",
                "Drive defensively"
            ])
        
        # Specific recommendations based on risk factors
        temporal_factors = [f for f in risk_factors if any(word in f.lower() for word in ['rush', 'night', 'weekend', 'friday'])]
        weather_factors = [f for f in risk_factors if any(word in f.lower() for word in ['rain', 'snow', 'fog', 'wind', 'visibility'])]
        traffic_factors = [f for f in risk_factors if any(word in f.lower() for word in ['traffic', 'incident', 'construction'])]
        
        if temporal_factors:
            recommendations.extend([
                "Plan for extra travel time during peak hours",
                "Consider alternative routes during high-risk times"
            ])
        
        if weather_factors:
            recommendations.extend([
                "Ensure vehicle is properly maintained for weather conditions",
                "Use appropriate lighting and visibility aids",
                "Check weather updates before traveling"
            ])
        
        if traffic_factors:
            recommendations.extend([
                "Monitor traffic reports for real-time updates",
                "Consider public transportation alternatives",
                "Allow extra time for traffic delays"
            ])
        
        return list(set(recommendations))  # Remove duplicates
    
    def calculate_contextual_score_trend(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate contextual risk trends over time
        """
        if not historical_data:
            return {'trend': 'stable', 'average_risk': 50}
        
        risk_scores = [data['contextual_risk_score'] for data in historical_data]
        
        # Calculate trend
        if len(risk_scores) > 1:
            recent_avg = np.mean(risk_scores[-5:])  # Last 5 data points
            earlier_avg = np.mean(risk_scores[:-5]) if len(risk_scores) > 5 else np.mean(risk_scores)
            
            if recent_avg > earlier_avg + 10:
                trend = 'increasing'
            elif recent_avg < earlier_avg - 10:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'trend': trend,
            'average_risk': np.mean(risk_scores),
            'max_risk': max(risk_scores),
            'min_risk': min(risk_scores),
            'risk_variance': np.var(risk_scores)
        }
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
