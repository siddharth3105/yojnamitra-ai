# Requirements Document: YojnaMitra AI Assistant

## Introduction

YojnaMitra AI Assistant is an intelligent conversational AI system designed to help Indian citizens discover, understand, and apply for government schemes. The assistant acts as a proactive guide that collects user information through natural conversation, searches for relevant schemes in real-time, matches users with eligible programs, and provides step-by-step application assistance. The system integrates with existing AWS infrastructure (Bedrock, DynamoDB, S3) and operates through a Streamlit-based chat interface supporting 12 Indian languages.

## Glossary

- **YojnaMitra_AI**: The conversational AI assistant powered by AWS Bedrock (Meta Llama 3.1 70B)
- **User_Profile**: Persistent storage of user information including demographics, occupation, income, and documents
- **Scheme**: Indian government welfare program with eligibility criteria, benefits, and application process
- **Scheme_Database**: DynamoDB table storing scheme information including eligibility rules and metadata
- **Eligibility_Score**: Calculated percentage (0-100%) indicating how well a user matches a scheme's criteria
- **Application_Session**: A tracked instance of a user applying for a specific scheme
- **Document_Store**: AWS S3 bucket for secure storage of user-uploaded documents
- **Notification_Service**: AWS SNS-based system for sending alerts via email/SMS
- **Web_Scraper**: Component that searches and extracts scheme information from government websites
- **Conversation_Memory**: Persistent storage of chat history and extracted user information across sessions
- **Auto_Fill_Engine**: Component that automatically populates application forms with user data
- **Deadline_Tracker**: System that monitors scheme deadlines and triggers reminders

## Requirements

### Requirement 1: Conversational Onboarding

**User Story:** As a new user, I want to have a natural conversation with the AI assistant, so that I can provide my information comfortably without filling complex forms.

#### Acceptance Criteria

1. WHEN a user initiates conversation with greetings like "hi", "hello", or "namaste", THEN THE YojnaMitra_AI SHALL respond with a friendly greeting and introduce itself
2. WHEN the user provides information in natural language (e.g., "I'm a 25-year-old farmer from Bihar"), THEN THE YojnaMitra_AI SHALL extract structured data (age=25, occupation=farmer, state=Bihar) from the conversation
3. WHEN the YojnaMitra_AI needs additional information, THEN THE YojnaMitra_AI SHALL ask follow-up questions in a conversational manner
4. WHEN the user provides information across multiple messages, THEN THE YojnaMitra_AI SHALL aggregate all extracted information into the User_Profile
5. WHEN onboarding is complete, THEN THE YojnaMitra_AI SHALL confirm collected information with the user before proceeding
6. THE YojnaMitra_AI SHALL collect at minimum: name, age, gender, state, district, occupation, annual income, and category (General/SC/ST/OBC)
7. WHEN a user returns in a future session, THEN THE YojnaMitra_AI SHALL retrieve their User_Profile from Conversation_Memory and greet them by name

### Requirement 2: Persistent User Memory

**User Story:** As a returning user, I want the AI to remember all my information from previous conversations, so that I don't have to repeat myself.

#### Acceptance Criteria

1. WHEN user information is extracted during conversation, THEN THE YojnaMitra_AI SHALL store it permanently in the User_Profile within DynamoDB
2. WHEN a user starts a new session, THEN THE YojnaMitra_AI SHALL load their complete User_Profile including all previously collected information
3. WHEN a user updates their information (e.g., "I changed my job"), THEN THE YojnaMitra_AI SHALL update the User_Profile with the new information
4. WHEN storing user data, THEN THE YojnaMitra_AI SHALL maintain conversation history for context in future interactions
5. THE User_Profile SHALL persist indefinitely until explicitly deleted by the user
6. WHEN retrieving user data, THEN THE YojnaMitra_AI SHALL use the user's unique identifier (phone number or email) as the primary key

### Requirement 3: Real-time Scheme Discovery

