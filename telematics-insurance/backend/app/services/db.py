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
        
        -- Risk assessments table
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
            assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_telematics_driver_timestamp ON telematics_data(driver_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_risk_assessments_driver ON risk_assessments(driver_id);
        CREATE INDEX IF NOT EXISTS idx_policies_driver ON insurance_policies(driver_id);
        CREATE INDEX IF NOT EXISTS idx_claims_policy ON claims(policy_id);
        CREATE INDEX IF NOT EXISTS idx_gamification_driver ON gamification_data(driver_id);
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

# Global database service instance
db_service = DatabaseService()
