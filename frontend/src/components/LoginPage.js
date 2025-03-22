import React, { useState } from 'react';
import { 
  Box, 
  Container,
  Typography, 
  TextField, 
  Button, 
  Link, 
  Alert,
  Paper,
  Grid,
  Divider,
  CircularProgress
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { config } from '../config';

const LoginPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');
    setLoading(true);

    try {
      // Form validation
      if (!email || !password) {
        setError('Please fill out all fields');
        setLoading(false);
        return;
      }

      // Email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        setError('Please enter a valid email address');
        setLoading(false);
        return;
      }

      // For registration, validate password match
      if (!isLogin) {
        if (password !== confirmPassword) {
          setError('Passwords do not match');
          setLoading(false);
          return;
        }

        // Password strength check
        if (password.length < 8) {
          setError('Password must be at least 8 characters');
          setLoading(false);
          return;
        }
      }

      // Determine API endpoint based on login/register mode
      const endpoint = isLogin ? 
        `${config.services.auth.url}/api/v1/auth/login` : 
        `${config.services.auth.url}/api/v1/auth/register`;

      // Prepare request data
      const requestData = { email, password };

      // Make API request
      const response = await axios.post(endpoint, requestData, {
        timeout: 10000
      });

      // Handle successful response
      if (response.data) {
        if (isLogin) {
          // Store JWT token in localStorage
          localStorage.setItem('token', response.data.access_token);
          
          // Check if user has completed persona questionnaire
          const hasPersona = response.data.has_persona;
          
          // Redirect based on persona status
          if (hasPersona) {
            // Navigate to main dashboard
            navigate('/dashboard');
          } else {
            // Navigate to onboarding chat
            navigate('/chat');
          }
        } else {
          // Show success message for registration
          setSuccessMessage('Registration successful! You can now log in.');
          setIsLogin(true);
        }
      }
    } catch (error) {
      console.error('Auth error:', error);
      
      if (error.response && error.response.data && error.response.data.error) {
        setError(error.response.data.error);
      } else if (error.code === 'ECONNABORTED') {
        setError('Connection timeout. Please try again later.');
      } else {
        setError('An error occurred. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  const toggleAuthMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setSuccessMessage('');
  };

  return (
    <Container component="main" maxWidth="md">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Grid container spacing={4}>
            <Grid item xs={12} md={6} sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              justifyContent: 'center',
              borderRight: { md: '1px solid #e0e0e0' },
              pr: { md: 4 }
            }}>
              <Typography component="h1" variant="h4" align="center" gutterBottom>
                Wells Fargo Financial Assistant
              </Typography>
              <Typography variant="body1" align="center" color="text.secondary" paragraph>
                Your personalized financial assistant to help you achieve your financial goals.
                Get tailored recommendations based on your unique financial situation.
              </Typography>
              <Box sx={{ 
                mt: 2, 
                display: 'flex', 
                justifyContent: 'center',
                '& img': {
                  maxWidth: '100%',
                  height: 'auto'
                }
              }}>
                <img 
                  src="/logo.png" 
                  alt="Wells Fargo Logo" 
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.style.display = 'none';
                  }}
                />
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography component="h2" variant="h5" align="center">
                {isLogin ? 'Sign In' : 'Create Account'}
              </Typography>
              
              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}
              
              {successMessage && (
                <Alert severity="success" sx={{ mt: 2 }}>
                  {successMessage}
                </Alert>
              )}
              
              <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="email"
                  label="Email Address"
                  name="email"
                  autoComplete="email"
                  autoFocus
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="password"
                  label="Password"
                  type="password"
                  id="password"
                  autoComplete={isLogin ? "current-password" : "new-password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                
                {!isLogin && (
                  <TextField
                    margin="normal"
                    required
                    fullWidth
                    name="confirmPassword"
                    label="Confirm Password"
                    type="password"
                    id="confirmPassword"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                  />
                )}
                
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  sx={{ mt: 3, mb: 2 }}
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : (isLogin ? 'Sign In' : 'Create Account')}
                </Button>
                
                <Box sx={{ textAlign: 'center', mt: 2 }}>
                  <Link href="#" variant="body2" onClick={toggleAuthMode}>
                    {isLogin ? "Don't have an account? Sign Up" : "Already have an account? Sign In"}
                  </Link>
                </Box>
                
                {isLogin && (
                  <Box sx={{ textAlign: 'center', mt: 1 }}>
                    <Link href="#" variant="body2">
                      Forgot password?
                    </Link>
                  </Box>
                )}
              </Box>
            </Grid>
          </Grid>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginPage;