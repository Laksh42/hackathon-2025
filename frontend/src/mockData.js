// Mock data to use in case of API connection issues
export const mockRecommendations = [
  {
    confidence: 0.95,
    confidence_score: 0.95,
    explanation: "Based on your high savings and moderate risk tolerance, this managed investment portfolio can help you grow your wealth through diversified investments.",
    product: {
      id: "investment_account",
      name: "Managed Investment Portfolio",
      description: "Let our experts manage your investments with a diversified portfolio tailored to your goals.",
      features: [
        "Professional management",
        "Diversified portfolio",
        "Low management fees",
        "Mobile account access"
      ],
      vector: [0.7, 0.4, 0.8, 0.7, 0.6, 0.3]
    }
  },
  {
    confidence: 0.91,
    confidence_score: 0.91,
    explanation: "Based on your financial goals and savings habits, this retirement account offers tax advantages to help you prepare for the future.",
    product: {
      id: "retirement_account",
      name: "IRA Retirement Account",
      description: "Plan for your retirement with tax-advantaged IRA accounts.",
      features: [
        "Tax-advantaged growth",
        "Multiple investment options",
        "No account fees",
        "Retirement planning tools"
      ],
      vector: [0.6, 0.3, 0.5, 0.9, 0.7, 0.2]
    }
  },
  {
    confidence: 0.87,
    confidence_score: 0.87,
    explanation: "With your goal of home ownership and stable financial profile, our fixed-rate mortgage offers competitive rates and predictable payments.",
    product: {
      id: "mortgage_30yr",
      name: "30-Year Fixed Mortgage",
      description: "Secure your dream home with our competitive 30-year fixed-rate mortgage.",
      features: [
        "Fixed interest rate",
        "Predictable monthly payments",
        "No prepayment penalties",
        "Online application process"
      ],
      vector: [0.3, 0.2, 0.4, 0.7, 0.8, 0.7]
    }
  }
];

export const mockNews = [
  {
    id: "housing_market_growth",
    title: "Housing Market Continues Strong Growth",
    summary: "The housing market continues to show strength with rising prices across most regions.",
    vector: [0.2, 0.1, 0.3, 0.8, 0.7, 0.4]
  },
  {
    id: "stock_market_volatility",
    title: "Stock Market Shows Increased Volatility",
    summary: "The stock market has experienced increased volatility in recent weeks.",
    vector: [0.1, 0.2, 0.9, 0.5, 0.4, 0.2]
  }
];

// Export a ready-to-use mock response object
export const mockResponse = {
  recommendations: mockRecommendations,
  relevant_news: mockNews
};