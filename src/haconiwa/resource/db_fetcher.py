import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import json
import yaml
from sqlalchemy.exc import SQLAlchemyError
from haconiwa.core.config import Config
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DBFetcher:
    def __init__(self):
        self.config = Config("config.yaml")
        # Default SQLite database for now
        self.engine = create_engine("sqlite:///haconiwa.db", pool_size=10, max_overflow=20)
        self.Session = sessionmaker(bind=self.engine)

    def execute_query(self, query, params=None):
        session = self.Session()
        try:
            result = session.execute(query, params)
            return result.fetchall()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def fetch_as_dataframe(self, query, params=None):
        try:
            result = self.execute_query(query, params)
            return pd.DataFrame(result)
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def fetch_as_json(self, query, params=None):
        df = self.fetch_as_dataframe(query, params)
        if df is not None:
            return df.to_json(orient='records')
        return None

    def fetch_as_yaml(self, query, params=None):
        df = self.fetch_as_dataframe(query, params)
        if df is not None:
            return yaml.dump(df.to_dict(orient='records'))
        return None

    def fetch_as_csv(self, query, params=None):
        df = self.fetch_as_dataframe(query, params)
        if df is not None:
            return df.to_csv(index=False)
        return None

    def retry_query(self, query, params=None, retries=3):
        for attempt in range(retries):
            try:
                return self.execute_query(query, params)
            except SQLAlchemyError as e:
                if attempt < retries - 1:
                    continue
                else:
                    raise e

class DatabaseManager:
    """Database scanner and connection manager"""
    
    _configs = {}
    
    def __init__(self):
        pass
    
    @classmethod
    def register_config(cls, name: str, config: Dict[str, Any]):
        """Register Database configuration"""
        cls._configs[name] = config
        logger.info(f"Registered Database config: {name}")
    
    def scan(self, config_name: str) -> Dict[str, Any]:
        """Scan database using configuration"""
        config = self._configs.get(config_name)
        if not config:
            logger.error(f"Database config not found: {config_name}")
            return {}
        
        # Mock implementation - would use actual database connection
        dsn = config.get("dsn")
        use_ssl = config.get("use_ssl", False)
        
        logger.info(f"Scanning database with DSN: {dsn}, SSL: {use_ssl}")
        
        # Return mock results
        return {
            "tables": ["users", "posts", "comments", "tags"],
            "views": ["user_posts", "comment_counts"],
            "indexes": ["idx_users_email", "idx_posts_created_at"]
        }

# Example usage:
# db_fetcher = DBFetcher()
# result = db_fetcher.fetch_as_json("SELECT * FROM users")
# print(result)