# Implementation Plan: User Authentication and Login System

## Overview

This implementation plan breaks down the user authentication and login system into four phases: Infrastructure Setup, Backend Implementation, Frontend Integration, and Testing & Deployment. The system will add phone number-based OTP authentication to YojnaMitra-AI using AWS Cognito, SNS, Lambda, DynamoDB, and Streamlit.

The implementation follows a bottom-up approach: infrastructure first, then backend services, frontend integration, and finally comprehensive testing with property-based tests for all 56 correctness properties.

## Tasks

- [ ] 1. Phase 1: Infrastructure Setup
  - [ ] 1.1 Create DynamoDB tables for authentication
    - Update cloudformation_template.yaml to add 6 DynamoDB tables: Users-Auth, OTP-Store, Conversations, Matched-Schemes, Applications-Auth, Auth-Tokens
    - Configure table schemas with partition keys, sort keys, and GSIs as specified in design
    - Enable encryption with KMS, TTL for OTP and token tables, point-in-time recovery
    - _Requirements: 5.1, 6.1, 7.1, 8.1, 9.2_
  
  - [ ]* 1.2 Write property tests for DynamoDB table schemas
    - **Property 12: User Record Creation with Required Fields**
    - **Property 18: Conversation Message Persistence**
    - **Property 22: Matched Scheme Persistence**
    - **Property 26: Application Record Creation**
    - **Validates: Requirements 5.1, 6.1, 6.2, 7.1, 8.1**
  
  - [ ] 1.3 Create AWS KMS encryption key and alias
    - Add KMS key resource to CloudFormation template
    - Configure key policy for Lambda access
    - Create key alias for easy reference
    - _Requirements: 11.2_

  - [ ] 1.4 Create SNS topic for OTP delivery
    - Add SNS topic resource to CloudFormation template
    - Configure SMS attributes (transactional type, sender ID)
    - Set up IAM permissions for Lambda to publish messages
    - _Requirements: 1.6, 3.5, 15.1_
  
  - [ ] 1.5 Create Lambda function resources in CloudFormation
    - Add AuthenticationFunction resource with API Gateway events
    - Configure environment variables for table names, KMS key, SNS topic
    - Set up IAM policies for DynamoDB, SNS, and KMS access
    - Configure timeout (30s) and memory settings
    - _Requirements: 1.1, 2.1, 3.1, 4.1_
  
  - [ ] 1.6 Create API Gateway endpoints
    - Define 7 API endpoints: /auth/register, /auth/verify-otp, /auth/login, /auth/verify-login, /auth/resend-otp, /auth/logout, /auth/refresh
    - Configure CORS settings for Streamlit frontend
    - Enable API Gateway logging and throttling
    - _Requirements: 1.8, 2.9, 3.7, 4.9_

- [ ] 2. Checkpoint - Infrastructure validation
  - Deploy CloudFormation stack to dev environment, verify all resources created successfully, ensure all tests pass, ask the user if questions arise.