**User Story:** As a system administrator, I want the AI to automatically discover and update government schemes from the internet, so that users always have access to the latest programs.

#### Acceptance Criteria

1. WHEN the Web_Scraper runs, THEN THE Web_Scraper SHALL search official government websites for scheme information
2. WHEN new schemes are discovered, THEN THE Web_Scraper SHALL extract scheme details including name, description, eligibility criteria, benefits, required documents, deadlines, and application URLs
3. WHEN scheme information is extracted, THEN THE Web_Scraper SHALL store it in the Scheme_Database with proper categorization
4. THE Web_Scraper SHALL run on a scheduled basis (daily or weekly) to keep the Scheme_Database current
5. WHEN a scheme's details are updated on government websites, THEN THE Web_Scraper SHALL detect changes and update the Scheme_Database accordingly
6. THE Web_Scraper SHALL prioritize official government domains (.gov.in, .nic.in) for scheme information
7. WHEN scraping fails or encounters errors, THEN THE Web_Scraper SHALL log the error and continue with other sources

### Requirement 4: Intelligent Scheme Matching

**User Story:** As a user, I want the AI to automatically find schemes I'm eligible for, so that I don't miss out on benefits I qualify for.

#### Acceptance Criteria

1. WHEN a User_Profile is complete, THEN THE YojnaMitra_AI SHALL automatically search the Scheme_Database for matching schemes
2. WHEN evaluating eligibility, THEN THE YojnaMitra_AI SHALL calculate an Eligibility_Score for each scheme based on how well the user matches the criteria
3. WHEN presenting schemes to users, THEN THE YojnaMitra_AI SHALL rank them by Eligibility_Score in descending order
4. WHEN a scheme has an Eligibility_Score above 70%, THEN THE YojnaMitra_AI SHALL proactively recommend it to the user
5. WHEN displaying scheme recommendations, THEN THE YojnaMitra_AI SHALL include scheme name, brief description, key benefits, and eligibility percentage
6. THE YojnaMitra_AI SHALL consider multiple criteria including age, income, occupation, state, category, gender, and disability status when calculating Eligibility_Score
7. WHEN a user asks "what schemes am I eligible for?", THEN THE YojnaMitra_AI SHALL provide a prioritized list with explanations

### Requirement 5: Step-by-Step Application Guidance

**User Story:** As a user unfamiliar with government applications, I want the AI to guide me through each step of the application process, so that I can successfully apply without confusion.

#### Acceptance Criteria

1. WHEN a user selects a scheme to apply for, THEN THE YojnaMitra_AI SHALL create an Application_Session and break down the process into numbered steps
2. WHEN presenting application steps, THEN THE YojnaMitra_AI SHALL explain each step in simple language using the user's preferred language
3. WHEN a step requires visiting an external portal, THEN THE YojnaMitra_AI SHALL provide a clickable link and explain what to do on that page
4. WHEN a step involves filling a form field, THEN THE YojnaMitra_AI SHALL explain what information is needed and why
5. WHEN the user completes a step, THEN THE YojnaMitra_AI SHALL acknowledge completion and present the next step
6. THE YojnaMitra_AI SHALL support bilingual explanations (Hindi + English) for all application steps
7. WHEN a user gets stuck or asks for help, THEN THE YojnaMitra_AI SHALL provide additional clarification or alternative approaches

### Requirement 6: Document Collection and Management

**User Story:** As a user, I want to upload my documents once and have the AI use them for multiple applications, so that I don't have to repeatedly provide the same documents.

#### Acceptance Criteria

1. WHEN the YojnaMitra_AI identifies required documents for a scheme, THEN THE YojnaMitra_AI SHALL ask the user to upload missing documents
2. WHEN a user uploads a document, THEN THE YojnaMitra_AI SHALL store it securely in the Document_Store (AWS S3) with encryption
3. WHEN storing documents, THEN THE YojnaMitra_AI SHALL associate them with the User_Profile and tag them by document type (Aadhaar, PAN, income certificate, etc.)
4. WHEN a document is already uploaded, THEN THE YojnaMitra_AI SHALL reuse it for new applications without asking the user again
5. THE YojnaMitra_AI SHALL support common document formats including PDF, JPG, PNG, and JPEG
6. WHEN a document upload fails, THEN THE YojnaMitra_AI SHALL provide a clear error message and allow retry
7. WHEN a user wants to view or delete their documents, THEN THE YojnaMitra_AI SHALL provide options to manage their Document_Store

