"""
Amazon S3 Integration for YojnaMitra
Handles PDF report storage and retrieval
"""

import os
import boto3
from datetime import datetime
from typing import Optional
import logging
import io

logger = logging.getLogger(__name__)

class S3Storage:
    """S3 storage interface for YojnaMitra"""
    
    def __init__(self):
        """Initialize S3 client"""
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=os.getenv("BEDROCK_REGION", "ap-south-1"),
                aws_access_key_id=os.getenv("BEDROCK_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("BEDROCK_SECRET_ACCESS_KEY")
            )
            self.bucket_name = os.getenv("S3_BUCKET_NAME", "yojnamitra-reports")
            logger.info(f"Connected to S3 bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Error connecting to S3: {str(e)}")
            self.s3_client = None
    
    def upload_pdf(self, pdf_buffer: io.BytesIO, user_id: str, filename: Optional[str] = None) -> Optional[str]:
        """
        Upload PDF report to S3
        
        Args:
            pdf_buffer: PDF file buffer
            user_id: User identifier
            filename: Optional custom filename
            
        Returns:
            Presigned URL for download or None if failed
        """
        if not self.s3_client:
            logger.warning("S3 client not available")
            return None
        
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_recommendations.pdf"
            
            # S3 key (path)
            key = f"reports/{user_id}/{filename}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=pdf_buffer.getvalue(),
                ContentType='application/pdf',
                Metadata={
                    'user_id': user_id,
                    'upload_time': datetime.now().isoformat()
                }
            )
            
            logger.info(f"Uploaded PDF to S3: {key}")
            
            # Generate presigned URL (valid for 1 hour)
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=3600  # 1 hour
            )
            
            return url
            
        except Exception as e:
            logger.error(f"Error uploading PDF to S3: {str(e)}")
            return None
    
    def list_user_reports(self, user_id: str) -> list:
        """
        List all reports for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of report metadata
        """
        if not self.s3_client:
            return []
        
        try:
            prefix = f"reports/{user_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            reports = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    reports.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'filename': obj['Key'].split('/')[-1]
                    })
            
            logger.info(f"Found {len(reports)} reports for user: {user_id}")
            return reports
            
        except Exception as e:
            logger.error(f"Error listing user reports: {str(e)}")
            return []
    
    def get_download_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for downloading a file
        
        Args:
            key: S3 object key
            expires_in: URL expiration time in seconds
            
        Returns:
            Presigned URL or None
        """
        if not self.s3_client:
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expires_in
            )
            
            logger.info(f"Generated download URL for: {key}")
            return url
            
        except Exception as e:
            logger.error(f"Error generating download URL: {str(e)}")
            return None
    
    def delete_report(self, key: str) -> bool:
        """
        Delete a report from S3
        
        Args:
            key: S3 object key
            
        Returns:
            True if successful, False otherwise
        """
        if not self.s3_client:
            return False
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            logger.info(f"Deleted report: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting report: {str(e)}")
            return False
    
    def upload_static_asset(self, file_buffer: io.BytesIO, filename: str, content_type: str) -> Optional[str]:
        """
        Upload static asset (images, etc.) to S3
        
        Args:
            file_buffer: File buffer
            filename: Filename
            content_type: MIME type
            
        Returns:
            Public URL or None
        """
        if not self.s3_client:
            return None
        
        try:
            key = f"assets/{filename}"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_buffer.getvalue(),
                ContentType=content_type,
                ACL='public-read'  # Make assets public
            )
            
            # Generate public URL
            url = f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION', 'ap-south-1')}.amazonaws.com/{key}"
            
            logger.info(f"Uploaded static asset: {key}")
            return url
            
        except Exception as e:
            logger.error(f"Error uploading static asset: {str(e)}")
            return None