- [ ] 3. Phase 2: Backend Implementation - Core Authentication
  - [ ] 3.1 Implement phone validation and hashing utilities
    - Create auth_handler.py with validate_phone_format() function
    - Implement hash_phone() using SHA-256 for lookups
    - Add input sanitization and format checking
    - _Requirements: 1.1, 1.2, 3.1_
  
  - [ ]* 3.2 Write property tests for phone validation
    - **Property 1: Phone Number Validation**
    - **Validates: Requirements 1.1, 1.2, 3.1**
  
  - [ ] 3.3 Implement OTP generation and storage
    - Create generate_otp() function using secrets.randbelow()
    - Implement store_otp() with bcrypt hashing (cost factor 12)
    - Add OTP expiration logic (10 minutes) with DynamoDB TTL
    - Track attempts, resend count, and invalidation status
    - _Requirements: 1.5, 1.7, 2.3, 3.4, 3.6_
  
  - [ ]* 3.4 Write property tests for OTP generation and storage
    - **Property 3: OTP Format Consistency**
    - **Property 7: OTP Storage with Expiration**
    - **Property 40: OTP Hashing**
    - **Validates: Requirements 1.5, 1.7, 3.4, 11.3**

  - [ ] 3.5 Implement OTP verification logic
    - Create verify_otp() function with bcrypt comparison
    - Implement failed attempt tracking and max attempts enforcement
    - Add OTP expiration checking
    - Handle OTP invalidation after max attempts
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 4.2, 4.3, 4.4_
  
  - [ ]* 3.6 Write property tests for OTP verification
    - **Property 4: OTP Verification Correctness**
    - **Property 5: OTP Expiration Enforcement**
    - **Property 6: Failed Attempt Tracking**
    - **Validates: Requirements 2.2, 2.3, 2.4, 4.2, 4.3, 4.4**
  
  - [ ] 3.7 Implement SNS OTP delivery with retry logic
    - Create send_otp_sms() function with AWS SNS client
    - Format SMS message with OTP and expiration time
    - Implement retry logic (3 attempts with 10-second intervals)
    - Add delivery status logging
    - _Requirements: 1.6, 3.5, 15.2, 15.4, 15.5, 15.7_
  
  - [ ]* 3.8 Write property tests for OTP delivery
    - **Property 50: SMS Message Format**
    - **Property 51: OTP Delivery Retry Logic**
    - **Property 52: Complete Delivery Failure Handling**
    - **Property 53: Delivery Status Logging**
    - **Validates: Requirements 15.2, 15.4, 15.5, 15.7**
  
  - [ ] 3.9 Implement user existence checking
    - Create user_exists() function querying Users table by phone_hash GSI
    - Handle DynamoDB query errors gracefully
    - _Requirements: 1.3, 1.4, 3.2, 3.3_
  
  - [ ]* 3.10 Write property tests for user existence checking
    - **Property 2: Duplicate Registration Prevention**
    - **Property 10: User Existence Validation for Login**
    - **Validates: Requirements 1.3, 1.4, 3.2, 3.3**

- [ ] 4. Phase 2: Backend Implementation - Registration Flow
  - [ ] 4.1 Implement registration request handler
    - Create handle_register() function in auth_handler.py
    - Validate phone format and check for existing user
    - Generate and store OTP, send via SNS
    - Return success response with expiration time
    - Add comprehensive error handling
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8_
  
  - [ ]* 4.2 Write unit tests for registration edge cases
    - Test invalid phone formats (9 digits, 11 digits, non-numeric, starting with 0-5)
    - Test duplicate registration attempts
    - Test OTP generation failures
    - Test SNS delivery failures
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [ ] 4.3 Implement authentication token generation
    - Create generate_auth_token() using secrets.token_urlsafe()
    - Store token in Auth-Tokens table with 24-hour TTL
    - Include user_id, creation time, expiration time, device info
    - _Requirements: 2.7, 4.7, 9.1, 11.4_
  
  - [ ]* 4.4 Write property tests for token generation
    - **Property 8: Token Generation on Success**
    - **Property 56: Session Token Storage**
    - **Validates: Requirements 2.7, 4.7, 9.2, 11.4**
  
  - [ ] 4.5 Implement user record creation
    - Create create_user() function to insert into Users table
    - Generate unique user_id using UUID
    - Encrypt phone number with KMS before storage
    - Store phone_hash for lookups, set timestamps
    - Initialize profile with default values
    - _Requirements: 2.6, 5.1, 11.2_
  
  - [ ]* 4.6 Write property tests for user creation
    - **Property 12: User Record Creation with Required Fields**
    - **Property 39: Phone Number Encryption**
    - **Validates: Requirements 2.6, 5.1, 11.2**
  
  - [ ] 4.7 Implement registration OTP verification handler
    - Create handle_verify_registration() function
    - Verify OTP with attempt tracking
    - Create user record on successful verification
    - Generate authentication token and clear OTP
    - Return token, user_id, and expiration
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9_
  
  - [ ]* 4.8 Write integration tests for complete registration flow
    - Test end-to-end registration: phone submission → OTP generation → OTP verification → user creation → token generation
    - Test registration with invalid OTP (3 failed attempts)
    - Test registration with expired OTP
    - _Requirements: 1.*, 2.*_

