# Requirements Document

## Introduction

This document specifies requirements for completing the AWS Hackathon submission for YojnaMitra-AI, an intelligent government scheme assistant. The feature integrates the existing RAG engine into the main application, deploys AWS infrastructure, and creates documentation evidence to achieve 100% hackathon compliance (50/50 points) before the March 8, 2026 deadline.

## Glossary

- **RAG_Engine**: The retrieval-augmented generation system implemented in `rag_engine.py` that uses Titan Embeddings for semantic search and Claude Sonnet 4.6 for response generation
- **Main_Application**: The Streamlit application in `yojnamitra_ai.py` that provides the user interface
- **Titan_Embeddings**: AWS Bedrock embedding model (amazon.titan-embed-text-v1) that converts text into vector representations
- **Claude_Sonnet**: AWS Bedrock foundation model (anthropic.claude-sonnet-4-20250514) that generates natural language responses
- **Semantic_Search**: Vector similarity search that finds relevant schemes based on embedding distance
- **DynamoDB_Table**: AWS NoSQL database table storing user profiles and conversation history
- **S3_Bucket**: AWS object storage bucket for documents, schemes, and reports
- **CloudWatch**: AWS monitoring service for application logs and metrics
- **Hackathon_Submission**: The complete submission package including code, documentation, screenshots, and demo video
- **ap-south-1**: AWS Mumbai region where all infrastructure must be deployed

## Requirements

### Requirement 1: RAG Engine Integration

**User Story:** As a developer, I want to integrate the RAG engine into the main application, so that users receive semantically relevant scheme recommendations powered by AWS Bedrock.

#### Acceptance Criteria

1. THE Main_Application SHALL import RAGEngine class from `rag_engine.py`
2. WHEN the Main_Application initializes, THE Main_Application SHALL create a RAG_Engine instance with AWS credentials from environment variables
3. WHEN a user provides their profile information, THE RAG_Engine SHALL generate embeddings using Titan_Embeddings within 2 seconds
4. WHEN embeddings are generated, THE RAG_Engine SHALL perform Semantic_Search to retrieve the top 5 relevant schemes
5. WHEN relevant schemes are retrieved, THE RAG_Engine SHALL use Claude_Sonnet to generate personalized recommendations with scheme context
6. IF RAG_Engine initialization fails, THEN THE Main_Application SHALL fall back to the existing scheme matching logic and log the error
7. IF any RAG operation fails during runtime, THEN THE Main_Application SHALL fall back to existing logic and continue operation
8. THE Main_Application SHALL log all RAG operations including embedding generation time, search results count, and recommendation generation time

### Requirement 2: AWS DynamoDB Deployment

**User Story:** As a system administrator, I want to deploy a DynamoDB table, so that user profiles and conversation history are persisted in AWS infrastructure.

#### Acceptance Criteria

1. THE DynamoDB_Table SHALL be named `YojnaMitra-Users-Demo`
2. THE DynamoDB_Table SHALL have partition key `user_id` of type String
3. THE DynamoDB_Table SHALL have attributes: name (String), age (Number), state (String), income (Number), occupation (String), matched_schemes (List), conversation_history (List), last_updated (String)
4. THE DynamoDB_Table SHALL be deployed in ap-south-1 region
5. THE DynamoDB_Table SHALL use on-demand billing mode for cost optimization
6. WHEN the DynamoDB_Table is created, THE Main_Application SHALL successfully write a test user record
7. WHEN a test record exists, THE Main_Application SHALL successfully read the record by user_id
8. THE DynamoDB_Table SHALL have read and write capacity sufficient for 100 concurrent users

### Requirement 3: AWS S3 Bucket Deployment

**User Story:** As a system administrator, I want to deploy an S3 bucket with organized folder structure, so that documents, schemes, and reports are stored in AWS object storage.

#### Acceptance Criteria

1. THE S3_Bucket SHALL be named with pattern `yojnamitra-hackathon-[name]-2026` where [name] is a unique identifier
2. THE S3_Bucket SHALL be deployed in ap-south-1 region
3. THE S3_Bucket SHALL contain three folders: `documents/`, `schemes/`, and `reports/`
4. THE S3_Bucket SHALL have versioning enabled for data protection
5. THE S3_Bucket SHALL have server-side encryption enabled using AES-256
6. WHEN the S3_Bucket is created, THE Main_Application SHALL successfully upload a test file to the `documents/` folder
7. WHEN a test file exists, THE Main_Application SHALL successfully download the file from S3
8. THE S3_Bucket SHALL have appropriate IAM policies allowing read and write access from the application

### Requirement 4: AWS Bedrock Model Enablement

**User Story:** As a developer, I want to enable required Bedrock models in AWS Console, so that the RAG engine can access Titan Embeddings and Claude Sonnet 4.6.

