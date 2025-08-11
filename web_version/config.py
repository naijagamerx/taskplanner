"""
Configuration settings for Task Planner Web Version
Supports both local development and online deployment
"""

import os
from urllib.parse import urlparse

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'task_planner_web_secret_key_2025'
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Default to SQLite for local development
    DB_TYPE = 'sqlite'
    DB_PATH = os.path.join(os.path.dirname(__file__), 'task_planner.db')
    
    # MySQL Configuration (for online deployment)
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'task_planner')
    MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    
    @classmethod
    def get_database_config(cls):
        """Get database configuration based on environment"""
        
        # If DATABASE_URL is provided (common in cloud deployments)
        if cls.DATABASE_URL:
            url = urlparse(cls.DATABASE_URL)
            
            if url.scheme == 'mysql':
                return {
                    'type': 'mysql',
                    'host': url.hostname,
                    'port': url.port or 3306,
                    'database': url.path.lstrip('/'),
                    'username': url.username,
                    'password': url.password
                }
            elif url.scheme in ['postgres', 'postgresql']:
                # Future PostgreSQL support
                return {
                    'type': 'postgresql',
                    'host': url.hostname,
                    'port': url.port or 5432,
                    'database': url.path.lstrip('/'),
                    'username': url.username,
                    'password': url.password
                }
        
        # Check if MySQL environment variables are set
        if cls.MYSQL_HOST != 'localhost' or cls.MYSQL_PASSWORD:
            return {
                'type': 'mysql',
                'host': cls.MYSQL_HOST,
                'port': cls.MYSQL_PORT,
                'database': cls.MYSQL_DATABASE,
                'username': cls.MYSQL_USERNAME,
                'password': cls.MYSQL_PASSWORD
            }
        
        # Default to SQLite
        return {
            'type': 'sqlite',
            'path': cls.DB_PATH
        }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Force HTTPS in production
    PREFERRED_URL_SCHEME = 'https'
    
    # Production database defaults to MySQL
    @classmethod
    def get_database_config(cls):
        config = super().get_database_config()
        
        # In production, prefer MySQL over SQLite
        if config['type'] == 'sqlite' and (cls.MYSQL_HOST != 'localhost' or cls.MYSQL_PASSWORD):
            return {
                'type': 'mysql',
                'host': cls.MYSQL_HOST,
                'port': cls.MYSQL_PORT,
                'database': cls.MYSQL_DATABASE,
                'username': cls.MYSQL_USERNAME,
                'password': cls.MYSQL_PASSWORD
            }
        
        return config

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
