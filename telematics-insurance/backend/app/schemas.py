"""
Pydantic request/response models for API schema validation
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class TelematicsData(BaseModel):
    """Request model for telematics driving data"""
    driver_id: str
    trip_id: str
    timestamp: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed: float = Field(..., ge=0)
    acceleration: float
    heading: float = Field(..., ge=0, le=360)
    phone_usage: bool = False
    
class WeatherData(BaseModel):
    """Weather conditions data"""
    temperature_c: float
    precipitation_mm: float = 0
    visibility_km: float = 10
    wind_speed_kmh: float = 0
    conditions: str = "clear"

class TrafficData(BaseModel):
    """Traffic conditions data"""
    density: str = Field(..., regex="^(light|moderate|heavy)$")
    average_speed_kmh: float
    speed_limit_kmh: float
    active_incidents: int = 0

class RiskAssessmentRequest(BaseModel):
    """Request model for comprehensive risk assessment"""
    driving_data: Dict[str, Any]
    location_data: Dict[str, float]
    weather_data: WeatherData
    traffic_data: TrafficData
    timestamp: datetime

class RiskScore(BaseModel):
    """Risk score response model"""
    score: float = Field(..., ge=0, le=100)
    category: str
    confidence: float = Field(..., ge=0, le=1)

class PremiumInfo(BaseModel):
    """Insurance premium information"""
    base_premium: float
    adjusted_premium: float
    adjustment_factor: float
    savings: float
    tier: str
    risk_score: float

class ExpertScores(BaseModel):
    """Individual expert model scores"""
    behavior: float
    geographic_risk: float
    contextual_risk: float

class Recommendations(BaseModel):
    """Driving recommendations from all models"""
    behavior: List[str]
    geographic: List[str]
    contextual: List[str]

class RiskAssessmentResponse(BaseModel):
    """Comprehensive risk assessment response"""
    overall_risk: RiskScore
    premium_information: PremiumInfo
    expert_scores: ExpertScores
    recommendations: Recommendations
    assessment_id: str
    timestamp: datetime

class GamificationRequest(BaseModel):
    """Request for gamification features"""
    driver_id: str
    trip_score: float
    distance_km: float
    safe_driving_events: int = 0

class GamificationResponse(BaseModel):
    """Gamification response with points and badges"""
    points_earned: int
    total_points: int
    badges_earned: List[str]
    level: str
    next_level_points: int

class ClaimsPredictionRequest(BaseModel):
    """Request for claims frequency/severity prediction"""
    driver_profile: Dict[str, Any]
    historical_data: List[Dict[str, Any]]
    coverage_type: str

class ClaimsPredictionResponse(BaseModel):
    """Claims prediction response"""
    frequency_prediction: float
    severity_prediction: float
    risk_factors: List[str]
    confidence_interval: Dict[str, float]

class HealthCheckResponse(BaseModel):
    """API health check response"""
    status: str
    timestamp: datetime
    version: str
    database_connected: bool
