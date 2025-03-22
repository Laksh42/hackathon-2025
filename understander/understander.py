from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import logging
import numpy as np

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Key financial terms and their associated vector indices
FINANCIAL_TERMS = {
    'income': 0,
    'salary': 0,
    'earn': 0,
    'make': 0,
    'expenses': 1,
    'spending': 1,
    'costs': 1,
    'bills': 1,
    'savings': 2,
    'saved': 2,
    'reserve': 2,
    'house': 3,
    'home': 3,
    'property': 3,
    'mortgage': 3,
    'retirement': 4,
    'retire': 4,
    'education': 5,
    'college': 5,
    'university': 5,
    'school': 5,
    'risk': 6,
    'conservative': 6,
    'moderate': 6,
    'aggressive': 6,
    'debt': 7,
    'loan': 7,
    'credit': 7,
    'car': 8,
    'vehicle': 8,
    'auto': 8,
    'invest': 9,
    'investment': 9,
    'stock': 9,
    'bond': 9,
    'fund': 9
}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "understander"})

@app.route('/process', methods=['POST'])
def process_conversation():
    try:
        # Extract conversation data from request
        data = request.json
        logger.info(f"Received data: {data}")
        
        if not data or 'conversation' not in data:
            return jsonify({"error": "Invalid request format. 'conversation' field is required."}), 400
        
        conversation = data['conversation']
        
        # Extract user information from the conversation
        user_vector = extract_user_vector(conversation)
        user_profile = create_user_profile(user_vector, conversation)
        
        logger.info(f"Extracted user vector: {user_vector}")
        logger.info(f"Created user profile: {user_profile}")
        
        return jsonify(user_profile)
    
    except Exception as e:
        error_msg = f"Error processing conversation: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

def extract_user_vector(conversation):
    """
    Extract a financial vector from the conversation.
    The vector represents key financial attributes.
    """
    # Initialize vector with default values
    # [income, expenses, savings, house_goal, retirement_goal, education_goal, 
    #  risk_tolerance, debt, car_loan, investment_interest]
    user_vector = [0.0] * 10
    
    # Extract income (index 0)
    income = extract_amount(conversation, ['income', 'salary', 'earn', 'make'])
    if income:
        # Normalize income (assuming max reasonable income is 500k)
        user_vector[0] = min(income / 500000.0, 1.0)
    
    # Extract expenses (index 1)
    expenses = extract_amount(conversation, ['expenses', 'spending', 'costs', 'bills'])
    if expenses:
        # Normalize expenses (assuming max is 20k monthly)
        user_vector[1] = min(expenses / 20000.0, 1.0)
    
    # Extract savings (index 2)
    savings = extract_amount(conversation, ['savings', 'saved', 'reserve'])
    if savings:
        # Normalize savings (assuming max is 1M)
        user_vector[2] = min(savings / 1000000.0, 1.0)
    
    # Extract goals (indices 3-5)
    for msg in [m for m in conversation if m['sender'] == 'user']:
        text = msg['text'].lower()
        
        # House goal (index 3)
        if any(term in text for term in ['house', 'home', 'property', 'mortgage']):
            user_vector[3] = 1.0
        
        # Retirement goal (index 4)
        if any(term in text for term in ['retirement', 'retire']):
            user_vector[4] = 1.0
        
        # Education goal (index 5)
        if any(term in text for term in ['education', 'college', 'university', 'school']):
            user_vector[5] = 1.0
    
    # Extract risk tolerance (index 6)
    risk_tolerance = extract_risk_tolerance(conversation)
    user_vector[6] = risk_tolerance
    
    # Extract debt/loan information (indices 7-8)
    debt = extract_amount(conversation, ['debt', 'loan', 'credit'])
    if debt:
        # Normalize debt (assuming max is 100k)
        user_vector[7] = min(debt / 100000.0, 1.0)
    
    # Extract car loan specifically
    car_loan = extract_car_loan(conversation)
    if car_loan:
        # Normalize car loan (assuming max is 50k)
        user_vector[8] = min(car_loan / 50000.0, 1.0)
    
    # Extract investment interest (index 9)
    for msg in [m for m in conversation if m['sender'] == 'user']:
        text = msg['text'].lower()
        if any(term in text for term in ['invest', 'investment', 'stock', 'bond', 'fund']):
            user_vector[9] = 1.0
    
    return user_vector

