import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { config } from '../config';

// Create the auth context
const AuthContext = createContext();

// Custom hook to use the auth context
export const useAuth = () => {
  return useContext(AuthContext);
};

// Provider component that wraps the app and provides auth context
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [userPersona, setUserPersona] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Initialize auth state on component mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Check if user is authenticated by token
        const token = localStorage.getItem(config.auth.tokenKey);
        console.log('AuthContext initAuth: Token from localStorage:', token ? 'Found' : 'Not found');
        
        if (!token) {
          console.log('AuthContext initAuth: No token found, setting loading to false');
          setLoading(false);
          return;
        }

        // Set default Authorization header for all axios requests
        console.log('AuthContext initAuth: Setting Authorization header');
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

        // Validate token and get user data
        console.log('AuthContext initAuth: Validating token with backend');
        const response = await axios.get(
          `${config.services.auth.url}/api/v1/auth/check-auth`,
          { timeout: 5000 }
        );

        console.log('AuthContext initAuth: Auth check response:', response.data);

        if (response.data && response.data.authenticated) {
          console.log('AuthContext initAuth: Token valid, setting user data');
          setCurrentUser(response.data.user);
          setIsAuthenticated(true);
          
          // Check if user has persona data
          if (response.data.has_persona) {
            console.log('AuthContext initAuth: User has persona, fetching data');
            try {
              const personaResponse = await axios.get(
                `${config.services.auth.url}/api/v1/auth/persona`,
                { timeout: 5000 }
              );
              
              if (personaResponse.data && personaResponse.data.persona) {
                console.log('AuthContext initAuth: Persona data received');
                setUserPersona(personaResponse.data.persona);
              }
            } catch (personaError) {
              console.error('Error fetching user persona during init:', personaError);
            }
          }
        } else {
          console.log('AuthContext initAuth: Token invalid, logging out');
          // Invalid token, clear auth state
          handleLogout();
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        
        if (error.response && error.response.status === 401) {
          // Unauthorized - clear auth data
          handleLogout();
        } else {
          // Other errors - might be network issues, etc.
          setError('Error connecting to authentication service');
        }
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  // Login user with email and password
  const login = async (email, password) => {
    try {
      setLoading(true);
      setError('');
      
      console.log('AuthContext: Attempting login for', email);
      
      const response = await axios.post(
        `${config.services.auth.url}/api/v1/auth/login`,
        { email, password },
        { timeout: 10000 }
      );

      console.log('AuthContext: Login response received:', response.data);

      if (response.data && response.data.access_token) {
        // Store token in localStorage
        localStorage.setItem(config.auth.tokenKey, response.data.access_token);
        
        console.log('AuthContext: Token stored in localStorage');
        
        // Set default Authorization header
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
        
        // Update user state
        setCurrentUser(response.data.user || { email });
        setIsAuthenticated(true);
        
        console.log('AuthContext: User authenticated, has_persona:', response.data.has_persona);
        
        // Check if user has persona
        if (response.data.has_persona) {
          try {
            const personaResponse = await axios.get(
              `${config.services.auth.url}/api/v1/auth/persona`,
              { timeout: 5000 }
            );
            
            if (personaResponse.data && personaResponse.data.persona) {
              setUserPersona(personaResponse.data.persona);
              console.log('AuthContext: User persona loaded');
            }
          } catch (personaError) {
            console.error('Error fetching user persona:', personaError);
          }
        }
        
        return {
          success: true,
          hasPersona: response.data.has_persona
        };
      } else {
        setError('Invalid login response');
        console.error('AuthContext: Invalid login response - no access_token');
        return { success: false, error: 'Invalid login response' };
      }
    } catch (error) {
      console.error('Login error:', error);
      
      let errorMessage = 'An error occurred during login';
      
      if (error.response && error.response.data && error.response.data.error) {
        errorMessage = error.response.data.error;
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'Connection timeout. Please try again.';
      }
      
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Register a new user
  const register = async (email, password) => {
    try {
      setLoading(true);
      setError('');

      console.log('AuthContext: Attempting registration for', email);

      const response = await axios.post(
        `${config.services.auth.url}/api/v1/auth/register`,
        { email, password },
        { timeout: 10000 }
      );

      console.log('AuthContext: Registration response received:', response.data);

      if (response.data && response.data.access_token) {
        // Registration successful
        console.log('AuthContext: Registration successful');
        return { success: true };
      } else {
        setError('Invalid registration response');
        console.error('AuthContext: Invalid registration response');
        return { success: false, error: 'Invalid registration response' };
      }
    } catch (error) {
      console.error('Registration error:', error);
      
      let errorMessage = 'An error occurred during registration';
      
      if (error.response && error.response.data && error.response.data.error) {
        errorMessage = error.response.data.error;
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'Connection timeout. Please try again.';
      }
      
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Save user persona after onboarding
  const saveUserPersona = async (persona) => {
    try {
      setLoading(true);
      setError('');

      const response = await axios.post(
        `${config.services.auth.url}/api/v1/auth/persona`,
        { persona },
        { timeout: 10000 }
      );

      if (response.data && response.data.success) {
        setUserPersona(persona);
        return { success: true };
      } else {
        setError('Failed to save user persona');
        return { success: false, error: 'Failed to save user persona' };
      }
    } catch (error) {
      console.error('Save persona error:', error);
      
      let errorMessage = 'An error occurred while saving your profile';
      
      if (error.response && error.response.data && error.response.data.error) {
        errorMessage = error.response.data.error;
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'Connection timeout. Please try again.';
      }
      
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Logout user
  const handleLogout = () => {
    // Remove token from localStorage
    localStorage.removeItem(config.auth.tokenKey);
    
    // Remove Authorization header
    delete axios.defaults.headers.common['Authorization'];
    
    // Reset state
    setCurrentUser(null);
    setUserPersona(null);
    setIsAuthenticated(false);
    setError('');
  };

  // Create value object with auth state and functions
  const value = {
    currentUser,
    userPersona,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout: handleLogout,
    saveUserPersona
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;