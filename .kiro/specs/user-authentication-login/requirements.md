# Requirements Document

## Introduction

This document specifies the requirements for adding user authentication and login capabilities to YojnaMitra-AI, a conversational AI assistant for Indian government schemes. The system currently operates without user authentication, storing data only in session memory. This feature will enable persistent user identification, secure access control, and long-term data storage for user profiles, conversation history, matched schemes, and application tracking.

The authentication system will use phone number-based OTP verification, optimized for Indian mobile users, and will integrate with AWS services (Cognito, SNS, DynamoDB) to provide secure, scalable authentication.

## Glossary

- **Authentication_Service**: The AWS Cognito or custom service responsible for verifying user identity through OTP
- **User_Profile_Store**: The DynamoDB table storing user profile information
- **Conversation_Store**: The DynamoDB table storing user conversation history
- **Scheme_Store**: The DynamoDB table storing matched schemes per user
- **Application_Store**: The DynamoDB table storing scheme application status per user
- **OTP_Service**: The AWS SNS service or custom service that sends one-time passwords via SMS
- **Session_Manager**: The component managing authenticated user sessions in the Streamlit application
- **Phone_Number**: A 10-digit Indian mobile number in the format specified by the Indian numbering plan
- **OTP**: One-Time Password, a 6-digit numeric code valid for a limited time period
- **Authentication_Token**: A secure token issued after successful authentication, used to maintain session state
- **User_Dashboard**: The personalized interface showing user-specific data after authentication

## Requirements

### Requirement 1: Phone Number Registration

**User Story:** As a new user, I want to register with my phone number, so that I can create an account and access personalized features.

#### Acceptance Criteria

1. THE Authentication_Service SHALL accept Phone_Numbers in 10-digit format
2. WHEN a Phone_Number is submitted for registration, THE Authentication_Service SHALL validate the format matches Indian mobile number standards
3. WHEN a valid Phone_Number is submitted for registration, THE Authentication_Service SHALL check if the Phone_Number already exists in the User_Profile_Store
4. IF a Phone_Number already exists in the User_Profile_Store, THEN THE Authentication_Service SHALL return an error indicating the account already exists
5. WHEN a new valid Phone_Number is submitted, THE Authentication_Service SHALL generate a 6-digit OTP
6. WHEN an OTP is generated, THE OTP_Service SHALL send the OTP to the provided Phone_Number within 5 seconds
7. THE Authentication_Service SHALL store the OTP with an expiration time of 10 minutes
8. WHEN an OTP is sent, THE Authentication_Service SHALL return a success response to the user interface

### Requirement 2: OTP Verification for Registration

**User Story:** As a new user, I want to verify my phone number with an OTP, so that I can complete my registration securely.

#### Acceptance Criteria

1. THE Authentication_Service SHALL accept OTP submissions with the associated Phone_Number
2. WHEN an OTP is submitted, THE Authentication_Service SHALL verify the OTP matches the stored value for that Phone_Number
3. WHEN an OTP is submitted, THE Authentication_Service SHALL verify the OTP has not expired
4. IF an incorrect OTP is submitted, THEN THE Authentication_Service SHALL return an error and increment the failed attempt counter
5. IF the failed attempt counter reaches 3 attempts, THEN THE Authentication_Service SHALL invalidate the OTP and require a new OTP request
6. WHEN a valid OTP is verified, THE Authentication_Service SHALL create a new user record in the User_Profile_Store
7. WHEN a new user record is created, THE Authentication_Service SHALL generate an Authentication_Token
8. WHEN an Authentication_Token is generated, THE Session_Manager SHALL establish an authenticated session
9. WHEN registration is complete, THE Authentication_Service SHALL return the Authentication_Token to the user interface

### Requirement 3: User Login

**User Story:** As a registered user, I want to log in with my phone number, so that I can access my saved data and continue using the application.

#### Acceptance Criteria

1. THE Authentication_Service SHALL accept Phone_Numbers for login attempts
2. WHEN a Phone_Number is submitted for login, THE Authentication_Service SHALL verify the Phone_Number exists in the User_Profile_Store
3. IF a Phone_Number does not exist in the User_Profile_Store, THEN THE Authentication_Service SHALL return an error indicating no account found
4. WHEN a registered Phone_Number is submitted for login, THE Authentication_Service SHALL generate a 6-digit OTP
5. WHEN an OTP is generated for login, THE OTP_Service SHALL send the OTP to the Phone_Number within 5 seconds
6. THE Authentication_Service SHALL store the login OTP with an expiration time of 10 minutes
7. WHEN a login OTP is sent, THE Authentication_Service SHALL return a success response to the user interface

### Requirement 4: OTP Verification for Login

**User Story:** As a registered user, I want to verify my identity with an OTP, so that I can securely access my account.

#### Acceptance Criteria

