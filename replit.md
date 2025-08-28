# Overview

CallBunker is a multi-tenant call screening service that acts as a protective layer between callers and final destinations. The system requires callers to authenticate via PIN codes or verbal codes before connecting them to the intended recipient. It integrates with Twilio for voice services and supports multiple tenants (screening numbers) with individual configurations for rate limiting, whitelisting, and forwarding modes.

The application provides both webhook endpoints for Twilio integration and a web-based admin interface for managing tenants, whitelists, and system configuration. It includes features like rate limiting to prevent abuse, blocklisting for repeated failures, and optional email notifications via SendGrid.

# User Preferences

Preferred communication style: Simple, everyday language.

# Recent Changes

## August 28, 2025 - Multi-User Tutorial System & UX Improvements
- **Feature**: Implemented personalized call screening tutorial system focused on multi-user functionality
- **Tutorial Integration**: Added interactive 5-step multi-user tutorial with progress tracking and personalized instructions
- **Seamless Google Voice Integration**: Added direct Google Voice links in signup form and dashboard for immediate configuration
- **Pricing Cleanup**: Removed pricing prompts from user interfaces for cleaner experience (pricing to be added later)
- **UX Enhancements**:
  - "Get Number" button in signup form links directly to voice.google.com
  - "Open Google Voice" button in user dashboard for immediate configuration
  - Detailed tutorial accessible from dashboard with personalized user data
  - Streamlined multi-user signup flow without pricing distractions
- **Navigation Updates**: Removed personal tutorial link from main dashboard, focused on multi-user system
- **Dashboard Polish**: Replaced "Monthly Cost" with "Status: Active" for cleaner account display

## August 27, 2025 - Android Dark Theme Visibility Fix
- **Issue**: Text and content invisible on Android devices due to dark theme compatibility problems
- **Root Cause**: Bootstrap's `bg-light`, `text-muted`, and `text-body` classes rendered invisible in dark mode on mobile browsers
- **Solution**: Replaced with explicit high-contrast color classes (`text-white`, `text-light`, `text-info`) and visible bordered backgrounds
- **Implementation**:
  - Updated both signup and how-it-works pages with reliable dark-theme compatible styling
  - Added colored borders with subtle RGBA backgrounds for better visibility
  - Implemented aggressive cache-busting headers and meta tags for mobile browsers
  - Fixed auto-dismiss JavaScript to preserve benefits messages permanently
- **User Verification**: Confirmed full readability on Android device with all content now clearly visible

## August 28, 2025 - Google Voice Caller ID Dilemma Resolution (Fully Operational)
- **Critical Issue Resolved**: Google Voice caller ID dilemma that prevented caller identification
- **Problem**: With Google Voice caller ID enabled, all calls showed user's own number instead of actual caller
- **Solution**: Modified system to work with Google Voice caller ID DISABLED for better user experience
- **Technical Implementation**:
  - Updated detection logic to identify Google Voice calls via ForwardedFrom field instead of caller ID
  - Fixed verify endpoint to properly handle Google Voice forwarded calls without application errors
  - Implemented proper caller ID forwarding showing original caller's number (eliminates spam warnings)
- **Complete User Experience**: 
  - See actual caller's number before answering (not Google Voice number)
  - CallBunker detects and authenticates Google Voice calls automatically  
  - PIN (8322) or verbal ("Black widow") authentication working perfectly
  - Original caller ID preserved in final call (no spam risk warnings)
  - Auto-whitelist bypasses authentication for verified callers on future calls
- **Cost-Effectiveness Maintained**: Free Google Voice solution eliminates TextNow $6.99/month subscription
- **Status**: Fully tested and operational - caller identification + call screening + cost savings achieved

## August 27, 2025 - Auto-Whitelist Phone Number Normalization Fix
- **Issue**: Auto-whitelist feature not recognizing previously whitelisted numbers due to phone number format inconsistencies
- **Root Cause**: Mixed storage formats in database (+15086388084 vs 15086388084) causing lookup failures
- **Solution**: Updated all whitelist lookup functions to check both legacy (+) and normalized (digits-only) formats
- **Impact**: Existing whitelisted numbers now properly bypass authentication, new entries use consistent normalized format
- **User Verification**: Successfully tested with user's whitelisted number - system correctly identifies and bypasses authentication

