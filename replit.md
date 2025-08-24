# Overview

CallShield AI is a multi-tenant call screening service that acts as a protective layer between callers and final destinations. The system requires callers to authenticate via PIN codes or verbal codes before connecting them to the intended recipient. It integrates with Twilio for voice services and supports multiple tenants (screening numbers) with individual configurations for rate limiting, whitelisting, and forwarding modes.

The application provides both webhook endpoints for Twilio integration and a web-based admin interface for managing tenants, whitelists, and system configuration. It includes features like rate limiting to prevent abuse, blocklisting for repeated failures, and optional email notifications via SendGrid.

# User Preferences

Preferred communication style: Simple, everyday language.

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
- **Whitelist System**: Bypass authentication for approved callers with optional custom PINs

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