from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import logging
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load product database
PRODUCTS_DB = [
    {
        "id": "prod-1",
        "name": "Premium Checking Account",
        "description": "A feature-rich checking account with no minimum balance requirements and zero monthly fees.",
        "features": [
            "No minimum balance requirements",
            "Zero monthly service fees",
            "Free online and mobile banking",
            "Free bill pay service",
            "24/7 customer support"
        ],
        "vector": [0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.5, 0.2, 0.1]
    },
    {
        "id": "prod-2",
        "name": "High-Yield Savings Account",
        "description": "Maximize your savings with our competitive interest rates and convenient access options.",
        "features": [
            "Competitive interest rates",
            "No monthly maintenance fees",
            "FDIC insured",
            "Automatic savings transfers",
            "Online and mobile access"
        ],
        "vector": [0.3, 0.1, 0.9, 0.2, 0.2, 0.2, 0.1, 0.2, 0.1, 0.3]
    },
    {
        "id": "prod-3",
        "name": "Managed Investment Portfolio",
        "description": "Our professionally managed investment portfolio offers diversified investments tailored to your risk profile and financial goals.",
        "features": [
            "Professional portfolio management",
            "Diversified investment selection",
            "Regular portfolio rebalancing",
            "Quarterly performance reviews",
            "Tax-efficient investment strategies"
        ],
        "vector": [0.6, 0.2, 0.8, 0.4, 0.6, 0.3, 0.7, 0.3, 0.3, 0.9]
    },
    {
        "id": "prod-4",
        "name": "30-Year Fixed Mortgage",
        "description": "Our 30-year fixed mortgage offers stable monthly payments with competitive interest rates to help you achieve your home ownership goals.",
        "features": [
            "Fixed interest rate for entire loan term",
            "Predictable monthly payments",
            "No prepayment penalties",
            "Rate lock options",
            "First-time homebuyer programs available"
        ],
        "vector": [0.7, 0.5, 0.3, 0.9, 0.3, 0.1, 0.3, 0.6, 0.2, 0.4]
    },
    {
        "id": "prod-5",
        "name": "15-Year Fixed Mortgage",
        "description": "Build equity faster with our 15-year fixed mortgage featuring lower interest rates and accelerated payoff timelines.",
        "features": [
            "Lower interest rates than 30-year mortgages",
            "Build equity faster",
            "Pay less total interest over the life of the loan",
            "Stable monthly payments",
            "No prepayment penalties"
        ],
        "vector": [0.8, 0.6, 0.6, 0.9, 0.3, 0.1, 0.4, 0.6, 0.2, 0.5]
    },
    {
        "id": "prod-6",
        "name": "Home Equity Line of Credit",
        "description": "Tap into your home's equity for home improvements, debt consolidation, or other major expenses with flexible terms.",
        "features": [
            "Competitive variable interest rates",
            "Interest may be tax-deductible",
            "Access funds as needed",
            "Flexible repayment options",
            "No application fees"
        ],
        "vector": [0.7, 0.4, 0.2, 0.9, 0.3, 0.2, 0.5, 0.7, 0.3, 0.5]
    },
    {
        "id": "prod-7",
        "name": "Auto Loan",
        "description": "Finance your new or used vehicle purchase with competitive rates and flexible terms designed to fit your budget.",
        "features": [
            "Competitive fixed rates",
            "Flexible terms up to 72 months",
            "No application fees",
            "Quick approval process",
            "No prepayment penalties"
        ],
        "vector": [0.5, 0.6, 0.2, 0.3, 0.1, 0.3, 0.4, 0.6, 0.9, 0.2]
    },
    {
        "id": "prod-8",
        "name": "Credit Builder Loan",
        "description": "Establish or improve your credit score with this specially designed loan program that reports to all three major credit bureaus.",
        "features": [
            "Build credit history",
            "Reports to all three major credit bureaus",
            "Small loan amounts available",
            "Affordable monthly payments",
            "Fixed terms with clear end date"
        ],
        "vector": [0.3, 0.7, 0.1, 0.2, 0.1, 0.2, 0.2, 0.8, 0.3, 0.1]
    },
    {
        "id": "prod-9",
        "name": "Student Loan Refinancing",
        "description": "Lower your monthly payments or pay off your student loans faster with our competitive refinancing options.",
        "features": [
            "Potentially lower interest rates",
            "Consolidate multiple loans into one",
            "Flexible repayment terms",
            "No application or origination fees",
            "Autopay discount available"
        ],
        "vector": [0.4, 0.7, 0.2, 0.2, 0.2, 0.8, 0.5, 0.9, 0.3, 0.4]
    },
    {
        "id": "prod-10",
        "name": "Personal Loan",
        "description": "Get the funds you need for debt consolidation, home improvements, or unexpected expenses with fixed rates and terms.",
        "features": [
            "Fixed interest rates",
            "No collateral required",
            "Quick application process",
            "Funds typically available within days",
            "No prepayment penalties"
        ],
        "vector": [0.4, 0.8, 0.3, 0.4, 0.2, 0.4, 0.6, 0.8, 0.5, 0.3]
    },
    {
        "id": "prod-11",
        "name": "IRA Retirement Account",
        "description": "Our IRA accounts offer tax-advantaged retirement savings with a wide range of investment options to meet your long-term financial goals.",
        "features": [
            "Tax-deferred or tax-free growth potential",
            "Multiple investment options",
            "Potential tax deductions",
            "Flexible contribution options",
            "Online account management"
        ],
        "vector": [0.5, 0.2, 0.7, 0.3, 0.9, 0.2, 0.5, 0.2, 0.1, 0.8]
    },
    {
        "id": "prod-12",
        "name": "401(k) Rollover",
        "description": "Consolidate and take control of your retirement savings from previous employers with our rollover options.",
        "features": [
            "Simplify retirement accounts",
            "More investment options",
            "Potentially lower fees",
            "Ongoing professional support",
            "Tax-deferred growth potential"
        ],
        "vector": [0.5, 0.2, 0.6, 0.3, 0.9, 0.1, 0.4, 0.1, 0.1, 0.7]
    },
    {
        "id": "prod-13",
        "name": "Premium Credit Card",
        "description": "Earn valuable rewards on everyday purchases with our premium credit card offering travel benefits, cash back, and more.",
        "features": [
            "Generous rewards program",
            "Travel benefits and protections",
            "No foreign transaction fees",
            "24/7 concierge service",
            "Enhanced security features"
        ],
        "vector": [0.8, 0.8, 0.4, 0.5, 0.4, 0.3, 0.7, 0.5, 0.5, 0.6]
    },
    {
        "id": "prod-14",
        "name": "Cash Rewards Credit Card",
        "description": "Earn cash back on all your purchases with no annual fee and easy redemption options.",
        "features": [
            "Cash back on all purchases",
            "Higher rewards in select categories",
            "No annual fee",
            "Simple redemption process",
            "Introductory APR offers"
        ],
        "vector": [0.6, 0.9, 0.3, 0.4, 0.3, 0.3, 0.5, 0.4, 0.4, 0.4]
    },
    {
        "id": "prod-15",
        "name": "529 College Savings Plan",
        "description": "Save for education expenses with tax advantages and flexible contribution options for family members of any age.",
        "features": [
            "Tax-free growth for qualified education expenses",
            "High contribution limits",
            "No income restrictions",
            "Flexible use for various education costs",
            "Gift tax benefits for contributors"
        ],
        "vector": [0.5, 0.5, 0.7, 0.3, 0.4, 0.9, 0.4, 0.2, 0.2, 0.6]
    }
]

# Sample news articles
NEWS_ARTICLES = [
    {
        "id": "news-1",
        "title": "Housing Market Continues Strong Growth",
        "summary": "The housing market continues to show strong growth with home prices rising in most metropolitan areas. Analysts suggest this trend may continue through the year, making it a potential opportunity for prospective homebuyers to enter the market before further increases."
    },
    {
        "id": "news-2",
        "title": "Stock Market Shows Increased Volatility",
        "summary": "Recent economic data has led to increased volatility in the stock market. Financial advisors recommend diversified portfolios and long-term investment strategies to navigate through market fluctuations."
    },
    {
        "id": "news-3", 
        "title": "Federal Reserve Holds Interest Rates Steady",
        "summary": "The Federal Reserve has decided to maintain current interest rates, citing balanced economic growth and inflation concerns. This decision impacts various financial products including mortgages, savings accounts, and loans."
    },
    {
        "id": "news-4",
        "title": "New Tax Benefits for Retirement Savers",
        "summary": "Recent legislation has introduced new tax advantages for retirement savings accounts. Financial experts advise reviewing your retirement strategy to maximize these new benefits."
    },
    {
        "id": "news-5",
        "title": "Student Loan Forgiveness Program Expanded",
        "summary": "The government has announced an expansion of student loan forgiveness programs, potentially benefiting millions of borrowers. Eligibility requirements have been modified to include more repayment plans."
    }
]

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "recommender"})

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Extract user data from request
        data = request.json
        logger.info(f"Received data: {data}")
        
        if not data or 'user_data' not in data:
            return jsonify({"error": "Invalid request format. 'user_data' field is required."}), 400
        
        user_data = data['user_data']
        
        # Extract user vector
        if 'vector' not in user_data:
            return jsonify({"error": "User vector is missing."}), 400
        
        user_vector = user_data['vector']
        
        # Find product recommendations based on vector similarity
        recommendations = generate_recommendations(user_vector, user_data)
        
        # Get relevant news articles
        relevant_news = get_relevant_news(user_data)
        
        # Return recommendations and news
        response = {
            "recommendations": recommendations,
            "relevant_news": relevant_news
        }
        
        logger.info(f"Returning recommendations: {response}")
        return jsonify(response)
    
    except Exception as e:
        error_msg = f"Error generating recommendations: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