### Requirement 7: Automatic Form Filling

**User Story:** As a user, I want the AI to automatically fill application forms with my information, so that I can save time and avoid data entry errors.

#### Acceptance Criteria

1. WHEN an application form is identified, THEN THE Auto_Fill_Engine SHALL map User_Profile fields to form fields
2. WHEN generating a pre-filled form, THEN THE Auto_Fill_Engine SHALL populate all matching fields with user data
3. WHEN a form field cannot be auto-filled, THEN THE YojnaMitra_AI SHALL prompt the user for the missing information
4. WHEN generating PDFs for offline applications, THEN THE Auto_Fill_Engine SHALL create downloadable pre-filled PDF forms
5. WHERE online submission is supported, THE Auto_Fill_Engine SHALL submit forms directly to government portals on behalf of the user
6. WHEN auto-filling forms, THEN THE Auto_Fill_Engine SHALL validate data format (e.g., date formats, phone number formats) before submission
7. WHEN submission is complete, THEN THE YojnaMitra_AI SHALL provide confirmation and store the application reference number

### Requirement 8: Application Status Tracking

**User Story:** As a user who has applied for schemes, I want to track the status of my applications, so that I know when action is required from my side.

#### Acceptance Criteria

1. WHEN a user submits an application, THEN THE YojnaMitra_AI SHALL store the Application_Session with submission date and reference number
2. WHEN a user asks about application status, THEN THE YojnaMitra_AI SHALL retrieve and display the current status of all their applications
3. WHERE status tracking APIs are available, THE YojnaMitra_AI SHALL automatically check application status periodically
4. WHEN an application status changes, THEN THE YojnaMitra_AI SHALL notify the user through the Notification_Service
5. WHEN displaying application status, THEN THE YojnaMitra_AI SHALL show scheme name, submission date, current status, and next steps if any
6. THE YojnaMitra_AI SHALL maintain a history of all status changes for each Application_Session
7. WHEN a user needs to take action (e.g., document verification), THEN THE YojnaMitra_AI SHALL provide clear instructions and deadlines

### Requirement 9: Proactive Scheme Notifications

**User Story:** As a user, I want to be notified when new schemes matching my profile are launched, so that I can apply early and not miss opportunities.

#### Acceptance Criteria

1. WHEN a new scheme is added to the Scheme_Database, THEN THE YojnaMitra_AI SHALL evaluate it against all User_Profiles
2. WHEN a new scheme matches a user's profile with Eligibility_Score above 70%, THEN THE Notification_Service SHALL send an alert to the user
3. WHEN an existing scheme's eligibility criteria or benefits are updated, THEN THE YojnaMitra_AI SHALL re-evaluate affected users and notify them
4. THE Notification_Service SHALL support multiple channels including email, SMS, and in-app notifications
5. WHEN sending notifications, THEN THE Notification_Service SHALL include scheme name, brief description, and a link to learn more
6. WHEN a user receives a notification, THEN THE YojnaMitra_AI SHALL allow them to express interest or dismiss the scheme
7. THE YojnaMitra_AI SHALL respect user notification preferences (frequency, channels) stored in the User_Profile

### Requirement 10: Deadline and Reminder System

**User Story:** As a user, I want to receive timely reminders about application deadlines, so that I don't miss important dates.

#### Acceptance Criteria

