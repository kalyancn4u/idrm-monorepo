"""
dbmodels/enums.py — the canonical enumerations, copied EXACTLY from the database
CHECK constraints in database/init/02-schema.sql (and FS §3.3).

These are plain `str` enums so a value like UserRole.CITIZEN behaves as the
string "CITIZEN" everywhere (JSON, SQL, comparisons). Pydantic schemas use them
for validation; the database enforces the same values via CHECK constraints.

⚠️ If you change a value here, change it in 02-schema.sql too — they must match.
"""
from enum import Enum


class UserRole(str, Enum):
    """The 10 account roles (FS §3.3). At signup a user may only pick one of the
    SELF_REGISTRABLE_ROLES below; all elevated roles are granted by an ADMIN."""

    CITIZEN = "CITIZEN"
    VOLUNTEER = "VOLUNTEER"
    ORGANIZER = "ORGANIZER"
    PROVIDER = "PROVIDER"
    MANAGER = "MANAGER"
    EVENT_MANAGER = "EVENT_MANAGER"
    EXECUTIVE = "EXECUTIVE"          # 🔒 Post-MVP
    DM_AUTHORITY = "DM_AUTHORITY"    # "Event Admin" — may be a GO or NGO
    AUDITOR = "AUDITOR"
    ADMIN = "ADMIN"


# Roles a user may pick at registration. Everything else is granted by an ADMIN.
SELF_REGISTRABLE_ROLES: set[UserRole] = {UserRole.CITIZEN, UserRole.PROVIDER, UserRole.VOLUNTEER}


class ServiceType(str, Enum):
    """The 6 kinds of help a request can ask for. Anything else → OTHER + a description."""

    RESCUE = "RESCUE"
    MEDICAL = "MEDICAL"
    FOOD = "FOOD"
    SHELTER = "SHELTER"
    WATER = "WATER"
    OTHER = "OTHER"


class Priority(str, Enum):
    """How urgent a request is. CRITICAL/HIGH (see EMERGENCY_PRIORITIES) are auto-approved."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# Emergencies are auto-approved by the system (SUBMITTED → APPROVED).
EMERGENCY_PRIORITIES: set[Priority] = {Priority.CRITICAL, Priority.HIGH}


class ServiceStatus(str, Enum):
    """The request lifecycle. Happy path:
    SUBMITTED → APPROVED → ACCEPTED → IN_PROGRESS → COMPLETED → VERIFIED.
    Terminal: REJECTED, CANCELLED, EXPIRED. DISPUTED is raised from IN_PROGRESS or
    COMPLETED and resolves back to IN_PROGRESS or REJECTED."""

    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    DISPUTED = "DISPUTED"


class PrivacyLevel(str, Enum):
    """Who may see the requestor's identity on a request. Default PROTECTED; raise-only."""

    PUBLIC = "PUBLIC"
    PROTECTED = "PROTECTED"     # default — public sees a redacted request
    PRIVATE = "PRIVATE"


class OrgType(str, Enum):
    """The kind of provider organization that can fulfil requests."""

    NGO = "NGO"
    HOSPITAL = "HOSPITAL"
    GOVT_AGENCY = "GOVT_AGENCY"
    VOLUNTEER_GROUP = "VOLUNTEER_GROUP"


class NotificationType(str, Enum):
    """What a notification is about (selects its title/body template)."""

    SERVICE_CREATED = "SERVICE_CREATED"
    SERVICE_ACCEPTED = "SERVICE_ACCEPTED"
    SERVICE_COMPLETED = "SERVICE_COMPLETED"
    VERIFICATION_REQUEST = "VERIFICATION_REQUEST"
    GENERAL = "GENERAL"
    SYSTEM = "SYSTEM"


class NotificationChannel(str, Enum):
    """How a notification is delivered to the user."""

    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
    IN_APP = "IN_APP"


class NotificationStatus(str, Enum):
    """Delivery state of a single notification."""

    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    READ = "READ"


class AuditResourceType(str, Enum):
    """Which kind of entity an audit-log row refers to. Note these are CamelCase
    (they mirror the ORM model names), unlike the UPPERCASE enums above."""

    USER = "User"
    SERVICE_REQUEST = "ServiceRequest"
    ORGANIZATION = "Organization"
    NOTIFICATION = "Notification"
    SYSTEM = "System"


class Language(str, Enum):
    """Supported UI / notification languages (the pilot region is Telugu-speaking)."""

    EN = "en"   # English
    HI = "hi"   # Hindi
    TE = "te"   # Telugu (pilot region)