- [ ] 5. Phase 2: Backend Implementation - Login Flow
  - [ ] 5.1 Implement login request handler
    - Create handle_login() function
    - Validate phone format and verify user exists
    - Generate and store login OTP
    - Send OTP via SNS
    - Return success response
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  
  - [ ]* 5.2 Write unit tests for login edge cases
    - Test login with non-existent phone number
    - Test login with invalid phone format
    - Test OTP generation for existing user
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ] 5.3 Implement account lockout mechanism
    - Add failed_login_attempts tracking in Users table
    - Implement 5 failed attempts within 15 minutes threshold
    - Lock account for 30 minutes on threshold breach
    - Store lock_until timestamp in user record
    - _Requirements: 4.5_
  
  - [ ]* 5.4 Write unit tests for account lockout
    - Test account locks after 5 failed login attempts
    - Test unlock after 30 minutes
    - Test successful login resets failed attempt counter
    - _Requirements: 4.5_
  
  - [ ] 5.5 Implement login OTP verification handler
    - Create handle_verify_login() function
    - Verify OTP with attempt tracking and account lockout check
    - Retrieve user profile from Users table
    - Update last_login timestamp and login_count
    - Generate new authentication token
    - Return token, user_id, and user profile
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_
  
  - [ ]* 5.6 Write property tests for login flow
    - **Property 10: User Existence Validation for Login**
    - **Property 11: User Profile Retrieval on Login**
    - **Property 13: Last Login Timestamp Update**
    - **Validates: Requirements 3.2, 3.3, 4.6, 4.9, 5.2**
  
  - [ ]* 5.7 Write integration tests for complete login flow
    - Test end-to-end login: phone submission → OTP generation → OTP verification → profile retrieval → token generation
    - Test login with account lockout scenario
    - Test login with expired OTP
    - _Requirements: 3.*, 4.*_

- [ ] 6. Phase 2: Backend Implementation - Session & OTP Management
  - [ ] 6.1 Implement OTP resend handler
    - Create handle_resend_otp() function
    - Enforce 30-second cooldown between requests
    - Track resend count and enforce 3 per hour limit
    - Invalidate previous OTP before generating new one
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_
  
  - [ ]* 6.2 Write property tests for OTP resend
    - **Property 29: OTP Resend Cooldown Enforcement**
    - **Property 30: OTP Resend Hourly Rate Limit**
    - **Property 31: Previous OTP Invalidation on Resend**
    - **Validates: Requirements 12.2, 12.3, 12.4, 12.6, 12.7**
  
  - [ ] 6.3 Implement logout handler
    - Create handle_logout() function
    - Invalidate authentication token in Auth-Tokens table
    - Record logout timestamp in user profile
    - Return success response
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ]* 6.4 Write property tests for logout
    - **Property 36: Token Invalidation on Logout**
    - **Property 37: Logout Timestamp Recording**
    - **Property 38: Invalidated Token Rejection**
    - **Validates: Requirements 10.2, 10.3, 10.5, 10.6**
  
  - [ ] 6.5 Implement token refresh handler
    - Create handle_refresh_token() function
    - Validate existing token and check expiration
    - Generate new token with extended expiration
    - Invalidate old token
    - _Requirements: 9.1, 9.6_
  
  - [ ] 6.6 Implement token validation utility
    - Create validate_token() function
    - Check token exists in Auth-Tokens table
    - Verify token not expired and not invalidated
    - Return user_id if valid
    - _Requirements: 9.3, 9.4_
  
  - [ ]* 6.7 Write property tests for session management
    - **Property 32: Session Token Validation**
    - **Property 33: Invalid Token Handling**
    - **Property 34: Session Restoration**
    - **Property 35: Session Cleanup on Expiration**
    - **Validates: Requirements 9.3, 9.4, 9.6, 9.7**

- [ ] 7. Phase 2: Backend Implementation - Error Handling
  - [ ] 7.1 Implement error response formatting
    - Create error_response() function with status code, error code, message
    - Define error classes: ValidationError, UnauthorizedError, NotFoundError, ConflictError, RateLimitError, ServerError
    - Implement error_handler decorator for Lambda functions
    - _Requirements: 13.1, 13.7_
  
  - [ ]* 7.2 Write property tests for error handling
    - **Property 42: Error Message Descriptiveness**
    - **Property 43: Phone Validation Error Message**
    - **Property 44: OTP Error with Remaining Attempts**
    - **Property 45: Expired OTP Error with Resend Option**
    - **Property 46: Account Lock Error with Unlock Time**
    - **Property 47: Error Logging Without PII**
    - **Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5, 13.7**
  
  - [ ] 7.3 Implement audit logging
    - Create log_auth_attempt() function
    - Log all authentication events with timestamp, phone_hash (not plaintext), action, result
    - Configure CloudWatch log groups and retention
    - _Requirements: 11.7_
  
  - [ ]* 7.4 Write property tests for audit logging
    - **Property 41: Authentication Audit Logging**
    - **Validates: Requirements 11.7**

  - [ ] 7.5 Implement main Lambda handler routing
    - Create lambda_handler() function with route mapping
    - Parse event path and HTTP method
    - Route to appropriate handler function
    - Wrap all handlers with error_handler decorator
    - Add request/response logging
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 10.1, 12.1_