## August 27, 2025 - Benefits Section Visibility Improvements
- **Issue**: Benefits sections disappearing from both onboarding page and main dashboard after 3-5 seconds
- **Root Cause**: JavaScript auto-dismiss code in app.js was removing ALL alert elements, including persistent benefits messages
- **Solutions Implemented**:
  - Enhanced onboarding page with sticky benefits reminder that appears when scrolling past main benefits section
  - Made main dashboard benefits message sticky and persistent with manual close option
  - Modified JavaScript auto-dismiss selector to exclude sticky benefits from automatic removal
- **Impact**: Benefits information now stays visible throughout user journey, improving user experience and feature awareness
- **User Verification**: Confirmed benefits messages no longer auto-disappear and remain accessible during navigation

# System Architecture

## Core Framework
- **Flask**: Web framework handling both webhook endpoints and admin interface
- **SQLAlchemy**: ORM for database operations with declarative base model structure
- **Blueprint Architecture**: Modular route organization separating voice webhooks, admin interface, and main routes

## Database Design
- **SQLite**: Default database with configurable DATABASE_URL for production deployments
- **Multi-tenant Architecture**: Each tenant identified by screening_number (Twilio E.164 format)
- **Core Models**:
  - `Tenant`: Main configuration per screening number with authentication settings and rate limiting rules
  - `Whitelist`: Per-tenant approved callers with optional custom PINs and verbal authentication flags
  - `FailLog`: Authentication failure tracking for rate limiting
  - `Blocklist`: Temporary blocks for callers exceeding failure thresholds

## Authentication & Security
- **Dual Authentication**: PIN-based (4-digit codes) and verbal code authentication
- **Session-based Admin Auth**: Web interface protection via session tokens
- **Rate Limiting**: Configurable windows, attempt limits, and block durations per tenant
- **Smart Whitelist System**: Auto-learns trusted callers after successful authentication, enabling bypass for future calls
- **Manual Whitelist**: Manually add approved callers with optional custom PINs for immediate bypass

## Voice Processing Architecture
- **Twilio Integration**: TwiML-based voice response system
- **Multi-step Verification**: Retry logic with configurable attempt limits
- **Forward Modes**: Bridge mode for call connection, voicemail mode for message recording
- **Speech Recognition**: Verbal code matching with normalized speech processing

## Admin Interface
- **Template-based UI**: Bootstrap-themed responsive interface with dark mode
- **Tenant Management**: CRUD operations for screening numbers and configurations
- **Whitelist Management**: Add/remove approved callers with annotation parsing
- **Real-time Monitoring**: View recent failures, active blocks, and system status

## Utility Layer
- **Twilio Helpers**: Centralized TwiML response handling and client configuration
- **Rate Limiting Engine**: Failure tracking and blocking logic with time-based windows
- **Authentication Utils**: Phone number normalization and speech processing
- **Optional Email Notifications**: SendGrid integration for system alerts

# External Dependencies

## Required Services
- **Twilio**: Voice services platform requiring TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
- **Public URL**: Webhook endpoint accessibility via PUBLIC_APP_URL environment variable

## Optional Services
- **SendGrid**: Email notification service with SENDGRID_API_KEY, EMAIL_TO, and EMAIL_FROM configuration
- **PostgreSQL**: Production database option via DATABASE_URL (defaults to SQLite)

## Frontend Dependencies
- **Bootstrap**: CSS framework via CDN for responsive UI components
- **Font Awesome**: Icon library for interface elements
- **Vanilla JavaScript**: Form validation, phone number formatting, and UI enhancements

## Python Libraries
- **Flask ecosystem**: flask-sqlalchemy for ORM integration
- **Twilio SDK**: twilio library for voice response generation and API calls
- **SendGrid SDK**: Optional sendgrid library for email notifications
- **Werkzeug**: ProxyFix middleware for proper header handling in deployed environments

## Environment Configuration
- **Session Security**: SESSION_SECRET for Flask session management
- **Database**: DATABASE_URL with connection pooling and health checks
- **Admin Access**: Optional ADMIN_TOKEN for web interface protection
- **Deployment**: DEBUG flag and host/port configuration for development vs production