1. THE Authentication_Service SHALL accept OTP submissions for login with the associated Phone_Number
2. WHEN a login OTP is submitted, THE Authentication_Service SHALL verify the OTP matches the stored value
3. WHEN a login OTP is submitted, THE Authentication_Service SHALL verify the OTP has not expired
4. IF an incorrect login OTP is submitted, THEN THE Authentication_Service SHALL return an error and increment the failed attempt counter
5. IF the failed login attempt counter reaches 5 attempts within 15 minutes, THEN THE Authentication_Service SHALL temporarily lock the account for 30 minutes
6. WHEN a valid login OTP is verified, THE Authentication_Service SHALL retrieve the user record from the User_Profile_Store
7. WHEN login is successful, THE Authentication_Service SHALL generate a new Authentication_Token
8. WHEN a login Authentication_Token is generated, THE Session_Manager SHALL establish an authenticated session
9. WHEN login is complete, THE Authentication_Service SHALL return the Authentication_Token and user profile data to the user interface

### Requirement 5: User Profile Persistence

**User Story:** As a registered user, I want my profile information saved, so that I don't have to re-enter my details each time I use the application.

#### Acceptance Criteria

1. WHEN a new user completes registration, THE User_Profile_Store SHALL create a record containing Phone_Number, user_id, creation_timestamp, and last_login_timestamp
2. WHEN a user logs in, THE User_Profile_Store SHALL update the last_login_timestamp
3. THE User_Profile_Store SHALL store optional profile fields including name, age, state, district, and preferred_language
4. WHEN a user updates profile information, THE User_Profile_Store SHALL persist the changes immediately
5. WHEN an authenticated user accesses the application, THE User_Dashboard SHALL retrieve and display the user profile from the User_Profile_Store
6. THE User_Profile_Store SHALL maintain data consistency across all user sessions

### Requirement 6: Conversation History Persistence

**User Story:** As a registered user, I want my conversation history saved, so that I can review previous interactions and continue conversations across sessions.

#### Acceptance Criteria

1. WHEN an authenticated user sends a message, THE Conversation_Store SHALL save the message with user_id, timestamp, message_text, and message_type
2. WHEN the AI assistant responds, THE Conversation_Store SHALL save the response with user_id, timestamp, response_text, and response_type
3. WHEN an authenticated user opens the application, THE User_Dashboard SHALL retrieve and display the conversation history from the Conversation_Store
4. THE Conversation_Store SHALL maintain chronological ordering of conversations by timestamp
5. THE Conversation_Store SHALL support retrieval of conversation history for the past 90 days
6. WHEN conversation history exceeds 90 days, THE Conversation_Store SHALL archive older conversations

### Requirement 7: Matched Schemes Persistence

**User Story:** As a registered user, I want my matched government schemes saved, so that I can review and apply to them later.

#### Acceptance Criteria

1. WHEN the AI assistant identifies a matching scheme for an authenticated user, THE Scheme_Store SHALL save the scheme with user_id, scheme_id, match_timestamp, match_score, and scheme_details
2. WHEN an authenticated user views matched schemes, THE User_Dashboard SHALL retrieve all matched schemes from the Scheme_Store
3. THE Scheme_Store SHALL prevent duplicate scheme entries for the same user_id and scheme_id combination
4. WHEN a scheme match is saved, THE Scheme_Store SHALL include the eligibility criteria that were matched
5. THE User_Dashboard SHALL display matched schemes sorted by match_score in descending order
6. THE Scheme_Store SHALL maintain matched schemes indefinitely until explicitly removed by the user

### Requirement 8: Application Status Tracking

**User Story:** As a registered user, I want to track my scheme application status, so that I can monitor my progress and know what actions to take next.

#### Acceptance Criteria

1. WHEN an authenticated user indicates intent to apply for a scheme, THE Application_Store SHALL create an application record with user_id, scheme_id, status, created_timestamp, and updated_timestamp
2. THE Application_Store SHALL support status values: "interested", "documents_pending", "submitted", "under_review", "approved", "rejected"
3. WHEN application status changes, THE Application_Store SHALL update the status and updated_timestamp
4. WHEN an authenticated user views applications, THE User_Dashboard SHALL retrieve all applications from the Application_Store
5. THE User_Dashboard SHALL display applications grouped by status
6. WHEN an application status is updated, THE User_Dashboard SHALL display a notification to the user
7. THE Application_Store SHALL maintain complete application history including all status transitions

### Requirement 9: Session Management

**User Story:** As a registered user, I want my session to remain active while I use the application, so that I don't have to repeatedly log in.

#### Acceptance Criteria

1. WHEN a user successfully authenticates, THE Session_Manager SHALL create a session with a validity period of 24 hours
2. WHILE a session is active, THE Session_Manager SHALL maintain the Authentication_Token in secure storage
3. WHEN a user performs an action, THE Session_Manager SHALL validate the Authentication_Token
4. IF an Authentication_Token is invalid or expired, THEN THE Session_Manager SHALL redirect the user to the login page
5. WHEN a user closes the browser, THE Session_Manager SHALL persist the session for the remaining validity period
6. WHEN a user reopens the application within the validity period, THE Session_Manager SHALL restore the authenticated session
7. WHEN a session expires, THE Session_Manager SHALL clear all session data and require re-authentication

### Requirement 10: Logout Functionality

**User Story:** As a registered user, I want to log out of my account, so that I can secure my data when using shared devices.

#### Acceptance Criteria

