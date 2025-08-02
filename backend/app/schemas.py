"""
Enhanced Pydantic request/response models for API schema validation
Updated to match comprehensive analysis from expert notebooks
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Enhanced Telematics Data Models
class SensorData(BaseModel):
    """Enhanced sensor data model for comprehensive analysis"""
    timestamp: datetime
    acc_x: float = Field(..., description="Acceleration X-axis (m/s²)")
    acc_y: float = Field(..., description="Acceleration Y-axis (m/s²)")  
    acc_z: float = Field(..., description="Acceleration Z-axis (m/s²)")
    gyro_x: float = Field(..., description="Gyroscope X-axis (rad/s)")
    gyro_y: float = Field(..., description="Gyroscope Y-axis (rad/s)")
    gyro_z: float = Field(..., description="Gyroscope Z-axis (rad/s)")
    speed: Optional[float] = Field(None, ge=0, description="Speed (km/h)")
    
class TelematicsData(BaseModel):
    """Enhanced request model for telematics driving data"""
    driver_id: str
    trip_id: str
    sensor_data: List[SensorData] = Field(..., description="Time series sensor data")
    location_data: Dict[str, float] = Field(..., description="Location information")
    trip_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional trip information")

class EnhancedWeatherData(BaseModel):
    """Comprehensive weather conditions data"""
    temperature_c: float = Field(..., description="Temperature in Celsius")
    precipitation_mm: float = Field(0, ge=0, description="Precipitation in millimeters")
    visibility_km: float = Field(10, ge=0, description="Visibility in kilometers")
    wind_speed_kmh: float = Field(0, ge=0, description="Wind speed in km/h")
    conditions: str = Field("clear", description="Weather condition description")
    humidity_percent: Optional[float] = Field(None, ge=0, le=100)
    pressure_hpa: Optional[float] = Field(None, ge=0)

class EnhancedTrafficData(BaseModel):
    """Comprehensive traffic conditions data"""
    density: str = Field(..., regex="^(light|moderate|heavy|severe)$")
    average_speed_kmh: float = Field(..., ge=0)
    speed_limit_kmh: float = Field(..., ge=0)
    active_incidents: int = Field(0, ge=0)
    construction_zones: int = Field(0, ge=0)
    traffic_flow_rate: Optional[float] = Field(None, ge=0)

class LocationData(BaseModel):
    """Enhanced location data with additional factors"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: Optional[float] = Field(None)
    road_type: Optional[str] = Field(None)
    speed_limit: Optional[int] = Field(None, ge=0)
    road_surface: Optional[str] = Field(None)
    lighting: Optional[str] = Field(None)
    traffic_signals: Optional[bool] = Field(None)

# Enhanced Assessment Request/Response Models
class ComprehensiveRiskAssessmentRequest(BaseModel):
    """Enhanced request model for comprehensive risk assessment"""
    telematics_data: TelematicsData
    weather_data: EnhancedWeatherData
    traffic_data: EnhancedTrafficData
    timestamp: datetime
    assessment_context: Optional[Dict[str, Any]] = Field(None)

class BehaviorAssessment(BaseModel):
    """Detailed behavior assessment results"""
    behavior_score: float = Field(..., ge=0, le=100)
    risk_level: str
    driving_style: str
    feature_scores: Dict[str, float]
    risk_factors: List[str]
    
class GeographicAssessment(BaseModel):
    """Detailed geographic risk assessment results"""
    geographic_risk_score: float = Field(..., ge=0, le=100)
    risk_category: str
    risk_components: Dict[str, Any]
    location_info: Dict[str, Any]

class ContextualAssessment(BaseModel):
    """Detailed contextual risk assessment results"""
    contextual_risk_score: float = Field(..., ge=0, le=100)
    risk_category: str
    risk_components: Dict[str, Any]
    interaction_bonus: float
    risk_factors: List[str]

class EnsembleDetails(BaseModel):
    """Ensemble model combination details"""
    risk_score: float = Field(..., ge=0, le=100)
    safety_score: float = Field(..., ge=0, le=100)
    risk_category: str
    weighted_components: Dict[str, float]
    interaction_effects: Dict[str, Any]
    expert_scores: Dict[str, float]

class EnhancedPremiumInfo(BaseModel):
    """Enhanced insurance premium information"""
    base_premium: float
    adjusted_premium: float
    adjustment_factor: float
    monthly_savings: float
    annual_savings: float
    additional_annual_cost: float
    tier: str
    risk_score: float
    discount_percentage: float
    surcharge_percentage: float

class ConfidenceMetrics(BaseModel):
    """Assessment confidence metrics"""
    behavior_confidence: float = Field(..., ge=0, le=1)
    geographic_confidence: float = Field(..., ge=0, le=1)
    contextual_confidence: float = Field(..., ge=0, le=1)
    overall_confidence: float = Field(..., ge=0, le=1)
    data_quality_score: float = Field(..., ge=0, le=1)

class ComprehensiveRecommendations(BaseModel):
    """Comprehensive recommendations from all models"""
    behavior: List[str]
    geographic: List[str]
    contextual: List[str]
    overall: List[str]

class OverallAssessment(BaseModel):
    """Overall risk assessment summary"""
    final_risk_score: float = Field(..., ge=0, le=100)
    safety_score: float = Field(..., ge=0, le=100)
    risk_category: str
    confidence: float = Field(..., ge=0, le=1)

class ExpertAssessments(BaseModel):
    """Individual expert model assessments"""
    behavior: BehaviorAssessment
    geographic: GeographicAssessment
    contextual: ContextualAssessment