#### Acceptance Criteria

1. THE Claude_Sonnet model (anthropic.claude-sonnet-4-20250514) SHALL be enabled in AWS Bedrock console for ap-south-1 region
2. THE Titan_Embeddings model (amazon.titan-embed-text-v1) SHALL be enabled in AWS Bedrock console for ap-south-1 region
3. WHEN models are enabled, THE RAG_Engine SHALL successfully invoke Titan_Embeddings API with sample text
4. WHEN models are enabled, THE RAG_Engine SHALL successfully invoke Claude_Sonnet API with sample prompt
5. THE Bedrock model access SHALL be verified through AWS Console before application deployment
6. IF model invocation fails, THEN THE RAG_Engine SHALL return a descriptive error message indicating which model failed

### Requirement 5: CloudWatch Logging Configuration

**User Story:** As a system administrator, I want to configure CloudWatch logging, so that application operations and errors are monitored in AWS infrastructure.

#### Acceptance Criteria

1. THE Main_Application SHALL create a CloudWatch log group named `/aws/yojnamitra/application`
2. THE Main_Application SHALL create log streams with timestamp-based naming pattern
3. WHEN any RAG operation executes, THE Main_Application SHALL write log entries to CloudWatch including operation type, duration, and status
4. WHEN any AWS service call fails, THE Main_Application SHALL write error logs to CloudWatch with error details and stack trace
5. THE CloudWatch log group SHALL retain logs for 7 days minimum
6. THE CloudWatch logs SHALL be accessible through AWS Console for monitoring and debugging
7. THE Main_Application SHALL log performance metrics including API latency, embedding generation time, and search duration

### Requirement 6: Screenshot Documentation

**User Story:** As a hackathon participant, I want to capture AWS infrastructure screenshots, so that the submission demonstrates actual AWS deployment.

#### Acceptance Criteria

1. THE Hackathon_Submission SHALL include a screenshot showing AWS Bedrock console with Claude_Sonnet and Titan_Embeddings models enabled
2. THE Hackathon_Submission SHALL include a screenshot showing DynamoDB console with `YojnaMitra-Users-Demo` table and its schema attributes
3. THE Hackathon_Submission SHALL include a screenshot showing S3 console with the created bucket and folder structure (documents/, schemes/, reports/)
4. THE Hackathon_Submission SHALL include a screenshot showing CloudWatch console with application log entries
5. THE screenshots SHALL clearly display the ap-south-1 region indicator
6. THE screenshots SHALL be saved in PNG or JPEG format with minimum resolution of 1280x720 pixels
7. THE screenshots SHALL be referenced in `HACKATHON_SUBMISSION.md` with descriptive captions

### Requirement 7: Demo Video Recording

**User Story:** As a hackathon participant, I want to record a demo video, so that judges can see the RAG workflow and AWS infrastructure in action.

#### Acceptance Criteria

1. THE demo video SHALL have duration between 2 minutes 30 seconds and 3 minutes 30 seconds
2. THE demo video SHALL show AWS Bedrock console with enabled models in the first 30 seconds
3. THE demo video SHALL show DynamoDB table with sample user data in the next 30 seconds
4. THE demo video SHALL show S3 bucket with uploaded files in the next 30 seconds
5. THE demo video SHALL demonstrate the complete RAG workflow: user query → Titan_Embeddings → Semantic_Search → Claude_Sonnet generation in the next 60 seconds
6. THE demo video SHALL show the Main_Application user interface with authentication, conversation, and scheme recommendations in the final 30 seconds
7. THE demo video SHALL include narration or text overlays explaining each component
8. THE demo video SHALL be uploaded to a publicly accessible platform (YouTube, Vimeo, or AWS S3 with public URL)
9. THE demo video link SHALL be included in `HACKATHON_SUBMISSION.md`

### Requirement 8: Submission Document Updates

**User Story:** As a hackathon participant, I want to update the submission document with deployment evidence, so that judges can verify AWS infrastructure and RAG implementation.

#### Acceptance Criteria

1. THE `HACKATHON_SUBMISSION.md` SHALL include a section titled "AWS Infrastructure Deployment" with DynamoDB_Table name, S3_Bucket name, and region
2. THE `HACKATHON_SUBMISSION.md` SHALL include embedded or linked screenshots for all four required screenshots
3. THE `HACKATHON_SUBMISSION.md` SHALL include the demo video link with viewing instructions
4. THE `HACKATHON_SUBMISSION.md` SHALL include performance metrics: average embedding generation time, average search time, average recommendation generation time
5. THE `HACKATHON_SUBMISSION.md` SHALL include a RAG workflow diagram showing data flow from user input through Titan_Embeddings, Semantic_Search, and Claude_Sonnet
6. THE `HACKATHON_SUBMISSION.md` SHALL document the complete tech stack with specific AWS service names and model versions
7. THE `HACKATHON_SUBMISSION.md` SHALL explain why AI is required, how AWS is used, and what value AI adds to the solution

