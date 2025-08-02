"""
Enhanced claims service for comprehensive claim frequency and severity calculations
Updated to integrate with advanced telematics analysis and expert model outputs
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import math

class ClaimsService:
    """
    Enhanced service for calculating claim frequency and severity predictions
    using comprehensive telematics analysis
    """
    
    def __init__(self):
        # Enhanced base frequency rates based on comprehensive data
        self.base_frequency_rates = {
            'comprehensive': 0.0180,
            'collision': 0.0340,
            'liability': 0.0520,
            'pip': 0.0890,
            'uninsured_motorist': 0.0145
        }
        
        # Enhanced severity amounts with inflation adjustments
        self.base_severity_amounts = {
            'comprehensive': 4200,
            'collision': 8500,
            'liability': 15800,
            'pip': 9500,
            'uninsured_motorist': 12000
        }
        
        # Enhanced risk factors with telematics integration
        self.telematics_frequency_adjustments = {
            'behavior_score_excellent': 0.65,    # 90+ behavior score
            'behavior_score_good': 0.78,         # 80-89 behavior score
            'behavior_score_average': 0.92,      # 70-79 behavior score
            'behavior_score_poor': 1.25,         # 60-69 behavior score
            'behavior_score_very_poor': 1.55,    # <60 behavior score
            
            'geographic_risk_very_low': 0.72,    # <25 geographic risk
            'geographic_risk_low': 0.85,         # 25-40 geographic risk
            'geographic_risk_moderate': 1.00,    # 40-60 geographic risk
            'geographic_risk_high': 1.28,        # 60-80 geographic risk
            'geographic_risk_very_high': 1.65,   # >80 geographic risk
            
            'contextual_risk_excellent': 0.68,   # <30 contextual risk
            'contextual_risk_good': 0.82,        # 30-45 contextual risk
            'contextual_risk_average': 1.00,     # 45-65 contextual risk
            'contextual_risk_poor': 1.35,        # 65-80 contextual risk
            'contextual_risk_very_poor': 1.75,   # >80 contextual risk
            
            'ensemble_premium_tier': {
                'Preferred': 0.60,
                'Standard Plus': 0.75,
                'Standard': 1.00,
                'Substandard': 1.40,
                'High Risk': 1.85
            }
        }
        
        # Enhanced severity multipliers
        self.telematics_severity_adjustments = {
            'aggressive_driving_style': 1.45,
            'smooth_driving_style': 0.78,
            'normal_driving_style': 1.00,
            
            'high_frequency_patterns': 1.35,     # High jerk/acceleration patterns
            'low_frequency_patterns': 0.82,      # Smooth patterns
            
            'high_risk_locations': 1.55,         # Frequent high-risk area driving
            'low_risk_locations': 0.85,          # Consistent low-risk areas
            
            'poor_weather_driving': 1.25,        # Frequent bad weather exposure
            'good_weather_driving': 0.90,        # Mostly good conditions
            
            'urban_high_traffic': 1.40,          # Dense urban driving
            'rural_low_traffic': 0.75,           # Rural/low traffic
        }
        
        # Traditional risk factors (enhanced)
        self.traditional_multipliers = {
            'demographic': {
                'age_16_20': 2.15,
                'age_21_25': 1.65,
                'age_26_35': 1.05,
                'age_36_55': 0.88,
                'age_56_65': 0.95,
                'age_over_65': 1.25
            },
            'experience': {
                'years_0_2': 1.45,
                'years_3_5': 1.15,
                'years_6_10': 0.95,
                'years_over_10': 0.85
            },
            'vehicle': {
                'luxury_high_performance': 1.85,
                'luxury_standard': 1.35,
                'standard_sedan': 1.00,
                'economy_compact': 0.82,
                'truck_suv': 1.15
            }
        }
    
    def predict_enhanced_claims(self, 
                              driver_profile: Dict[str, Any],
                              historical_assessments: List[Dict[str, Any]],
                              coverage_type: str,
                              policy_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced claims prediction using comprehensive telematics analysis
        """
        if not historical_assessments:
            return self._predict_without_telematics(driver_profile, coverage_type)
        
        # Calculate telematics-based adjustments
        telematics_analysis = self._analyze_telematics_history(historical_assessments)
        
        # Base frequency and severity
        base_frequency = self.base_frequency_rates.get(coverage_type, 0.035)
        base_severity = self.base_severity_amounts.get(coverage_type, 8000)
        
        # Apply telematics adjustments
        frequency_adjustment = self._calculate_frequency_adjustment(
            telematics_analysis, driver_profile
        )
        
        severity_adjustment = self._calculate_severity_adjustment(
            telematics_analysis, driver_profile, policy_details
        )
        
        # Apply traditional risk factors
        traditional_adjustment = self._calculate_traditional_adjustments(driver_profile)
        
        # Final calculations
        predicted_frequency = (base_frequency * 
                             frequency_adjustment['total_multiplier'] * 
                             traditional_adjustment['frequency_multiplier'])
        
        predicted_severity = (base_severity * 
                            severity_adjustment['total_multiplier'] * 
                            traditional_adjustment['severity_multiplier'])
        
        # Calculate confidence intervals
        confidence_interval = self._calculate_confidence_intervals(
            predicted_frequency, predicted_severity, len(historical_assessments)
        )
        
        # Identify key risk factors
        risk_factors = self._identify_key_risk_factors(
            frequency_adjustment, severity_adjustment, traditional_adjustment
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            predicted_frequency, predicted_severity, telematics_analysis
        )
        
        return {
            'frequency_prediction': predicted_frequency,
            'severity_prediction': predicted_severity,
            'confidence_interval': confidence_interval,
            'risk_factors': risk_factors,
            'recommendation': recommendation,
            'telematics_impact': {
                'frequency_reduction': (1 - frequency_adjustment['total_multiplier']) * 100,
                'severity_reduction': (1 - severity_adjustment['total_multiplier']) * 100,
                'data_quality_score': telematics_analysis['data_quality_score']
            },
            'prediction_metadata': {
                'coverage_type': coverage_type,
                'assessments_analyzed': len(historical_assessments),
                'prediction_confidence': confidence_interval['confidence_level'],
                'model_version': '2.0'
            }
        }
    
    def _analyze_telematics_history(self, assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze historical telematics assessments for patterns
        """
        if not assessments:
            return {'data_quality_score': 0}
        
        # Extract key metrics from assessments
        behavior_scores = []
        geographic_risks = []
        contextual_risks = []
        overall_risks = []
        driving_styles = []
        premium_tiers = []
        
        for assessment in assessments:
            expert_assessments = assessment.get('expert_assessments', {})
            overall_assessment = assessment.get('overall_assessment', {})
            premium_info = assessment.get('premium_information', {})
            
            behavior_scores.append(
                expert_assessments.get('behavior', {}).get('behavior_score', 70)
            )
            geographic_risks.append(
                expert_assessments.get('geographic', {}).get('geographic_risk_score', 50)
            )
            contextual_risks.append(
                expert_assessments.get('contextual', {}).get('contextual_risk_score', 50)
            )
            overall_risks.append(
                overall_assessment.get('final_risk_score', 50)
            )
            driving_styles.append(
                expert_assessments.get('behavior', {}).get('driving_style', 'NORMAL')
            )
            premium_tiers.append(
                premium_info.get('tier', 'Standard')
            )
        
        # Calculate averages and trends
        avg_behavior_score = np.mean(behavior_scores)
        avg_geographic_risk = np.mean(geographic_risks)
        avg_contextual_risk = np.mean(contextual_risks)
        avg_overall_risk = np.mean(overall_risks)
        
        # Determine most common driving style
        most_common_style = max(set(driving_styles), key=driving_styles.count)
        most_common_tier = max(set(premium_tiers), key=premium_tiers.count)
        
        # Calculate risk trends
        if len(overall_risks) >= 3:
            recent_risk = np.mean(overall_risks[-3:])
            earlier_risk = np.mean(overall_risks[:-3])
            risk_trend = 'improving' if recent_risk < earlier_risk - 5 else 'stable'
        else:
            risk_trend = 'insufficient_data'
        
        # Calculate consistency (lower variance = more consistent)
        behavior_consistency = 1 / (1 + np.var(behavior_scores))
        risk_consistency = 1 / (1 + np.var(overall_risks))
        
        # Data quality score
        data_quality_score = min(1.0, len(assessments) / 10) * (behavior_consistency + risk_consistency) / 2
        
        return {
            'avg_behavior_score': avg_behavior_score,
            'avg_geographic_risk': avg_geographic_risk,
            'avg_contextual_risk': avg_contextual_risk,
            'avg_overall_risk': avg_overall_risk,
            'most_common_driving_style': most_common_style,
            'most_common_tier': most_common_tier,
            'risk_trend': risk_trend,
            'behavior_consistency': behavior_consistency,
            'risk_consistency': risk_consistency,
            'data_quality_score': data_quality_score,
            'assessment_count': len(assessments)
        }
    
    def _calculate_frequency_adjustment(self, telematics_analysis: Dict, driver_profile: Dict) -> Dict[str, Any]:
        """
        Calculate frequency adjustment based on telematics analysis
        """
        multiplier = 1.0
        applied_factors = []
        
        # Behavior score adjustment
        avg_behavior = telematics_analysis['avg_behavior_score']
        if avg_behavior >= 90:
            behavior_mult = self.telematics_frequency_adjustments['behavior_score_excellent']
            applied_factors.append('excellent_behavior')
        elif avg_behavior >= 80:
            behavior_mult = self.telematics_frequency_adjustments['behavior_score_good']
            applied_factors.append('good_behavior')
        elif avg_behavior >= 70:
            behavior_mult = self.telematics_frequency_adjustments['behavior_score_average']
            applied_factors.append('average_behavior')
        elif avg_behavior >= 60:
            behavior_mult = self.telematics_frequency_adjustments['behavior_score_poor']
            applied_factors.append('poor_behavior')
        else:
            behavior_mult = self.telematics_frequency_adjustments['behavior_score_very_poor']
            applied_factors.append('very_poor_behavior')
        
        multiplier *= behavior_mult
        
        # Geographic risk adjustment
        avg_geo_risk = telematics_analysis['avg_geographic_risk']
        if avg_geo_risk < 25:
            geo_mult = self.telematics_frequency_adjustments['geographic_risk_very_low']
            applied_factors.append('very_low_geographic_risk')
        elif avg_geo_risk < 40:
            geo_mult = self.telematics_frequency_adjustments['geographic_risk_low']
            applied_factors.append('low_geographic_risk')
        elif avg_geo_risk < 60:
            geo_mult = self.telematics_frequency_adjustments['geographic_risk_moderate']
        elif avg_geo_risk < 80:
            geo_mult = self.telematics_frequency_adjustments['geographic_risk_high']
            applied_factors.append('high_geographic_risk')
        else:
            geo_mult = self.telematics_frequency_adjustments['geographic_risk_very_high']
            applied_factors.append('very_high_geographic_risk')
        
        multiplier *= geo_mult
        
        # Contextual risk adjustment
        avg_context_risk = telematics_analysis['avg_contextual_risk']
        if avg_context_risk < 30:
            context_mult = self.telematics_frequency_adjustments['contextual_risk_excellent']
            applied_factors.append('excellent_contextual_management')
        elif avg_context_risk < 45:
            context_mult = self.telematics_frequency_adjustments['contextual_risk_good']
            applied_factors.append('good_contextual_management')
        elif avg_context_risk < 65:
            context_mult = self.telematics_frequency_adjustments['contextual_risk_average']
        elif avg_context_risk < 80:
            context_mult = self.telematics_frequency_adjustments['contextual_risk_poor']
            applied_factors.append('poor_contextual_management')
        else:
            context_mult = self.telematics_frequency_adjustments['contextual_risk_very_poor']
            applied_factors.append('very_poor_contextual_management')
        
        multiplier *= context_mult
        
        # Premium tier adjustment
        tier = telematics_analysis['most_common_tier']
        tier_mult = self.telematics_frequency_adjustments['ensemble_premium_tier'].get(tier, 1.0)
        multiplier *= tier_mult
        
        if tier in ['Preferred', 'Standard Plus']:
            applied_factors.append(f'{tier.lower()}_tier')
        elif tier in ['Substandard', 'High Risk']:
            applied_factors.append(f'{tier.lower()}_tier')
        
        return {
            'total_multiplier': multiplier,
            'applied_factors': applied_factors,
            'component_multipliers': {
                'behavior': behavior_mult,
                'geographic': geo_mult,
                'contextual': context_mult,
                'tier': tier_mult
            }
        }
    
    def _calculate_severity_adjustment(self, telematics_analysis: Dict, 
                                     driver_profile: Dict, policy_details: Dict) -> Dict[str, Any]:
        """
        Calculate severity adjustment based on telematics patterns
        """
        multiplier = 1.0
        applied_factors = []
        
        # Driving style impact on severity
        driving_style = telematics_analysis['most_common_driving_style']
        if driving_style == 'AGGRESSIVE':
            style_mult = self.telematics_severity_adjustments['aggressive_driving_style']
            applied_factors.append('aggressive_driving_increases_severity')
        elif driving_style == 'SMOOTH':
            style_mult = self.telematics_severity_adjustments['smooth_driving_style']
            applied_factors.append('smooth_driving_reduces_severity')
        else:
            style_mult = self.telematics_severity_adjustments['normal_driving_style']
        
        multiplier *= style_mult
        
        # Geographic risk patterns
        avg_geo_risk = telematics_analysis['avg_geographic_risk']
        if avg_geo_risk > 70:
            geo_mult = self.telematics_severity_adjustments['high_risk_locations']
            applied_factors.append('frequent_high_risk_locations')
        elif avg_geo_risk < 30:
            geo_mult = self.telematics_severity_adjustments['low_risk_locations']
            applied_factors.append('consistent_low_risk_locations')
        else:
            geo_mult = 1.0
        
        multiplier *= geo_mult
        
        # Contextual risk patterns (weather/traffic exposure)
        avg_context_risk = telematics_analysis['avg_contextual_risk']
        if avg_context_risk > 70:
            context_mult = self.telematics_severity_adjustments['poor_weather_driving']
            applied_factors.append('frequent_poor_conditions_exposure')
        elif avg_context_risk < 35:
            context_mult = self.telematics_severity_adjustments['good_weather_driving']
            applied_factors.append('mostly_good_conditions')
        else:
            context_mult = 1.0
        
        multiplier *= context_mult
        
        return {
            'total_multiplier': multiplier,
            'applied_factors': applied_factors,
            'component_multipliers': {
                'driving_style': style_mult,
                'geographic_patterns': geo_mult,
                'contextual_patterns': context_mult
            }
        }
    
    def _calculate_traditional_adjustments(self, driver_profile: Dict) -> Dict[str, Any]:
        """
        Calculate traditional risk factor adjustments
        """
        freq_mult = 1.0
        sev_mult = 1.0
        
        # Age adjustments
        age = driver_profile.get('age', 35)
        if age <= 20:
            freq_mult *= self.traditional_multipliers['demographic']['age_16_20']
        elif age <= 25:
            freq_mult *= self.traditional_multipliers['demographic']['age_21_25']
        elif age <= 35:
            freq_mult *= self.traditional_multipliers['demographic']['age_26_35']
        elif age <= 55:
            freq_mult *= self.traditional_multipliers['demographic']['age_36_55']
        elif age <= 65:
            freq_mult *= self.traditional_multipliers['demographic']['age_56_65']
        else:
            freq_mult *= self.traditional_multipliers['demographic']['age_over_65']
        
        # Experience adjustments
        years_licensed = driver_profile.get('years_licensed', 10)
        if years_licensed <= 2:
            freq_mult *= self.traditional_multipliers['experience']['years_0_2']
        elif years_licensed <= 5:
            freq_mult *= self.traditional_multipliers['experience']['years_3_5']
        elif years_licensed <= 10:
            freq_mult *= self.traditional_multipliers['experience']['years_6_10']
        else:
            freq_mult *= self.traditional_multipliers['experience']['years_over_10']
        
        # Vehicle type adjustments
        vehicle_type = driver_profile.get('vehicle_type', 'standard_sedan')
        if vehicle_type in self.traditional_multipliers['vehicle']:
            vehicle_mult = self.traditional_multipliers['vehicle'][vehicle_type]
            freq_mult *= vehicle_mult
            sev_mult *= vehicle_mult
        
        return {
            'frequency_multiplier': freq_mult,
            'severity_multiplier': sev_mult
        }
    
    def _calculate_confidence_intervals(self, frequency: float, severity: float, 
                                      data_points: int) -> Dict[str, float]:
        """
        Calculate confidence intervals for predictions
        """
        # Confidence decreases with fewer data points
        confidence_level = min(0.95, 0.6 + (data_points / 50))
        
        # Standard errors (simplified)
        freq_std_error = frequency * (0.3 / math.sqrt(max(1, data_points)))
        sev_std_error = severity * (0.25 / math.sqrt(max(1, data_points)))
        
        # 95% confidence intervals
        z_score = 1.96  # 95% confidence
        
        return {
            'frequency_lower': max(0, frequency - z_score * freq_std_error),
            'frequency_upper': frequency + z_score * freq_std_error,
            'severity_lower': max(0, severity - z_score * sev_std_error),
            'severity_upper': severity + z_score * sev_std_error,
            'confidence_level': confidence_level
        }
    
    def _identify_key_risk_factors(self, freq_adj: Dict, sev_adj: Dict, trad_adj: Dict) -> List[str]:
        """
        Identify the most significant risk factors affecting claims
        """
        risk_factors = []
        
        # Frequency risk factors
        risk_factors.extend(freq_adj.get('applied_factors', []))
        
        # Severity risk factors  
        risk_factors.extend(sev_adj.get('applied_factors', []))
        
        # Traditional risk factors (simplified)
        if trad_adj['frequency_multiplier'] > 1.2:
            risk_factors.append('demographic_risk_factors')
        
        return list(set(risk_factors))  # Remove duplicates
    
    def _generate_recommendation(self, frequency: float, severity: float, 
                               telematics_analysis: Dict) -> str:
        """
        Generate recommendation based on prediction results
        """
        if frequency < 0.02 and severity < 5000:
            return "Excellent risk profile - consider preferred rates and lower deductibles"
        elif frequency < 0.035 and severity < 8000:
            return "Good risk profile - standard rates with potential discounts"
        elif frequency < 0.05 and severity < 12000:
            return "Average risk profile - monitor telematics data for improvement opportunities"
        elif frequency < 0.08 and severity < 18000:
            return "Elevated risk - recommend driver training and increased deductibles"
        else:
            return "High risk profile - comprehensive risk management program recommended"
    
    def _predict_without_telematics(self, driver_profile: Dict, coverage_type: str) -> Dict[str, Any]:
        """
        Fallback prediction without telematics data
        """
        base_frequency = self.base_frequency_rates.get(coverage_type, 0.035)
        base_severity = self.base_severity_amounts.get(coverage_type, 8000)
        
        traditional_adj = self._calculate_traditional_adjustments(driver_profile)
        
        predicted_frequency = base_frequency * traditional_adj['frequency_multiplier']
        predicted_severity = base_severity * traditional_adj['severity_multiplier']
        
        return {
            'frequency_prediction': predicted_frequency,
            'severity_prediction': predicted_severity,
            'confidence_interval': {
                'confidence_level': 0.60,
                'frequency_lower': predicted_frequency * 0.7,
                'frequency_upper': predicted_frequency * 1.3,
                'severity_lower': predicted_severity * 0.8,
                'severity_upper': predicted_severity * 1.2
            },
            'risk_factors': ['insufficient_telematics_data'],
            'recommendation': 'Limited data available - consider enrolling in telematics program for better rates',
            'telematics_impact': {
                'frequency_reduction': 0,
                'severity_reduction': 0,
                'data_quality_score': 0
            }
        }
    
    def calculate_legacy_claim_severity(self, driver_profile: Dict[str, Any], 
                                      coverage_type: str) -> Dict[str, Any]:
        """
        Legacy method for calculating expected claim severity for given coverage type
        Maintained for backward compatibility
        """
        if coverage_type not in self.base_severity_amounts:
            raise ValueError(f"Unknown coverage type: {coverage_type}")
        
        base_severity = self.base_severity_amounts[coverage_type]
        adjusted_severity = base_severity
        applied_factors = []
        
        # Vehicle type adjustments
        vehicle_type = driver_profile.get('vehicle_type', 'standard').lower()
        if vehicle_type == 'luxury':
            adjusted_severity *= self.telematics_severity_adjustments.get('luxury_vehicle', 1.85)
            applied_factors.append('luxury_vehicle')
        elif vehicle_type == 'economy':
            adjusted_severity *= 0.75  # Economy vehicle multiplier
            applied_factors.append('economy_vehicle')
        else:
            applied_factors.append('standard_vehicle')
        
        # Safety rating adjustments
        safety_rating = driver_profile.get('safety_rating', 'standard').lower()
        if safety_rating == 'high':
            adjusted_severity *= 0.88
            applied_factors.append('high_safety_rating')
        elif safety_rating == 'poor':
            adjusted_severity *= 1.25
            applied_factors.append('poor_safety_rating')
        
        # Location-based repair cost adjustments
        area_type = driver_profile.get('area_type', 'suburban').lower()
        if area_type == 'urban':
            adjusted_severity *= 1.35
            applied_factors.append('urban_repairs')
        elif area_type == 'rural':
            adjusted_severity *= 0.92
            applied_factors.append('rural_repairs')
        
        return {
            'base_severity': base_severity,
            'adjusted_severity': adjusted_severity,
            'cost_impact': adjusted_severity - base_severity,
            'applied_factors': applied_factors
        }
    
    def calculate_premium_impact(self, frequency_results: Dict[str, Any], 
                               severity_results: Dict[str, Any],
                               current_premium: float) -> Dict[str, Any]:
        """
        Calculate the impact of claims predictions on insurance premiums
        """
        total_expected_cost = 0
        coverage_impacts = {}
        
        for coverage_type in frequency_results:
            if coverage_type in severity_results:
                expected_cost = (frequency_results[coverage_type]['adjusted_frequency'] * 
                               severity_results[coverage_type]['adjusted_severity'])
                
                coverage_impacts[coverage_type] = {
                    'expected_annual_cost': expected_cost,
                    'frequency_component': frequency_results[coverage_type]['adjusted_frequency'],
                    'severity_component': severity_results[coverage_type]['adjusted_severity']
                }
                
                total_expected_cost += expected_cost
        
        # Calculate risk-based premium adjustment
        risk_multiplier = min(2.0, max(0.5, total_expected_cost / 1000))
        adjusted_premium = current_premium * risk_multiplier
        premium_change = adjusted_premium - current_premium
        
        return {
            'current_premium': current_premium,
            'adjusted_premium': adjusted_premium,
            'premium_change': premium_change,
            'premium_change_percent': (premium_change / current_premium) * 100,
            'total_expected_cost': total_expected_cost,
            'risk_multiplier': risk_multiplier,
            'coverage_breakdown': coverage_impacts
        }
    
    def generate_claims_risk_report(self, driver_profile: Dict[str, Any],
                                   historical_assessments: List[Dict[str, Any]] = None,
                                   current_premium: float = 1200) -> Dict[str, Any]:
        """
        Generate comprehensive claims risk report
        """
        report_data = {
            'driver_profile': driver_profile,
            'analysis_timestamp': datetime.now().isoformat(),
            'coverage_analysis': {},
            'overall_assessment': {},
            'recommendations': []
        }
        
        # Analyze each coverage type
        for coverage_type in self.base_frequency_rates:
            # Use enhanced prediction if historical data available
            if historical_assessments:
                prediction = self.predict_enhanced_claims(
                    driver_profile, historical_assessments, coverage_type, {}
                )
            else:
                prediction = self._predict_without_telematics(driver_profile, coverage_type)
            
            report_data['coverage_analysis'][coverage_type] = prediction
        
        # Generate overall risk assessment
        avg_frequency = np.mean([
            pred['frequency_prediction'] 
            for pred in report_data['coverage_analysis'].values()
        ])
        
        avg_severity = np.mean([
            pred['severity_prediction'] 
            for pred in report_data['coverage_analysis'].values()
        ])
        
        # Risk classification
        if avg_frequency < 0.03 and avg_severity < 6000:
            risk_class = 'Low Risk'
            recommended_action = 'Offer preferred rates and reduced deductibles'
        elif avg_frequency < 0.05 and avg_severity < 10000:
            risk_class = 'Standard Risk'
            recommended_action = 'Standard rates with potential telematics discounts'
        elif avg_frequency < 0.08 and avg_severity < 15000:
            risk_class = 'Moderate Risk'
            recommended_action = 'Standard rates with enhanced monitoring'
        else:
            risk_class = 'High Risk'
            recommended_action = 'Comprehensive risk management program required'
        
        report_data['overall_assessment'] = {
            'risk_classification': risk_class,
            'average_frequency': avg_frequency,
            'average_severity': avg_severity,
            'recommended_action': recommended_action,
            'confidence_score': np.mean([
                pred['confidence_interval']['confidence_level']
                for pred in report_data['coverage_analysis'].values()
            ])
        }
        
        # Generate specific recommendations
        if historical_assessments:
            telematics_analysis = self._analyze_telematics_history(historical_assessments)
            if telematics_analysis['data_quality_score'] > 0.7:
                report_data['recommendations'].append(
                    "High-quality telematics data available - leverage for competitive pricing"
                )
            
            if telematics_analysis['risk_trend'] == 'improving':
                report_data['recommendations'].append(
                    "Positive risk trend observed - consider progressive rate reductions"
                )
        else:
            report_data['recommendations'].append(
                "Consider implementing telematics program for better risk assessment"
            )
        
        return report_data
    
    def _calculate_telematics_impact(self, driver_profile: Dict[str, Any], 
                                   telematics_score: float, 
                                   current_cost: float) -> Dict[str, Any]:
        """
        Calculate the impact of telematics on claim costs
        """
        # Calculate costs without telematics adjustment
        frequency_without_telematics = self.calculate_claim_frequency(
            driver_profile, 0  # Score of 0 means no telematics benefit
        )
        
        cost_without_telematics = 0
        for coverage_type in self.base_frequency_rates.keys():
            frequency = frequency_without_telematics[coverage_type]['adjusted_frequency']
            severity = self.calculate_claim_severity(driver_profile, coverage_type)['adjusted_severity']
            cost_without_telematics += frequency * severity
        
        savings = cost_without_telematics - current_cost
        savings_percentage = (savings / cost_without_telematics * 100) if cost_without_telematics > 0 else 0
        
        return {
            'cost_without_telematics': cost_without_telematics,
            'cost_with_telematics': current_cost,
            'annual_savings': savings,
            'savings_percentage': savings_percentage,
            'telematics_score': telematics_score
        }
    
    def generate_claims_report(self, driver_profile: Dict[str, Any], 
                             telematics_score: float) -> Dict[str, Any]:
        """
        Generate comprehensive claims analysis report
        """
        frequency_analysis = self.calculate_claim_frequency(driver_profile, telematics_score)
        cost_analysis = self.calculate_expected_annual_cost(driver_profile, telematics_score)
        
        # Risk level assessment
        total_frequency = sum([data['adjusted_frequency'] for data in frequency_analysis.values()])
        
        if total_frequency < 0.08:
            risk_level = "Low"
        elif total_frequency < 0.15:
            risk_level = "Moderate"
        elif total_frequency < 0.25:
            risk_level = "High"
        else:
            risk_level = "Very High"
        
        return {
            'driver_profile': driver_profile,
            'telematics_score': telematics_score,
            'risk_level': risk_level,
            'frequency_analysis': frequency_analysis,
            'cost_analysis': cost_analysis,
            'recommendations': self._generate_recommendations(
                frequency_analysis, cost_analysis, telematics_score
            ),
            'report_date': datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, frequency_analysis: Dict[str, Any], 
                                cost_analysis: Dict[str, Any], 
                                telematics_score: float) -> List[str]:
        """
        Generate recommendations based on claims analysis
        """
        recommendations = []
        
        if telematics_score < 70:
            recommendations.append("Improve driving behavior to reduce claim frequency by up to 18%")
        
        if cost_analysis['telematics_impact']['savings_percentage'] > 10:
            recommendations.append(f"Continue safe driving practices - saving ${cost_analysis['telematics_impact']['annual_savings']:.0f} annually")
        
        # Coverage-specific recommendations
        highest_cost_coverage = max(
            cost_analysis['coverage_breakdown'].items(),
            key=lambda x: x[1]['expected_annual_cost']
        )
        
        recommendations.append(
            f"Focus on {highest_cost_coverage[0]} risk factors - represents "
            f"{highest_cost_coverage[1]['cost_percentage']:.1f}% of expected costs"
        )
        
        return recommendations