1. THE User_Dashboard SHALL provide a logout button accessible from all authenticated pages
2. WHEN a user clicks the logout button, THE Session_Manager SHALL invalidate the current Authentication_Token
3. WHEN logout is initiated, THE Session_Manager SHALL clear all session data from local storage
4. WHEN logout is complete, THE Session_Manager SHALL redirect the user to the login page
5. WHEN a user logs out, THE Authentication_Service SHALL record the logout timestamp in the User_Profile_Store
6. IF a user attempts to use an invalidated Authentication_Token, THEN THE Session_Manager SHALL reject the request and require re-authentication

### Requirement 11: Security and Data Protection

**User Story:** As a user, I want my authentication data protected, so that my account remains secure from unauthorized access.

#### Acceptance Criteria

1. THE Authentication_Service SHALL transmit all authentication data over HTTPS connections
2. THE User_Profile_Store SHALL store Phone_Numbers in encrypted format
3. THE Authentication_Service SHALL hash all OTP values before storage
4. THE Authentication_Service SHALL generate Authentication_Tokens using cryptographically secure random number generation
5. WHEN an OTP expires, THE Authentication_Service SHALL immediately delete the OTP from storage
6. THE Session_Manager SHALL implement CSRF protection for all authenticated requests
7. THE Authentication_Service SHALL log all authentication attempts including timestamp, Phone_Number, and result
8. IF suspicious activity is detected (multiple failed attempts from different locations), THEN THE Authentication_Service SHALL temporarily suspend the account and notify the user

### Requirement 12: OTP Resend Functionality

**User Story:** As a user, I want to request a new OTP if I don't receive it, so that I can complete authentication without being blocked.

#### Acceptance Criteria

1. THE Authentication_Service SHALL provide an OTP resend function accessible during registration and login
2. WHEN a user requests OTP resend, THE Authentication_Service SHALL invalidate the previous OTP
3. WHEN OTP resend is requested, THE Authentication_Service SHALL enforce a 30-second cooldown period between requests
4. IF a user requests OTP resend before the cooldown period expires, THEN THE Authentication_Service SHALL return an error with the remaining wait time
5. WHEN the cooldown period has elapsed, THE OTP_Service SHALL generate and send a new OTP
6. THE Authentication_Service SHALL limit OTP resend requests to 3 attempts per Phone_Number per hour
7. IF the resend limit is exceeded, THEN THE Authentication_Service SHALL block further OTP requests for 1 hour

### Requirement 13: Error Handling and User Feedback

**User Story:** As a user, I want clear error messages when authentication fails, so that I understand what went wrong and how to fix it.

#### Acceptance Criteria

1. WHEN an authentication error occurs, THE Authentication_Service SHALL return a descriptive error message
2. IF a Phone_Number format is invalid, THEN THE Authentication_Service SHALL return an error message specifying the correct format
3. IF an OTP is incorrect, THEN THE Authentication_Service SHALL return an error message indicating the number of remaining attempts
4. IF an OTP has expired, THEN THE Authentication_Service SHALL return an error message with an option to resend
5. IF an account is temporarily locked, THEN THE Authentication_Service SHALL return an error message with the unlock time
6. WHEN a network error occurs, THE User_Dashboard SHALL display a user-friendly error message and retry option
7. THE Authentication_Service SHALL log all errors with sufficient detail for debugging without exposing sensitive information

### Requirement 14: Integration with Existing Application

**User Story:** As a user, I want authentication to integrate seamlessly with the existing application, so that I can access all features without disruption.

#### Acceptance Criteria

1. WHEN a user is not authenticated, THE User_Dashboard SHALL display only the login and registration interface
2. WHEN a user is authenticated, THE User_Dashboard SHALL display the full conversational AI interface
3. THE Session_Manager SHALL pass the user_id to all backend services for data association
4. WHEN the AI assistant processes a request, THE system SHALL associate all generated data with the authenticated user_id
5. THE User_Dashboard SHALL maintain the existing Streamlit interface design while adding authentication components
6. WHEN a user transitions from unauthenticated to authenticated state, THE User_Dashboard SHALL load user-specific data without page refresh
7. THE Authentication_Service SHALL integrate with the existing AWS Lambda and API Gateway infrastructure

### Requirement 15: OTP Format and Delivery

**User Story:** As a user, I want to receive OTPs in a clear, standard format, so that I can easily read and enter them.

#### Acceptance Criteria

1. THE OTP_Service SHALL generate OTPs as 6-digit numeric codes
2. WHEN an OTP is sent, THE OTP_Service SHALL format the SMS message as: "Your YojnaMitra-AI verification code is: [OTP]. Valid for 10 minutes. Do not share this code."
3. THE OTP_Service SHALL use a registered sender ID recognizable as YojnaMitra-AI
4. WHEN OTP delivery fails, THE OTP_Service SHALL retry up to 2 additional times with 10-second intervals
5. IF all OTP delivery attempts fail, THEN THE Authentication_Service SHALL return an error to the user with an option to retry
6. THE OTP_Service SHALL support delivery to all major Indian mobile network operators
7. THE OTP_Service SHALL log delivery status for monitoring and debugging purposes
