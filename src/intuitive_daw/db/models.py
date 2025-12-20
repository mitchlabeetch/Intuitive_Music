"""Database models for the DAW"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class ProjectModel(Base):
    """Database model for projects"""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    path = Column(String(512), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    author = Column(String(255))
    description = Column(Text)
    tempo = Column(Float, default=120.0)
    time_signature_num = Column(Integer, default=4)
    time_signature_den = Column(Integer, default=4)
    key = Column(String(10), default='C')
    
    tracks = relationship('TrackModel', back_populates='project', cascade='all, delete-orphan')
    sessions = relationship('SessionModel', back_populates='project', cascade='all, delete-orphan')


class TrackModel(Base):
    """Database model for tracks"""
    __tablename__ = 'tracks'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    name = Column(String(255), nullable=False)
    track_type = Column(String(50), nullable=False)
    index = Column(Integer, default=0)
    volume = Column(Float, default=0.0)
    pan = Column(Float, default=0.0)
    mute = Column(Boolean, default=False)
    solo = Column(Boolean, default=False)
    color = Column(String(7), default='#3498db')
    
    project = relationship('ProjectModel', back_populates='tracks')


class SessionModel(Base):
    """Database model for work sessions"""
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    started_at = Column(DateTime, default=datetime.now)
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer)
    notes = Column(Text)
    
    project = relationship('ProjectModel', back_populates='sessions')


class PresetModel(Base):
    """Database model for effect/instrument presets"""
    __tablename__ = 'presets'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    plugin_type = Column(String(100))
    parameters = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.now)
    tags = Column(Text)  # Comma-separated tags


class DatabaseManager:
    """Manage database connections and operations"""
    
    def __init__(self, database_url: str = 'sqlite:///intuitive_music.db'):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def init_db(self):
        """Initialize database tables"""
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """Get a database session"""
        return self.Session()
    
    def save_project(self, project) -> bool:
        """Save project to database"""
        session = self.get_session()
        try:
            # Check if project exists
            existing = session.query(ProjectModel).filter_by(
                path=project.path
            ).first()
            
            if existing:
                # Update existing
                existing.name = project.metadata.name
                existing.modified_at = datetime.now()
                existing.tempo = project.metadata.tempo
                existing.time_signature_num = project.metadata.time_signature[0]
                existing.time_signature_den = project.metadata.time_signature[1]
            else:
                # Create new
                db_project = ProjectModel(
                    name=project.metadata.name,
                    path=project.path,
                    tempo=project.metadata.tempo,
                    time_signature_num=project.metadata.time_signature[0],
                    time_signature_den=project.metadata.time_signature[1],
                    key=project.metadata.key,
                    author=project.metadata.author,
                    description=project.metadata.description
                )
                session.add(db_project)
            
            session.commit()
            return True
        except Exception as e:
            print(f"Failed to save project to database: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def load_project_metadata(self, path: str):
        """Load project metadata from database"""
        session = self.get_session()
        try:
            project = session.query(ProjectModel).filter_by(path=path).first()
            return project
        finally:
            session.close()
    
    def list_projects(self):
        """List all projects in database"""
        session = self.get_session()
        try:
            return session.query(ProjectModel).all()
        finally:
            session.close()
