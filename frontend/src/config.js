// Configuration for the frontend application

// Determine the environment
const isDevelopment = process.env.NODE_ENV === 'development';
const isDocker = process.env.REACT_APP_DOCKER === 'true';

// Base URLs for services
const getServiceUrl = (serviceName, defaultPort) => {
  if (isDocker) {
    // In Docker, use the service name as hostname
    return `http://${serviceName}:${defaultPort}`;
  } else if (isDevelopment) {
    // In development, use localhost
    return `http://localhost:${defaultPort}`;
  } else {
    // In production, use relative URLs to the same domain
    return '';
  }
};

export const config = {
  // API service URLs
  services: {
    auth: {
      url: getServiceUrl('auth', 5053)
    },
    backend: {
      url: getServiceUrl('backend', 5050)
    },
    understander: {
      url: getServiceUrl('understander', 5052)
    },
    recommender: {
      url: getServiceUrl('recommender', 5051)
    }
  },
  
  // Application settings
  app: {
    name: 'Wells Fargo Financial Assistant',
    version: '2.0.0',
    logoUrl: '/logo.png'
  },
  
  // Authentication settings
  auth: {
    tokenKey: 'token',
    refreshTokenKey: 'refreshToken',
    userKey: 'currentUser',
    expiryKey: 'tokenExpiry'
  },
  
  // Chat interface settings
  chat: {
    maxMessages: 10,
    typingIndicatorDelay: 1000,
    aiResponseDelay: 800,
    sessionStorageKey: 'chatSession',
    welcomeMessage: 'Welcome to the Wells Fargo Financial Assistant! I\'m here to help you with your financial goals.'
  },
  
  // Recommendation settings
  recommendations: {
    maxRecommendations: 5,
    confidenceThreshold: 0.65,
    storageKey: 'userRecommendations',
    refreshInterval: 24 * 60 * 60 * 1000 // 24 hours
  },
  
  // Feature flags
  features: {
    enableMockData: isDevelopment,
    enableDebugLogging: isDevelopment,
    showLoginForm: true,
    showNewsSection: true
  },
  
  // Debug settings
  debug: {
    logApiCalls: isDevelopment,
    verboseErrors: isDevelopment,
    mockApiResponses: false
  }
};