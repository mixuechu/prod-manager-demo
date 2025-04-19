from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Enum, DateTime, Text
from sqlalchemy.orm import relationship
import enum
from .base import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DIRECTOR = "director"
    PRODUCER = "producer"
    STAFF = "staff"

class ScriptStatus(str, enum.Enum):
    UPLOADING = "uploading"
    PARSING = "parsing"
    PARSED = "parsed"
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"

class User(Base):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole))
    
    projects = relationship("Project", secondary="project_users", back_populates="team_members")
    comments = relationship("Comment", back_populates="author")

class Project(Base):
    __tablename__ = "projects"

    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    scripts = relationship("Script", back_populates="project")
    team_members = relationship("User", secondary="project_users", back_populates="projects")

class ProjectUser(Base):
    __tablename__ = "project_users"

    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(Enum(UserRole))

class Script(Base):
    __tablename__ = "scripts"

    project_id = Column(Integer, ForeignKey("projects.id"))
    filename = Column(String)
    file_path = Column(String)
    status = Column(Enum(ScriptStatus), default=ScriptStatus.UPLOADING)
    metadata = Column(JSON, default={})
    
    project = relationship("Project", back_populates="scripts")
    scenes = relationship("Scene", back_populates="script")
    resources = relationship("Resource", back_populates="script")
    comments = relationship("Comment", back_populates="script")

class Scene(Base):
    __tablename__ = "scenes"

    script_id = Column(Integer, ForeignKey("scripts.id"))
    scene_number = Column(String)
    location = Column(String)
    time_of_day = Column(String)
    summary = Column(Text)
    page_number = Column(String)
    characters = Column(JSON, default=[])
    props = Column(JSON, default=[])
    
    script = relationship("Script", back_populates="scenes")
    resources = relationship("Resource", back_populates="scenes")

class Resource(Base):
    __tablename__ = "resources"

    script_id = Column(Integer, ForeignKey("scripts.id"))
    scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=True)
    type = Column(String)  # costume, prop, location
    name = Column(String)
    description = Column(Text, nullable=True)
    metadata = Column(JSON, default={})
    
    script = relationship("Script", back_populates="resources")
    scenes = relationship("Scene", back_populates="resources")

class Comment(Base):
    __tablename__ = "comments"

    script_id = Column(Integer, ForeignKey("scripts.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    target_element = Column(String)  # scene:S1, resource:R1
    content = Column(Text)
    mentions = Column(JSON, default=[])
    
    script = relationship("Script", back_populates="comments")
    author = relationship("User", back_populates="comments") 