- [ ] 8. Checkpoint - Backend validation
  - Deploy Lambda function to dev environment, test all API endpoints with Postman/curl, verify DynamoDB data persistence, ensure all tests pass, ask the user if questions arise.

- [-] 9. Phase 3: Frontend Integration - Authentication UI
  - [x] 9.1 Create Streamlit authentication components file
    - Create auth_components.py with imports (streamlit, requests, datetime)
    - Define API_BASE_URL configuration
    - Set up error handling utilities
    - _Requirements: 1.1, 3.1_
  
  - [x] 9.2 Implement LoginPage component
    - Create LoginPage class with render() method
    - Add phone number input field (10 digits, validation)
    - Add OTP input field (6 digits, shown after phone submission)
    - Add "Send OTP" and "Verify OTP" buttons
    - Add "Resend OTP" button with cooldown display
    - Add link to registration page
    - _Requirements: 3.1, 4.1, 12.1_
  
  - [x] 9.3 Implement login API calls in LoginPage
    - Create request_login_otp() method calling POST /auth/login
    - Create verify_login_otp() method calling POST /auth/verify-login
    - Create resend_otp() method calling POST /auth/resend-otp
    - Handle API responses and errors
    - _Requirements: 3.7, 4.9, 12.1_
  
  - [-] 9.4 Implement RegistrationPage component
    - Create RegistrationPage class with render() method
    - Add phone number input with validation
    - Add OTP verification flow
    - Add terms acceptance checkbox
    - Add registration completion flow
    - _Requirements: 1.1, 2.1_
  
  - [x] 9.5 Implement registration API calls in RegistrationPage
    - Create register_user() method calling POST /auth/register
    - Create verify_registration_otp() method calling POST /auth/verify-otp
    - Handle successful registration and session creation
    - _Requirements: 1.8, 2.9_

- [-] 10. Phase 3: Frontend Integration - Session Management
  - [-] 10.1 Implement SessionManager component
    - Create SessionManager class with session state management
    - Implement create_session() to store token, user_id, profile, expiration
    - Implement is_authenticated() to check session validity
    - Implement get_user_id() to retrieve current user
    - Implement clear_session() to remove all session data
    - _Requirements: 2.8, 4.8, 9.1, 9.2, 9.7_

  - [ ]* 10.2 Write property tests for session management
    - **Property 9: Session Creation on Authentication**
    - **Property 32: Session Token Validation**
    - **Property 34: Session Restoration**
    - **Property 35: Session Cleanup on Expiration**
    - **Validates: Requirements 2.8, 4.8, 9.1, 9.3, 9.6, 9.7**
  
  - [x] 10.3 Implement logout functionality in SessionManager
    - Create logout() method calling POST /auth/logout
    - Clear all session state
    - Redirect to login page
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [ ] 10.4 Implement session validation middleware
    - Create validate_session() to check token on every page load
    - Handle expired sessions with automatic redirect
    - Implement token refresh for near-expiry sessions
    - _Requirements: 9.3, 9.4, 9.6_
  
  - [ ]* 10.5 Write property tests for session validation
    - **Property 33: Invalid Token Handling**
    - **Property 38: Invalidated Token Rejection**
    - **Validates: Requirements 9.4, 10.6**