1. WHEN a scheme has an application deadline, THEN THE Deadline_Tracker SHALL store the deadline date in the Scheme_Database
2. WHEN a user shows interest in a scheme with a deadline, THEN THE Deadline_Tracker SHALL schedule reminders for that user
3. THE Deadline_Tracker SHALL send reminders at 7 days, 3 days, and 1 day before the deadline
4. WHEN a deadline reminder is triggered, THEN THE Notification_Service SHALL send an alert through the user's preferred channels
5. WHEN a user completes an application before the deadline, THEN THE Deadline_Tracker SHALL cancel remaining reminders for that scheme
6. WHEN a scheme deadline is extended, THEN THE Deadline_Tracker SHALL update reminder schedules accordingly
7. WHEN a user has document verification appointments, THEN THE Deadline_Tracker SHALL send reminders 2 days and 1 day before the appointment

### Requirement 11: Multi-language Support

**User Story:** As a user who prefers to communicate in my regional language, I want the AI to understand and respond in my language, so that I can interact comfortably.

#### Acceptance Criteria

1. THE YojnaMitra_AI SHALL support 12 Indian languages: Hindi, English, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, and Assamese
2. WHEN a user starts a conversation, THEN THE YojnaMitra_AI SHALL detect the language from the user's input
3. WHEN responding to users, THEN THE YojnaMitra_AI SHALL use the same language as the user's input
4. WHEN a user switches languages mid-conversation, THEN THE YojnaMitra_AI SHALL adapt and respond in the new language
5. WHEN translating scheme information, THEN THE YojnaMitra_AI SHALL maintain accuracy of eligibility criteria and benefits
6. THE YojnaMitra_AI SHALL store the user's preferred language in the User_Profile for future sessions
7. WHEN language detection fails, THEN THE YojnaMitra_AI SHALL default to English and ask the user to confirm their preferred language

### Requirement 12: Conversational Context Management

**User Story:** As a user having a multi-turn conversation, I want the AI to remember what we discussed earlier in the conversation, so that I don't have to repeat context.

#### Acceptance Criteria

1. WHEN a user sends a message, THEN THE YojnaMitra_AI SHALL maintain the full conversation history in Conversation_Memory
2. WHEN interpreting user input, THEN THE YojnaMitra_AI SHALL consider previous messages for context
3. WHEN a user refers to something mentioned earlier (e.g., "tell me more about that scheme"), THEN THE YojnaMitra_AI SHALL correctly identify the reference
4. WHEN a conversation spans multiple sessions, THEN THE YojnaMitra_AI SHALL load previous conversation history to maintain continuity
5. THE Conversation_Memory SHALL store at minimum the last 50 messages per user
6. WHEN a user starts a completely new topic, THEN THE YojnaMitra_AI SHALL recognize the context shift and adapt accordingly
7. WHEN memory limits are reached, THEN THE YojnaMitra_AI SHALL retain the most recent and most important messages while summarizing older context

### Requirement 13: Proactive Assistance

**User Story:** As a user, I want the AI to anticipate my needs and suggest next steps, so that I don't have to figure out what to do next.

#### Acceptance Criteria

1. WHEN a user completes onboarding, THEN THE YojnaMitra_AI SHALL automatically present top matching schemes without being asked
2. WHEN a user views a scheme, THEN THE YojnaMitra_AI SHALL proactively offer to start the application process
3. WHEN a user is missing documents for a scheme, THEN THE YojnaMitra_AI SHALL proactively ask to collect those documents
4. WHEN an application deadline is approaching, THEN THE YojnaMitra_AI SHALL proactively remind the user and offer to help complete the application
5. WHEN a user hasn't interacted for a while but has pending applications, THEN THE YojnaMitra_AI SHALL send a check-in message
6. WHEN a user successfully applies for a scheme, THEN THE YojnaMitra_AI SHALL suggest other relevant schemes they might be interested in
7. THE YojnaMitra_AI SHALL balance proactivity with user preferences to avoid being intrusive

### Requirement 14: Error Handling and Recovery

**User Story:** As a user, I want the AI to handle errors gracefully and help me recover, so that technical issues don't prevent me from accessing schemes.

#### Acceptance Criteria