def generate_recommendations(user_vector, user_data):
    """
    Generate product recommendations based on vector similarity.
    """
    # Calculate cosine similarity between user vector and product vectors
    similarities = []
    for product in PRODUCTS_DB:
        # Extract product vector
        product_vector = product['vector']
        
        # Calculate cosine similarity
        similarity = cosine_similarity(user_vector, product_vector)
        
        # Store product and similarity score
        similarities.append((product, similarity))
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Generate recommendations with explanations
    recommendations = []
    for i, (product, similarity) in enumerate(similarities[:3]):  # Top 3 recommendations
        # Generate explanation based on user data and product features
        explanation = generate_explanation(product, user_data)
        
        # Add recommendation
        recommendations.append({
            "product": product,
            "confidence": similarity,
            "explanation": explanation
        })
    
    return recommendations

def cosine_similarity(v1, v2):
    """
    Calculate cosine similarity between two vectors.
    """
    v1 = np.array(v1)
    v2 = np.array(v2)
    
    # Calculate dot product and norms
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    # Calculate cosine similarity
    similarity = dot_product / (norm_v1 * norm_v2) if norm_v1 * norm_v2 != 0 else 0
    
    return float(similarity)

def generate_explanation(product, user_data):
    """
    Generate a personalized explanation for a product recommendation.
    """
    # Extract financial information
    financial_info = user_data.get('financial_info', {})
    annual_income = financial_info.get('annual_income', 0)
    total_savings = financial_info.get('total_savings', 0)
    monthly_expenses = financial_info.get('monthly_expenses', 0)
    
    # Extract risk profile and goals
    risk_profile = user_data.get('risk_profile', 'moderate')
    goals = user_data.get('financial_goals', [])
    
    # Generate explanation based on product type and user data
    product_name = product['name'].lower()
    
    if 'mortgage' in product_name or 'home' in product_name:
        if 'home_purchase' in goals:
            return f"Based on your income of ${annual_income:,.0f} and your goal to purchase a home, this mortgage product aligns with your financial objectives."
        else:
            return f"With your strong income of ${annual_income:,.0f}, this home financing option could help you build equity and potentially save on taxes."
    
    elif 'investment' in product_name or 'portfolio' in product_name:
        if risk_profile == 'aggressive':
            return f"Given your aggressive risk profile and savings of ${total_savings:,.0f}, this investment product could help maximize your growth potential."
        elif risk_profile == 'conservative':
            return f"With your conservative risk approach and savings of ${total_savings:,.0f}, this investment option provides a balanced approach to wealth growth."
        else:
            return f"Considering your moderate risk tolerance and savings of ${total_savings:,.0f}, this investment product offers a balanced approach to wealth building."
    
    elif 'ira' in product_name or 'retirement' in product_name or '401' in product_name:
        if 'retirement' in goals:
            return f"This retirement account aligns with your stated retirement goals and can help you build your nest egg with tax advantages."
        else:
            return f"Even though retirement wasn't explicitly mentioned, this tax-advantaged account could help you prepare for the future while potentially reducing your tax burden."
    
    elif 'saving' in product_name:
        return f"With monthly expenses of ${monthly_expenses:,.0f}, this savings account could help you build your emergency fund while earning competitive interest."
    
    elif 'credit card' in product_name:
        return f"Based on your spending patterns of ${monthly_expenses:,.0f} monthly, this card's rewards structure could maximize your everyday purchases."
    
    elif 'loan' in product_name:
        return f"With your income level of ${annual_income:,.0f}, this loan product offers competitive rates and terms that align with your financial situation."
    
    elif 'education' in product_name or 'college' in product_name or '529' in product_name:
        if 'education' in goals:
            return f"This education savings plan directly supports your goal of funding education expenses with tax advantages."
        else:
            return f"Although not explicitly mentioned, this education savings product could help you or your family members fund future educational expenses with tax benefits."
    
    # Default explanation
    return f"Based on your financial profile, this product aligns well with your current situation and goals."