### Requirement 9: End-to-End RAG Testing

**User Story:** As a developer, I want to test the complete RAG workflow, so that I can verify all components work correctly before submission.

#### Acceptance Criteria

1. WHEN a test user profile is provided, THE RAG_Engine SHALL generate embeddings using Titan_Embeddings and return a 1536-dimension vector
2. WHEN embeddings are generated, THE Semantic_Search SHALL return exactly 5 relevant schemes ranked by similarity score
3. WHEN relevant schemes are retrieved, THE Claude_Sonnet SHALL generate personalized recommendations that reference at least 3 of the retrieved schemes
4. THE end-to-end RAG workflow SHALL complete within 5 seconds for a single user query
5. WHEN 10 consecutive user queries are processed, THE RAG_Engine SHALL maintain average latency below 5 seconds per query
6. WHEN invalid input is provided, THE RAG_Engine SHALL return descriptive error messages without crashing
7. THE RAG_Engine SHALL successfully process queries in both English and Hindi languages

### Requirement 10: AWS Service Integration Testing

**User Story:** As a developer, I want to test all AWS service integrations, so that I can verify the application works with deployed infrastructure.

#### Acceptance Criteria

1. WHEN the Main_Application starts, THE Main_Application SHALL successfully connect to DynamoDB_Table in ap-south-1 region
2. WHEN the Main_Application starts, THE Main_Application SHALL successfully connect to S3_Bucket in ap-south-1 region
3. WHEN the Main_Application starts, THE Main_Application SHALL successfully connect to CloudWatch in ap-south-1 region
4. WHEN a user registers, THE Main_Application SHALL write the user profile to DynamoDB_Table and verify the write succeeded
5. WHEN a user uploads a document, THE Main_Application SHALL upload the file to S3_Bucket and return a valid S3 URL
6. WHEN any operation executes, THE Main_Application SHALL write logs to CloudWatch and verify logs are visible in AWS Console
7. IF any AWS service is unavailable, THEN THE Main_Application SHALL display a user-friendly error message and continue operating with degraded functionality

### Requirement 11: Hackathon Compliance Verification

**User Story:** As a hackathon participant, I want to verify compliance with all mandatory requirements, so that the submission achieves maximum points (50/50).

#### Acceptance Criteria

1. THE Hackathon_Submission SHALL use AWS Bedrock with Claude_Sonnet and Titan_Embeddings models
2. THE Hackathon_Submission SHALL use DynamoDB for data persistence
3. THE Hackathon_Submission SHALL use S3 for object storage
4. THE Hackathon_Submission SHALL use CloudWatch for monitoring and logging
5. THE Hackathon_Submission SHALL demonstrate a complete RAG workflow with Retrieval, Augmentation, and Generation phases clearly identified
6. THE Hackathon_Submission SHALL include documentation explaining why AI is required for the problem domain
7. THE Hackathon_Submission SHALL include documentation explaining how AWS services are used and integrated
8. THE Hackathon_Submission SHALL include documentation explaining what value AI adds compared to traditional approaches
9. THE Hackathon_Submission SHALL follow AWS-native patterns using serverless and managed services
10. THE Hackathon_Submission SHALL include evidence of Kiro spec-driven development methodology

### Requirement 12: Backward Compatibility and Error Handling

**User Story:** As a developer, I want to maintain existing functionality with graceful degradation, so that the application continues working even if RAG or AWS services fail.

#### Acceptance Criteria

1. WHEN RAG_Engine initialization fails, THEN THE Main_Application SHALL use the existing rule-based scheme matching logic
2. WHEN DynamoDB_Table is unavailable, THEN THE Main_Application SHALL use in-memory session state for user data
3. WHEN S3_Bucket is unavailable, THEN THE Main_Application SHALL disable document upload features and display a notification
4. WHEN CloudWatch is unavailable, THEN THE Main_Application SHALL write logs to local files
5. WHEN Bedrock API calls fail, THEN THE RAG_Engine SHALL retry up to 3 times with exponential backoff before falling back
6. THE Main_Application SHALL display user-friendly error messages that do not expose AWS credentials or internal implementation details
7. WHEN any fallback mechanism activates, THE Main_Application SHALL log the fallback event with reason and timestamp
8. THE existing authentication system SHALL continue working without modification
9. THE existing conversation interface SHALL continue working without modification
10. THE existing scheme matching logic SHALL remain available as a fallback option

