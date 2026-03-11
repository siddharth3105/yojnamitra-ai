"""
DynamoDB Integration for YojnaMitra
Stores user profiles, search history, and saved schemes
"""

import os
import boto3
from datetime import datetime
from typing import Dict, List, Optional
import logging
import json

logger = logging.getLogger(__name__)

class YojnaMitraDB:
    """DynamoDB interface for YojnaMitra"""
    
    def __init__(self):
        """Initialize DynamoDB connection"""
        try:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=os.getenv("BEDROCK_REGION", "ap-south-1"),
                aws_access_key_id=os.getenv("BEDROCK_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("BEDROCK_SECRET_ACCESS_KEY")
            )
            self.table_name = 'YojnaMitra-Users'
            self.table = self.dynamodb.Table(self.table_name)
            logger.info(f"Connected to DynamoDB table: {self.table_name}")
        except Exception as e:
            logger.error(f"Error connecting to DynamoDB: {str(e)}")
            self.table = None
    
    def save_user_profile(self, user_id: str, profile: Dict) -> bool:
        """
        Save user profile to DynamoDB
        
        Args:
            user_id: Unique user identifier (phone number)
            profile: User profile dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.table:
            logger.warning("DynamoDB table not available")
            return False
        
        try:
            item = {
                'user_id': user_id,
                'name': profile.get('name', ''),
                'age': profile.get('age', 0),
                'state': profile.get('state', ''),
                'occupation': profile.get('occupation', ''),
                'income': profile.get('income', 0),
                'category': profile.get('category', ''),
                'gender': profile.get('gender', ''),
                'email': profile.get('email', ''),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'search_history': [],
                'saved_schemes': []
            }
            
            self.table.put_item(Item=item)
            logger.info(f"Saved profile for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user profile: {str(e)}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """
        Retrieve user profile from DynamoDB
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            User profile dictionary or None
        """
        if not self.table:
            return None
        
        try:
            response = self.table.get_item(Key={'user_id': user_id})
            item = response.get('Item')
            
            if item:
                logger.info(f"Retrieved profile for user: {user_id}")
                return dict(item)
            else:
                logger.info(f"No profile found for user: {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving user profile: {str(e)}")
            return None
    
    def update_search_history(self, user_id: str, search_data: Dict) -> bool:
        """
        Add search to user's history
        
        Args:
            user_id: Unique user identifier
            search_data: Search details (query, results, timestamp)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.table:
            return False
        
        try:
            search_entry = {
                'timestamp': datetime.now().isoformat(),
                'query': search_data.get('query', ''),
                'schemes_found': search_data.get('schemes_found', 0),
                'user_profile': search_data.get('user_profile', {})
            }
            
            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='SET search_history = list_append(if_not_exists(search_history, :empty_list), :val), updated_at = :updated',
                ExpressionAttributeValues={
                    ':val': [search_entry],
                    ':empty_list': [],
                    ':updated': datetime.now().isoformat()
                }
            )
            
            logger.info(f"Updated search history for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating search history: {str(e)}")
            return False
    
    def save_scheme(self, user_id: str, scheme: Dict) -> bool:
        """
        Save a scheme to user's saved schemes
        
        Args:
            user_id: Unique user identifier
            scheme: Scheme details
            
        Returns:
            True if successful, False otherwise
        """
        if not self.table:
            return False
        
        try:
            saved_entry = {
                'timestamp': datetime.now().isoformat(),
                'scheme_name': scheme.get('name', ''),
                'scheme_category': scheme.get('category', ''),
                'scheme_data': json.dumps(scheme)
            }
            
            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='SET saved_schemes = list_append(if_not_exists(saved_schemes, :empty_list), :val), updated_at = :updated',
                ExpressionAttributeValues={
                    ':val': [saved_entry],
                    ':empty_list': [],
                    ':updated': datetime.now().isoformat()
                }
            )
            
            logger.info(f"Saved scheme for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving scheme: {str(e)}")
            return False
    
    def get_search_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get user's search history
        
        Args:
            user_id: Unique user identifier
            limit: Maximum number of entries to return
            
        Returns:
            List of search history entries
        """
        profile = self.get_user_profile(user_id)
        if profile and 'search_history' in profile:
            history = profile['search_history']
            return history[-limit:] if len(history) > limit else history
        return []
    
    def get_saved_schemes(self, user_id: str) -> List[Dict]:
        """
        Get user's saved schemes
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            List of saved schemes
        """
        profile = self.get_user_profile(user_id)
        if profile and 'saved_schemes' in profile:
            return profile['saved_schemes']
        return []
    
    def update_user_profile(self, user_id: str, updates: Dict) -> bool:
        """
        Update specific fields in user profile
        
        Args:
            user_id: Unique user identifier
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        if not self.table:
            return False
        
        try:
            # Build update expression
            update_expr = "SET updated_at = :updated"
            expr_values = {':updated': datetime.now().isoformat()}
            
            for key, value in updates.items():
                if key != 'user_id':  # Don't update primary key
                    update_expr += f", {key} = :{key}"
                    expr_values[f":{key}"] = value
            
            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_values
            )
            
            logger.info(f"Updated profile for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return False
    
    def delete_user_profile(self, user_id: str) -> bool:
        """
        Delete user profile (for GDPR compliance)
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            True if successful, False otherwise
        """
        if not self.table:
            return False
        
        try:
            self.table.delete_item(Key={'user_id': user_id})
            logger.info(f"Deleted profile for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user profile: {str(e)}")
            return False
