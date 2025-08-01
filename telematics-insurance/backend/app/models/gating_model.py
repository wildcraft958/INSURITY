"""
Gating Model: Combines expert models into final insurance risk score
Implements ensemble learning approach for comprehensive risk assessment
"""
import numpy as np
from typing import Dict, Any, List
from .behavior_model import BehaviorModel
from .geo_model import GeoModel
from .context_model import ContextModel

class GatingModel:
    """
    Gating model that combines outputs from all expert models
    """
    
    def __init__(self):
        self.behavior_model = BehaviorModel()
        self.geo_model = GeoModel()
        self.context_model = ContextModel()
        
        # Model weights (can be learned from data)
        self.expert_weights = {
            'behavior': 0.4,
            'geographic': 0.3,
            'contextual': 0.3
        }
        
        # Risk thresholds for insurance pricing
        self.risk_thresholds = {
            'low': 30,
            'moderate': 60,
            'high': 80
        }
    
    def combine_expert_scores(self, 
                            behavior_score: float,
                            geo_risk: float,
                            context_risk: float) -> Dict[str, Any]:
        """
        Combine scores from all expert models using weighted ensemble
        """
        # Convert geo and context risk to safety scores (inverse of risk)
        geo_safety = 100 - geo_risk
        context_safety = 100 - context_risk
        
        # Weighted combination
        combined_safety_score = (
            behavior_score * self.expert_weights['behavior'] +
            geo_safety * self.expert_weights['geographic'] +
            context_safety * self.expert_weights['contextual']
        )
        
        # Convert back to risk score for insurance purposes
        risk_score = 100 - combined_safety_score
        
        return {
            'safety_score': combined_safety_score,
            'risk_score': risk_score,
            'risk_category': self._determine_risk_category(risk_score),
            'expert_contributions': {
                'behavior': behavior_score,
                'geographic': geo_safety,
                'contextual': context_safety
            }
        }
    
    def calculate_premium_adjustment(self, risk_score: float, base_premium: float = 1000) -> Dict[str, Any]:
        """
        Calculate insurance premium based on risk score
        """
        # Premium adjustment factors based on risk
        if risk_score < self.risk_thresholds['low']:
            adjustment_factor = 0.8  # 20% discount
            tier = "Preferred"
        elif risk_score < self.risk_thresholds['moderate']:
            adjustment_factor = 0.9  # 10% discount
            tier = "Standard Plus"
        elif risk_score < self.risk_thresholds['high']:
            adjustment_factor = 1.0  # Standard rate
            tier = "Standard"
        else:
            adjustment_factor = 1.3  # 30% surcharge
            tier = "High Risk"
        
        adjusted_premium = base_premium * adjustment_factor
        savings = base_premium - adjusted_premium
        
        return {
            'base_premium': base_premium,
            'adjusted_premium': adjusted_premium,
            'adjustment_factor': adjustment_factor,
            'savings': savings,
            'tier': tier,
            'risk_score': risk_score
        }
    
    def _determine_risk_category(self, risk_score: float) -> str:
        """
        Determine risk category based on score
        """
        if risk_score < self.risk_thresholds['low']:
            return "Low Risk"
        elif risk_score < self.risk_thresholds['moderate']:
            return "Moderate Risk"
        elif risk_score < self.risk_thresholds['high']:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def get_comprehensive_assessment(self, 
                                   driving_data: Dict[str, Any],
                                   location_data: Dict[str, Any],
                                   context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment using all expert models
        """
        # Get scores from each expert model
        behavior_score = self.behavior_model.score_behavior(driving_data)
        geo_risk = self.geo_model.calculate_zone_risk(
            location_data['latitude'], 
            location_data['longitude']
        )
        context_assessment = self.context_model.get_comprehensive_context_score(
            context_data['timestamp'],
            context_data['weather'],
            context_data['traffic']
        )
        
        # Combine expert scores
        combined_results = self.combine_expert_scores(
            behavior_score,
            geo_risk,
            context_assessment['overall_risk']
        )
        
        # Calculate premium
        premium_info = self.calculate_premium_adjustment(
            combined_results['risk_score']
        )
        
        # Get recommendations from all models
        behavior_recommendations = self.behavior_model.get_recommendations(behavior_score)
        geo_recommendations = self.geo_model.get_location_recommendations(geo_risk)
        context_recommendations = self.context_model.get_contextual_recommendations(context_assessment)
        
        return {
            'overall_assessment': combined_results,
            'premium_information': premium_info,
            'expert_scores': {
                'behavior': behavior_score,
                'geographic_risk': geo_risk,
                'contextual_risk': context_assessment['overall_risk']
            },
            'recommendations': {
                'behavior': behavior_recommendations,
                'geographic': geo_recommendations,
                'contextual': context_recommendations
            },
            'detailed_context': context_assessment
        }
    
    def update_model_weights(self, new_weights: Dict[str, float]):
        """
        Update expert model weights based on performance data
        """
        if abs(sum(new_weights.values()) - 1.0) < 0.001:  # Weights should sum to 1
            self.expert_weights = new_weights
        else:
            raise ValueError("Model weights must sum to 1.0")
    
    def get_model_performance_metrics(self) -> Dict[str, Any]:
        """
        Return current model configuration and performance metrics
        """
        return {
            'expert_weights': self.expert_weights,
            'risk_thresholds': self.risk_thresholds,
            'model_version': "1.0.0",
            'last_updated': "2025-08-02"
        }
