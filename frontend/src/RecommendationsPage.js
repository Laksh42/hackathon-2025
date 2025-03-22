import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Box, CircularProgress, Container, Typography, Button } from '@mui/material';
import RecommendationDisplay from './RecommendationDisplay';
import { mockRecommendations, mockNews } from './mockData';

const RecommendationsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Get recommendations data passed from chat interface
  useEffect(() => {
    console.log('RecommendationsPage mounted, location state:', location.state);
    
    // Check if we have real data from the API
    if (location.state && location.state.recommendations) {
      console.log('Using real API recommendation data:', location.state.recommendations);
      setRecommendations(location.state.recommendations);
      setLoading(false);
    } 
    // Check if we're using mock data
    else if (location.state && location.state.useMockData) {
      console.log('Using mock recommendation data');
      // Small delay to simulate API call
      setTimeout(() => {
        const mockData = {
          recommendations: mockRecommendations,
          relevant_news: mockNews
        };
        setRecommendations(mockData);
        setLoading(false);
      }, 1500);
    } 
    // No data was provided
    else {
      console.log('No recommendation data available');
      setError('No recommendation data available. Please complete the onboarding chat first.');
      setLoading(false);
    }
  }, [location]);

  const handleReset = () => {
    console.log('Resetting chat and returning to home page');
    navigate('/', { replace: true });
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center', 
          justifyContent: 'center', 
          minHeight: '80vh'
        }}>
          <CircularProgress size={60} thickness={4} sx={{ mb: 3 }} />
          <Typography variant="h6" color="text.secondary">
            Generating your personalized recommendations...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center', 
          justifyContent: 'center', 
          minHeight: '80vh'
        }}>
          <Typography variant="h5" color="error" gutterBottom>
            {error}
          </Typography>
          <Button 
            variant="contained" 
            color="primary"
            onClick={handleReset}
          >
            Return to Chat
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <RecommendationDisplay 
        recommendationData={recommendations} 
        onReset={handleReset} 
      />
    </Container>
  );
};

export default RecommendationsPage;