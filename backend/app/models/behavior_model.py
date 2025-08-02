"""
Expert 1: Driver Behavior Scoring Model
Analyzes driving patterns from accelerometer and gyroscope sensor data
Based on comprehensive telematics analysis including time/frequency domain features
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from scipy import signal
from scipy.ndimage import gaussian_filter1d
from sklearn.preprocessing import StandardScaler, MinMaxScaler

class BehaviorModel:
    """
    Advanced driver behavior scoring model for telematics sensor data
    Implements feature extraction from accelerometer/gyroscope data
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.sampling_rate = 2  # 2 samples per second
        self.window_size = 8  # 4-second windows
        self.overlap_ratio = 0.25
        
        # Enhanced feature columns based on notebook analysis
        self.sensor_columns = ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ']
        self.feature_columns = self._get_all_feature_columns()
        
        # Behavior classification mapping
        self.class_mapping = {'SLOW': 0, 'NORMAL': 1, 'AGGRESSIVE': 2}
        self.inverse_class_mapping = {0: 'SLOW', 1: 'NORMAL', 2: 'AGGRESSIVE'}
    
    def _get_all_feature_columns(self) -> List[str]:
        """
        Generate comprehensive feature column names based on notebook analysis
        """
        features = []
        
        # Time domain features for each sensor
        for sensor in self.sensor_columns:
            features.extend([
                f'{sensor}_mean', f'{sensor}_std', f'{sensor}_min', f'{sensor}_max',
                f'{sensor}_median', f'{sensor}_range', f'{sensor}_rms', 
                f'{sensor}_var', f'{sensor}_skew', f'{sensor}_kurtosis'
            ])
        
        # Jerk features (derivative of acceleration)
        jerk_columns = ['JerkX', 'JerkY', 'JerkZ', 'Jerk_magnitude']
        for jerk in jerk_columns:
            features.extend([f'{jerk}_mean', f'{jerk}_std', f'{jerk}_max', f'{jerk}_rms'])
        
        # Magnitude features
        mag_columns = ['Acc_magnitude', 'Gyro_magnitude', 'Total_magnitude', 'Magnitude_ratio']
        for mag in mag_columns:
            features.extend([f'{mag}_mean', f'{mag}_std', f'{mag}_max', f'{mag}_min', f'{mag}_range'])
        
        # Frequency domain features
        for sensor in self.sensor_columns:
            features.extend([
                f'{sensor}_total_energy', f'{sensor}_mean_frequency', f'{sensor}_spectral_centroid',
                f'{sensor}_energy_band_0_0.5', f'{sensor}_energy_band_0.5_1', f'{sensor}_energy_band_1_2',
                f'{sensor}_spectral_variance', f'{sensor}_spectral_skewness', f'{sensor}_spectral_kurtosis'
            ])
        
        return features
    
    def preprocess_sensor_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess raw sensor data with smoothing and normalization
        """
        processed = data.copy()
        
        # Ensure data is sorted by timestamp
        if 'Timestamp' in processed.columns:
            processed = processed.sort_values('Timestamp').reset_index(drop=True)
        
        # Normalize sensor data
        if all(col in processed.columns for col in self.sensor_columns):
            scaler = MinMaxScaler()
            processed[self.sensor_columns] = scaler.fit_transform(processed[self.sensor_columns])
        
        # Apply rolling average smoothing
        for col in self.sensor_columns:
            if col in processed.columns:
                processed[f'{col}_smooth'] = processed[col].rolling(
                    window=self.window_size, center=True
                ).mean()
        
        # Fill NaN values from smoothing
        processed = processed.fillna(method='bfill').fillna(method='ffill')
        
        return processed
    
    def calculate_jerk_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate jerk (derivative of acceleration) features
        """
        jerk_data = data.copy()
        
        # Calculate time differences
        if 'Timestamp' in data.columns:
            time_diff = data['Timestamp'].diff().fillna(0.5)
        else:
            time_diff = 0.5  # Default 0.5s sampling
        
        # Calculate jerk for each acceleration axis
        for axis in ['X', 'Y', 'Z']:
            acc_col = f'Acc{axis}'
            jerk_col = f'Jerk{axis}'
            if acc_col in data.columns:
                jerk_data[jerk_col] = data[acc_col].diff().div(time_diff, fill_value=0)
        
        # Calculate jerk magnitude
        if all(f'Jerk{axis}' in jerk_data.columns for axis in ['X', 'Y', 'Z']):
            jerk_data['Jerk_magnitude'] = np.sqrt(
                jerk_data['JerkX']**2 + jerk_data['JerkY']**2 + jerk_data['JerkZ']**2
            )
        
        # Fill NaN values
        jerk_data = jerk_data.fillna(0)
        
        return jerk_data
    
    def calculate_magnitude_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate magnitude features for acceleration and gyroscope
        """
        mag_data = data.copy()
        
        # Calculate acceleration magnitude
        if all(f'Acc{axis}' in data.columns for axis in ['X', 'Y', 'Z']):
            mag_data['Acc_magnitude'] = np.sqrt(
                data['AccX']**2 + data['AccY']**2 + data['AccZ']**2
            )
        
        # Calculate gyroscope magnitude
        if all(f'Gyro{axis}' in data.columns for axis in ['X', 'Y', 'Z']):
            mag_data['Gyro_magnitude'] = np.sqrt(
                data['GyroX']**2 + data['GyroY']**2 + data['GyroZ']**2
            )
        
        # Calculate combined magnitudes
        if 'Acc_magnitude' in mag_data.columns and 'Gyro_magnitude' in mag_data.columns:
            mag_data['Total_magnitude'] = mag_data['Acc_magnitude'] + mag_data['Gyro_magnitude']
            mag_data['Magnitude_ratio'] = mag_data['Acc_magnitude'] / (mag_data['Gyro_magnitude'] + 1e-8)
        
        return mag_data
    
    def extract_time_domain_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract time domain features using sliding windows approach from notebook
        """
        features_list = []
        overlap = int(self.window_size * self.overlap_ratio)
        
        for i in range(0, len(data) - self.window_size + 1, overlap):
            window = data.iloc[i:i+self.window_size]
            
            features_dict = {
                'window_start': i,
                'timestamp': window.get('Timestamp', pd.Series([i])).iloc[-1],
                'class': window.get('Class_numeric', pd.Series([1])).iloc[-1]
            }
            
            # Extract features for each sensor column
            for col in self.sensor_columns:
                if col in window.columns:
                    values = window[col].values
                    features_dict.update({
                        f'{col}_mean': np.mean(values),
                        f'{col}_std': np.std(values),
                        f'{col}_min': np.min(values),
                        f'{col}_max': np.max(values),
                        f'{col}_median': np.median(values),
                        f'{col}_range': np.max(values) - np.min(values),
                        f'{col}_rms': np.sqrt(np.mean(values**2)),
                        f'{col}_var': np.var(values),
                        f'{col}_skew': pd.Series(values).skew(),
                        f'{col}_kurtosis': pd.Series(values).kurtosis()
                    })
            
            features_list.append(features_dict)
        
        return pd.DataFrame(features_list)
    
    def calculate_frequency_features(self, signal_data: np.ndarray) -> Dict[str, float]:
        """
        Calculate frequency domain features using FFT
        """
        # Apply FFT
        fft = np.fft.fft(signal_data)
        freqs = np.fft.fftfreq(len(signal_data), 1/self.sampling_rate)
        
        # Power spectral density
        psd = np.abs(fft)**2
        
        freq_features = {}
        
        # Basic frequency features
        freq_features['total_energy'] = np.sum(psd)
        
        # Only use positive frequencies
        pos_freqs = freqs[:len(freqs)//2]
        pos_psd = psd[:len(psd)//2]
        
        if np.sum(pos_psd) > 0:
            freq_features['mean_frequency'] = np.sum(pos_freqs * pos_psd) / np.sum(pos_psd)
            freq_features['spectral_centroid'] = freq_features['mean_frequency']
        else:
            freq_features['mean_frequency'] = 0
            freq_features['spectral_centroid'] = 0
        
        # Energy in different frequency bands
        band1 = (pos_freqs >= 0) & (pos_freqs < 0.5)
        band2 = (pos_freqs >= 0.5) & (pos_freqs < 1.0)
        band3 = (pos_freqs >= 1.0) & (pos_freqs < 2.0)
        
        freq_features['energy_band_0_0.5'] = np.sum(pos_psd[band1])
        freq_features['energy_band_0.5_1'] = np.sum(pos_psd[band2])
        freq_features['energy_band_1_2'] = np.sum(pos_psd[band3])
        
        # Spectral statistics
        freq_features['spectral_variance'] = np.var(pos_psd)
        freq_features['spectral_skewness'] = pd.Series(pos_psd).skew()
        freq_features['spectral_kurtosis'] = pd.Series(pos_psd).kurtosis()
        
        return freq_features
    
    def preprocess_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Complete feature preprocessing pipeline based on notebook analysis
        """
        # Step 1: Preprocess sensor data
        processed = self.preprocess_sensor_data(data)
        
        # Step 2: Calculate jerk features
        processed = self.calculate_jerk_features(processed)
        
        # Step 3: Calculate magnitude features
        processed = self.calculate_magnitude_features(processed)
        
        # Step 4: Extract time domain features
        time_features = self.extract_time_domain_features(processed)
        
        # Step 5: Add frequency domain features
        time_features = self._add_frequency_features(time_features, processed)
        
        # Step 6: Handle missing values and infinite values
        feature_cols = [col for col in time_features.columns 
                       if col not in ['window_start', 'timestamp', 'class']]
        X = time_features[feature_cols].fillna(0)
        X = X.replace([np.inf, -np.inf], np.nan).fillna(X.median())
        
        return X
    
    def _add_frequency_features(self, time_features: pd.DataFrame, signal_data: pd.DataFrame) -> pd.DataFrame:
        """
        Add frequency domain features to time domain features
        """
        overlap = int(self.window_size * self.overlap_ratio)
        
        for i, row in time_features.iterrows():
            start_idx = int(row['window_start'])
            end_idx = start_idx + self.window_size
            
            if end_idx <= len(signal_data):
                window_data = signal_data.iloc[start_idx:end_idx]
                
                # Calculate frequency features for each sensor
                for col in self.sensor_columns:
                    if col in window_data.columns:
                        signal_values = window_data[col].values
                        freq_features = self.calculate_frequency_features(signal_values)
                        
                        for freq_name, freq_value in freq_features.items():
                            time_features.loc[i, f'{col}_{freq_name}'] = freq_value
        
        return time_features
    
    def score_behavior(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive driver behavior score using advanced features
        """
        # Initialize scoring components
        base_score = 100
        risk_factors = []
        feature_scores = {}
        
        # Acceleration-based scoring
        acc_magnitude_mean = features.get('Acc_magnitude_mean', 0)
        if acc_magnitude_mean > 0.8:  # High acceleration patterns
            penalty = min(20, (acc_magnitude_mean - 0.8) * 50)
            base_score -= penalty
            risk_factors.append(f"High acceleration patterns (penalty: {penalty:.1f})")
        
        # Jerk-based scoring (smoothness of driving)
        jerk_magnitude_mean = features.get('Jerk_magnitude_mean', 0)
        if jerk_magnitude_mean > 0.5:  # Jerky driving
            penalty = min(15, (jerk_magnitude_mean - 0.5) * 30)
            base_score -= penalty
            risk_factors.append(f"Jerky driving patterns (penalty: {penalty:.1f})")
        
        # Gyroscope-based scoring (steering behavior)
        gyro_magnitude_std = features.get('Gyro_magnitude_std', 0)
        if gyro_magnitude_std > 0.3:  # Erratic steering
            penalty = min(10, (gyro_magnitude_std - 0.3) * 25)
            base_score -= penalty
            risk_factors.append(f"Erratic steering (penalty: {penalty:.1f})")
        
        # Frequency domain analysis
        high_freq_energy = sum([
            features.get(f'{sensor}_energy_band_1_2', 0) 
            for sensor in self.sensor_columns
        ])
        if high_freq_energy > 100:  # High frequency vibrations
            penalty = min(8, (high_freq_energy - 100) / 50)
            base_score -= penalty
            risk_factors.append(f"High frequency driving patterns (penalty: {penalty:.1f})")
        
        # Calculate individual component scores
        feature_scores = {
            'acceleration_score': max(0, 100 - (acc_magnitude_mean * 100)),
            'smoothness_score': max(0, 100 - (jerk_magnitude_mean * 100)),
            'steering_score': max(0, 100 - (gyro_magnitude_std * 100)),
            'frequency_score': max(0, 100 - (high_freq_energy / 10))
        }
        
        # Apply bounds
        final_score = max(0, min(100, base_score))
        
        return {
            'behavior_score': final_score,
            'risk_level': self._categorize_behavior_risk(final_score),
            'feature_scores': feature_scores,
            'risk_factors': risk_factors,
            'driving_style': self._classify_driving_style(features)
        }
    
    def _categorize_behavior_risk(self, score: float) -> str:
        """Categorize behavior risk level"""
        if score >= 80:
            return "Low Risk"
        elif score >= 60:
            return "Moderate Risk" 
        elif score >= 40:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def _classify_driving_style(self, features: Dict[str, Any]) -> str:
        """Classify overall driving style based on features"""
        acc_mag = features.get('Acc_magnitude_mean', 0)
        jerk_mag = features.get('Jerk_magnitude_mean', 0)
        gyro_std = features.get('Gyro_magnitude_std', 0)
        
        if acc_mag < 0.3 and jerk_mag < 0.2 and gyro_std < 0.15:
            return "SMOOTH"
        elif acc_mag > 0.7 or jerk_mag > 0.6:
            return "AGGRESSIVE"
        else:
            return "NORMAL"
    
    def get_recommendations(self, score: float, risk_factors: List[str]) -> List[str]:
        """
        Provide personalized driving improvement recommendations
        """
        recommendations = []
        
        if score < 40:
            recommendations.extend([
                "Focus on smooth acceleration and braking",
                "Maintain steady steering inputs",
                "Reduce aggressive driving behaviors",
                "Practice defensive driving techniques"
            ])
        elif score < 60:
            recommendations.extend([
                "Work on maintaining consistent speeds",
                "Avoid sudden steering movements", 
                "Practice gradual acceleration and deceleration"
            ])
        elif score < 80:
            recommendations.extend([
                "Continue practicing smooth driving habits",
                "Monitor your acceleration patterns"
            ])
        else:
            recommendations.append("Excellent driving! Maintain these safe habits")
        
        # Add specific recommendations based on risk factors
        if any("acceleration" in factor for factor in risk_factors):
            recommendations.append("Practice gentler acceleration and braking")
        if any("steering" in factor for factor in risk_factors):
            recommendations.append("Focus on smooth, gradual steering inputs")
        if any("frequency" in factor for factor in risk_factors):
            recommendations.append("Avoid rapid, jerky movements while driving")
        
        return recommendations
    
    def predict_behavior_class(self, features: pd.DataFrame) -> Dict[str, Any]:
        """
        Predict driving behavior class (SLOW, NORMAL, AGGRESSIVE) using extracted features
        """
        # This would use a trained model in production
        # For now, use rule-based classification
        
        predictions = []
        confidence_scores = []
        
        for _, row in features.iterrows():
            acc_mag = row.get('Acc_magnitude_mean', 0)
            jerk_mag = row.get('Jerk_magnitude_mean', 0)
            
            if acc_mag < 0.3 and jerk_mag < 0.2:
                pred_class = 'SLOW'
                confidence = 0.8
            elif acc_mag > 0.7 or jerk_mag > 0.6:
                pred_class = 'AGGRESSIVE'
                confidence = 0.9
            else:
                pred_class = 'NORMAL'
                confidence = 0.7
            
            predictions.append(pred_class)
            confidence_scores.append(confidence)
        
        return {
            'predictions': predictions,
            'confidence_scores': confidence_scores,
            'class_distribution': pd.Series(predictions).value_counts().to_dict()
        }
