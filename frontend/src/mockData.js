// Mock data for testing the UI without backend connectivity

export const mockRecommendations = [
  {
    confidence: 0.97,
    explanation: "Based on your income level, savings amount, and moderate risk tolerance, a managed investment portfolio would help grow your wealth while working towards your home buying goal.",
    product: {
      description: "Our professionally managed investment portfolio offers diversified investments tailored to your risk profile and financial goals.",
      features: [
        "Professional portfolio management",
        "Diversified investment selection",
        "Regular portfolio rebalancing",
        "Quarterly performance reviews",
        "Tax-efficient investment strategies"
      ],
      id: "inv-port-01",
      name: "Managed Investment Portfolio",
      vector: [0.8, 0.6, 0.7, 0.9, 0.5]
    }
  },
  {
    confidence: 0.95,
    explanation: "Your income level and goal to buy a house make you an excellent candidate for our 30-year fixed mortgage product with competitive rates.",
    product: {
      description: "Our 30-year fixed mortgage offers stable monthly payments with competitive interest rates to help you achieve your home ownership goals.",
      features: [
        "Fixed interest rate for entire loan term",
        "Predictable monthly payments",
        "No prepayment penalties",
        "Rate lock options",
        "First-time homebuyer programs available"
      ],
      id: "mort-30yr-01",
      name: "30-Year Fixed Mortgage",
      vector: [0.9, 0.2, 0.8, 0.7, 0.3]
    }
  },
  {
    confidence: 0.92,
    explanation: "With your stated savings goals and moderate risk tolerance, an IRA retirement account would provide tax advantages while building your long-term wealth.",
    product: {
      description: "Our IRA accounts offer tax-advantaged retirement savings with a wide range of investment options to meet your long-term financial goals.",
      features: [
        "Tax-deferred or tax-free growth potential",
        "Multiple investment options",
        "Potential tax deductions",
        "Flexible contribution options",
        "Online account management"
      ],
      id: "ret-ira-01",
      name: "IRA Retirement Account",
      vector: [0.7, 0.8, 0.6, 0.5, 0.9]
    }
  }
];

export const mockNews = [
  {
    id: "news-1",
    title: "Housing Market Continues Strong Growth",
    summary: "The housing market continues to show strong growth with home prices rising in most metropolitan areas. Analysts suggest this trend may continue through the year, making it a potential opportunity for prospective homebuyers to enter the market before further increases."
  },
  {
    id: "news-2",
    title: "Stock Market Shows Increased Volatility",
    summary: "Recent economic data has led to increased volatility in the stock market. Financial advisors recommend diversified portfolios and long-term investment strategies to navigate through market fluctuations."
  }
];