- [ ] 11. Phase 3: Frontend Integration - Error Handling UI
  - [ ] 11.1 Implement ErrorHandler component
    - Create ErrorHandler class with handle_api_error() method
    - Map error codes to user-friendly messages
    - Display appropriate Streamlit error/warning/info messages
    - Add retry buttons for recoverable errors
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6_
  
  - [ ] 11.2 Implement network error handling
    - Create handle_network_error() for connection failures
    - Create handle_timeout_error() for request timeouts
    - Add retry mechanisms with exponential backoff
    - _Requirements: 13.6_
  
  - [ ] 11.3 Add error display for all authentication flows
    - Integrate ErrorHandler into LoginPage
    - Integrate ErrorHandler into RegistrationPage
    - Display validation errors inline with form fields
    - Show countdown timers for cooldowns and lockouts
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [ ] 12. Phase 3: Frontend Integration - Main Application
  - [x] 12.1 Integrate authentication into yojnamitra_ai.py
    - Import AuthenticationUI and SessionManager
    - Add authentication check at application entry point
    - Redirect unauthenticated users to login page
    - Show authenticated dashboard for logged-in users
    - _Requirements: 9.1, 9.3, 9.4_
  
  - [x] 12.2 Add user profile display in sidebar
    - Show user name and phone in sidebar
    - Add logout button in sidebar
    - Display session expiration time
    - _Requirements: 5.5, 10.1_

  - [ ] 12.3 Implement user profile persistence in conversations
    - Modify conversation saving to include user_id
    - Update save_conversation_message() to use Conversations table
    - Retrieve conversation history on app load for authenticated user
    - Display conversation history in chronological order
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [ ]* 12.4 Write property tests for conversation persistence
    - **Property 18: Conversation Message Persistence**
    - **Property 19: Conversation History Retrieval**
    - **Property 20: Conversation Chronological Ordering**
    - **Property 21: Conversation History Time Window**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**
  
  - [ ] 12.5 Implement matched schemes persistence
    - Create save_matched_scheme() function using Matched-Schemes table
    - Include user_id, scheme_id, match_score, scheme_details, eligibility_matched
    - Prevent duplicate scheme saves
    - Retrieve and display matched schemes sorted by match_score
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ]* 12.6 Write property tests for matched schemes
    - **Property 22: Matched Scheme Persistence**
    - **Property 23: Matched Scheme Retrieval**
    - **Property 24: Duplicate Scheme Prevention**
    - **Property 25: Matched Scheme Sorting**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**
  
  - [ ] 12.7 Implement application status tracking
    - Create save_application() function using Applications table
    - Track status transitions: interested → documents_pending → submitted → under_review → approved/rejected
    - Update application status with timestamp and history
    - Display applications grouped by status
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.7_
  
  - [ ]* 12.8 Write property tests for application tracking
    - **Property 26: Application Record Creation**
    - **Property 27: Application Status Validation**
    - **Property 28: Application Status Update**
    - **Property 54: Application Retrieval by User**
    - **Property 55: Application Grouping by Status**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.7**
  
  - [ ] 12.9 Implement user profile updates
    - Create update_user_profile() function
    - Allow users to update name, age, state, district, occupation, income, category, gender, preferred_language
    - Persist updates to Users table immediately
    - Verify round-trip persistence (update → retrieve → verify)
    - _Requirements: 5.3, 5.4_
  
  - [ ]* 12.10 Write property tests for profile updates
    - **Property 14: Profile Update Persistence**
    - **Property 15: Profile Retrieval on Dashboard Access**
    - **Validates: Requirements 5.3, 5.4, 5.5**

  - [ ] 12.11 Add user_id propagation to all backend calls
    - Update all API calls to include user_id in request context
    - Ensure AI assistant responses are associated with correct user
    - Validate user_id on backend for all authenticated operations
    - _Requirements: 14.3, 14.4_
  
  - [ ]* 12.12 Write property tests for user ID propagation
    - **Property 48: User ID Propagation**
    - **Property 49: Data Association with User ID**
    - **Validates: Requirements 14.3, 14.4**

- [ ] 13. Checkpoint - Frontend integration validation
  - Test complete user flows in Streamlit app, verify session persistence across page reloads, test error handling with various scenarios, ensure all tests pass, ask the user if questions arise.

