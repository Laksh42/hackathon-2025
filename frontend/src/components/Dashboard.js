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
  Avatar
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
import RecommendationDisplay from './RecommendationDisplay';

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
  
  // Fetch recommendations and news
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError('');
        
        // Fetch recommendations
        const recommendationsResponse = await axios.get(
          `${config.services.backend.url}/api/v1/recommendations`,
          { timeout: 10000 }
        );
        
        if (recommendationsResponse.data && recommendationsResponse.data.recommendations) {
          setRecommendations(recommendationsResponse.data.recommendations);
        }
        
        // Fetch news
        const newsResponse = await axios.get(
          `${config.services.backend.url}/api/v1/news`,
          { timeout: 10000 }
        );
        
        if (newsResponse.data && newsResponse.data.news) {
          setNews(newsResponse.data.news);
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        
        if (error.response && error.response.data && error.response.data.error) {
          setError(error.response.data.error);
        } else if (error.code === 'ECONNABORTED') {
          setError('Connection timeout. Please try again later.');
        } else {
          setError('An error occurred. Please try again later.');
        }
        
        // If in development, use mock data
        if (config.features.enableMockData) {
          import('../mockData').then(mockData => {
            setRecommendations(mockData.mockRecommendations);
            setNews(mockData.mockNews);
            setError('');
          });
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  // Retry data fetch
  const handleRetry = () => {
    setLoading(true);
    setError('');
    
    // Re-run the effect
    useEffect(() => {}, []);
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
            {/* Recommendations Section */}
            <Typography variant="h5" gutterBottom>
              Your Top Recommendations
            </Typography>
            <Grid container spacing={3} sx={{ mb: 4 }}>
              {recommendations.length > 0 ? (
                recommendations.slice(0, 3).map((recommendation, index) => (
                  <Grid item xs={12} md={4} key={index}>
                    <RecommendationDisplay recommendation={recommendation} compact={true} />
                  </Grid>
                ))
              ) : (
                <Grid item xs={12}>
                  <Paper sx={{ p: 3, textAlign: 'center' }}>
                    <Typography variant="body1">
                      No recommendations available. Complete the onboarding chat to get personalized recommendations.
                    </Typography>
                    <Button 
                      variant="contained" 
                      color="primary"
                      sx={{ mt: 2 }}
                      onClick={() => navigate('/chat')}
                    >
                      Start Chat
                    </Button>
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