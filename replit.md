# Overview

CallBunker is a comprehensive communication security platform featuring both backend call screening services and a complete mobile application. The system protects users from unwanted calls through PIN/verbal authentication while providing cost-effective native mobile calling with caller ID spoofing. It integrates with Twilio for voice services and Google Voice for privacy protection, offering a complete solution for secure business and personal communications, now including protected texting functionality.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## UI/UX Decisions
The system features a Bootstrap-themed responsive interface with a dark mode, maintaining a clean, professional appearance. It uses defense-themed language and branding ("Defense Number," "Trusted Callers," etc.) to enhance the user experience. Key UI elements include prominent "CallBunker Dialer" buttons and clear, mobile-optimized guides with large buttons and improved readability for various screen sizes.

## Technical Implementations
- **Core Framework**: Flask serves as the web framework for both webhook endpoints and the admin interface.
- **Database**: SQLAlchemy is used for ORM operations, with SQLite as the default and PostgreSQL as an option for production.
- **Modularity**: A Blueprint architecture organizes routes for voice webhooks, admin, and main application logic.
- **Authentication**: Supports dual PIN and verbal code authentication. The admin interface is protected by session tokens.
- **Call Handling**: Utilizes Twilio for voice services, with TwiML-based responses for multi-step verification and configurable retry logic. It supports bridge and voicemail forwarding modes and uses speech recognition for verbal codes.
- **Rate Limiting**: Configurable rate limiting with attempt limits and block durations per tenant to prevent abuse.
- **Smart Whitelist**: Automatically whitelists trusted callers after successful authentication for future bypass. Manual whitelisting with custom PINs is also supported.
- **Outgoing Call Protection**: Integrates with Google Voice to route outgoing calls, ensuring the user's real number remains protected and preventing bypass of CallBunker's system. It identifies Google Voice calls via the `ForwardedFrom` field.
- **Native Mobile Calling**: Implements cost-effective native device calling with caller ID spoofing, eliminating per-minute charges while maintaining Google Voice number protection. Mobile apps use device's built-in calling capabilities with clean API integration.
- **Complete Mobile Application**: Full-featured React Native app with protected dialer, messaging system, call history, trusted contacts management, and native calling integration. Provides intuitive user interface for all CallBunker features including anonymous texting through Google Voice.

## Feature Specifications
- **Multi-tenancy**: Each tenant is identified by a `screening_number` with individual configurations.
- **Admin Interface**: Provides CRUD operations for tenants and whitelists, with real-time monitoring of failures and blocks.
- **Phone Number Normalization**: Ensures consistent handling of phone number formats across the system for accurate whitelisting.

## System Design Choices
The architecture prioritizes clear separation of concerns, robust security measures, and a user-friendly interface. It emphasizes a "business system" focus, removing personal setup sections to streamline the user experience for professional use cases. The system is designed to be highly configurable for each tenant, offering flexibility in authentication and forwarding.

# External Dependencies

## Required Services
- **Twilio**: Essential for all voice services, requiring `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`.
- **Public URL**: Necessary for Twilio to access webhook endpoints, configured via `PUBLIC_APP_URL`.

## Optional Services
- **SendGrid**: Used for email notifications, configured with `SENDGRID_API_KEY`, `EMAIL_TO`, and `EMAIL_FROM`.
- **PostgreSQL**: An optional database for production deployments, specified via `DATABASE_URL`.

## Frontend Dependencies
- **Bootstrap**: CSS framework for responsive web UI.
- **Font Awesome**: Icon library for web interface elements.
- **Vanilla JavaScript**: Used for form validation, phone number formatting, and web UI enhancements.
- **React Native**: Cross-platform mobile framework for iOS and Android applications.
- **React Navigation**: Mobile app navigation and routing system.
- **Native Modules**: iOS CallKit and Android TelecomManager integration for native calling.

## Python Libraries
- **Flask Ecosystem**: Includes `Flask-SQLAlchemy` for ORM.
- **Twilio SDK**: `twilio` library for API interactions and TwiML generation.
- **SendGrid SDK**: `sendgrid` library for optional email functionality.
- **Werkzeug**: `ProxyFix` middleware for proper header handling in deployed environments.