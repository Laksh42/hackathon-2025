import React from 'react';
import { Box, Typography } from '@mui/material';
import ChatInterface from '../ChatInterface';
import { useNavigate } from 'react-router-dom';

const ChatPage = () => {
  const navigate = useNavigate();

  const handleChatComplete = (data) => {
    console.log('CHAT COMPLETED - Chat completed, redirecting with recommendation data');
    console.log('Recommendation data structure:', {
      hasData: !!data,
      dataType: typeof data,
      isArray: Array.isArray(data),
      dataKeys: data ? Object.keys(data) : []
    });
    
    try {
      // Validate the data structure
      if (!data || !data.recommendations) {
        console.error('Invalid recommendation data structure:', data);
      }
      
      // Store data in sessionStorage to pass between pages
      sessionStorage.setItem('recommendationData', JSON.stringify(data));
      console.log('Data successfully stored in sessionStorage');
      
      // Try also storing in localStorage as a backup
      try {
        localStorage.setItem('recommendationData', JSON.stringify(data));
        console.log('Data also stored in localStorage as backup');
      } catch (e) {
        console.log('Could not store in localStorage:', e);
      }
      
      // Redirect to the recommendations page
      console.log('About to navigate to /recommendations...');
      navigate('/recommendations');
      
      // Add a fallback direct navigation as backup
      setTimeout(() => {
        if (window.location.pathname !== '/recommendations') {
          console.log('React Router navigation may have failed, using direct navigation');
          window.location.href = '/recommendations';
        }
      }, 500);
    } catch (error) {
      console.error('Error in handleChatComplete:', error);
      alert('There was an error processing your data. Please try again.');
    }
  };

  return (
    <Box>
      <Typography variant="h4" align="center" gutterBottom>
        Let's Find the Right Financial Products for You
      </Typography>
      <Typography variant="subtitle1" align="center" color="text.secondary" sx={{ mb: 4 }}>
        Answer a few questions about your financial situation and goals, and we'll recommend the best products for you.
      </Typography>
      <ChatInterface onChatComplete={handleChatComplete} />
    </Box>
  );
};

export default ChatPage;