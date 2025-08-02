"""
Data preparation utilities for shared data cleaning and imputation
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataPreprocessor:
    """
    Utility class for cleaning and preprocessing telematics data
    """
    
    def __init__(self):
        # Define expected data ranges for validation
        self.valid_ranges = {
            'speed': (0, 200),  # km/h
            'acceleration': (-10, 10),  # m/s²
            'latitude': (-90, 90),
            'longitude': (-180, 180),
            'heading': (0, 360),  # degrees
        }
        
        # Define outlier thresholds (z-score)
        self.outlier_threshold = 3.0
    
    def clean_telematics_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Clean raw telematics data and return cleaned data with quality report
        """
        original_count = len(data)
        cleaning_report = {
            'original_records': original_count,
            'issues_found': [],
            'records_removed': 0,
            'records_imputed': 0
        }
        
        # Make a copy to avoid modifying original data
        cleaned_data = data.copy()
        
        # 1. Remove duplicate records
        duplicates = cleaned_data.duplicated()
        if duplicates.sum() > 0:
            cleaned_data = cleaned_data.drop_duplicates()
            cleaning_report['issues_found'].append(f"Removed {duplicates.sum()} duplicate records")
        
        # 2. Validate timestamp format and sequence
        cleaned_data, timestamp_issues = self._clean_timestamps(cleaned_data)
        if timestamp_issues:
            cleaning_report['issues_found'].extend(timestamp_issues)
        
        # 3. Validate coordinate ranges
        cleaned_data, coord_issues = self._clean_coordinates(cleaned_data)
        if coord_issues:
            cleaning_report['issues_found'].extend(coord_issues)
        
        # 4. Clean speed data
        cleaned_data, speed_issues = self._clean_speed_data(cleaned_data)
        if speed_issues:
            cleaning_report['issues_found'].extend(speed_issues)
        
        # 5. Clean acceleration data
        cleaned_data, accel_issues = self._clean_acceleration_data(cleaned_data)
        if accel_issues:
            cleaning_report['issues_found'].extend(accel_issues)
        
        # 6. Handle missing values
        cleaned_data, imputation_count = self._handle_missing_values(cleaned_data)
        cleaning_report['records_imputed'] = imputation_count
        
        # 7. Remove statistical outliers
        cleaned_data, outlier_count = self._remove_outliers(cleaned_data)
        cleaning_report['records_removed'] += outlier_count
        
        cleaning_report['final_records'] = len(cleaned_data)
        cleaning_report['data_quality_score'] = self._calculate_quality_score(
            original_count, len(cleaned_data), cleaning_report
        )
        
        return cleaned_data, cleaning_report
    
    def _clean_timestamps(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Clean and validate timestamp data
        """
        issues = []
        
        # Convert timestamp column to datetime if not already
        if 'timestamp' in data.columns:
            try:
                data['timestamp'] = pd.to_datetime(data['timestamp'])
            except Exception as e:
                issues.append(f"Timestamp conversion error: {e}")
                return data, issues
        
        # Remove records with invalid timestamps (null or future dates)
        invalid_timestamps = (
            data['timestamp'].isna() | 
            (data['timestamp'] > datetime.now() + timedelta(days=1))
        )
        
        if invalid_timestamps.sum() > 0:
            data = data[~invalid_timestamps]
            issues.append(f"Removed {invalid_timestamps.sum()} records with invalid timestamps")
        
        # Sort by timestamp for sequence validation
        data = data.sort_values('timestamp')
        
        return data, issues
    
    def _clean_coordinates(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Clean and validate GPS coordinates
        """
        issues = []
        
        # Check for invalid latitude values
        invalid_lat = (
            (data['latitude'] < self.valid_ranges['latitude'][0]) |
            (data['latitude'] > self.valid_ranges['latitude'][1]) |
            data['latitude'].isna()
        )
        
        # Check for invalid longitude values
        invalid_lon = (
            (data['longitude'] < self.valid_ranges['longitude'][0]) |
            (data['longitude'] > self.valid_ranges['longitude'][1]) |
            data['longitude'].isna()
        )
        
        # Remove records with invalid coordinates
        invalid_coords = invalid_lat | invalid_lon
        if invalid_coords.sum() > 0:
            data = data[~invalid_coords]
            issues.append(f"Removed {invalid_coords.sum()} records with invalid coordinates")
        
        # Check for GPS drift (coordinates that haven't changed for too long)
        if len(data) > 1:
            coord_changes = (
                (data['latitude'].diff().abs() < 0.0001) & 
                (data['longitude'].diff().abs() < 0.0001)
            )
            consecutive_same = coord_changes.rolling(10).sum() >= 9  # 9 consecutive same coordinates
            
            if consecutive_same.sum() > 0:
                issues.append(f"Warning: {consecutive_same.sum()} potential GPS drift records detected")
        
        return data, issues
    
    def _clean_speed_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Clean and validate speed data
        """
        issues = []
        
        # Remove records with invalid speed values
        invalid_speed = (
            (data['speed'] < self.valid_ranges['speed'][0]) |
            (data['speed'] > self.valid_ranges['speed'][1]) |
            data['speed'].isna()
        )
        
        if invalid_speed.sum() > 0:
            data = data[~invalid_speed]
            issues.append(f"Removed {invalid_speed.sum()} records with invalid speed values")
        
        # Detect and flag unrealistic speed changes
        if len(data) > 1:
            speed_diff = data['speed'].diff().abs()
            time_diff = data['timestamp'].diff().dt.total_seconds()
            
            # Flag acceleration > 20 m/s² (unrealistic for normal vehicles)
            unrealistic_accel = (speed_diff / 3.6) / time_diff > 20  # Convert km/h to m/s
            
            if unrealistic_accel.sum() > 0:
                issues.append(f"Warning: {unrealistic_accel.sum()} records with unrealistic speed changes")
        
        return data, issues
    
    def _clean_acceleration_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Clean and validate acceleration data
        """
        issues = []
        
        # Remove records with invalid acceleration values
        invalid_accel = (
            (data['acceleration'] < self.valid_ranges['acceleration'][0]) |
            (data['acceleration'] > self.valid_ranges['acceleration'][1]) |
            data['acceleration'].isna()
        )
        
        if invalid_accel.sum() > 0:
            data = data[~invalid_accel]
            issues.append(f"Removed {invalid_accel.sum()} records with invalid acceleration values")
        
        return data, issues
    
    def _handle_missing_values(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        """
        Handle missing values through imputation or removal
        """
        imputation_count = 0
        
        # For speed: use forward fill (last known speed)
        if 'speed' in data.columns:
            missing_speed = data['speed'].isna().sum()
            if missing_speed > 0:
                data['speed'] = data['speed'].fillna(method='ffill')
                imputation_count += missing_speed
        
        # For acceleration: use 0 (no acceleration)
        if 'acceleration' in data.columns:
            missing_accel = data['acceleration'].isna().sum()
            if missing_accel > 0:
                data['acceleration'] = data['acceleration'].fillna(0)
                imputation_count += missing_accel
        
        # For heading: use forward fill
        if 'heading' in data.columns:
            missing_heading = data['heading'].isna().sum()
            if missing_heading > 0:
                data['heading'] = data['heading'].fillna(method='ffill')
                imputation_count += missing_heading
        
        # For phone_usage: assume False if missing
        if 'phone_usage' in data.columns:
            missing_phone = data['phone_usage'].isna().sum()
            if missing_phone > 0:
                data['phone_usage'] = data['phone_usage'].fillna(False)
                imputation_count += missing_phone
        
        return data, imputation_count
    
    def _remove_outliers(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        """
        Remove statistical outliers using z-score method
        """
        initial_count = len(data)
        
        for column in ['speed', 'acceleration']:
            if column in data.columns:
                z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
                outliers = z_scores > self.outlier_threshold
                data = data[~outliers]
        
        outliers_removed = initial_count - len(data)
        return data, outliers_removed
    
    def _calculate_quality_score(self, original_count: int, final_count: int, 
                               report: Dict[str, Any]) -> float:
        """
        Calculate data quality score (0-100)
        """
        if original_count == 0:
            return 0.0
        
        # Base score from data retention
        retention_score = (final_count / original_count) * 70
        
        # Bonus points for successful cleaning
        cleaning_bonus = min(30, len(report['issues_found']) * 5)
        
        # Penalty for high imputation rate
        imputation_rate = report['records_imputed'] / original_count
        imputation_penalty = min(20, imputation_rate * 100)
        
        quality_score = retention_score + cleaning_bonus - imputation_penalty
        return max(0, min(100, quality_score))
    
    def create_trip_features(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Create aggregated features for a trip from cleaned telematics data
        """
        if len(data) == 0:
            return {}
        
        features = {}
        
        # Basic trip statistics
        features['trip_duration_minutes'] = (
            data['timestamp'].max() - data['timestamp'].min()
        ).total_seconds() / 60
        
        features['total_distance_km'] = self._calculate_distance(data)
        features['avg_speed'] = data['speed'].mean()
        features['max_speed'] = data['speed'].max()
        features['speed_variance'] = data['speed'].var()
        
        # Acceleration statistics
        features['avg_acceleration'] = data['acceleration'].mean()
        features['max_acceleration'] = data['acceleration'].max()
        features['min_acceleration'] = data['acceleration'].min()
        
        # Driving behavior metrics
        features['harsh_acceleration_count'] = (data['acceleration'] > 2.5).sum()
        features['harsh_braking_count'] = (data['acceleration'] < -2.5).sum()
        features['speeding_events'] = self._count_speeding_events(data)
        
        # Phone usage statistics
        if 'phone_usage' in data.columns:
            features['phone_usage_duration'] = data['phone_usage'].sum() * 30  # Assuming 30-second intervals
            features['phone_usage_percentage'] = (data['phone_usage'].sum() / len(data)) * 100
        
        # Time-based features
        features['is_night_trip'] = self._is_night_driving(data)
        features['is_weekend'] = data['timestamp'].iloc[0].weekday() >= 5
        features['peak_hour_percentage'] = self._calculate_peak_hour_percentage(data)
        
        return features
    
    def _calculate_distance(self, data: pd.DataFrame) -> float:
        """
        Calculate total trip distance using Haversine formula
        """
        if len(data) < 2:
            return 0.0
        
        def haversine(lat1, lon1, lat2, lon2):
            """Calculate distance between two GPS points"""
            R = 6371  # Earth's radius in kilometers
            
            lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
            c = 2 * np.arcsin(np.sqrt(a))
            distance = R * c
            
            return distance
        
        # Calculate distances between consecutive points
        distances = []
        for i in range(1, len(data)):
            dist = haversine(
                data.iloc[i-1]['latitude'], data.iloc[i-1]['longitude'],
                data.iloc[i]['latitude'], data.iloc[i]['longitude']
            )
            distances.append(dist)
        
        return sum(distances)
    
    def _count_speeding_events(self, data: pd.DataFrame, speed_limit: float = 80) -> int:
        """
        Count speeding events (assuming speed limit)
        """
        return (data['speed'] > speed_limit).sum()
    
    def _is_night_driving(self, data: pd.DataFrame) -> bool:
        """
        Determine if trip occurred during night hours (10 PM - 6 AM)
        """
        night_hours = data['timestamp'].apply(
            lambda x: x.hour >= 22 or x.hour <= 6
        )
        return night_hours.sum() / len(data) > 0.5
    
    def _calculate_peak_hour_percentage(self, data: pd.DataFrame) -> float:
        """
        Calculate percentage of trip during peak hours (7-9 AM, 5-7 PM)
        """
        peak_hours = data['timestamp'].apply(
            lambda x: (7 <= x.hour <= 9) or (17 <= x.hour <= 19)
        )
        return (peak_hours.sum() / len(data)) * 100
