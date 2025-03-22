import json
import logging
import random
import re
import os
import uuid
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DialogueState:
    """Class to track the state of a dialogue"""
    
    def __init__(self, session_id=None, config=None):
        """Initialize a new dialogue state"""
        self.session_id = session_id or str(uuid.uuid4())
        self.conversation = []
        self.current_topic = None
        self.topics_covered = set()
        self.confidence_scores = {}
        self.dialogue_turn = 0
        self.last_activity = datetime.utcnow()
        self.config = config or self._load_default_config()
        self.is_complete = False
    
    def _load_default_config(self):
        """Load default configuration"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load config.json: {str(e)}. Using default values.")
            return {
                "max_dialogues": 5,
                "chat_timeout": 300,
                "confidence_threshold": 0.7,
                "dialogue_templates": {
                    "greeting": "Welcome to the Wells Fargo Financial Assistant!",
                    "income_question": "What's your annual income?",
                    "expenses_question": "What are your monthly expenses?",
                    "savings_question": "How much do you have in savings?",
                    "goals_question": "Do you have any specific financial goals?",
                    "risk_question": "How would you describe your risk tolerance?",
                    "debt_question": "Do you have any outstanding loans or debts?",
                    "closing_question": "Would you like to see personalized recommendations?",
                    "clarification_templates": [
                        "Could you please provide more details about your {topic}?",
                        "I'd like to better understand your {topic}. Can you elaborate?"
                    ]
                }
            }
    
    def add_message(self, text, sender):
        """Add a message to the conversation"""
        message = {
            'text': text,
            'sender': sender,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.conversation.append(message)
        self.last_activity = datetime.utcnow()
        self.dialogue_turn += 1 if sender == 'bot' else 0
        return message
    
    def is_expired(self):
        """Check if the dialogue has expired due to inactivity"""
        timeout = self.config.get('chat_timeout', 300)  # Default 5 minutes
        return datetime.utcnow() > self.last_activity + timedelta(seconds=timeout)
    
    def is_max_turns_reached(self):
        """Check if the maximum number of dialogue turns has been reached"""
        max_dialogues = self.config.get('max_dialogues', 5)
        return self.dialogue_turn >= max_dialogues
    
    def set_topic_confidence(self, topic, confidence):
        """Set confidence score for a topic"""
        self.confidence_scores[topic] = confidence
        if confidence >= self.config.get('confidence_threshold', 0.7):
            self.topics_covered.add(topic)
    
    def needs_clarification(self, topic):
        """Check if a topic needs clarification based on confidence score"""
        if topic not in self.confidence_scores:
            return True
        return self.confidence_scores.get(topic, 0) < self.config.get('confidence_threshold', 0.7)
    
    def get_dialogue_template(self, template_key, **kwargs):
        """Get a dialogue template with formatting"""
        templates = self.config.get('dialogue_templates', {})
        template = templates.get(template_key, "")
        return template.format(**kwargs) if template else ""
    
    def get_random_clarification_template(self, topic):
        """Get a random clarification template for a topic"""
        templates = self.config.get('dialogue_templates', {}).get('clarification_templates', [])
        if not templates:
            return f"Could you tell me more about your {topic}?"
        return random.choice(templates).format(topic=topic)
    
    def get_next_topic(self):
        """Get the next topic to discuss"""
        # List of all topics in order of priority
        all_topics = [
            'income', 'expenses', 'savings', 'goals', 'risk_tolerance', 'debt'
        ]
        
        # Return the first topic not yet covered with sufficient confidence
        for topic in all_topics:
            if topic not in self.topics_covered:
                return topic
        
        return None
    
    def to_dict(self):
        """Convert state to dictionary for API responses"""
        return {
            'session_id': self.session_id,
            'dialogue_turn': self.dialogue_turn,
            'current_topic': self.current_topic,
            'topics_covered': list(self.topics_covered),
            'confidence_scores': self.confidence_scores,
            'is_complete': self.is_complete,
            'last_activity': self.last_activity.isoformat()
        }


class DialogueManager:
    """Manager for adaptive dialogue flows"""
    
    def __init__(self, config_path='config.json'):
        """Initialize the dialogue manager"""
        self.sessions = {}
        self.load_config(config_path)
    
    def load_config(self, config_path):
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            self.config = {
                "max_dialogues": 5,
                "chat_timeout": 300,
                "confidence_threshold": 0.7
            }
    
    def get_session(self, session_id=None):
        """Get or create a dialogue session"""
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            
            # Check if session has expired
            if session.is_expired():
                logger.info(f"Session {session_id} has expired. Creating new session.")
                session = DialogueState(session_id, self.config)
                self.sessions[session_id] = session
            
            return session
        
        # Create new session
        new_session = DialogueState(session_id, self.config)
        self.sessions[new_session.session_id] = new_session
        return new_session
    
    def process_message(self, session_id, message_text, sender='user'):
        """Process a message and determine the next action"""
        # Get or create session
        session = self.get_session(session_id)
        
        # Add message to conversation
        session.add_message(message_text, sender)
        
        # Process user messages
        if sender == 'user':
            # Extract information from the message
            topics = self._extract_topics(message_text, session.current_topic)
            
            # Update confidence scores
            for topic, confidence in topics.items():
                session.set_topic_confidence(topic, confidence)
        
        # Determine next action
        if session.is_max_turns_reached():
            session.is_complete = True
            return self._create_response(session, "closing")
        
        # Get next topic if needed
        if not session.current_topic or not session.needs_clarification(session.current_topic):
            session.current_topic = session.get_next_topic()
        
        # Check if all topics are covered
        if not session.current_topic:
            session.is_complete = True
            return self._create_response(session, "closing")
        
        # Generate response for current topic
        return self._create_response(session, session.current_topic)
    
    def _create_response(self, session, topic_or_action):
        """Create a response based on topic or action"""
        if topic_or_action == "greeting":
            response_text = session.get_dialogue_template("greeting")
            next_topic = session.get_next_topic()
            if next_topic:
                response_text += " " + self._get_question_for_topic(session, next_topic)
        
        elif topic_or_action == "closing":
            response_text = session.get_dialogue_template("closing_question")
        
        elif session.needs_clarification(topic_or_action):
            # Need more information about this topic
            response_text = session.get_random_clarification_template(topic_or_action)
        
        else:
            # Topic covered, move to next topic
            next_topic = session.get_next_topic()
            if next_topic:
                response_text = self._get_question_for_topic(session, next_topic)
            else:
                response_text = session.get_dialogue_template("closing_question")
                session.is_complete = True
        
        # Add bot message to conversation
        session.add_message(response_text, 'bot')
        
        return {
            'text': response_text,
            'session_id': session.session_id,
            'state': session.to_dict()
        }
    
    def _get_question_for_topic(self, session, topic):
        """Get the question for a specific topic"""
        topic_question_mapping = {
            'income': 'income_question',
            'expenses': 'expenses_question',
            'savings': 'savings_question',
            'goals': 'goals_question',
            'risk_tolerance': 'risk_question',
            'debt': 'debt_question'
        }
        
        template_key = topic_question_mapping.get(topic, 'general_question')
        return session.get_dialogue_template(template_key)
    
    def _extract_topics(self, message, current_topic):
        """Extract information about topics from a message"""
        topics = {}
        
        # Income extraction
        if current_topic == 'income' or not current_topic:
            income_confidence, income_value = self._extract_income(message)
            if income_confidence > 0:
                topics['income'] = income_confidence
        
        # Expenses extraction
        if current_topic == 'expenses' or not current_topic:
            expenses_confidence, expenses_value = self._extract_expenses(message)
            if expenses_confidence > 0:
                topics['expenses'] = expenses_confidence
        
        # Savings extraction
        if current_topic == 'savings' or not current_topic:
            savings_confidence, savings_value = self._extract_savings(message)
            if savings_confidence > 0:
                topics['savings'] = savings_confidence
        
        # Goals extraction
        if current_topic == 'goals' or not current_topic:
            goals_confidence, goals = self._extract_goals(message)
            if goals_confidence > 0:
                topics['goals'] = goals_confidence
        
        # Risk tolerance extraction
        if current_topic == 'risk_tolerance' or not current_topic:
            risk_confidence, risk_level = self._extract_risk_tolerance(message)
            if risk_confidence > 0:
                topics['risk_tolerance'] = risk_confidence
        
        # Debt extraction
        if current_topic == 'debt' or not current_topic:
            debt_confidence, debt_value = self._extract_debt(message)
            if debt_confidence > 0:
                topics['debt'] = debt_confidence
        
        return topics
    
    def _extract_income(self, message):
        """Extract income information from message"""
        # Simple pattern matching for income
        income_pattern = r'(?:income|make|earn|salary)\s+(?:is|of|about)?\s*(?:[\$£€]?\s*(\d[,\d]*(?:\.\d+)?)\s*(?:k|thousand|million|m|per year|yearly|annually|a year)?)'
        match = re.search(income_pattern, message.lower())
        
        if match:
            try:
                income_value = match.group(1).replace(',', '')
                income = float(income_value)
                
                # Adjust for shorthand (k/m)
                if 'k' in message.lower() or 'thousand' in message.lower():
                    income *= 1000
                elif 'm' in message.lower() or 'million' in message.lower():
                    income *= 1000000
                
                # Higher confidence for specific values
                return 0.9, income
            except:
                return 0.3, 0
        
        # Check for approximate income
        approx_patterns = [
            (r'(?:about|around|approximately|roughly)\s+(?:[\$£€]?\s*(\d[,\d]*(?:\.\d+)?)\s*(?:k|thousand|million|m)?)', 0.7),
            (r'(?:low|middle|high)\s+(?:income|earner)', 0.5),
            (r'(?:make|earn|salary)\s+(?:good|great|decent|lot)', 0.4)
        ]
        
        for pattern, confidence in approx_patterns:
            if re.search(pattern, message.lower()):
                return confidence, 0
        
        return 0.0, 0
    
    def _extract_expenses(self, message):
        """Extract monthly expenses information from message"""
        # Pattern matching for expenses
        expenses_pattern = r'(?:expenses|spending|costs|bills)\s+(?:is|are|of|about)?\s*(?:[\$£€]?\s*(\d[,\d]*(?:\.\d+)?)\s*(?:k|thousand|million|m|per month|monthly|a month)?)'
        match = re.search(expenses_pattern, message.lower())
        
        if match:
            try:
                expenses_value = match.group(1).replace(',', '')
                expenses = float(expenses_value)
                
                # Adjust for shorthand (k/m)
                if 'k' in message.lower() or 'thousand' in message.lower():
                    expenses *= 1000
                elif 'm' in message.lower() or 'million' in message.lower():
                    expenses *= 1000000
                
                return 0.9, expenses
            except:
                return 0.3, 0
        
        return 0.0, 0
    
    def _extract_savings(self, message):
        """Extract savings information from message"""
        # Pattern matching for savings
        savings_pattern = r'(?:savings|saved|save|reserve)\s+(?:is|are|of|about)?\s*(?:[\$£€]?\s*(\d[,\d]*(?:\.\d+)?)\s*(?:k|thousand|million|m)?)'
        match = re.search(savings_pattern, message.lower())
        
        if match:
            try:
                savings_value = match.group(1).replace(',', '')
                savings = float(savings_value)
                
                # Adjust for shorthand (k/m)
                if 'k' in message.lower() or 'thousand' in message.lower():
                    savings *= 1000
                elif 'm' in message.lower() or 'million' in message.lower():
                    savings *= 1000000
                
                return 0.9, savings
            except:
                return 0.3, 0
        
        return 0.0, 0
    
    def _extract_goals(self, message):
        """Extract financial goals from message"""
        goal_keywords = {
            'home_purchase': ['house', 'home', 'property', 'mortgage', 'buy', 'real estate'],
            'retirement': ['retire', 'retirement', 'pension', '401k', 'ira'],
            'education': ['education', 'college', 'university', 'school', 'tuition', 'student'],
            'investment': ['invest', 'investment', 'stock', 'bond', 'portfolio', 'wealth'],
            'debt_payment': ['pay off', 'debt', 'loan', 'credit card', 'student loan'],
            'emergency_fund': ['emergency', 'fund', 'rainy day', 'safety net'],
            'travel': ['travel', 'vacation', 'trip', 'holiday'],
            'business': ['business', 'startup', 'company', 'entrepreneur']
        }
        
        found_goals = []
        msg_lower = message.lower()
        
        for goal, keywords in goal_keywords.items():
            if any(keyword in msg_lower for keyword in keywords):
                found_goals.append(goal)
        
        confidence = 0.0
        if found_goals:
            # More goals = higher confidence that we understood correctly
            confidence = min(0.5 + (len(found_goals) * 0.1), 0.9)
        
        return confidence, found_goals
    
    def _extract_risk_tolerance(self, message):
        """Extract risk tolerance information from message"""
        risk_keywords = {
            'conservative': ['conservative', 'low risk', 'safe', 'security', 'cautious', 'minimal risk'],
            'moderate': ['moderate', 'balanced', 'middle', 'average', 'medium'],
            'aggressive': ['aggressive', 'high risk', 'risky', 'growth', 'ambitious']
        }
        
        msg_lower = message.lower()
        for tolerance, keywords in risk_keywords.items():
            if any(keyword in msg_lower for keyword in keywords):
                return 0.8, tolerance
        
        return 0.0, None
    
    def _extract_debt(self, message):
        """Extract debt information from message"""
        # Pattern matching for debt
        debt_pattern = r'(?:debt|loan|credit|owe)\s+(?:is|of|about)?\s*(?:[\$£€]?\s*(\d[,\d]*(?:\.\d+)?)\s*(?:k|thousand|million|m)?)'
        match = re.search(debt_pattern, message.lower())
        
        if match:
            try:
                debt_value = match.group(1).replace(',', '')
                debt = float(debt_value)
                
                # Adjust for shorthand (k/m)
                if 'k' in message.lower() or 'thousand' in message.lower():
                    debt *= 1000
                elif 'm' in message.lower() or 'million' in message.lower():
                    debt *= 1000000
                
                return 0.9, debt
            except:
                return 0.3, 0
        
        # Specific types of debt
        debt_types = ['mortgage', 'student loan', 'car loan', 'auto loan', 'credit card', 'personal loan']
        if any(debt_type in message.lower() for debt_type in debt_types):
            return 0.7, 0
        
        # Check for debt-free
        if any(term in message.lower() for term in ['no debt', 'debt free', 'no loans', 'paid off']):
            return 0.8, 0
        
        return 0.0, 0
    
    def extract_user_vector(self, session_id):
        """Extract a financial vector from the conversation"""
        session = self.get_session(session_id)
        
        # Initialize vector with default values
        # [income, expenses, savings, house_goal, retirement_goal, education_goal, 
        #  risk_tolerance, debt, car_loan, investment_interest]
        user_vector = [0.0] * 10
        
        # Process all user messages
        for message in [m for m in session.conversation if m['sender'] == 'user']:
            text = message['text'].lower()
            
            # Extract income (index 0)
            income_confidence, income = self._extract_income(text)
            if income_confidence > 0.7 and income > 0:
                # Normalize income (assuming max reasonable income is 500k)
                user_vector[0] = min(income / 500000.0, 1.0)
            
            # Extract expenses (index 1)
            expenses_confidence, expenses = self._extract_expenses(text)
            if expenses_confidence > 0.7 and expenses > 0:
                # Normalize expenses (assuming max is 20k monthly)
                user_vector[1] = min(expenses / 20000.0, 1.0)
            
            # Extract savings (index 2)
            savings_confidence, savings = self._extract_savings(text)
            if savings_confidence > 0.7 and savings > 0:
                # Normalize savings (assuming max is 1M)
                user_vector[2] = min(savings / 1000000.0, 1.0)
            
            # Extract goals (indices 3-5)
            goals_confidence, goals = self._extract_goals(text)
            if goals_confidence > 0.7:
                # House goal (index 3)
                if 'home_purchase' in goals:
                    user_vector[3] = 1.0
                
                # Retirement goal (index 4)
                if 'retirement' in goals:
                    user_vector[4] = 1.0
                
                # Education goal (index 5)
                if 'education' in goals:
                    user_vector[5] = 1.0
            
            # Extract risk tolerance (index 6)
            risk_confidence, risk_level = self._extract_risk_tolerance(text)
            if risk_confidence > 0.7:
                if risk_level == 'conservative':
                    user_vector[6] = 0.25
                elif risk_level == 'moderate':
                    user_vector[6] = 0.5
                elif risk_level == 'aggressive':
                    user_vector[6] = 0.75
            
            # Extract debt (index 7)
            debt_confidence, debt = self._extract_debt(text)
            if debt_confidence > 0.7 and debt > 0:
                # Normalize debt (assuming max is 100k)
                user_vector[7] = min(debt / 100000.0, 1.0)
            
            # Extract car loan (index 8)
            if 'car loan' in text or 'auto loan' in text or 'vehicle loan' in text:
                # Simple detection of car loan mention
                user_vector[8] = 0.5
            
            # Extract investment interest (index 9)
            if any(term in text for term in ['invest', 'investment', 'stock', 'bond', 'fund']):
                user_vector[9] = 1.0
        
        return user_vector
    
    def create_user_profile(self, session_id):
        """Create a comprehensive user profile from the conversation"""
        session = self.get_session(session_id)
        user_vector = self.extract_user_vector(session_id)
        
        # Extract more detailed information from the conversation
        income = 0
        expenses = 0
        savings = 0
        debt = 0
        goals = []
        risk_profile = "moderate"  # Default
        
        # Process all user messages for specific details
        for message in [m for m in session.conversation if m['sender'] == 'user']:
            text = message['text'].lower()
            
            # Extract income
            income_confidence, income_value = self._extract_income(text)
            if income_confidence > 0.7 and income_value > 0:
                income = income_value
            
            # Extract expenses
            expenses_confidence, expenses_value = self._extract_expenses(text)
            if expenses_confidence > 0.7 and expenses_value > 0:
                expenses = expenses_value
            
            # Extract savings
            savings_confidence, savings_value = self._extract_savings(text)
            if savings_confidence > 0.7 and savings_value > 0:
                savings = savings_value
            
            # Extract debt
            debt_confidence, debt_value = self._extract_debt(text)
            if debt_confidence > 0.7 and debt_value > 0:
                debt = debt_value
            
            # Extract goals
            goals_confidence, goals_list = self._extract_goals(text)
            if goals_confidence > 0.7:
                goals.extend(goals_list)
            
            # Extract risk profile
            risk_confidence, risk_level = self._extract_risk_tolerance(text)
            if risk_confidence > 0.7 and risk_level:
                risk_profile = risk_level
        
        # Calculate financial metrics
        savings_ratio = savings / income if income > 0 else 0
        debt_to_income = debt / income if income > 0 else 0
        monthly_savings = income / 12 - expenses if income > 0 and expenses > 0 else 0
        
        # Create the profile
        user_profile = {
            "vector": user_vector,
            "financial_info": {
                "annual_income": income,
                "monthly_expenses": expenses,
                "total_savings": savings,
                "total_debt": debt,
                "monthly_savings": monthly_savings,
                "savings_ratio": savings_ratio,
                "debt_to_income": debt_to_income
            },
            "risk_profile": risk_profile,
            "financial_goals": list(set(goals))  # Remove duplicates
        }
        
        return user_profile