from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and persona tracking"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    has_persona = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, email, password):
        """Initialize a new user with email and password"""
        self.email = email
        self.set_password(password)
        self.has_persona = False

    def set_password(self, password):
        """Set the password hash from a plaintext password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def set_has_persona(self, has_persona):
        """Set whether the user has a persona vector"""
        self.has_persona = has_persona
        self.updated_at = datetime.utcnow()
    
    @classmethod
    def get_by_email(cls, email):
        """Find a user by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def create_user(cls, email, password):
        """Create a new user with the provided email and password"""
        user = cls(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return user
    
    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            'id': self.id,
            'email': self.email,
            'has_persona': self.has_persona,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class UserPersona(db.Model):
    """Model for storing user financial persona vectors"""
    __tablename__ = 'user_personas'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    persona_vector = db.Column(db.JSON, nullable=False)  # Store the vector as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('persona', uselist=False))

    def __init__(self, user_id, persona_vector):
        """Initialize a new user persona with user_id and vector"""
        self.user_id = user_id
        self.persona_vector = persona_vector

    @classmethod
    def get_by_user_id(cls, user_id):
        """Find a persona by user_id"""
        return cls.query.filter_by(user_id=user_id).first()
    
    @classmethod
    def create_or_update(cls, user_id, persona_vector):
        """Create a new persona or update existing one"""
        persona = cls.get_by_user_id(user_id)
        user = User.query.get(user_id)
        
        if persona:
            persona.persona_vector = persona_vector
            persona.updated_at = datetime.utcnow()
        else:
            persona = cls(user_id=user_id, persona_vector=persona_vector)
            db.session.add(persona)
        
        # Update user has_persona flag
        if user:
            user.set_has_persona(True)
            
        db.session.commit()
        return persona
    
    def to_dict(self):
        """Convert persona to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'persona_vector': self.persona_vector,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }