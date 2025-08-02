"""
Expert 2: Geographic Risk Scoring Model
Analyzes location-based risk factors using spatial clustering and accident history analysis
Based on comprehensive geographic analysis notebook findings
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import cdist

class GeoModel:
    """
    Advanced geographic risk scoring model for location-based insurance assessment
    Implements spatial analysis and clustering techniques
    """
    
    def __init__(self):
        self.grid_size = 0.01  # ~1km grid cells
        self.risk_zones = {}
        self.accident_clusters = {}
        self.grid_stats = None
        self.scaler = StandardScaler()
        
        # Risk classification thresholds
        self.risk_thresholds = {
            'very_low': 20,
            'low': 40,
            'moderate': 60,
            'high': 80
        }
        
        # Geographic risk factors
        self.location_risk_factors = {
            'urban_center': 35,
            'highway': 40,
            'rural': 15,
            'suburban': 25,
            'industrial': 30,
            'commercial': 28
        }
    
    def calculate_comprehensive_geographic_risk(self, 
                                             latitude: float, 
                                             longitude: float,
                                             additional_factors: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive geographic risk score using spatial analysis
        """
        # Validate coordinates
        if not self._validate_coordinates(latitude, longitude):
            return {'error': 'Invalid coordinates provided'}
        
        # Calculate grid-based risk
        grid_risk = self._calculate_grid_risk(latitude, longitude)
        
        # Calculate accident cluster proximity risk
        cluster_risk = self._calculate_cluster_proximity_risk(latitude, longitude)
        
        # Calculate road type and infrastructure risk
        infrastructure_risk = self._calculate_infrastructure_risk(latitude, longitude, additional_factors)
        
        # Calculate historical accident frequency
        historical_risk = self._calculate_historical_risk(latitude, longitude)
        
        # Weighted combination of risk factors
        weights = {'grid': 0.3, 'cluster': 0.25, 'infrastructure': 0.25, 'historical': 0.2}
        
        combined_risk = (
            grid_risk['risk_score'] * weights['grid'] +
            cluster_risk['risk_score'] * weights['cluster'] +
            infrastructure_risk['risk_score'] * weights['infrastructure'] +
            historical_risk['risk_score'] * weights['historical']
        )
        
        # Apply location-specific modifiers
        final_risk = self._apply_location_modifiers(combined_risk, latitude, longitude)
        
        return {
            'geographic_risk_score': final_risk,
            'risk_category': self._categorize_geographic_risk(final_risk),
            'risk_components': {
                'grid_based': grid_risk,
                'cluster_proximity': cluster_risk,
                'infrastructure': infrastructure_risk,
                'historical': historical_risk
            },
            'location_info': {
                'latitude': latitude,
                'longitude': longitude,
                'grid_cell': self._get_grid_cell(latitude, longitude),
                'location_type': self._classify_location_type(latitude, longitude)
            }
        }
    
    def _validate_coordinates(self, lat: float, lon: float) -> bool:
        """Validate latitude and longitude ranges"""
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    def _get_grid_cell(self, lat: float, lon: float) -> str:
        """Get grid cell identifier for coordinates"""
        lat_grid = np.round(lat / self.grid_size) * self.grid_size
        lon_grid = np.round(lon / self.grid_size) * self.grid_size
        return f"{lat_grid}_{lon_grid}"
    
    def _calculate_grid_risk(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Calculate risk based on grid cell accident statistics
        """
        grid_cell = self._get_grid_cell(lat, lon)
        
        # Simulate grid statistics (in production, query from database)
        base_risk = 30
        accident_frequency = self._get_grid_accident_frequency(lat, lon)
        casualty_rate = self._get_grid_casualty_rate(lat, lon)
        
        # Risk calculation based on accident patterns
        frequency_risk = min(40, accident_frequency * 2)
        casualty_risk = min(30, casualty_rate * 15)
        
        total_risk = base_risk + frequency_risk + casualty_risk
        
        return {
            'risk_score': min(100, total_risk),
            'accident_frequency': accident_frequency,
            'casualty_rate': casualty_rate,
            'grid_cell': grid_cell
        }
    
    def _calculate_cluster_proximity_risk(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Calculate risk based on proximity to accident clusters
        """
        # Simulate accident hotspots (in production, use real cluster data)
        hotspots = self._get_nearby_accident_clusters(lat, lon)
        
        base_risk = 20
        proximity_risk = 0
        nearest_cluster_distance = float('inf')
        
        if hotspots:
            # Calculate distance to nearest high-risk cluster
            distances = [self._haversine_distance(lat, lon, hs['lat'], hs['lon']) for hs in hotspots]
            nearest_distance = min(distances)
            nearest_cluster_distance = nearest_distance
            
            # Risk decreases with distance from cluster
            if nearest_distance < 0.5:  # Within 500m
                proximity_risk = 40
            elif nearest_distance < 1.0:  # Within 1km
                proximity_risk = 25
            elif nearest_distance < 2.0:  # Within 2km
                proximity_risk = 15
            elif nearest_distance < 5.0:  # Within 5km
                proximity_risk = 8
        
        return {
            'risk_score': base_risk + proximity_risk,
            'nearest_cluster_distance': nearest_cluster_distance,
            'nearby_clusters': len(hotspots),
            'proximity_risk': proximity_risk
        }
    
    def _calculate_infrastructure_risk(self, lat: float, lon: float, factors: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate risk based on road infrastructure and conditions
        """
        if not factors:
            factors = {}
        
        base_risk = 25
        infrastructure_factors = []
        
        # Road type analysis
        road_type = factors.get('road_type', 'urban')
        road_risk = self.location_risk_factors.get(road_type, 25)
        
        # Speed limit factor
        speed_limit = factors.get('speed_limit', 50)
        if speed_limit > 80:
            speed_risk = 20
            infrastructure_factors.append(f"High speed limit ({speed_limit} km/h)")
        elif speed_limit > 60:
            speed_risk = 10
        else:
            speed_risk = 0
        
        # Road surface conditions
        road_surface = factors.get('road_surface', 'good')
        surface_risks = {'poor': 25, 'fair': 15, 'good': 5, 'excellent': 0}
        surface_risk = surface_risks.get(road_surface, 5)
        
        # Lighting conditions
        lighting = factors.get('lighting', 'adequate')
        lighting_risks = {'poor': 20, 'limited': 15, 'adequate': 5, 'good': 0}
        lighting_risk = lighting_risks.get(lighting, 5)
        
        # Traffic control features
        traffic_signals = factors.get('traffic_signals', True)
        signal_risk = 0 if traffic_signals else 10
        
        total_risk = base_risk + road_risk + speed_risk + surface_risk + lighting_risk + signal_risk
        
        return {
            'risk_score': min(100, total_risk),
            'road_type': road_type,
            'road_risk': road_risk,
            'speed_limit_risk': speed_risk,
            'surface_risk': surface_risk,
            'lighting_risk': lighting_risk,
            'infrastructure_factors': infrastructure_factors
        }
    
    def _calculate_historical_risk(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Calculate risk based on historical accident data
        """
        # Simulate historical analysis (in production, query historical database)
        base_risk = 20
        
        # Get historical accident data for area
        historical_data = self._get_historical_accidents(lat, lon)
        
        # Calculate risk based on historical patterns
        accident_count = historical_data.get('total_accidents', 5)
        severity_avg = historical_data.get('average_severity', 2.0)
        casualties_total = historical_data.get('total_casualties', 8)
        
        # Risk components
        frequency_risk = min(30, accident_count * 2)
        severity_risk = min(25, (severity_avg - 1) * 12.5)
        casualty_risk = min(20, casualties_total)
        
        total_risk = base_risk + frequency_risk + severity_risk + casualty_risk
        
        return {
            'risk_score': min(100, total_risk),
            'historical_accidents': accident_count,
            'average_severity': severity_avg,
            'total_casualties': casualties_total,
            'time_period': 'last_5_years'
        }
    
    def _apply_location_modifiers(self, base_risk: float, lat: float, lon: float) -> float:
        """
        Apply location-specific risk modifiers
        """
        modified_risk = base_risk
        
        # Urban density modifier
        if self._is_urban_area(lat, lon):
            modified_risk *= 1.1  # 10% increase for urban areas
        
        # Highway proximity modifier
        if self._near_highway(lat, lon):
            modified_risk *= 1.08  # 8% increase near highways
        
        # Weather-prone area modifier
        if self._is_weather_prone_area(lat, lon):
            modified_risk *= 1.05  # 5% increase for weather-prone areas
        
        return min(100, modified_risk)
    
    def _get_grid_accident_frequency(self, lat: float, lon: float) -> float:
        """Get accident frequency for grid cell (simulated)"""
        # In production, query from spatial database
        return np.random.poisson(3) + 1
    
    def _get_grid_casualty_rate(self, lat: float, lon: float) -> float:
        """Get casualty rate for grid cell (simulated)"""
        return np.random.uniform(0.5, 3.0)
    
    def _get_nearby_accident_clusters(self, lat: float, lon: float) -> List[Dict]:
        """Get nearby accident clusters (simulated)"""
        # In production, query from cluster database
        clusters = []
        for i in range(np.random.poisson(2)):
            clusters.append({
                'lat': lat + np.random.uniform(-0.05, 0.05),
                'lon': lon + np.random.uniform(-0.05, 0.05),
                'severity': np.random.uniform(1, 5),
                'accident_count': np.random.poisson(10) + 5
            })
        return clusters
    
    def _get_historical_accidents(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get historical accident data for location (simulated)"""
        return {
            'total_accidents': np.random.poisson(8) + 2,
            'average_severity': np.random.uniform(1.5, 3.0),
            'total_casualties': np.random.poisson(12) + 3
        }
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate haversine distance between two points in kilometers"""
        R = 6371  # Earth's radius in kilometers
        
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        
        a = (np.sin(dlat/2)**2 + 
             np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c
    
    def _classify_location_type(self, lat: float, lon: float) -> str:
        """Classify location type (simulated)"""
        # In production, use geospatial databases
        location_types = ['urban', 'suburban', 'rural', 'highway', 'commercial', 'industrial']
        return np.random.choice(location_types, p=[0.3, 0.25, 0.2, 0.1, 0.1, 0.05])
    
    def _is_urban_area(self, lat: float, lon: float) -> bool:
        """Check if location is in urban area (simulated)"""
        return np.random.choice([True, False], p=[0.6, 0.4])
    
    def _near_highway(self, lat: float, lon: float) -> bool:
        """Check if location is near highway (simulated)"""
        return np.random.choice([True, False], p=[0.3, 0.7])
    
    def _is_weather_prone_area(self, lat: float, lon: float) -> bool:
        """Check if area is prone to severe weather (simulated)"""
        return np.random.choice([True, False], p=[0.4, 0.6])
    
    def _categorize_geographic_risk(self, risk_score: float) -> str:
        """Categorize geographic risk level"""
        if risk_score < self.risk_thresholds['very_low']:
            return "Very Low Risk"
        elif risk_score < self.risk_thresholds['low']:
            return "Low Risk"
        elif risk_score < self.risk_thresholds['moderate']:
            return "Moderate Risk"
        elif risk_score < self.risk_thresholds['high']:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def get_route_risk_assessment(self, route_points: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Assess risk for an entire route using comprehensive analysis
        """
        risk_scores = []
        high_risk_segments = []
        risk_details = []
        
        for i, point in enumerate(route_points):
            lat, lon = point['latitude'], point['longitude']
            risk_assessment = self.calculate_comprehensive_geographic_risk(lat, lon)
            
            if 'error' not in risk_assessment:
                risk_score = risk_assessment['geographic_risk_score']
                risk_scores.append(risk_score)
                
                risk_details.append({
                    'segment': i,
                    'coordinates': point,
                    'risk_score': risk_score,
                    'risk_category': risk_assessment['risk_category']
                })
                
                if risk_score > 75:  # High risk threshold
                    high_risk_segments.append({
                        'segment': i,
                        'risk_score': risk_score,
                        'coordinates': point,
                        'risk_factors': risk_assessment['risk_components']
                    })
        
        if not risk_scores:
            return {'error': 'No valid route points provided'}
        
        # Calculate route statistics
        average_risk = np.mean(risk_scores)
        max_risk = max(risk_scores)
        min_risk = min(risk_scores)
        risk_variance = np.var(risk_scores)
        
        # Categorize overall route risk
        if average_risk > 70:
            route_category = "High Risk Route"
        elif average_risk > 50:
            route_category = "Moderate Risk Route"
        else:
            route_category = "Low Risk Route"
        
        return {
            'route_risk_summary': {
                'average_risk': average_risk,
                'max_risk': max_risk,
                'min_risk': min_risk,
                'risk_variance': risk_variance,
                'route_category': route_category
            },
            'high_risk_segments': high_risk_segments,
            'segment_details': risk_details,
            'total_segments': len(route_points),
            'high_risk_segment_count': len(high_risk_segments)
        }
    
    def get_location_recommendations(self, risk_assessment: Dict[str, Any]) -> List[str]:
        """
        Provide location-specific driving recommendations based on comprehensive risk assessment
        """
        recommendations = []
        risk_score = risk_assessment.get('geographic_risk_score', 50)
        risk_components = risk_assessment.get('risk_components', {})
        location_info = risk_assessment.get('location_info', {})
        
        # General recommendations based on risk level
        if risk_score > 80:
            recommendations.extend([
                "Exercise extreme caution in this high-risk area",
                "Consider alternative routes if possible",
                "Reduce speed significantly below posted limits",
                "Maintain maximum alertness for potential hazards"
            ])
        elif risk_score > 60:
            recommendations.extend([
                "Drive with increased caution in this area",
                "Be aware of higher accident potential",
                "Maintain safe following distances"
            ])
        elif risk_score > 40:
            recommendations.extend([
                "Stay alert to local road conditions",
                "Follow standard safe driving practices"
            ])
        
        # Specific recommendations based on risk components
        grid_risk = risk_components.get('grid_based', {})
        if grid_risk.get('accident_frequency', 0) > 5:
            recommendations.append("Be aware of frequent accident history in this area")
        
        cluster_risk = risk_components.get('cluster_proximity', {})
        if cluster_risk.get('proximity_risk', 0) > 20:
            recommendations.append("You are near a known accident hotspot - exercise extra caution")
        
        infrastructure_risk = risk_components.get('infrastructure', {})
        if infrastructure_risk.get('speed_limit_risk', 0) > 15:
            recommendations.append("High-speed area - maintain vehicle control and awareness")
        if infrastructure_risk.get('lighting_risk', 0) > 10:
            recommendations.append("Poor lighting conditions - use headlights and reduce speed")
        
        # Location-specific recommendations
        location_type = location_info.get('location_type', 'unknown')
        if location_type == 'urban':
            recommendations.extend([
                "Watch for pedestrians and cyclists",
                "Be prepared for frequent stops and traffic signals"
            ])
        elif location_type == 'highway':
            recommendations.extend([
                "Maintain highway speeds and proper lane discipline",
                "Be aware of merging traffic and construction zones"
            ])
        elif location_type == 'rural':
            recommendations.extend([
                "Watch for wildlife and agricultural vehicles",
                "Be prepared for limited lighting and emergency services"
            ])
        
        return list(set(recommendations))  # Remove duplicates
    
    def analyze_location_patterns(self, location_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze patterns in location risk for a driver's typical routes
        """
        if not location_history:
            return {'error': 'No location history provided'}
        
        risk_scores = []
        location_types = []
        high_risk_locations = []
        
        for location in location_history:
            lat = location.get('latitude')
            lon = location.get('longitude')
            
            if lat is not None and lon is not None:
                risk_assessment = self.calculate_comprehensive_geographic_risk(lat, lon)
                
                if 'error' not in risk_assessment:
                    risk_score = risk_assessment['geographic_risk_score']
                    risk_scores.append(risk_score)
                    
                    location_type = risk_assessment['location_info']['location_type']
                    location_types.append(location_type)
                    
                    if risk_score > 70:
                        high_risk_locations.append({
                            'latitude': lat,
                            'longitude': lon,
                            'risk_score': risk_score,
                            'location_type': location_type
                        })
        
        if not risk_scores:
            return {'error': 'No valid location data found'}
        
        # Calculate patterns
        avg_risk = np.mean(risk_scores)
        risk_variance = np.var(risk_scores)
        most_common_location_type = max(set(location_types), key=location_types.count)
        
        # Risk trend analysis
        if len(risk_scores) > 10:
            recent_risk = np.mean(risk_scores[-10:])
            earlier_risk = np.mean(risk_scores[:-10])
            trend = 'increasing' if recent_risk > earlier_risk + 5 else 'decreasing' if recent_risk < earlier_risk - 5 else 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'risk_patterns': {
                'average_risk': avg_risk,
                'risk_variance': risk_variance,
                'risk_trend': trend,
                'high_risk_location_count': len(high_risk_locations)
            },
            'location_patterns': {
                'most_common_type': most_common_location_type,
                'location_type_distribution': {loc_type: location_types.count(loc_type) for loc_type in set(location_types)}
            },
            'high_risk_locations': high_risk_locations,
            'recommendations': self._get_pattern_recommendations(avg_risk, most_common_location_type, len(high_risk_locations))
        }
    
    def _get_pattern_recommendations(self, avg_risk: float, common_type: str, high_risk_count: int) -> List[str]:
        """Get recommendations based on location patterns"""
        recommendations = []
        
        if avg_risk > 60:
            recommendations.append("Consider planning routes through lower-risk areas when possible")
        
        if high_risk_count > 5:
            recommendations.append("You frequently travel through high-risk areas - maintain extra vigilance")
        
        if common_type == 'urban':
            recommendations.append("Focus on urban driving safety: pedestrians, cyclists, and traffic signals")
        elif common_type == 'highway':
            recommendations.append("Emphasize highway safety: proper following distance and lane discipline")
        elif common_type == 'rural':
            recommendations.append("Rural driving focus: wildlife awareness and limited emergency services")
        
        return recommendations
    
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
