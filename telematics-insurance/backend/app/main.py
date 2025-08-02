"""
Enhanced FastAPI application for comprehensive telematics insurance platform
Updated to support advanced expert models and comprehensive risk assessment
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List
import uvicorn

from .schemas import (
    ComprehensiveRiskAssessmentRequest,
    ComprehensiveRiskAssessmentResponse,
    RouteAssessmentRequest,
    RouteAssessmentResponse,
    AdvancedGamificationRequest,
    AdvancedGamificationResponse,
    EnhancedClaimsPredictionRequest,
    ClaimsPredictionResponse,
    EnhancedHealthCheckResponse,
    RiskTrendAnalysis,
    TierExplanation,
    BatchAssessmentRequest,
    BatchAssessmentResponse,
    ErrorResponse
)

from .models.gating_model import GatingModel
from .services.gamification import GamificationService
from .services.claims import ClaimsService
from .utils.logging import setup_logging

# Initialize logging
logger = setup_logging()

app = FastAPI(
    title="Enhanced Telematics Insurance API",
    description="AI-powered telematics insurance platform with comprehensive expert models",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models and services
gating_model = GatingModel()
gamification_service = GamificationService()
claims_service = ClaimsService()

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Enhanced Telematics Insurance API is running",
        "version": "2.0.0",
        "features": [
            "Comprehensive behavior analysis from sensor data",
            "Advanced geographic risk assessment",
            "Contextual risk scoring with weather and traffic",
            "Ensemble model with interaction effects",
            "Route risk assessment",
            "Trend analysis and tier explanations",
            "Enhanced gamification features"
        ]
    }

@app.post("/assess/comprehensive", response_model=ComprehensiveRiskAssessmentResponse)
async def comprehensive_risk_assessment(request: ComprehensiveRiskAssessmentRequest):
    """
    Perform comprehensive risk assessment using all expert models
    """
    try:
        # Prepare data for expert models
        behavior_data = {
            'sensor_data': [sensor.dict() for sensor in request.telematics_data.sensor_data],
            'trip_metadata': request.telematics_data.trip_metadata or {}
        }
        
        location_data = {
            'latitude': request.telematics_data.location_data.get('latitude'),
            'longitude': request.telematics_data.location_data.get('longitude'),
            'additional_factors': {
                'road_type': request.assessment_context.get('road_type') if request.assessment_context else None,
                'speed_limit': request.assessment_context.get('speed_limit') if request.assessment_context else None
            }
        }
        
        context_data = {
            'timestamp': request.timestamp,
            'weather_data': request.weather_data.dict(),
            'traffic_data': request.traffic_data.dict(),
            'location_data': location_data,
            'base_premium': request.assessment_context.get('base_premium', 1000) if request.assessment_context else 1000
        }
        
        # Perform comprehensive assessment
        assessment_result = gating_model.comprehensive_risk_assessment(
            behavior_data, location_data, context_data
        )
        
        logger.info(f"Comprehensive assessment completed for driver {request.telematics_data.driver_id}")
        
        return ComprehensiveRiskAssessmentResponse(**assessment_result)
        
    except Exception as e:
        logger.error(f"Error in comprehensive assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

@app.post("/assess/route", response_model=RouteAssessmentResponse)
async def route_risk_assessment(request: RouteAssessmentRequest):
    """
    Assess risk for an entire route
    """
    try:
        route_points = [point.dict() for point in request.route_points]
        
        route_assessment = gating_model.geo_model.get_route_risk_assessment(route_points)
        
        if 'error' in route_assessment:
            raise HTTPException(status_code=400, detail=route_assessment['error'])
        
        logger.info(f"Route assessment completed for {len(route_points)} points")
        
        return RouteAssessmentResponse(**route_assessment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in route assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Route assessment failed: {str(e)}")

@app.post("/gamification/advanced", response_model=AdvancedGamificationResponse)
async def advanced_gamification(request: AdvancedGamificationRequest):
    """
    Enhanced gamification features with detailed analytics
    """
    try:
        gamification_result = gamification_service.calculate_advanced_gamification(
            request.driver_id,
            request.assessment_result.dict(),
            request.trip_distance_km,
            request.trip_duration_minutes
        )
        
        logger.info(f"Advanced gamification calculated for driver {request.driver_id}")
        
        return AdvancedGamificationResponse(**gamification_result)
        
    except Exception as e:
        logger.error(f"Error in advanced gamification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gamification calculation failed: {str(e)}")

@app.post("/claims/predict", response_model=ClaimsPredictionResponse)
async def predict_claims(request: EnhancedClaimsPredictionRequest):
    """
    Predict claims frequency and severity using enhanced models
    """
    try:
        prediction_result = claims_service.predict_enhanced_claims(
            request.driver_profile.dict(),
            [assessment.dict() for assessment in request.historical_assessments],
            request.coverage_type,
            request.policy_details
        )
        
        logger.info(f"Claims prediction completed for driver age {request.driver_profile.age}")
        
        return ClaimsPredictionResponse(**prediction_result)
        
    except Exception as e:
        logger.error(f"Error in claims prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Claims prediction failed: {str(e)}")

@app.post("/analysis/trends", response_model=RiskTrendAnalysis)
async def analyze_risk_trends(historical_assessments: List[ComprehensiveRiskAssessmentResponse]):
    """
    Analyze risk trends over time from historical assessments
    """
    try:
        if len(historical_assessments) < 2:
            raise HTTPException(
                status_code=400, 
                detail="At least 2 historical assessments required for trend analysis"
            )
        
        trend_analysis = gating_model.analyze_risk_trends(
            [assessment.dict() for assessment in historical_assessments]
        )
        
        logger.info(f"Trend analysis completed for {len(historical_assessments)} assessments")
        
        return RiskTrendAnalysis(**trend_analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in trend analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")

@app.get("/insurance/tier-explanation/{tier}/{risk_score}", response_model=TierExplanation)
async def get_tier_explanation(tier: str, risk_score: float):
    """
    Get detailed explanation of insurance tier assignment
    """
    try:
        if not 0 <= risk_score <= 100:
            raise HTTPException(status_code=400, detail="Risk score must be between 0 and 100")
        
        explanation = gating_model.get_insurance_tier_explanation(tier, risk_score)
        
        logger.info(f"Tier explanation provided for {tier} tier with risk score {risk_score}")
        
        return TierExplanation(**explanation)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tier explanation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tier explanation failed: {str(e)}")

@app.post("/assess/batch", response_model=BatchAssessmentResponse)
async def batch_assessment(request: BatchAssessmentRequest, background_tasks: BackgroundTasks):
    """
    Process multiple assessments in batch
    """
    try:
        # For now, process synchronously (in production, use background tasks)
        results = []
        successful = 0
        failed = 0
        start_time = datetime.now()
        
        for assessment_request in request.assessments:
            try:
                # Process individual assessment
                behavior_data = {
                    'sensor_data': [sensor.dict() for sensor in assessment_request.telematics_data.sensor_data],
                    'trip_metadata': assessment_request.telematics_data.trip_metadata or {}
                }
                
                location_data = {
                    'latitude': assessment_request.telematics_data.location_data.get('latitude'),
                    'longitude': assessment_request.telematics_data.location_data.get('longitude')
                }
                
                context_data = {
                    'timestamp': assessment_request.timestamp,
                    'weather_data': assessment_request.weather_data.dict(),
                    'traffic_data': assessment_request.traffic_data.dict(),
                    'location_data': location_data
                }
                
                assessment_result = gating_model.comprehensive_risk_assessment(
                    behavior_data, location_data, context_data
                )
                
                results.append(ComprehensiveRiskAssessmentResponse(**assessment_result))
                successful += 1
                
            except Exception as e:
                error_response = ErrorResponse(
                    error_type="assessment_error",
                    message=str(e),
                    timestamp=datetime.now()
                )
                results.append(error_response)
                failed += 1
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        batch_response = {
            'batch_id': request.batch_id,
            'total_assessments': len(request.assessments),
            'successful_assessments': successful,
            'failed_assessments': failed,
            'results': results,
            'processing_time_seconds': processing_time
        }
        
        logger.info(f"Batch assessment completed: {successful} successful, {failed} failed")
        
        return BatchAssessmentResponse(**batch_response)
        
    except Exception as e:
        logger.error(f"Error in batch assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch assessment failed: {str(e)}")

@app.get("/health", response_model=EnhancedHealthCheckResponse)
async def enhanced_health_check():
    """
    Enhanced health check with model performance metrics
    """
    try:
        # Simulate model performance metrics (in production, get from monitoring)
        model_performance = {
            'behavior_model_accuracy': 0.89,
            'geographic_model_accuracy': 0.85,
            'contextual_model_accuracy': 0.87,
            'ensemble_performance': 0.91,
            'last_updated': datetime.now()
        }
        
        system_load = {
            'cpu_usage_percent': 45.2,
            'memory_usage_percent': 62.1,
            'disk_usage_percent': 38.7
        }
        
        health_response = {
            'status': 'healthy',
            'timestamp': datetime.now(),
            'version': '2.0.0',
            'database_connected': True,  # In production, check actual DB connection
            'model_performance': model_performance,
            'system_load': system_load
        }
        
        return EnhancedHealthCheckResponse(**health_response)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
