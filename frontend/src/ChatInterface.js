import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Box, 
  TextField, 
  Button, 
  Paper, 
  Typography, 
  IconButton, 
  Avatar,
  Divider,
  CircularProgress,
  Alert,
  Card,
  CardContent,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import AssistantIcon from '@mui/icons-material/Assistant';
import PersonIcon from '@mui/icons-material/Person';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import { ThemeProvider, createTheme } from '@mui/material/styles';

const ONBOARDING_QUESTIONS = [
  "Welcome to the Wells Fargo Financial Assistant! I'll help you discover financial products tailored to your needs. First, what's your annual income?",
  "What are your monthly expenses?",
  "How much do you have in savings?",
  "Do you have any specific financial goals? (e.g., buying a home, retirement, education)",
  "How would you describe your risk tolerance? (conservative, moderate, aggressive)",
  "Do you have any outstanding loans or debts? If so, please share the details.",
  "Thank you for sharing your information. Would you like to see personalized product recommendations based on your profile?"
];

const theme = createTheme({
  palette: {
    primary: {
      main: '#d71e28', // Wells Fargo red
    },
    secondary: {
      main: '#ffff00', // Wells Fargo yellow
    },
  },
});

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationComplete, setConversationComplete] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();
  
  // Start the conversation when component mounts
  useEffect(() => {
    addBotMessage(ONBOARDING_QUESTIONS[0]);
  }, []);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const addUserMessage = (text) => {
    console.log('Adding user message:', text);
    const newMessages = [...messages, { text, sender: 'user' }];
    setMessages(newMessages);
    return newMessages;
  };

  const addBotMessage = (text) => {
    console.log('Adding bot message:', text);
    setMessages(prev => [...prev, { text, sender: 'bot' }]);
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const updatedMessages = addUserMessage(input);
    setInput('');

    if (currentQuestion < ONBOARDING_QUESTIONS.length - 1) {
      // Move to next question
      setCurrentQuestion(prev => prev + 1);
      
      // Add a small delay before bot responds
      setTimeout(() => {
        addBotMessage(ONBOARDING_QUESTIONS[currentQuestion + 1]);
      }, 500);
    } else if (currentQuestion === ONBOARDING_QUESTIONS.length - 1) {
      // This is the final question in the onboarding process
      setConversationComplete(true);

      // Check if user wants to proceed with recommendations
      const userResponse = input.toLowerCase();
      if (userResponse.includes('yes') || userResponse.includes('sure') || userResponse.includes('ok')) {
        handleProcessRecommendations(updatedMessages);
      } else if (userResponse.includes('mock') || userResponse.includes('sample')) {
        // If user specifically asks for mock data
        navigate('/recommendations', { 
          state: { useMockData: true }
        });
      } else {
        addBotMessage("I understand you don't want recommendations right now. Feel free to restart the conversation whenever you're ready.");
        setConversationComplete(true);
      }
    }
  };

  const handleProcessRecommendations = async (updatedConversation) => {
    console.log('Preparing to get recommendations from API');
    setIsLoading(true);
    setError(null);

    // Extract just the text from the messages for the API request
    const conversationText = updatedConversation.map(msg => ({
      text: msg.text,
      sender: msg.sender
    }));

    console.log('Sending conversation to API:', conversationText);

    try {
      // Call the backend API with the conversation history
      const response = await axios.post('http://localhost:5050/api/chat', {
        conversation: conversationText
      }, {
        timeout: 10000 // 10 second timeout
      });

      console.log('API response received:', response.data);
      
      if (response.data) {
        // Navigate to recommendations page with the data
        navigate('/recommendations', { 
          state: { recommendations: response.data }
        });
      } else {
        throw new Error('API response is empty');
      }
    } catch (err) {
      console.error('Error getting recommendations:', err);
      
      let errorMessage = "Sorry, there was an error processing your request.";
      
      if (err.code === 'ECONNABORTED') {
        errorMessage = "Request timed out. The backend service might be unavailable.";
      } else if (err.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        errorMessage = `Server error: ${err.response.status} - ${err.response.data.message || err.response.statusText}`;
      } else if (err.request) {
        // The request was made but no response was received
        errorMessage = "No response from server. Please check your connection or try again later.";
      }
      
      setError(errorMessage);
      setIsLoading(false);
      addBotMessage(errorMessage);
    }
  };

  const handleRetry = () => {
    // Add a message indicating we're going to use mock data
    addBotMessage("Let me show you some sample recommendations instead.");
    
    // Navigate using mock data
    setTimeout(() => {
      navigate('/recommendations', { 
        state: { useMockData: true }
      });
    }, 1000);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const resetConversation = () => {
    console.log('Resetting conversation');
    setMessages([]);
    setCurrentQuestion(0);
    setConversationComplete(false);
    setIsLoading(false);
    setError(null);
    
    // Add a small delay before adding the first question
    setTimeout(() => {
      addBotMessage(ONBOARDING_QUESTIONS[0]);
    }, 200);
  };

  return (
    <ThemeProvider theme={theme}>
      <Paper 
        elevation={3} 
        sx={{ 
          maxWidth: 800, 
          mx: 'auto', 
          mt: 4, 
          height: 'calc(100vh - 100px)',
          display: 'flex',
          flexDirection: 'column',
          borderRadius: 2,
          overflow: 'hidden'
        }}
      >
        {/* Header */}
        <Box 
          sx={{ 
            p: 2, 
            bgcolor: 'primary.main', 
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <AssistantIcon sx={{ mr: 1 }} />
            <Typography variant="h6">
              Wells Fargo Financial Assistant
            </Typography>
          </Box>
          <IconButton 
            color="inherit" 
            onClick={resetConversation}
            title="Reset conversation"
          >
            <RestartAltIcon />
          </IconButton>
        </Box>
        
        <Divider />
        
        {/* Messages area */}
        <Box 
          sx={{ 
            p: 2, 
            flexGrow: 1, 
            overflow: 'auto',
            bgcolor: '#f5f5f5'
          }}
        >
          {messages.map((message, index) => (
            <Box 
              key={index} 
              sx={{ 
                display: 'flex', 
                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                mb: 2
              }}
            >
              <Card 
                elevation={1}
                sx={{ 
                  maxWidth: '80%', 
                  borderRadius: 2,
                  bgcolor: message.sender === 'user' ? 'primary.light' : 'white',
                  color: message.sender === 'user' ? 'white' : 'text.primary',
                }}
              >
                <CardContent sx={{ 
                  display: 'flex', 
                  alignItems: 'flex-start', 
                  p: 2, 
                  '&:last-child': { pb: 2 }
                }}>
                  {message.sender === 'bot' && (
                    <Avatar 
                      sx={{ 
                        bgcolor: 'primary.main', 
                        width: 32, 
                        height: 32, 
                        mr: 1
                      }}
                    >
                      <AssistantIcon fontSize="small" />
                    </Avatar>
                  )}
                  <Typography variant="body1" component="div" sx={{ whiteSpace: 'pre-wrap' }}>
                    {message.text}
                  </Typography>
                  {message.sender === 'user' && (
                    <Avatar 
                      sx={{ 
                        bgcolor: 'grey.700', 
                        width: 32, 
                        height: 32, 
                        ml: 1
                      }}
                    >
                      <PersonIcon fontSize="small" />
                    </Avatar>
                  )}
                </CardContent>
              </Card>
            </Box>
          ))}
          
          {isLoading && (
            <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                p: 2,
                flexDirection: 'column'
              }}
            >
              <CircularProgress size={40} thickness={4} />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Analyzing your financial profile...
              </Typography>
            </Box>
          )}
          
          {error && (
            <Alert 
              severity="error" 
              sx={{ mb: 2 }}
              action={
                <Button color="inherit" size="small" onClick={handleRetry}>
                  Try Sample Data
                </Button>
              }
            >
              {error}
            </Alert>
          )}
          
          <div ref={messagesEndRef} />
        </Box>
        
        <Divider />
        
        {/* Input area */}
        <Box 
          sx={{ 
            p: 2, 
            bgcolor: 'background.paper', 
            display: 'flex',
            alignItems: 'center'
          }}
        >
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading || conversationComplete}
            size="small"
            sx={{ mr: 1 }}
          />
          <Button
            variant="contained"
            color="primary"
            endIcon={<SendIcon />}
            onClick={handleSendMessage}
            disabled={!input.trim() || isLoading || conversationComplete}
          >
            Send
          </Button>
        </Box>
      </Paper>
    </ThemeProvider>
  );
};

export default ChatInterface;