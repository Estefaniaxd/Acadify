from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import enum

# ---------- ENUMS ----------
class DocumentType(enum.Enum):
    TI = "ti"
    CC = "cc"
    CE = "ce"

class UserRole(enum.Enum):
    ADMINISTRATOR = "administrator"
    COORDINATOR = "coordinator"
    TEACHER = "teacher"
    STUDENT = "student"

class AccountStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class InstitutionAffiliationType(enum.Enum):
    PERMANENT = "permanent"
    ADJUNCT = "adjunct"
    OCCASIONAL = "occasional"
    VISITING = "visiting"
    HONORARY = "honorary"

class EducationalStage(enum.Enum):
    STAGE_I = "i"
    STAGE_II = "ii"
    STAGE_III = "iii"
    STAGE_IV = "iv"
    STAGE_V = "v"
    STAGE_VI = "vi"
    STAGE_VII = "vii"
    STAGE_VIII = "viii"
    STAGE_IX = "ix"
    STAGE_X = "x"
    STAGE_XI = "xi"
    STAGE_XII = "xii"

# ---------- MODELOS ----------
class User(BaseModel):
    """Modelo principal de usuario"""
    __tablename__ = "users"

    institutional_email = Column(String(100), nullable=False, unique=True, index=True)
    first_names = Column(String(100), nullable=False)
    last_names = Column(String(100), nullable=False)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    document_number = Column(String(20), nullable=False, unique=True)
    role = Column(SQLEnum(UserRole), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    account_status = Column(SQLEnum(AccountStatus), default=AccountStatus.ACTIVE, nullable=False)
    last_access = Column(DateTime(timezone=True), nullable=True)
    profile_image_url = Column(Text, nullable=True)
    cover_image_url = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True, unique=True)
    biography = Column(Text, nullable=True)

    # Relaciones uno a uno con roles
    system_admin = relationship("SystemAdministrator", back_populates="user", uselist=False)
    teacher = relationship("Teacher", back_populates="user", uselist=False)
    coordinator = relationship("Coordinator", back_populates="user", uselist=False)
    student = relationship("Student", back_populates="user", uselist=False)

    # Relaciones varios a muchos
    user_badges = relationship("UserBadge", back_populates="user")
    user_rewards = relationship("UserReward", back_populates="user")
    user_points = relationship("UserPoints", back_populates="user", uselist=False)
    user_themes = relationship("UserTheme", back_populates="user")

    # Chat y bot
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    bot_messages = relationship("BotMessage", back_populates="user")
    chat_files = relationship("ChatFile", back_populates="user")

# ---------- ROLES ESPECÍFICOS ----------
class SystemAdministrator(BaseModel):
    __tablename__ = "system_administrators"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="system_admin")
    managed_institutions = relationship("Institution", back_populates="administrator")

class Teacher(BaseModel):
    __tablename__ = "teachers"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    knowledge_area = Column(String(50), nullable=False)
    affiliation_date = Column(DateTime(timezone=True), nullable=False)
    affiliation_type = Column(SQLEnum(InstitutionAffiliationType), default=InstitutionAffiliationType.PERMANENT)
    academic_title = Column(String(50), nullable=True)
    weekly_hours = Column(String(10), nullable=True)

    user = relationship("User", back_populates="teacher")
    group_courses = relationship("GroupCourse", back_populates="teacher")
    assignments = relationship("Assignment", back_populates="teacher")
    tutored_groups = relationship("Group", back_populates="tutor_teacher")

class Coordinator(BaseModel):
    __tablename__ = "coordinators"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    office_hours = Column(String(50), nullable=True)
    career_start_date = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="coordinator")
    institution = relationship("Institution", back_populates="coordinators")
    courses = relationship("Course", back_populates="coordinator")

class Student(BaseModel):
    __tablename__ = "students"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id", ondelete="CASCADE"), nullable=False)
    enrollment_date = Column(DateTime(timezone=True), nullable=False)
    approved_credits = Column(String(10), nullable=True)
    educational_stage = Column(SQLEnum(EducationalStage), default=EducationalStage.STAGE_I)
    cumulative_average = Column(String(10), nullable=True)

    user = relationship("User", back_populates="student")
    program = relationship("Program", back_populates="students")
    student_groups = relationship("StudentGroup", back_populates="student")
    assignment_submissions = relationship("AssignmentSubmission", back_populates="student")
    attendances = relationship("Attendance", back_populates="student")