- [ ] 14. Phase 4: Testing & Deployment - Property-Based Tests
  - [ ] 14.1 Set up property-based testing framework
    - Install hypothesis library
    - Create tests/property/ directory structure
    - Configure hypothesis settings (100 iterations minimum)
    - Set up test fixtures for DynamoDB mocking
    - _Requirements: All_
  
  - [ ] 14.2 Implement phone validation property tests
    - Create test_phone_validation_properties.py
    - Implement Property 1: Phone Number Validation
    - Implement Property 43: Phone Validation Error Message
    - Tag tests with feature and property references
    - _Requirements: 1.1, 1.2, 3.1, 13.2_
  
  - [ ] 14.3 Implement OTP property tests
    - Create test_otp_properties.py
    - Implement Property 3: OTP Format Consistency
    - Implement Property 4: OTP Verification Correctness
    - Implement Property 5: OTP Expiration Enforcement
    - Implement Property 6: Failed Attempt Tracking
    - Implement Property 7: OTP Storage with Expiration
    - Implement Property 29: OTP Resend Cooldown Enforcement
    - Implement Property 30: OTP Resend Hourly Rate Limit
    - Implement Property 31: Previous OTP Invalidation on Resend
    - Implement Property 40: OTP Hashing
    - _Requirements: 1.5, 1.7, 2.2, 2.3, 2.4, 3.4, 3.6, 4.2, 4.3, 4.4, 11.3, 12.2, 12.3, 12.4, 12.6, 12.7_
  
  - [ ] 14.4 Implement session property tests
    - Create test_session_properties.py
    - Implement Property 8: Token Generation on Success
    - Implement Property 9: Session Creation on Authentication
    - Implement Property 32: Session Token Validation
    - Implement Property 33: Invalid Token Handling
    - Implement Property 34: Session Restoration
    - Implement Property 35: Session Cleanup on Expiration
    - Implement Property 36: Token Invalidation on Logout
    - Implement Property 37: Logout Timestamp Recording
    - Implement Property 38: Invalidated Token Rejection
    - Implement Property 56: Session Token Storage
    - _Requirements: 2.7, 2.8, 4.7, 4.8, 9.1, 9.2, 9.3, 9.4, 9.6, 9.7, 10.2, 10.3, 10.5, 10.6, 11.4_

  - [ ] 14.5 Implement data persistence property tests
    - Create test_data_persistence_properties.py
    - Implement Property 2: Duplicate Registration Prevention
    - Implement Property 10: User Existence Validation for Login
    - Implement Property 11: User Profile Retrieval on Login
    - Implement Property 12: User Record Creation with Required Fields
    - Implement Property 13: Last Login Timestamp Update
    - Implement Property 14: Profile Update Persistence (Round Trip)
    - Implement Property 15: Profile Retrieval on Dashboard Access
    - Implement Property 18: Conversation Message Persistence
    - Implement Property 19: Conversation History Retrieval
    - Implement Property 20: Conversation Chronological Ordering
    - Implement Property 21: Conversation History Time Window
    - Implement Property 22: Matched Scheme Persistence
    - Implement Property 23: Matched Scheme Retrieval
    - Implement Property 24: Duplicate Scheme Prevention
    - Implement Property 25: Matched Scheme Sorting
    - Implement Property 26: Application Record Creation
    - Implement Property 27: Application Status Validation
    - Implement Property 28: Application Status Update
    - Implement Property 54: Application Retrieval by User
    - Implement Property 55: Application Grouping by Status
    - _Requirements: 1.3, 1.4, 2.6, 3.2, 3.3, 4.6, 4.9, 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5, 8.7_
  
  - [ ] 14.6 Implement security property tests
    - Create test_security_properties.py
    - Implement Property 39: Phone Number Encryption
    - Implement Property 40: OTP Hashing (if not in OTP tests)
    - Implement Property 41: Authentication Audit Logging
    - Implement Property 47: Error Logging Without PII
    - _Requirements: 11.2, 11.3, 11.7, 13.7_
  
  - [ ] 14.7 Implement API response property tests
    - Create test_api_response_properties.py
    - Implement Property 16: API Response Format Consistency
    - Implement Property 17: Registration Response Completeness
    - Implement Property 42: Error Message Descriptiveness
    - Implement Property 44: OTP Error with Remaining Attempts
    - Implement Property 45: Expired OTP Error with Resend Option
    - Implement Property 46: Account Lock Error with Unlock Time
    - _Requirements: 1.8, 2.9, 3.7, 13.1, 13.3, 13.4, 13.5_
  
  - [ ] 14.8 Implement SMS delivery property tests
    - Create test_sms_delivery_properties.py
    - Implement Property 50: SMS Message Format
    - Implement Property 51: OTP Delivery Retry Logic
    - Implement Property 52: Complete Delivery Failure Handling
    - Implement Property 53: Delivery Status Logging
    - _Requirements: 15.2, 15.4, 15.5, 15.7_
  
  - [ ] 14.9 Implement user ID propagation property tests
    - Create test_user_context_properties.py
    - Implement Property 48: User ID Propagation
    - Implement Property 49: Data Association with User ID
    - _Requirements: 14.3, 14.4_

  - [ ] 14.10 Run all property tests with 100 iterations
    - Execute all property test suites
    - Verify all 56 properties pass
    - Document any failures with counterexamples
    - Fix identified issues and re-run tests
    - _Requirements: All_