def extract_amount(conversation, keywords):
    """Extract monetary amount related to specific keywords"""
    amount_pattern = r'\\$?(\\d+[,\\.]?\\d*)[k|K|thousand|million|M|m]?'
    
    for msg in [m for m in conversation if m['sender'] == 'user']:
        text = msg['text'].lower()
        
        # Check if any of the keywords are in the text
        if any(keyword in text for keyword in keywords):
            # Find all monetary amounts in the text
            matches = re.findall(amount_pattern, text)
            if matches:
                # Convert the matched amount to a number
                amount_str = matches[0].replace(',', '')
                amount = float(amount_str)
                
                # Adjust for shorthand (k/m)
                if 'k' in text or 'K' in text or 'thousand' in text:
                    amount *= 1000
                elif 'm' in text or 'M' in text or 'million' in text:
                    amount *= 1000000
                
                return amount
    
    return 0

def extract_risk_tolerance(conversation):
    """Extract risk tolerance level from conversation"""
    risk_level = 0.5  # Default to moderate
    
    for msg in [m for m in conversation if m['sender'] == 'user']:
        text = msg['text'].lower()
        
        if 'risk' in text:
            if any(term in text for term in ['conservative', 'low', 'safe', 'minimal']):
                risk_level = 0.25
            elif any(term in text for term in ['moderate', 'medium', 'balanced']):
                risk_level = 0.5
            elif any(term in text for term in ['aggressive', 'high', 'risky', 'growth']):
                risk_level = 0.75
    
    return risk_level

def extract_car_loan(conversation):
    """Extract car loan amount from conversation"""
    for msg in [m for m in conversation if m['sender'] == 'user']:
        text = msg['text'].lower()
        
        # Check if car loan is mentioned
        if any(term in text for term in ['car loan', 'auto loan', 'vehicle loan']):
            return extract_amount([msg], ['loan', 'debt'])
    
    return 0

def create_user_profile(user_vector, conversation):
    """Create a comprehensive user profile from the vector and conversation"""
    # Extract more detailed information from the conversation
    income = extract_amount(conversation, ['income', 'salary', 'earn', 'make'])
    expenses = extract_amount(conversation, ['expenses', 'spending', 'costs', 'bills'])
    savings = extract_amount(conversation, ['savings', 'saved', 'reserve'])
    debt = extract_amount(conversation, ['debt', 'loan', 'credit'])
    car_loan = extract_car_loan(conversation)
    
    # Extract financial goals
    goals = []
    for msg in [m for m in conversation if m['sender'] == 'user']:
        text = msg['text'].lower()
        
        if any(term in text for term in ['house', 'home', 'property', 'mortgage']):
            goals.append("home_purchase")
        
        if any(term in text for term in ['retirement', 'retire']):
            goals.append("retirement")
        
        if any(term in text for term in ['education', 'college', 'university', 'school']):
            goals.append("education")
            
        if any(term in text for term in ['invest', 'investment', 'stock', 'bond', 'fund']):
            goals.append("investment")
    
    # Determine risk profile
    risk_levels = ["conservative", "moderate", "aggressive"]
    risk_index = min(2, int(user_vector[6] * 3))
    risk_profile = risk_levels[risk_index]
    
    # Calculate financial metrics
    savings_ratio = savings / income if income > 0 else 0
    debt_to_income = debt / income if income > 0 else 0
    monthly_savings = income - expenses if income > expenses else 0
    
    # Create the profile
    user_profile = {
        "vector": user_vector,
        "financial_info": {
            "annual_income": income,
            "monthly_expenses": expenses,
            "total_savings": savings,
            "total_debt": debt,
            "car_loan": car_loan,
            "monthly_savings": monthly_savings,
            "savings_ratio": savings_ratio,
            "debt_to_income": debt_to_income
        },
        "risk_profile": risk_profile,
        "financial_goals": goals
    }
    
    return user_profile

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5051, debug=True)