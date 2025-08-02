"""
Gating Model: Combines expert models into final insurance risk score
Implements advanced ensemble learning approach for comprehensive risk assessment
Based on ensemble analysis from gating notebook
"""
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from .behavior_model import BehaviorModel
from .geo_model import GeoModel
from .context_model import ContextModel

class GatingModel:
    """
    Advanced gating model that combines outputs from all expert models using ensemble methods
    """
    
    def __init__(self):
        self.behavior_model = BehaviorModel()
        self.geo_model = GeoModel()
        self.context_model = ContextModel()
        
        # Enhanced model weights based on analysis (can be learned from data)
        self.expert_weights = {
            'behavior': 0.4,      # Driver behavior has highest weight
            'geographic': 0.3,    # Geographic factors
            'contextual': 0.3     # Contextual factors
        }
        
        # Risk thresholds for insurance pricing tiers
        self.risk_thresholds = {
            'preferred': 25,      # Preferred tier (best rates)
            'standard_plus': 45,  # Standard plus tier
            'standard': 65,       # Standard tier
            'substandard': 85     # Substandard tier (highest rates)
        }
        
        # Premium adjustment factors
        self.premium_adjustments = {
            'preferred': 0.75,        # 25% discount
            'standard_plus': 0.85,    # 15% discount  
            'standard': 1.0,          # Base rate
            'substandard': 1.25,      # 25% surcharge
            'high_risk': 1.5          # 50% surcharge
        }
    
    def comprehensive_risk_assessment(self, 
                                    behavior_data: Dict[str, Any],
                                    location_data: Dict[str, Any], 
                                    context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment using all expert models
        """
        # Get assessments from each expert model
        behavior_assessment = self._assess_behavior(behavior_data)
        geographic_assessment = self._assess_geographic_risk(location_data)
        contextual_assessment = self._assess_contextual_risk(context_data)
        
        # Combine expert scores using ensemble method
        ensemble_result = self.combine_expert_scores(
            behavior_assessment['behavior_score'],
            geographic_assessment['geographic_risk_score'],
            contextual_assessment['contextual_risk_score']
        )
        
        # Calculate premium information
        premium_info = self.calculate_premium_adjustment(
            ensemble_result['risk_score'], 
            context_data.get('base_premium', 1000)
        )
        
        # Generate comprehensive recommendations
        recommendations = self._generate_comprehensive_recommendations(
            behavior_assessment, geographic_assessment, contextual_assessment
        )
        
        # Calculate confidence scores
        confidence_metrics = self._calculate_confidence_metrics(
            behavior_assessment, geographic_assessment, contextual_assessment
        )
        
        return {
            'overall_assessment': {
                'final_risk_score': ensemble_result['risk_score'],
                'safety_score': ensemble_result['safety_score'],
                'risk_category': ensemble_result['risk_category'],
                'confidence': confidence_metrics['overall_confidence']
            },
            'expert_assessments': {
                'behavior': behavior_assessment,
                'geographic': geographic_assessment,
                'contextual': contextual_assessment
            },
            'ensemble_details': ensemble_result,
            'premium_information': premium_info,
            'recommendations': recommendations,
            'confidence_metrics': confidence_metrics,
            'model_metadata': {
                'assessment_timestamp': pd.Timestamp.now(),
                'model_version': '2.0',
                'expert_weights': self.expert_weights
            }
        }
    
    def combine_expert_scores(self, 
                            behavior_score: float,
                            geo_risk: float,
                            context_risk: float) -> Dict[str, Any]:
        """
        Advanced ensemble combination of expert scores with interaction effects
        """
        # Convert scores to consistent scale (0-100, higher = more risk)
        behavior_risk = 100 - behavior_score  # Convert safety score to risk score
        
        # Basic weighted combination
        weighted_risk = (
            behavior_risk * self.expert_weights['behavior'] +
            geo_risk * self.expert_weights['geographic'] +
            context_risk * self.expert_weights['contextual']
        )
        
        # Calculate interaction effects
        interaction_effects = self._calculate_interaction_effects(
            behavior_risk, geo_risk, context_risk
        )
        
        # Apply interaction adjustments
        final_risk = min(100, max(0, weighted_risk + interaction_effects['total_interaction']))
        final_safety = 100 - final_risk
        
        return {
            'risk_score': final_risk,
            'safety_score': final_safety,
            'risk_category': self._determine_risk_category(final_risk),
            'weighted_components': {
                'behavior_contribution': behavior_risk * self.expert_weights['behavior'],
                'geographic_contribution': geo_risk * self.expert_weights['geographic'],
                'contextual_contribution': context_risk * self.expert_weights['contextual']
            },
            'interaction_effects': interaction_effects,
            'expert_scores': {
                'behavior_safety': behavior_score,
                'behavior_risk': behavior_risk,
                'geographic_risk': geo_risk,
                'contextual_risk': context_risk
            }
        }
    
    def _calculate_interaction_effects(self, behavior_risk: float, geo_risk: float, context_risk: float) -> Dict[str, Any]:
        """
        Calculate interaction effects between expert model scores
        """
        interactions = {}
        
        # High-risk behavior in high-risk location
        if behavior_risk > 60 and geo_risk > 60:
            interactions['behavior_geo'] = min(15, (behavior_risk + geo_risk - 120) * 0.3)
        else:
            interactions['behavior_geo'] = 0
        
        # High-risk behavior in high-risk context (e.g., bad weather)
        if behavior_risk > 60 and context_risk > 60:
            interactions['behavior_context'] = min(12, (behavior_risk + context_risk - 120) * 0.25)
        else:
            interactions['behavior_context'] = 0
        
        # High geographic and contextual risk combination
        if geo_risk > 50 and context_risk > 50:
            interactions['geo_context'] = min(10, (geo_risk + context_risk - 100) * 0.2)
        else:
            interactions['geo_context'] = 0
        
        # Triple interaction for very high risk scenarios
        if all(risk > 70 for risk in [behavior_risk, geo_risk, context_risk]):
            interactions['triple_interaction'] = 8
        else:
            interactions['triple_interaction'] = 0
        
        interactions['total_interaction'] = sum(interactions.values())
        
        return interactions
    
    def calculate_premium_adjustment(self, risk_score: float, base_premium: float = 1000) -> Dict[str, Any]:
        """
        Calculate detailed insurance premium based on comprehensive risk score
        """
        # Determine tier based on risk score
        if risk_score < self.risk_thresholds['preferred']:
            tier = "Preferred"
            adjustment_factor = self.premium_adjustments['preferred']
        elif risk_score < self.risk_thresholds['standard_plus']:
            tier = "Standard Plus"
            adjustment_factor = self.premium_adjustments['standard_plus']
        elif risk_score < self.risk_thresholds['standard']:
            tier = "Standard"
            adjustment_factor = self.premium_adjustments['standard']
        elif risk_score < self.risk_thresholds['substandard']:
            tier = "Substandard"
            adjustment_factor = self.premium_adjustments['substandard']
        else:
            tier = "High Risk"
            adjustment_factor = self.premium_adjustments['high_risk']
        
        adjusted_premium = base_premium * adjustment_factor
        savings = base_premium - adjusted_premium
        
        # Calculate additional details
        annual_savings = savings * 12 if savings > 0 else 0
        additional_cost = abs(savings) * 12 if savings < 0 else 0
        
        return {
            'base_premium': base_premium,
            'adjusted_premium': adjusted_premium,
            'adjustment_factor': adjustment_factor,
            'monthly_savings': savings,
            'annual_savings': annual_savings,
            'additional_annual_cost': additional_cost,
            'tier': tier,
            'risk_score': risk_score,
            'discount_percentage': (1 - adjustment_factor) * 100 if adjustment_factor < 1 else 0,
            'surcharge_percentage': (adjustment_factor - 1) * 100 if adjustment_factor > 1 else 0
        }
    
    def _assess_behavior(self, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process behavior data through behavior model"""
        try:
            # Extract sensor data if available
            if 'sensor_data' in behavior_data:
                processed_features = self.behavior_model.preprocess_features(
                    pd.DataFrame(behavior_data['sensor_data'])
                )
                
                # Convert to dictionary for scoring
                features_dict = processed_features.iloc[0].to_dict() if len(processed_features) > 0 else {}
                
                return self.behavior_model.score_behavior(features_dict)
            else:
                # Use simplified scoring if no sensor data
                return self.behavior_model.score_behavior(behavior_data)
        except Exception as e:
            # Fallback scoring
            return {
                'behavior_score': 70,
                'risk_level': 'Moderate Risk',
                'feature_scores': {},
                'risk_factors': [f'Error in behavior assessment: {str(e)}'],
                'driving_style': 'NORMAL'
            }
    
    def _assess_geographic_risk(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process location data through geographic model"""
        try:
            lat = location_data.get('latitude')
            lon = location_data.get('longitude')
            additional_factors = location_data.get('additional_factors', {})
            
            if lat is not None and lon is not None:
                return self.geo_model.calculate_comprehensive_geographic_risk(
                    lat, lon, additional_factors
                )
            else:
                return {'geographic_risk_score': 50, 'risk_category': 'Moderate Risk'}
        except Exception as e:
            return {'geographic_risk_score': 50, 'risk_category': 'Moderate Risk', 'error': str(e)}
    
    def _assess_contextual_risk(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process contextual data through context model"""
        try:
            timestamp = context_data.get('timestamp', pd.Timestamp.now())
            weather_data = context_data.get('weather_data', {})
            traffic_data = context_data.get('traffic_data', {})
            location_data = context_data.get('location_data', {})
            
            return self.context_model.calculate_comprehensive_contextual_risk(
                timestamp, weather_data, traffic_data, location_data
            )
        except Exception as e:
            return {'contextual_risk_score': 50, 'risk_category': 'Moderate Risk', 'error': str(e)}
    
    def _determine_risk_category(self, risk_score: float) -> str:
        """
        Determine overall risk category based on score
        """
        if risk_score < self.risk_thresholds['preferred']:
            return "Very Low Risk"
        elif risk_score < self.risk_thresholds['standard_plus']:
            return "Low Risk"
        elif risk_score < self.risk_thresholds['standard']:
            return "Moderate Risk"
        elif risk_score < self.risk_thresholds['substandard']:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def _generate_comprehensive_recommendations(self, behavior_assessment: Dict, 
                                              geographic_assessment: Dict, 
                                              contextual_assessment: Dict) -> Dict[str, List[str]]:
        """Generate comprehensive recommendations from all expert models"""
        recommendations = {
            'behavior': [],
            'geographic': [],
            'contextual': [],
            'overall': []
        }
        
        # Behavior recommendations
        behavior_score = behavior_assessment.get('behavior_score', 70)
        behavior_risk_factors = behavior_assessment.get('risk_factors', [])
        recommendations['behavior'] = self.behavior_model.get_recommendations(
            behavior_score, behavior_risk_factors
        )
        
        # Geographic recommendations
        if 'error' not in geographic_assessment:
            recommendations['geographic'] = self.geo_model.get_location_recommendations(
                geographic_assessment
            )
        
        # Contextual recommendations
        if 'error' not in contextual_assessment:
            recommendations['contextual'] = self.context_model.get_contextual_recommendations(
                contextual_assessment
            )
        
        # Overall recommendations based on combined analysis
        behavior_risk = 100 - behavior_score
        geo_risk = geographic_assessment.get('geographic_risk_score', 50)
        context_risk = contextual_assessment.get('contextual_risk_score', 50)
        
        if behavior_risk > 60 and geo_risk > 60:
            recommendations['overall'].append(
                "High-risk driver in high-risk location - consider advanced driver training"
            )
        
        if context_risk > 70:
            recommendations['overall'].append(
                "Avoid driving in high-risk conditions when possible"
            )
        
        if all(risk > 70 for risk in [behavior_risk, geo_risk, context_risk]):
            recommendations['overall'].extend([
                "Consider usage-based insurance monitoring",
                "Implement comprehensive risk mitigation strategies"
            ])
        
        return recommendations
    
    def _calculate_confidence_metrics(self, behavior_assessment: Dict, 
                                    geographic_assessment: Dict, 
                                    contextual_assessment: Dict) -> Dict[str, float]:
        """Calculate confidence metrics for the assessment"""
        
        # Base confidence scores
        behavior_confidence = 0.9 if 'error' not in behavior_assessment else 0.5
        geo_confidence = 0.8 if 'error' not in geographic_assessment else 0.5
        context_confidence = 0.85 if 'error' not in contextual_assessment else 0.5
        
        # Adjust confidence based on data quality
        if behavior_assessment.get('driving_style') == 'NORMAL':
            behavior_confidence *= 0.95  # Slightly lower confidence for normal cases
        
        # Overall confidence is weighted average
        overall_confidence = (
            behavior_confidence * self.expert_weights['behavior'] +
            geo_confidence * self.expert_weights['geographic'] +
            context_confidence * self.expert_weights['contextual']
        )
        
        return {
            'behavior_confidence': behavior_confidence,
            'geographic_confidence': geo_confidence,
            'contextual_confidence': context_confidence,
            'overall_confidence': overall_confidence,
            'data_quality_score': (behavior_confidence + geo_confidence + context_confidence) / 3
        }
    
    def analyze_risk_trends(self, historical_assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze risk trends over time from historical assessments
        """
        if len(historical_assessments) < 2:
            return {'trend': 'insufficient_data', 'message': 'Need at least 2 assessments for trend analysis'}
        
        # Extract risk scores over time
        risk_scores = [assessment['overall_assessment']['final_risk_score'] 
                      for assessment in historical_assessments]
        
        behavior_scores = [assessment['expert_assessments']['behavior']['behavior_score']
                          for assessment in historical_assessments]
        
        # Calculate trends
        if len(risk_scores) >= 5:
            recent_avg = np.mean(risk_scores[-5:])
            earlier_avg = np.mean(risk_scores[:-5])
        else:
            recent_avg = np.mean(risk_scores[-2:])
            earlier_avg = np.mean(risk_scores[:-2])
        
        # Determine trend direction
        if recent_avg > earlier_avg + 10:
            risk_trend = 'deteriorating'
        elif recent_avg < earlier_avg - 10:
            risk_trend = 'improving'
        else:
            risk_trend = 'stable'
        
        # Behavior trend
        if len(behavior_scores) >= 3:
            behavior_trend_slope = np.polyfit(range(len(behavior_scores)), behavior_scores, 1)[0]
            if behavior_trend_slope > 2:
                behavior_trend = 'improving'
            elif behavior_trend_slope < -2:
                behavior_trend = 'deteriorating'
            else:
                behavior_trend = 'stable'
        else:
            behavior_trend = 'insufficient_data'
        
        return {
            'risk_trend': risk_trend,
            'behavior_trend': behavior_trend,
            'current_risk': risk_scores[-1],
            'average_risk': np.mean(risk_scores),
            'risk_variance': np.var(risk_scores),
            'assessments_analyzed': len(historical_assessments),
            'trend_confidence': min(1.0, len(historical_assessments) / 10)  # Higher confidence with more data
        }
    
    def get_insurance_tier_explanation(self, tier: str, risk_score: float) -> Dict[str, Any]:
        """
        Provide detailed explanation of insurance tier assignment
        """
        tier_explanations = {
            'Preferred': {
                'description': 'Excellent safety record with minimal risk factors',
                'benefits': ['Maximum discount available', 'Priority claims processing', 'Additional coverage options'],
                'requirements': 'Risk score below 25'
            },
            'Standard Plus': {
                'description': 'Good safety record with minor risk factors',
                'benefits': ['Moderate discount', 'Standard claims processing', 'Good coverage options'],
                'requirements': 'Risk score between 25-45'
            },
            'Standard': {
                'description': 'Average risk profile',
                'benefits': ['Base premium rates', 'Standard coverage and service'],
                'requirements': 'Risk score between 45-65'
            },
            'Substandard': {
                'description': 'Elevated risk factors requiring premium adjustment',
                'benefits': ['Standard coverage with premium surcharge'],
                'requirements': 'Risk score between 65-85'
            },
            'High Risk': {
                'description': 'Significant risk factors requiring careful monitoring',
                'benefits': ['Coverage available with higher premiums', 'Risk management resources'],
                'requirements': 'Risk score above 85'
            }
        }
        
        explanation = tier_explanations.get(tier, {})
        
        # Add specific risk score context
        distance_to_better_tier = self._calculate_distance_to_better_tier(risk_score)
        improvement_suggestions = self._get_tier_improvement_suggestions(tier, risk_score)
        
        return {
            'current_tier': tier,
            'risk_score': risk_score,
            'explanation': explanation,
            'improvement_potential': distance_to_better_tier,
            'improvement_suggestions': improvement_suggestions
        }
    
    def _calculate_distance_to_better_tier(self, current_risk: float) -> Dict[str, Any]:
        """Calculate how much improvement needed for better tier"""
        thresholds = [
            ('Preferred', self.risk_thresholds['preferred']),
            ('Standard Plus', self.risk_thresholds['standard_plus']),
            ('Standard', self.risk_thresholds['standard']),
            ('Substandard', self.risk_thresholds['substandard'])
        ]
        
        for tier, threshold in thresholds:
            if current_risk >= threshold:
                points_needed = current_risk - threshold + 1
                return {
                    'next_better_tier': tier,
                    'points_reduction_needed': points_needed,
                    'potential_savings': self._calculate_potential_savings(current_risk, threshold)
                }
        
        return {'message': 'Already in best tier available'}
    
    def _calculate_potential_savings(self, current_risk: float, target_risk: float) -> Dict[str, float]:
        """Calculate potential premium savings from risk reduction"""
        current_premium = self.calculate_premium_adjustment(current_risk)
        target_premium = self.calculate_premium_adjustment(target_risk)
        
        monthly_savings = current_premium['adjusted_premium'] - target_premium['adjusted_premium']
        annual_savings = monthly_savings * 12
        
        return {
            'monthly_savings': monthly_savings,
            'annual_savings': annual_savings,
            'percentage_savings': (monthly_savings / current_premium['adjusted_premium']) * 100
        }
    
    def _get_tier_improvement_suggestions(self, current_tier: str, risk_score: float) -> List[str]:
        """Get specific suggestions for tier improvement"""
        suggestions = []
        
        if current_tier in ['High Risk', 'Substandard']:
            suggestions.extend([
                "Focus on improving driving behavior through defensive driving courses",
                "Consider telematics monitoring to demonstrate safe driving",
                "Avoid high-risk locations and times when possible"
            ])
        
        if current_tier in ['Standard', 'Standard Plus']:
            suggestions.extend([
                "Maintain consistent safe driving habits",
                "Continue avoiding risky driving conditions",
                "Consider advanced driver safety programs"
            ])
        
        if risk_score > 60:
            suggestions.append("Significant improvement needed - consider comprehensive driver training")
        elif risk_score > 40:
            suggestions.append("Moderate improvement possible with focused safety efforts")
        
        return suggestions
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
