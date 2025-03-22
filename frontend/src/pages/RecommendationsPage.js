import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, Alert } from '@mui/material';
import RecommendationDisplay from '../RecommendationDisplay';
import { useNavigate } from 'react-router-dom';

const RecommendationsPage = () => {
  const [recommendationData, setRecommendationData] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    console.log("RecommendationsPage mounted");
    
    // Get data from sessionStorage
    const storedData = sessionStorage.getItem('recommendationData');
    console.log("Session storage data retrieved:", storedData ? "Found data" : "No data found");
    
    if (storedData) {
      try {
        const parsedData = JSON.parse(storedData);
        console.log('Retrieved recommendation data details:', parsedData);
        
        // Validate data structure
        if (!parsedData.recommendations) {
          console.error("Missing recommendations in parsed data");
          setError("The recommendation data is incomplete. Try redoing the chat.");
        }
        
        setRecommendationData(parsedData);
      } catch (error) {
        console.error('Error parsing recommendation data:', error);
        setError("There was an error processing your recommendations. Please try again.");
      }
    } else {
      // If no data is found, redirect back to chat
      console.warn('No recommendation data found, redirecting to chat');
      setError("No recommendation data was found. You'll be redirected to start a new chat.");
      
      // Set a timeout before redirecting to allow error to be displayed
      setTimeout(() => {
        navigate('/');
      }, 2000);
    }
    
    // For testing - Try to access data directly from localStorage as well
    try {
      const localData = localStorage.getItem('recommendationData');
      console.log("LocalStorage check:", localData ? "Found data in localStorage" : "No data in localStorage");
    } catch (e) {
      console.log("LocalStorage check failed:", e);
    }
  }, [navigate]);

  const handleReset = () => {
    // Clear stored data and navigate back to chat page
    console.log("Reset requested, clearing data and navigating to chat");
    sessionStorage.removeItem('recommendationData');
    navigate('/');
  };

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {recommendationData ? (
        <RecommendationDisplay 
          recommendationData={recommendationData} 
          onReset={handleReset} 
        />
      ) : (
        <Box sx={{ textAlign: 'center', my: 4 }}>
          <Typography variant="h6" gutterBottom>
            {error ? "Redirecting..." : "Loading recommendations..."}
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={() => navigate('/')}
            sx={{ mt: 2 }}
          >
            Return to Chat
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default RecommendationsPage;