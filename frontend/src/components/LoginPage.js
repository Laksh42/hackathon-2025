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
import { useAuth } from '../contexts/AuthContext';
import { config } from '../config';

const LoginPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Reset error and success messages
    setError('');
    setSuccessMessage('');
    setLoading(true);
    
    try {
      // Validate form
      if (!email || !password) {
        setError('Email and password are required');
        setLoading(false);
        return;
      }
      
      // Email validation
      const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      if (!emailRegex.test(email)) {
        setError('Please enter a valid email address');
        setLoading(false);
        return;
      }
      
      if (!isLogin) {
        // Password strength check
        if (password.length < 8) {
          setError('Password must be at least 8 characters');
          setLoading(false);
          return;
        }
      }

      if (isLogin) {
        console.log('Using auth context login');
        // Use the AuthContext login function
        const result = await login(email, password);
        console.log('Login result:', result);
        
        if (result.success) {
          console.log('Login successful, hasPersona:', result.hasPersona);
          // Navigate based on persona status
          if (result.hasPersona) {
            console.log('Navigating to dashboard');
            navigate('/dashboard');
          } else {
            console.log('Navigating to chat');
            navigate('/chat');
          }
        } else {
          setError(result.error || 'Login failed');
        }
      } else {
        console.log('Using auth context register');
        // Use the AuthContext register function
        const result = await register(email, password);
        
        if (result.success) {
          // Show success message for registration
          setSuccessMessage('Registration successful! You can now log in.');
          setIsLogin(true);
        } else {
          setError(result.error || 'Registration failed');
        }
      }
    } catch (error) {
      console.error('Auth error:', error);
      setError('An unexpected error occurred. Please try again.');
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