def get_relevant_news(user_data):
    """
    Get relevant news articles based on user data.
    """
    # Extract goals and user profile
    goals = user_data.get('financial_goals', [])
    
    # Select relevant news articles
    relevant_news = []
    
    # Home purchase goal -> housing market news
    if 'home_purchase' in goals:
        housing_news = [article for article in NEWS_ARTICLES if 'housing' in article['title'].lower() or 'home' in article['title'].lower()]
        relevant_news.extend(housing_news[:1])  # Add up to 1 housing news article
    
    # Investment goal -> stock market news
    if 'investment' in goals:
        investment_news = [article for article in NEWS_ARTICLES if 'stock' in article['title'].lower() or 'market' in article['title'].lower()]
        relevant_news.extend(investment_news[:1])  # Add up to 1 investment news article
    
    # Education goal -> education financing news
    if 'education' in goals:
        education_news = [article for article in NEWS_ARTICLES if 'student' in article['title'].lower() or 'education' in article['title'].lower()]
        relevant_news.extend(education_news[:1])  # Add up to 1 education news article
    
    # Retirement goal -> retirement news
    if 'retirement' in goals:
        retirement_news = [article for article in NEWS_ARTICLES if 'retirement' in article['title'].lower() or 'tax' in article['title'].lower()]
        relevant_news.extend(retirement_news[:1])  # Add up to 1 retirement news article
    
    # If no specific news articles match, add general financial news
    if not relevant_news:
        relevant_news = NEWS_ARTICLES[:2]  # Add first 2 general news articles
    
    # Limit to 2 news articles maximum
    return relevant_news[:2]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5052, debug=True)