- [ ] 15. Phase 4: Testing & Deployment - Integration Tests
  - [ ] 15.1 Implement registration flow integration test
    - Create test_registration_flow.py
    - Test complete flow: phone submission → OTP generation → OTP verification → user creation → token generation → session creation
    - Test with valid inputs and verify database state
    - _Requirements: 1.*, 2.*_
  
  - [ ] 15.2 Implement login flow integration test
    - Create test_login_flow.py
    - Test complete flow: phone submission → user existence check → OTP generation → OTP verification → profile retrieval → token generation → session restoration
    - Test with existing user and verify session state
    - _Requirements: 3.*, 4.*_
  
  - [ ] 15.3 Implement logout flow integration test
    - Create test_logout_flow.py
    - Test complete flow: authenticated session → logout request → token invalidation → session cleanup → redirect to login
    - Verify token cannot be reused after logout
    - _Requirements: 10.*_
  
  - [ ] 15.4 Implement conversation persistence integration test
    - Create test_conversation_persistence.py
    - Test saving multiple messages with user_id
    - Test retrieving conversation history in chronological order
    - Test 90-day retention window
    - _Requirements: 6.*_
  
  - [ ] 15.5 Implement scheme matching integration test
    - Create test_scheme_matching.py
    - Test saving matched schemes with user_id
    - Test duplicate prevention
    - Test retrieval sorted by match_score
    - _Requirements: 7.*_
  
  - [ ] 15.6 Implement application tracking integration test
    - Create test_application_tracking.py
    - Test creating application records
    - Test status transitions with history
    - Test retrieval grouped by status
    - _Requirements: 8.*_
  
  - [ ] 15.7 Implement error handling integration test
    - Create test_error_handling.py
    - Test all error scenarios: invalid phone, expired OTP, account lockout, rate limiting
    - Verify error responses match specifications
    - Test error logging without PII
    - _Requirements: 13.*_

- [ ] 16. Phase 4: Testing & Deployment - Deployment
  - [ ] 16.1 Create Lambda deployment package
    - Install all dependencies in lambda_functions/ directory
    - Create requirements.txt with boto3, bcrypt, PyJWT
    - Package Lambda code into ZIP file
    - _Requirements: All backend_
  
  - [ ] 16.2 Deploy CloudFormation stack to production
    - Review CloudFormation template for production settings
    - Deploy stack with Environment=prod parameter
    - Verify all resources created successfully
    - Note API Gateway endpoint URL
    - _Requirements: All infrastructure_
  
  - [ ] 16.3 Deploy Lambda function code
    - Upload Lambda deployment package
    - Update function code for AuthenticationFunction
    - Verify environment variables configured correctly
    - Test Lambda function with sample events
    - _Requirements: All backend_
  
  - [ ] 16.4 Configure SNS for production
    - Request SMS spending limit increase from AWS
    - Set default SMS type to Transactional
    - Configure sender ID (if available in region)
    - Test OTP delivery to real phone numbers
    - _Requirements: 1.6, 3.5, 15.*_
  
  - [ ] 16.5 Update Streamlit app configuration
    - Set API_BASE_URL to production API Gateway endpoint
    - Configure environment variables in .env file
    - Test authentication flows in Streamlit app
    - _Requirements: All frontend_
  
  - [ ] 16.6 Deploy Streamlit app to production
    - Deploy to Streamlit Cloud or EC2 instance
    - Configure HTTPS with SSL certificate
    - Set up custom domain (if applicable)
    - Verify app accessible and functional
    - _Requirements: All frontend_
  
  - [ ] 16.7 Configure monitoring and alerting
    - Set up CloudWatch dashboards for Lambda metrics
    - Create alarms for error rates, latency, throttling
    - Configure SNS topic for alert notifications
    - Set up log retention policies
    - _Requirements: 11.7, 15.7_
  
  - [ ] 16.8 Perform post-deployment verification
    - Test complete registration flow end-to-end
    - Test complete login flow end-to-end
    - Test OTP resend with cooldown
    - Test session persistence across browser sessions
    - Test logout functionality
    - Test conversation persistence
    - Test matched schemes persistence
    - Test application tracking
    - Verify all error scenarios handled correctly
    - Check CloudWatch logs for errors
    - Monitor API Gateway metrics
    - _Requirements: All_

