"""
Database service for Aiven Postgres client
Handles database connections and operations
"""
import os
import asyncpg
import asyncio
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Service for managing Aiven Postgres database connections and operations
    """
    
    def __init__(self):
        self.pool = None
        self.connection_string = settings.aiven_postgres_uri
    
    async def initialize_pool(self):
        """
        Initialize the connection pool
        """
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close_pool(self):
        """
        Close the connection pool
        """
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """
        Get a database connection from the pool
        """
        if not self.pool:
            await self.initialize_pool()
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results
        """
        async with self.get_connection() as conn:
            try:
                rows = await conn.fetch(query, *args)
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise
    
    async def execute_command(self, command: str, *args) -> str:
        """
        Execute an INSERT, UPDATE, or DELETE command
        """
        async with self.get_connection() as conn:
            try:
                result = await conn.execute(command, *args)
                return result
            except Exception as e:
                logger.error(f"Command execution failed: {e}")
                raise
    
    async def create_tables(self):
        """
        Create database tables for telematics insurance platform
        """
        tables_sql = """
        -- Drivers table
        CREATE TABLE IF NOT EXISTS drivers (
            driver_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            age INTEGER,
            gender VARCHAR(10),
            license_number VARCHAR(50),
            phone_number VARCHAR(20),
            address TEXT,
            city VARCHAR(100),
            state VARCHAR(50),
            zip_code VARCHAR(10),
            credit_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Vehicles table
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            driver_id UUID REFERENCES drivers(driver_id) ON DELETE CASCADE,
            make VARCHAR(50),
            model VARCHAR(50),
            year INTEGER,
            vin VARCHAR(17) UNIQUE,
            vehicle_type VARCHAR(20),
            safety_rating INTEGER,
            safety_features JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Telematics data table
        CREATE TABLE IF NOT EXISTS telematics_data (
            data_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            driver_id UUID REFERENCES drivers(driver_id) ON DELETE CASCADE,
            vehicle_id UUID REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
            trip_id UUID,
            timestamp TIMESTAMP NOT NULL,
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            speed DECIMAL(5, 2),
            acceleration DECIMAL(5, 2),
            heading DECIMAL(5, 2),
            phone_usage BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Risk assessments table (enhanced for comprehensive analysis)
        CREATE TABLE IF NOT EXISTS risk_assessments (
            assessment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            driver_id UUID REFERENCES drivers(driver_id) ON DELETE CASCADE,
            trip_id UUID,
            behavior_score DECIMAL(5, 2),
            geographic_risk DECIMAL(5, 2),
            contextual_risk DECIMAL(5, 2),
            overall_risk DECIMAL(5, 2),
            risk_category VARCHAR(20),
            expert_scores JSONB,
            recommendations JSONB,
            assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            -- Enhanced fields for comprehensive analysis
            detailed_behavior_analysis JSONB,
            geographic_analysis JSONB,
            contextual_analysis JSONB,
            ensemble_analysis JSONB,
            premium_information JSONB,
            trend_indicators JSONB,
            weather_conditions JSONB,
            traffic_conditions JSONB,
            route_information JSONB
        );
        
        -- Enhanced sensor data table for detailed analysis
        CREATE TABLE IF NOT EXISTS enhanced_sensor_data (
            sensor_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            driver_id UUID REFERENCES drivers(driver_id) ON DELETE CASCADE,
            trip_id UUID,
            timestamp TIMESTAMP NOT NULL,
            sensor_type VARCHAR(20), -- accelerometer, gyroscope, gps, etc.
            raw_data JSONB, -- Raw sensor readings
            processed_features JSONB, -- Extracted features (jerk, frequency domain, etc.)
            quality_metrics JSONB, -- Data quality indicators
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Trip analysis table for comprehensive trip data
        CREATE TABLE IF NOT EXISTS trip_analysis (
            trip_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            driver_id UUID REFERENCES drivers(driver_id) ON DELETE CASCADE,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            distance_km DECIMAL(8, 3),
            duration_minutes INTEGER,
            start_location JSONB,
            end_location JSONB,
            route_points JSONB,
            behavior_summary JSONB,
            geographic_summary JSONB,
            contextual_summary JSONB,
            overall_risk_score DECIMAL(5, 2),
            gamification_points INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Enhanced claims predictions table
        CREATE TABLE IF NOT EXISTS claims_predictions (
            prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            driver_id UUID REFERENCES drivers(driver_id) ON DELETE CASCADE,
            prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            coverage_type VARCHAR(30),
            frequency_prediction DECIMAL(6, 4),
            severity_prediction DECIMAL(10, 2),
            confidence_interval JSONB,
            risk_factors JSONB,
            telematics_impact JSONB,
            recommendation TEXT,
            model_version VARCHAR(10) DEFAULT '2.0',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Driver scoring history for trend analysis
        CREATE TABLE IF NOT EXISTS driver_scoring_history (
            scoring_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            driver_id UUID REFERENCES drivers(driver_id) ON DELETE CASCADE,
            assessment_date DATE,
            behavior_score DECIMAL(5, 2),
            geographic_risk DECIMAL(5, 2),
            contextual_risk DECIMAL(5, 2),
            overall_risk DECIMAL(5, 2),
            tier VARCHAR(20),
            premium_adjustment DECIMAL(5, 3),
            data_quality_score DECIMAL(3, 2),
            trend_direction VARCHAR(15), -- improving, stable, declining
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Enhanced gamification with detailed tracking
        CREATE TABLE IF NOT EXISTS enhanced_gamification (
            gamification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            driver_id UUID REFERENCES drivers(driver_id) ON DELETE CASCADE,
            total_points INTEGER DEFAULT 0,
            current_level INTEGER DEFAULT 1,
            badges_earned JSONB DEFAULT '[]',
            achievements JSONB DEFAULT '{}',
            recent_achievements JSONB DEFAULT '[]',
            point_breakdown JSONB DEFAULT '{}',
            streak_information JSONB DEFAULT '{}',
            comparison_data JSONB DEFAULT '{}',
            monthly_summary JSONB DEFAULT '{}',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Insurance policies table
        CREATE TABLE IF NOT EXISTS insurance_policies (
            policy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            driver_id UUID REFERENCES drivers(driver_id) ON DELETE CASCADE,
            vehicle_id UUID REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
            base_premium DECIMAL(10, 2),
            adjusted_premium DECIMAL(10, 2),
            adjustment_factor DECIMAL(4, 3),
            tier VARCHAR(20),
            coverage_types JSONB,
            effective_date DATE,
            expiration_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Claims table
        CREATE TABLE IF NOT EXISTS claims (
            claim_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            policy_id UUID REFERENCES insurance_policies(policy_id) ON DELETE CASCADE,
            driver_id UUID REFERENCES drivers(driver_id) ON DELETE CASCADE,
            claim_type VARCHAR(20),
            claim_amount DECIMAL(10, 2),
            claim_date DATE,
            status VARCHAR(20),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Gamification data table
        CREATE TABLE IF NOT EXISTS gamification_data (
            gamification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            driver_id UUID REFERENCES drivers(driver_id) ON DELETE CASCADE,
            total_points INTEGER DEFAULT 0,
            current_level INTEGER DEFAULT 1,
            badges_earned JSONB DEFAULT '[]',
            achievements JSONB DEFAULT '{}',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create enhanced indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_telematics_driver_timestamp ON telematics_data(driver_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_risk_assessments_driver ON risk_assessments(driver_id);
        CREATE INDEX IF NOT EXISTS idx_policies_driver ON insurance_policies(driver_id);
        CREATE INDEX IF NOT EXISTS idx_claims_policy ON claims(policy_id);
        CREATE INDEX IF NOT EXISTS idx_gamification_driver ON gamification_data(driver_id);
        
        -- Enhanced indexes for new tables
        CREATE INDEX IF NOT EXISTS idx_enhanced_sensor_trip ON enhanced_sensor_data(trip_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_enhanced_sensor_driver ON enhanced_sensor_data(driver_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_trip_analysis_driver ON trip_analysis(driver_id, start_time);
        CREATE INDEX IF NOT EXISTS idx_claims_predictions_driver ON claims_predictions(driver_id, prediction_date);
        CREATE INDEX IF NOT EXISTS idx_scoring_history_driver ON driver_scoring_history(driver_id, assessment_date);
        CREATE INDEX IF NOT EXISTS idx_enhanced_gamification_driver ON enhanced_gamification(driver_id);
        
        -- Performance indexes for complex queries
        CREATE INDEX IF NOT EXISTS idx_risk_assessments_composite ON risk_assessments(driver_id, assessment_date, overall_risk);
        CREATE INDEX IF NOT EXISTS idx_trip_analysis_risk ON trip_analysis(driver_id, overall_risk_score);
        CREATE INDEX IF NOT EXISTS idx_scoring_trend ON driver_scoring_history(driver_id, trend_direction, assessment_date);
        """
        
        async with self.get_connection() as conn:
            try:
                await conn.execute(tables_sql)
                logger.info("Database tables created successfully")
            except Exception as e:
                logger.error(f"Failed to create tables: {e}")
                raise
    
    # Driver operations
    async def create_driver(self, driver_data: Dict[str, Any]) -> str:
        """
        Create a new driver record
        """
        query = """
        INSERT INTO drivers (email, first_name, last_name, age, gender, license_number, 
                           phone_number, address, city, state, zip_code, credit_score)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        RETURNING driver_id
        """
        
        async with self.get_connection() as conn:
            result = await conn.fetchrow(query, 
                driver_data['email'], driver_data.get('first_name'),
                driver_data.get('last_name'), driver_data.get('age'),
                driver_data.get('gender'), driver_data.get('license_number'),
                driver_data.get('phone_number'), driver_data.get('address'),
                driver_data.get('city'), driver_data.get('state'),
                driver_data.get('zip_code'), driver_data.get('credit_score')
            )
            return str(result['driver_id'])
    
    async def get_driver(self, driver_id: str) -> Optional[Dict[str, Any]]:
        """
        Get driver information by ID
        """
        query = "SELECT * FROM drivers WHERE driver_id = $1"
        results = await self.execute_query(query, driver_id)
        return results[0] if results else None
    
    # Telematics data operations
    async def save_telematics_data(self, telematics_records: List[Dict[str, Any]]):
        """
        Bulk save telematics data records
        """
        query = """
        INSERT INTO telematics_data (driver_id, vehicle_id, trip_id, timestamp, 
                                   latitude, longitude, speed, acceleration, heading, phone_usage)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """
        
        async with self.get_connection() as conn:
            await conn.executemany(query, [
                (record['driver_id'], record.get('vehicle_id'), record.get('trip_id'),
                 record['timestamp'], record['latitude'], record['longitude'],
                 record['speed'], record['acceleration'], record['heading'],
                 record.get('phone_usage', False))
                for record in telematics_records
            ])
    
    # Risk assessment operations
    async def save_risk_assessment(self, assessment_data: Dict[str, Any]) -> str:
        """
        Save risk assessment results
        """
        query = """
        INSERT INTO risk_assessments (driver_id, trip_id, behavior_score, geographic_risk,
                                    contextual_risk, overall_risk, risk_category, 
                                    expert_scores, recommendations)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING assessment_id
        """
        
        async with self.get_connection() as conn:
            result = await conn.fetchrow(query,
                assessment_data['driver_id'], assessment_data.get('trip_id'),
                assessment_data['behavior_score'], assessment_data['geographic_risk'],
                assessment_data['contextual_risk'], assessment_data['overall_risk'],
                assessment_data['risk_category'], assessment_data['expert_scores'],
                assessment_data['recommendations']
            )
            return str(result['assessment_id'])
    
    # Gamification operations
    async def update_driver_points(self, driver_id: str, points_to_add: int, 
                                 new_badges: List[str] = None):
        """
        Update driver's gamification points and badges
        """
        if new_badges is None:
            new_badges = []
        
        query = """
        INSERT INTO gamification_data (driver_id, total_points, badges_earned, last_updated)
        VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
        ON CONFLICT (driver_id) 
        DO UPDATE SET 
            total_points = gamification_data.total_points + $2,
            badges_earned = $3,
            last_updated = CURRENT_TIMESTAMP
        """
        
        await self.execute_command(query, driver_id, points_to_add, new_badges)
    
    async def get_driver_gamification_data(self, driver_id: str) -> Optional[Dict[str, Any]]:
        """
        Get driver's gamification data
        """
        query = "SELECT * FROM gamification_data WHERE driver_id = $1"
        results = await self.execute_query(query, driver_id)
        return results[0] if results else None
    
    # Enhanced methods for comprehensive analysis
    async def save_enhanced_risk_assessment(self, assessment_data: Dict[str, Any]) -> str:
        """
        Save comprehensive risk assessment with enhanced data
        """
        query = """
        INSERT INTO risk_assessments (
            driver_id, trip_id, behavior_score, geographic_risk, contextual_risk, 
            overall_risk, risk_category, expert_scores, recommendations,
            detailed_behavior_analysis, geographic_analysis, contextual_analysis,
            ensemble_analysis, premium_information, trend_indicators,
            weather_conditions, traffic_conditions, route_information
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
        RETURNING assessment_id
        """
        
        async with self.get_connection() as conn:
            result = await conn.fetchrow(query,
                assessment_data['driver_id'], assessment_data.get('trip_id'),
                assessment_data['behavior_score'], assessment_data['geographic_risk'],
                assessment_data['contextual_risk'], assessment_data['overall_risk'],
                assessment_data['risk_category'], assessment_data['expert_scores'],
                assessment_data['recommendations'], assessment_data.get('detailed_behavior_analysis'),
                assessment_data.get('geographic_analysis'), assessment_data.get('contextual_analysis'),
                assessment_data.get('ensemble_analysis'), assessment_data.get('premium_information'),
                assessment_data.get('trend_indicators'), assessment_data.get('weather_conditions'),
                assessment_data.get('traffic_conditions'), assessment_data.get('route_information')
            )
            return str(result['assessment_id'])
    
    async def save_trip_analysis(self, trip_data: Dict[str, Any]) -> str:
        """
        Save comprehensive trip analysis
        """
        query = """
        INSERT INTO trip_analysis (
            trip_id, driver_id, start_time, end_time, distance_km, duration_minutes,
            start_location, end_location, route_points, behavior_summary,
            geographic_summary, contextual_summary, overall_risk_score, gamification_points
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
        RETURNING trip_id
        """
        
        async with self.get_connection() as conn:
            result = await conn.fetchrow(query,
                trip_data['trip_id'], trip_data['driver_id'], trip_data['start_time'],
                trip_data['end_time'], trip_data['distance_km'], trip_data['duration_minutes'],
                trip_data['start_location'], trip_data['end_location'], trip_data['route_points'],
                trip_data['behavior_summary'], trip_data['geographic_summary'],
                trip_data['contextual_summary'], trip_data['overall_risk_score'],
                trip_data['gamification_points']
            )
            return str(result['trip_id'])
    
    async def save_enhanced_sensor_data(self, sensor_records: List[Dict[str, Any]]):
        """
        Bulk save enhanced sensor data with processed features
        """
        query = """
        INSERT INTO enhanced_sensor_data (
            driver_id, trip_id, timestamp, sensor_type, raw_data, 
            processed_features, quality_metrics
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """
        
        async with self.get_connection() as conn:
            await conn.executemany(query, [
                (record['driver_id'], record.get('trip_id'), record['timestamp'],
                 record['sensor_type'], record['raw_data'], record.get('processed_features'),
                 record.get('quality_metrics'))
                for record in sensor_records
            ])
    
    async def save_claims_prediction(self, prediction_data: Dict[str, Any]) -> str:
        """
        Save claims prediction results
        """
        query = """
        INSERT INTO claims_predictions (
            driver_id, coverage_type, frequency_prediction, severity_prediction,
            confidence_interval, risk_factors, telematics_impact, recommendation, model_version
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING prediction_id
        """
        
        async with self.get_connection() as conn:
            result = await conn.fetchrow(query,
                prediction_data['driver_id'], prediction_data['coverage_type'],
                prediction_data['frequency_prediction'], prediction_data['severity_prediction'],
                prediction_data['confidence_interval'], prediction_data['risk_factors'],
                prediction_data['telematics_impact'], prediction_data['recommendation'],
                prediction_data.get('model_version', '2.0')
            )
            return str(result['prediction_id'])
    
    async def save_driver_scoring_history(self, scoring_data: Dict[str, Any]):
        """
        Save driver scoring history for trend analysis
        """
        query = """
        INSERT INTO driver_scoring_history (
            driver_id, assessment_date, behavior_score, geographic_risk, contextual_risk,
            overall_risk, tier, premium_adjustment, data_quality_score, trend_direction
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT (driver_id, assessment_date) 
        DO UPDATE SET 
            behavior_score = EXCLUDED.behavior_score,
            geographic_risk = EXCLUDED.geographic_risk,
            contextual_risk = EXCLUDED.contextual_risk,
            overall_risk = EXCLUDED.overall_risk,
            tier = EXCLUDED.tier,
            premium_adjustment = EXCLUDED.premium_adjustment,
            data_quality_score = EXCLUDED.data_quality_score,
            trend_direction = EXCLUDED.trend_direction
        """
        
        await self.execute_command(query,
            scoring_data['driver_id'], scoring_data['assessment_date'],
            scoring_data['behavior_score'], scoring_data['geographic_risk'],
            scoring_data['contextual_risk'], scoring_data['overall_risk'],
            scoring_data['tier'], scoring_data['premium_adjustment'],
            scoring_data['data_quality_score'], scoring_data['trend_direction']
        )
    
    async def update_enhanced_gamification(self, driver_id: str, gamification_data: Dict[str, Any]):
        """
        Update enhanced gamification data with detailed tracking
        """
        query = """
        INSERT INTO enhanced_gamification (
            driver_id, total_points, current_level, badges_earned, achievements,
            recent_achievements, point_breakdown, streak_information, 
            comparison_data, monthly_summary, last_updated
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, CURRENT_TIMESTAMP)
        ON CONFLICT (driver_id)
        DO UPDATE SET
            total_points = EXCLUDED.total_points,
            current_level = EXCLUDED.current_level,
            badges_earned = EXCLUDED.badges_earned,
            achievements = EXCLUDED.achievements,
            recent_achievements = EXCLUDED.recent_achievements,
            point_breakdown = EXCLUDED.point_breakdown,
            streak_information = EXCLUDED.streak_information,
            comparison_data = EXCLUDED.comparison_data,
            monthly_summary = EXCLUDED.monthly_summary,
            last_updated = CURRENT_TIMESTAMP
        """
        
        await self.execute_command(query,
            driver_id, gamification_data['total_points'], gamification_data['current_level'],
            gamification_data['badges_earned'], gamification_data['achievements'],
            gamification_data['recent_achievements'], gamification_data['point_breakdown'],
            gamification_data['streak_information'], gamification_data['comparison_data'],
            gamification_data['monthly_summary']
        )
    
    # Analysis and reporting methods
    async def get_driver_risk_history(self, driver_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get driver's risk assessment history for trend analysis
        """
        query = """
        SELECT * FROM driver_scoring_history 
        WHERE driver_id = $1 AND assessment_date >= CURRENT_DATE - INTERVAL '%s days'
        ORDER BY assessment_date DESC
        """ % days
        
        return await self.execute_query(query, driver_id)
    
    async def get_driver_trip_summary(self, driver_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get driver's trip summary for the specified period
        """
        query = """
        SELECT * FROM trip_analysis 
        WHERE driver_id = $1 AND start_time >= CURRENT_TIMESTAMP - INTERVAL '%s days'
        ORDER BY start_time DESC
        """ % days
        
        return await self.execute_query(query, driver_id)
    
    async def get_claims_prediction_history(self, driver_id: str, coverage_type: str = None) -> List[Dict[str, Any]]:
        """
        Get driver's claims prediction history
        """
        if coverage_type:
            query = """
            SELECT * FROM claims_predictions 
            WHERE driver_id = $1 AND coverage_type = $2
            ORDER BY prediction_date DESC LIMIT 10
            """
            return await self.execute_query(query, driver_id, coverage_type)
        else:
            query = """
            SELECT * FROM claims_predictions 
            WHERE driver_id = $1
            ORDER BY prediction_date DESC LIMIT 20
            """
            return await self.execute_query(query, driver_id)
    
    async def get_enhanced_gamification_data(self, driver_id: str) -> Optional[Dict[str, Any]]:
        """
        Get enhanced gamification data for a driver
        """
        query = "SELECT * FROM enhanced_gamification WHERE driver_id = $1"
        results = await self.execute_query(query, driver_id)
        return results[0] if results else None
    
    async def get_comprehensive_driver_profile(self, driver_id: str) -> Dict[str, Any]:
        """
        Get comprehensive driver profile with all related data
        """
        # Get basic driver info
        driver_info = await self.get_driver(driver_id)
        if not driver_info:
            return {}
        
        # Get risk history
        risk_history = await self.get_driver_risk_history(driver_id, 90)
        
        # Get recent trips
        trip_summary = await self.get_driver_trip_summary(driver_id, 30)
        
        # Get gamification data
        gamification = await self.get_enhanced_gamification_data(driver_id)
        
        # Get recent claims predictions
        claims_predictions = await self.get_claims_prediction_history(driver_id)
        
        return {
            'driver_info': driver_info,
            'risk_history': risk_history,
            'recent_trips': trip_summary,
            'gamification': gamification,
            'claims_predictions': claims_predictions,
            'profile_completeness': self._calculate_profile_completeness(
                driver_info, risk_history, trip_summary, gamification
            )
        }
    
    def _calculate_profile_completeness(self, driver_info: Dict, risk_history: List, 
                                      trip_summary: List, gamification: Dict) -> float:
        """
        Calculate driver profile completeness score
        """
        score = 0.0
        
        # Basic info (25%)
        if driver_info:
            basic_fields = ['email', 'age', 'gender', 'license_number']
            filled_fields = sum(1 for field in basic_fields if driver_info.get(field))
            score += (filled_fields / len(basic_fields)) * 0.25
        
        # Risk history (35%)
        if risk_history:
            score += min(len(risk_history) / 30, 1.0) * 0.35
        
        # Trip data (30%)
        if trip_summary:
            score += min(len(trip_summary) / 20, 1.0) * 0.30
        
        # Gamification engagement (10%)
        if gamification and gamification.get('total_points', 0) > 0:
            score += 0.10
        
        return round(score, 2)

# Global database service instance
db_service = DatabaseService()
