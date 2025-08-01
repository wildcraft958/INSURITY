"""
Claims service for industry-standard claim frequency and severity calculations
Based on PMC11386000 Section 4 methodology
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import math

class ClaimsService:
    """
    Service for calculating claim frequency and severity predictions
    """
    
    def __init__(self):
        # Industry standard claim frequency rates (claims per year)
        self.base_frequency_rates = {
            'comprehensive': 0.0180,  # 1.8% annually
            'collision': 0.0340,      # 3.4% annually
            'liability': 0.0520,      # 5.2% annually
            'pip': 0.0890            # 8.9% annually (Personal Injury Protection)
        }
        
        # Average claim severity amounts (USD)
        self.base_severity_amounts = {
            'comprehensive': 3500,
            'collision': 6800,
            'liability': 12500,
            'pip': 8200
        }
        
        # Risk factors and their multipliers
        self.frequency_multipliers = {
            'age_under_25': 1.45,
            'age_25_to_35': 1.15,
            'age_35_to_55': 0.95,
            'age_over_55': 1.05,
            'male_driver': 1.12,
            'female_driver': 0.94,
            'urban_area': 1.28,
            'suburban_area': 1.05,
            'rural_area': 0.85,
            'high_mileage': 1.22,  # >15k miles/year
            'medium_mileage': 1.00,  # 7-15k miles/year
            'low_mileage': 0.78,   # <7k miles/year
            'poor_credit': 1.35,
            'good_credit': 0.88,
            'telematics_participant': 0.82,  # Proven reduction
            'safety_features': 0.91
        }
        
        self.severity_multipliers = {
            'luxury_vehicle': 1.85,
            'standard_vehicle': 1.00,
            'economy_vehicle': 0.75,
            'high_safety_rating': 0.88,
            'poor_safety_rating': 1.25,
            'urban_repairs': 1.35,
            'rural_repairs': 0.92
        }
    
    def calculate_claim_frequency(self, driver_profile: Dict[str, Any], 
                                telematics_score: float) -> Dict[str, Any]:
        """
        Calculate expected claim frequency based on driver profile and telematics
        """
        results = {}
        
        for coverage_type, base_rate in self.base_frequency_rates.items():
            adjusted_rate = base_rate
            applied_factors = []
            
            # Age-based adjustments
            age = driver_profile.get('age', 35)
            if age < 25:
                adjusted_rate *= self.frequency_multipliers['age_under_25']
                applied_factors.append('age_under_25')
            elif age <= 35:
                adjusted_rate *= self.frequency_multipliers['age_25_to_35']
                applied_factors.append('age_25_to_35')
            elif age <= 55:
                adjusted_rate *= self.frequency_multipliers['age_35_to_55']
                applied_factors.append('age_35_to_55')
            else:
                adjusted_rate *= self.frequency_multipliers['age_over_55']
                applied_factors.append('age_over_55')
            
            # Gender-based adjustments
            if driver_profile.get('gender', '').lower() == 'male':
                adjusted_rate *= self.frequency_multipliers['male_driver']
                applied_factors.append('male_driver')
            elif driver_profile.get('gender', '').lower() == 'female':
                adjusted_rate *= self.frequency_multipliers['female_driver']
                applied_factors.append('female_driver')
            
            # Location-based adjustments
            area_type = driver_profile.get('area_type', 'suburban').lower()
            if area_type in self.frequency_multipliers:
                adjusted_rate *= self.frequency_multipliers[area_type + '_area']
                applied_factors.append(area_type + '_area')
            
            # Mileage-based adjustments
            annual_mileage = driver_profile.get('annual_mileage', 12000)
            if annual_mileage > 15000:
                adjusted_rate *= self.frequency_multipliers['high_mileage']
                applied_factors.append('high_mileage')
            elif annual_mileage < 7000:
                adjusted_rate *= self.frequency_multipliers['low_mileage']
                applied_factors.append('low_mileage')
            else:
                adjusted_rate *= self.frequency_multipliers['medium_mileage']
                applied_factors.append('medium_mileage')
            
            # Credit-based adjustments (where legally allowed)
            credit_score = driver_profile.get('credit_score', 700)
            if credit_score < 600:
                adjusted_rate *= self.frequency_multipliers['poor_credit']
                applied_factors.append('poor_credit')
            elif credit_score > 750:
                adjusted_rate *= self.frequency_multipliers['good_credit']
                applied_factors.append('good_credit')
            
            # Telematics adjustment based on driving score
            if telematics_score > 80:
                adjusted_rate *= self.frequency_multipliers['telematics_participant']
                applied_factors.append('telematics_participant')
            
            # Vehicle safety features
            if driver_profile.get('safety_features', False):
                adjusted_rate *= self.frequency_multipliers['safety_features']
                applied_factors.append('safety_features')
            
            results[coverage_type] = {
                'base_frequency': base_rate,
                'adjusted_frequency': adjusted_rate,
                'reduction_factor': (base_rate - adjusted_rate) / base_rate,
                'applied_factors': applied_factors
            }
        
        return results
    
    def calculate_claim_severity(self, driver_profile: Dict[str, Any], 
                               coverage_type: str) -> Dict[str, Any]:
        """
        Calculate expected claim severity for given coverage type
        """
        if coverage_type not in self.base_severity_amounts:
            raise ValueError(f"Unknown coverage type: {coverage_type}")
        
        base_severity = self.base_severity_amounts[coverage_type]
        adjusted_severity = base_severity
        applied_factors = []
        
        # Vehicle type adjustments
        vehicle_type = driver_profile.get('vehicle_type', 'standard').lower()
        if vehicle_type == 'luxury':
            adjusted_severity *= self.severity_multipliers['luxury_vehicle']
            applied_factors.append('luxury_vehicle')
        elif vehicle_type == 'economy':
            adjusted_severity *= self.severity_multipliers['economy_vehicle']
            applied_factors.append('economy_vehicle')
        else:
            adjusted_severity *= self.severity_multipliers['standard_vehicle']
            applied_factors.append('standard_vehicle')
        
        # Safety rating adjustments
        safety_rating = driver_profile.get('safety_rating', 4)
        if safety_rating >= 5:
            adjusted_severity *= self.severity_multipliers['high_safety_rating']
            applied_factors.append('high_safety_rating')
        elif safety_rating <= 2:
            adjusted_severity *= self.severity_multipliers['poor_safety_rating']
            applied_factors.append('poor_safety_rating')
        
        # Repair cost location adjustments
        area_type = driver_profile.get('area_type', 'suburban').lower()
        if area_type == 'urban':
            adjusted_severity *= self.severity_multipliers['urban_repairs']
            applied_factors.append('urban_repairs')
        elif area_type == 'rural':
            adjusted_severity *= self.severity_multipliers['rural_repairs']
            applied_factors.append('rural_repairs')
        
        return {
            'base_severity': base_severity,
            'adjusted_severity': adjusted_severity,
            'adjustment_factor': adjusted_severity / base_severity,
            'applied_factors': applied_factors
        }
    
    def calculate_expected_annual_cost(self, driver_profile: Dict[str, Any], 
                                     telematics_score: float) -> Dict[str, Any]:
        """
        Calculate expected annual claim costs across all coverage types
        """
        frequency_results = self.calculate_claim_frequency(driver_profile, telematics_score)
        total_expected_cost = 0
        coverage_breakdown = {}
        
        for coverage_type in self.base_frequency_rates.keys():
            frequency_data = frequency_results[coverage_type]
            severity_data = self.calculate_claim_severity(driver_profile, coverage_type)
            
            # Expected annual cost = frequency × severity
            expected_cost = frequency_data['adjusted_frequency'] * severity_data['adjusted_severity']
            total_expected_cost += expected_cost
            
            coverage_breakdown[coverage_type] = {
                'frequency': frequency_data['adjusted_frequency'],
                'severity': severity_data['adjusted_severity'],
                'expected_annual_cost': expected_cost,
                'cost_percentage': 0  # Will be calculated after total is known
            }
        
        # Calculate cost percentages
        for coverage_type in coverage_breakdown:
            coverage_breakdown[coverage_type]['cost_percentage'] = (
                coverage_breakdown[coverage_type]['expected_annual_cost'] / total_expected_cost * 100
            )
        
        return {
            'total_expected_annual_cost': total_expected_cost,
            'coverage_breakdown': coverage_breakdown,
            'telematics_impact': self._calculate_telematics_impact(
                driver_profile, telematics_score, total_expected_cost
            )
        }
    
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