- [ ] 17. Phase 4: Testing & Deployment - Security Validation
  - [ ] 17.1 Verify encryption at rest
    - Confirm all DynamoDB tables use KMS encryption
    - Verify phone numbers stored encrypted in Users table
    - Verify OTPs stored hashed (not plaintext) in OTP-Store table
    - Check KMS key rotation enabled
    - _Requirements: 11.2, 11.3_
  
  - [ ] 17.2 Verify encryption in transit
    - Confirm all API endpoints use HTTPS/TLS
    - Test that HTTP requests redirect to HTTPS
    - Verify TLS version 1.2 or higher
    - _Requirements: 11.1_
  
  - [ ] 17.3 Verify IAM permissions follow least privilege
    - Review Lambda execution role permissions
    - Ensure Lambda can only access required DynamoDB tables
    - Verify KMS key policy restricts access appropriately
    - Check SNS publish permissions scoped correctly
    - _Requirements: 11.2_
  
  - [ ] 17.4 Verify rate limiting and throttling
    - Test API Gateway throttling limits
    - Verify OTP resend cooldown enforcement (30 seconds)
    - Verify hourly OTP resend limit (3 per hour)
    - Test account lockout after 5 failed login attempts
    - _Requirements: 4.5, 12.3, 12.4, 12.6, 12.7_
  
  - [ ] 17.5 Verify audit logging
    - Check all authentication attempts logged to CloudWatch
    - Verify logs contain timestamp, phone_hash (not plaintext), action, result
    - Confirm no PII (phone numbers, OTPs) in logs
    - Test log retention policy configured
    - _Requirements: 11.7, 13.7_
  
  - [ ] 17.6 Verify DynamoDB backup and recovery
    - Confirm point-in-time recovery enabled on all tables
    - Test backup restoration process
    - Verify TTL configured for OTP-Store and Auth-Tokens tables
    - _Requirements: 5.6, 6.6_
  
  - [ ] 17.7 Perform security penetration testing
    - Test SQL injection attempts (should not apply to DynamoDB)
    - Test XSS attempts in Streamlit UI
    - Test CSRF protection in API calls
    - Test brute force OTP guessing (should be blocked by rate limiting)
    - Test session hijacking attempts
    - _Requirements: 11.1, 11.6, 11.8_

- [ ] 18. Final checkpoint - Production readiness
  - Verify all tests pass (unit, property, integration), confirm all security measures in place, validate monitoring and alerting configured, perform load testing with expected user volume, ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at phase boundaries
- Property tests validate universal correctness properties (56 total)
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end user flows
- All code examples use Python as specified in the design document
- AWS region: ap-south-1 (Mumbai) for optimal latency for Indian users
- OTP expiration: 10 minutes
- Session expiration: 24 hours
- Account lockout: 30 minutes after 5 failed login attempts
- OTP resend cooldown: 30 seconds
- OTP resend limit: 3 per hour

## Implementation Strategy

This plan follows a 4-phase approach:

1. **Phase 1: Infrastructure Setup** - Create all AWS resources (DynamoDB, Lambda, API Gateway, SNS, KMS)
2. **Phase 2: Backend Implementation** - Implement Lambda handlers for all authentication flows
3. **Phase 3: Frontend Integration** - Create Streamlit UI components and integrate with existing app
4. **Phase 4: Testing & Deployment** - Comprehensive testing and production deployment

Each phase includes a checkpoint to validate progress before moving to the next phase. Property-based tests are included as optional sub-tasks throughout to enable early bug detection, but can be deferred to Phase 4 for faster initial implementation.

The implementation is designed to be incremental, with each task building on previous work. No code is left orphaned - all components are integrated into the main application by the end of Phase 3.