class ModelMetadata(BaseModel):
    """Model metadata and versioning"""
    assessment_timestamp: datetime
    model_version: str
    expert_weights: Dict[str, float]

class ComprehensiveRiskAssessmentResponse(BaseModel):
    """Enhanced comprehensive risk assessment response"""
    overall_assessment: OverallAssessment
    expert_assessments: ExpertAssessments
    ensemble_details: EnsembleDetails
    premium_information: EnhancedPremiumInfo
    recommendations: ComprehensiveRecommendations
    confidence_metrics: ConfidenceMetrics
    model_metadata: ModelMetadata

# Route Assessment Models
class RoutePoint(BaseModel):
    """Individual route point data"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timestamp: Optional[datetime] = None

class RouteAssessmentRequest(BaseModel):
    """Route risk assessment request"""
    route_points: List[RoutePoint]
    driver_profile: Optional[Dict[str, Any]] = None

class RouteRiskSummary(BaseModel):
    """Route risk assessment summary"""
    average_risk: float
    max_risk: float
    min_risk: float
    risk_variance: float
    route_category: str

class RouteSegmentDetail(BaseModel):
    """Individual route segment details"""
    segment: int
    coordinates: RoutePoint
    risk_score: float
    risk_category: str

class HighRiskSegment(BaseModel):
    """High risk route segment information"""
    segment: int
    risk_score: float
    coordinates: RoutePoint
    risk_factors: Dict[str, Any]

class RouteAssessmentResponse(BaseModel):
    """Route risk assessment response"""
    route_risk_summary: RouteRiskSummary
    high_risk_segments: List[HighRiskSegment]
    segment_details: List[RouteSegmentDetail]
    total_segments: int
    high_risk_segment_count: int

# Trend Analysis Models
class RiskTrendAnalysis(BaseModel):
    """Risk trend analysis over time"""
    risk_trend: str
    behavior_trend: str
    current_risk: float
    average_risk: float
    risk_variance: float
    assessments_analyzed: int
    trend_confidence: float

class TierImprovementPotential(BaseModel):
    """Insurance tier improvement potential"""
    next_better_tier: Optional[str] = None
    points_reduction_needed: Optional[float] = None
    potential_savings: Optional[Dict[str, float]] = None
    message: Optional[str] = None

class TierExplanation(BaseModel):
    """Insurance tier explanation"""
    current_tier: str
    risk_score: float
    explanation: Dict[str, Any]
    improvement_potential: TierImprovementPotential
    improvement_suggestions: List[str]

# Enhanced Gamification Models
class AdvancedGamificationRequest(BaseModel):
    """Enhanced gamification features request"""
    driver_id: str
    assessment_result: ComprehensiveRiskAssessmentResponse
    trip_distance_km: float
    trip_duration_minutes: float

class AdvancedGamificationResponse(BaseModel):
    """Enhanced gamification response with detailed analytics"""
    points_earned: int
    total_points: int
    badges_earned: List[str]
    level: str
    next_level_points: int
    safety_streak: int
    improvement_metrics: Dict[str, float]
    challenges_completed: List[str]

# Claims Prediction Models (Enhanced)
class DriverProfile(BaseModel):
    """Comprehensive driver profile"""
    age: int = Field(..., ge=16, le=100)
    years_licensed: int = Field(..., ge=0)
    previous_claims: int = Field(..., ge=0)
    annual_mileage: float = Field(..., ge=0)
    vehicle_type: str
    risk_history: List[Dict[str, Any]]

class EnhancedClaimsPredictionRequest(BaseModel):
    """Enhanced claims frequency/severity prediction request"""
    driver_profile: DriverProfile
    historical_assessments: List[ComprehensiveRiskAssessmentResponse]
    coverage_type: str
    policy_details: Dict[str, Any]

class ClaimsPredictionResponse(BaseModel):
    """Enhanced claims prediction response"""
    frequency_prediction: float = Field(..., ge=0)
    severity_prediction: float = Field(..., ge=0)
    risk_factors: List[str]
    confidence_interval: Dict[str, float]
    recommendation: str

# System Health and Monitoring
class ModelPerformanceMetrics(BaseModel):
    """Model performance monitoring metrics"""
    behavior_model_accuracy: float
    geographic_model_accuracy: float
    contextual_model_accuracy: float
    ensemble_performance: float
    last_updated: datetime

class EnhancedHealthCheckResponse(BaseModel):
    """Enhanced API health check response"""
    status: str
    timestamp: datetime
    version: str
    database_connected: bool
    model_performance: ModelPerformanceMetrics
    system_load: Dict[str, float]

# Error Handling Models
class ValidationError(BaseModel):
    """Validation error details"""
    field: str
    message: str
    invalid_value: Any

class ErrorResponse(BaseModel):
    """Standardized error response"""
    error_type: str
    message: str
    details: Optional[List[ValidationError]] = None
    timestamp: datetime
    request_id: Optional[str] = None

# Batch Processing Models
class BatchAssessmentRequest(BaseModel):
    """Batch assessment request for multiple drivers/trips"""
    assessments: List[ComprehensiveRiskAssessmentRequest]
    batch_id: str
    priority: Optional[str] = Field("normal", regex="^(low|normal|high)$")

class BatchAssessmentResponse(BaseModel):
    """Batch assessment response"""
    batch_id: str
    total_assessments: int
    successful_assessments: int
    failed_assessments: int
    results: List[Union[ComprehensiveRiskAssessmentResponse, ErrorResponse]]
    processing_time_seconds: float
