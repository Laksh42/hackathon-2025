import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Grid, 
  Paper, 
  Typography, 
  Button, 
  CircularProgress,
  Divider,
  Card,
  CardContent,
  AppBar,
  Toolbar,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  CardActions
} from '@mui/material';
import { 
  AccountCircle,
  NotificationsOutlined,
  DashboardOutlined,
  InsertChartOutlined,
  AccountBalanceOutlined,
  AttachMoneyOutlined,
  ExitToAppOutlined
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { config } from '../config';
import RecommendationDisplay from '../RecommendationDisplay';

const Dashboard = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  
  const { currentUser, userPersona, logout } = useAuth();
  const navigate = useNavigate();
  
  // Handle menu open
  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  // Handle menu close
  const handleClose = () => {
    setAnchorEl(null);
  };
  
  // Handle logout
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  // Function to fetch data (moved outside of useEffect)
  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Get authorization token
      const token = localStorage.getItem(config.auth.tokenKey);
      console.log('Auth token key:', config.auth.tokenKey);
      console.log('Token first 10 chars:', token ? token.substring(0, 10) + '...' : 'No token');
      
      const headers = { 
        Authorization: token ? `Bearer ${token}` : '' 
      };
      
      console.log('Auth headers:', headers);
      
      // First, check if the persona exists in the auth service
      try {
        const personaResponse = await axios.get(
          `${config.services.auth.url}/api/v1/auth/persona`,
          { headers, timeout: 5000 }
        );
        console.log('Persona check response:', personaResponse.data);
      } catch (personaError) {
        console.error('Error checking persona:', personaError.response?.status, personaError.response?.data);
      }
      
      // Fetch recommendations
      console.log('Fetching recommendations from:', `${config.services.backend.url}/api/v1/recommendations`);
      const recommendationsResponse = await axios.get(
        `${config.services.backend.url}/api/v1/recommendations`,
        { 
          headers,
          timeout: 10000 
        }
      );
      
      console.log('Recommendations response:', recommendationsResponse.data);
      
      if (recommendationsResponse.data && recommendationsResponse.data.recommendations) {
        console.log('Setting recommendations:', recommendationsResponse.data.recommendations.length);
        setRecommendations(recommendationsResponse.data.recommendations);
      } else {
        console.error('No recommendations data in response:', recommendationsResponse.data);
        setError('No recommendation data was received. Please try again or contact support.');
      }
      
      // Fetch news
      const newsResponse = await axios.get(
        `${config.services.backend.url}/api/v1/news`,
        { 
          headers,
          timeout: 10000 
        }
      );
      
      if (newsResponse.data && newsResponse.data.news) {
        setNews(newsResponse.data.news);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
      }
      
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
  
  // Fetch recommendations and news on component mount
  useEffect(() => {
    fetchData();
  }, []);
  
  // Retry data fetch
  const handleRetry = () => {
    fetchData();
  };
  
  // Format date for display
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };
  
  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* App Bar */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Wells Fargo Financial Assistant
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Button 
              color="inherit"
              startIcon={<AttachMoneyOutlined />}
              onClick={() => navigate('/recommendations')}
            >
              View All Recommendations
            </Button>
            <IconButton color="inherit">
              <NotificationsOutlined />
            </IconButton>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
            >
              <AccountCircle />
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={handleClose}>Profile</MenuItem>
              <MenuItem onClick={handleClose}>My Account</MenuItem>
              <MenuItem onClick={handleLogout}>
                <ExitToAppOutlined sx={{ mr: 1 }} />
                Logout
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>
      
      {/* Main Content */}
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Welcome Section */}
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Welcome, {currentUser?.email || 'User'}
          </Typography>
          <Typography variant="body1" paragraph>
            Your personalized financial recommendations are ready. Our AI has analyzed your profile
            and prepared tailored suggestions to help you achieve your financial goals.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button 
              variant="contained" 
              color="primary"
              startIcon={<DashboardOutlined />}
              onClick={() => navigate('/dashboard')}
            >
              Dashboard
            </Button>
            <Button 
              variant="outlined"
              startIcon={<InsertChartOutlined />}
              onClick={() => navigate('/chat')}
            >
              Financial Chat
            </Button>
          </Box>
        </Paper>
        
        {/* Loading/Error State */}
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Paper sx={{ p: 3, mb: 4, bgcolor: 'error.light' }}>
            <Typography variant="h6" gutterBottom>
              Error Loading Data
            </Typography>
            <Typography variant="body1" paragraph>
              {error}
            </Typography>
            <Button 
              variant="contained" 
              color="primary"
              onClick={handleRetry}
            >
              Retry
            </Button>
          </Paper>
        ) : (
          <>
            {/* Recommendations Banner - with white background */}
            {recommendations.length > 0 && (
              <Paper sx={{ p: 3, mb: 4 }}>
                <Typography variant="h5" gutterBottom>
                  Top Recommendation
                </Typography>
                <RecommendationDisplay 
                  recommendationData={{ recommendations: [recommendations[0]] }} 
                  compact={false}
                />
              </Paper>
            )}
            
            {/* Recommendations Section */}
            <Typography variant="h5" gutterBottom>
              Your Top Recommendations
            </Typography>
            <Grid container spacing={3} sx={{ mb: 4 }}>
              {recommendations.length > 0 ? (
                recommendations.slice(0, 3).map((recommendation, index) => (
                  <Grid item xs={12} md={4} key={index}>
                    <RecommendationDisplay 
                      recommendationData={{ recommendations: [recommendation] }} 
                      compact={true}
                    />
                  </Grid>
                ))
              ) : (
                <Grid item xs={12}>
                  <Paper sx={{ p: 3, textAlign: 'center' }}>
                    <Typography variant="body1">
                      No recommendations available. Complete the onboarding chat to get personalized recommendations.
                    </Typography>
                  </Paper>
                </Grid>
              )}
            </Grid>
            
            {/* Financial News Section */}
            <Typography variant="h5" gutterBottom>
              Latest Financial News
            </Typography>
            <Grid container spacing={3}>
              {news.length > 0 ? (
                news.map((newsItem, index) => (
                  <Grid item xs={12} md={6} key={index}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          {newsItem.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" paragraph>
                          {newsItem.summary}
                        </Typography>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          {newsItem.date && (
                            <Typography variant="caption" color="text.secondary">
                              {formatDate(newsItem.date)}
                            </Typography>
                          )}
                          <Button size="small" color="primary">
                            Read More
                          </Button>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))
              ) : (
                <Grid item xs={12}>
                  <Paper sx={{ p: 3, textAlign: 'center' }}>
                    <Typography variant="body1">
                      No news articles available at this time.
                    </Typography>
                  </Paper>
                </Grid>
              )}
            </Grid>
          </>
        )}
      </Container>
    </Box>
  );
};

export default Dashboard;