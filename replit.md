# Overview

CallBunker is a comprehensive communication security platform featuring both backend call screening services and a complete multi-user mobile application. The system protects users from unwanted calls through PIN/verbal authentication while providing cost-effective native mobile calling with caller ID spoofing. It integrates with Twilio for voice services and Google Voice for privacy protection, offering a complete solution for secure business and personal communications. The project now features a production-ready mobile app configured for multi-user operation with automatic signup flow, unique Defense Number assignment per user, and seamless integration with the phone pool system. The mobile app supports both Android APK and iOS builds through Expo Application Services. Multi-user architecture ensures each user gets their own isolated CallBunker experience with unique Twilio number assignment to avoid Google Voice verification conflicts. Complete mobile interface includes protected dialer, call history, trusted contacts management, anonymous messaging, and comprehensive settings with authentication.

# User Preferences

Preferred communication style: Simple, everyday language.

# Recent Changes (August 31, 2025)

## Multi-User Mobile App Integration Complete
- **Updated all mobile API endpoints** from single-user `/api/users/` to multi-user `/multi/` routes
- **Implemented complete signup flow** with SignupScreen.js for new user registration
- **Added authentication state management** with persistent user sessions
- **Integrated phone pool assignment** - each user receives unique Defense Number automatically
- **Updated App.js navigation** to handle authentication flow and user onboarding
- **Completed multi-user APK configuration** - ready for production build and distribution

# System Architecture

## UI/UX Decisions
The system features a Bootstrap-themed responsive interface with a dark mode, maintaining a clean, professional appearance. It uses defense-themed language and branding ("Defense Number," "Trusted Callers," etc.) to enhance the user experience. Key UI elements include prominent "CallBunker Dialer" buttons with authentic DTMF touch tones and clear, mobile-optimized guides with large buttons and improved readability for various screen sizes. Advanced UX patterns include intuitive "Select Multiple" button for batch operations, custom modal confirmations replacing browser prompts, and clean gesture-based interactions optimized for mobile users. The interface prioritizes smooth scrolling and intentional user actions over complex touch gestures. Recent enhancements include seamless blocked call integration into trusted contacts, real-time analytics displaying actual usage data, and enhanced privacy settings focused on unique PIN/voice authentication features.

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
- **Complete Multi-User Mobile Application**: Full-featured React Native app with signup flow, protected dialer, messaging system, call history, trusted contacts management, and native calling integration. Each user gets their own isolated CallBunker experience with unique Defense Number assignment. Includes seamless authentication handling and automatic backend integration with multi-user API endpoints.

## Feature Specifications
- **Multi-tenancy**: Each tenant is identified by a `screening_number` with individual configurations.
- **Admin Interface**: Provides CRUD operations for tenants and whitelists, with real-time monitoring of failures and blocks.
- **Phone Number Normalization**: Ensures consistent handling of phone number formats across the system for accurate whitelisting.

## System Design Choices
The architecture prioritizes clear separation of concerns, robust security measures, and a user-friendly interface. It emphasizes a "business system" focus, removing personal setup sections to streamline the user experience for professional use cases. The system is designed to be highly configurable for each tenant, offering flexibility in authentication and forwarding.

# External Dependencies

## Required Services
- **Twilio**: Essential for voice services and SMS messaging, requiring `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`.
- **A2P 10DLC Registration**: Required for US SMS delivery (Twilio compliance requirement).
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