1. WHEN an external service (AWS Bedrock, DynamoDB, S3) fails, THEN THE YojnaMitra_AI SHALL display a user-friendly error message
2. WHEN a web scraping operation fails, THEN THE Web_Scraper SHALL log the error and retry with exponential backoff
3. WHEN a document upload fails, THEN THE YojnaMitra_AI SHALL allow the user to retry without losing other progress
4. WHEN form submission fails, THEN THE YojnaMitra_AI SHALL save the user's data and offer to retry
5. WHEN the AI cannot understand user input, THEN THE YojnaMitra_AI SHALL ask clarifying questions rather than giving up
6. WHEN a scheme URL is broken or outdated, THEN THE YojnaMitra_AI SHALL notify administrators and provide alternative information to the user
7. IF an unrecoverable error occurs, THEN THE YojnaMitra_AI SHALL apologize, explain the issue in simple terms, and suggest contacting support

### Requirement 15: Security and Privacy

**User Story:** As a user, I want my personal information and documents to be stored securely, so that my privacy is protected.

#### Acceptance Criteria

1. WHEN storing user data in DynamoDB, THEN THE YojnaMitra_AI SHALL encrypt sensitive fields (Aadhaar, PAN, bank details) at rest
2. WHEN storing documents in S3, THEN THE Document_Store SHALL use server-side encryption (SSE-S3 or SSE-KMS)
3. WHEN transmitting data between components, THEN THE YojnaMitra_AI SHALL use HTTPS/TLS encryption
4. THE YojnaMitra_AI SHALL implement access controls ensuring users can only access their own data
5. WHEN a user requests data deletion, THEN THE YojnaMitra_AI SHALL remove all their data from DynamoDB, S3, and Conversation_Memory within 30 days
6. THE YojnaMitra_AI SHALL not log or store sensitive information (passwords, full Aadhaar numbers) in plain text
7. WHEN accessing AWS services, THEN THE YojnaMitra_AI SHALL use IAM roles with least-privilege permissions

### Requirement 16: Integration with Existing System

**User Story:** As a system administrator, I want the AI assistant to integrate seamlessly with the existing YojnaMitra app, so that we can enhance functionality without disrupting current users.

#### Acceptance Criteria

1. THE YojnaMitra_AI SHALL integrate with the existing app_premium.py Streamlit application
2. WHEN integrating, THEN THE YojnaMitra_AI SHALL reuse existing AWS Bedrock configuration and credentials
3. WHEN integrating, THEN THE YojnaMitra_AI SHALL use the existing DynamoDB tables or create new tables with compatible schemas
4. WHEN integrating, THEN THE YojnaMitra_AI SHALL use the existing S3 bucket or create a new bucket with proper permissions
5. THE YojnaMitra_AI SHALL maintain backward compatibility with existing user data and workflows
6. WHEN deployed, THEN THE YojnaMitra_AI SHALL be accessible through the existing Streamlit chat interface
7. THE YojnaMitra_AI SHALL follow the existing code structure and naming conventions in app_premium.py

### Requirement 17: Performance and Scalability

**User Story:** As a system administrator, I want the AI assistant to handle multiple concurrent users efficiently, so that the system remains responsive under load.

#### Acceptance Criteria

1. WHEN processing user messages, THEN THE YojnaMitra_AI SHALL respond within 3 seconds for 95% of requests
2. WHEN multiple users interact simultaneously, THEN THE YojnaMitra_AI SHALL maintain separate conversation contexts without interference
3. THE Scheme_Database SHALL support at least 10,000 schemes without performance degradation
4. THE Document_Store SHALL support at least 100,000 documents with efficient retrieval
5. WHEN the Web_Scraper runs, THEN THE Web_Scraper SHALL process at least 100 government websites within 24 hours
6. THE YojnaMitra_AI SHALL handle at least 1,000 concurrent users without service degradation
7. WHEN database queries are slow, THEN THE YojnaMitra_AI SHALL use caching to improve response times
