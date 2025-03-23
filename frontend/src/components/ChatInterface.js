import React, { useState, useEffect, useRef } from 'react';
import { 
  Container, 
  Paper, 
  Typography, 
  TextField, 
  Button, 
  Box, 
  CircularProgress, 
  Alert,
  Divider,
  Card,
  CardContent,
  Grid,
  AppBar,
  Toolbar,
  IconButton
} from '@mui/material';
import { 
  Send as SendIcon, 
  ArrowBack as ArrowBackIcon,
  AutoAwesome as AutoAwesomeIcon
} from '@mui/icons-material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { config } from '../config';
import { useAuth } from '../contexts/AuthContext';

const ChatInterface = ({ isOnboarding = false }) => {
  // State for chat messages
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const [userPersona, setUserPersona] = useState(null);
  
  // Reference for auto-scrolling to bottom
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();
  const { saveUserPersona } = useAuth();

  // Initialize chat with welcome message
  useEffect(() => {
    // Load existing session or start new one
    const savedSession = sessionStorage.getItem(config.chat.sessionStorageKey);
    
    if (savedSession) {
      try {
        const parsedSession = JSON.parse(savedSession);
        setMessages(parsedSession.messages || []);
        setSessionId(parsedSession.sessionId || '');
        setIsComplete(parsedSession.isComplete || false);
      } catch (e) {
        console.error('Error parsing saved session:', e);
        initializeChat();
      }
    } else {
      initializeChat();
    }
  }, []);

  // Function to initialize a new chat
  const initializeChat = async () => {
    // Clear previous state
    setMessages([]);
    setSessionId('');
    setIsComplete(false);
    setError('');
    
    // Add initial welcome message
    const welcomeMessage = {
      text: config.chat.welcomeMessage,
      sender: 'bot',
      timestamp: new Date().toISOString()
    };
    
    setMessages([welcomeMessage]);
    
    try {
      // Get a new session ID from the understander service
      const response = await axios.post(
        `${config.services.understander.url}/api/v1/understand`,
        {
          message: 'Hello',
          session_id: null
        },
        { timeout: 10000 }
      );
      
      if (response.data && response.data.session_id) {
        setSessionId(response.data.session_id);
        
        // Add the bot's first question
        if (response.data.text) {
          setMessages(prevMessages => [
            ...prevMessages,
            {
              text: response.data.text,
              sender: 'bot',
              timestamp: new Date().toISOString()
            }
          ]);
        }
        
        // Save to session storage
        saveToSessionStorage(
          [welcomeMessage, {
            text: response.data.text,
            sender: 'bot',
            timestamp: new Date().toISOString()
          }],
          response.data.session_id,
          false
        );
      }
    } catch (error) {
      console.error('Error initializing chat:', error);
      setError('Failed to initialize chat. Please try again.');
    }
  };

  // Save chat session to session storage
  const saveToSessionStorage = (messages, sessionId, isComplete) => {
    const sessionData = {
      messages,
      sessionId,
      isComplete,
      lastUpdated: new Date().toISOString()
    };
    
    sessionStorage.setItem(config.chat.sessionStorageKey, JSON.stringify(sessionData));
  };

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle sending a message
  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    // Add user message to chat
    const userMessage = {
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInputMessage('');
    setLoading(true);
    setError('');
    
    try {
      // Send message to understander service
      const response = await axios.post(
        `${config.services.understander.url}/api/v1/understand`,
        {
          message: inputMessage,
          session_id: sessionId
        },
        { timeout: 15000 }
      );
      
      // Debug logging
      if (config.debug.logApiCalls) {
        console.log('Understand API Response:', response.data);
      }
      
      // Update session ID if needed
      if (response.data && response.data.session_id) {
        setSessionId(response.data.session_id);
      }
      
      // Add bot response to chat
      if (response.data && response.data.text) {
        // Add a slight delay to make the conversation feel more natural
        setTimeout(() => {
          const botMessage = {
            text: response.data.text,
            sender: 'bot',
            timestamp: new Date().toISOString()
          };
          
          setMessages(prevMessages => [...prevMessages, botMessage]);
          
          // Check if dialogue is complete
          if (response.data.state && response.data.state.is_complete) {
            setIsComplete(true);
            
            // Extract user persona
            extractUserPersona(response.data.session_id);
          }
          
          // Save updated chat to session storage
          saveToSessionStorage(
            [...messages, userMessage, botMessage],
            response.data.session_id,
            response.data.state?.is_complete || false
          );
        }, config.chat.aiResponseDelay);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      if (error.response && error.response.data && error.response.data.error) {
        setError(error.response.data.error);
      } else if (error.code === 'ECONNABORTED') {
        setError('Connection timeout. Please try again.');
      } else {
        setError('Failed to send message. Please try again.');
      }
      
      // When in development, generate a mock response
      if (config.features.enableMockData) {
        setTimeout(() => {
          const mockResponse = {
            text: "I'm having trouble connecting to the server. How else can I help you today?",
            sender: 'bot',
            timestamp: new Date().toISOString()
          };
          
          setMessages(prevMessages => [...prevMessages, mockResponse]);
        }, config.chat.aiResponseDelay);
      }
    } finally {
      setLoading(false);
    }
  };

  // Extract user persona from dialogue history
  const extractUserPersona = async (sid) => {
    console.log('Extracting user persona for session:', sid || sessionId);
    try {
      const response = await axios.post(
        `${config.services.understander.url}/api/v1/user/profile`,
        {
          session_id: sid || sessionId
        },
        { timeout: 10000 }
      );
      
      console.log('User profile API response:', response.data);
      
      if (response.data) {
        console.log('Setting user persona:', response.data);
        setUserPersona(response.data);
        return response.data;
      } else {
        console.error('No data in profile response');
        setError('Unable to create your financial profile. Please try again.');
        return null;
      }
    } catch (error) {
      console.error('Error extracting user persona:', error);
      setError('Failed to create your financial profile. Please try again.');
      return null;
    }
  };

  // Handle completing the onboarding
  const handleCompleteOnboarding = async () => {
    console.log('Complete onboarding called, userPersona:', userPersona);
    
    try {
      // If userPersona is null, try to extract it again
      let persona = userPersona;
      if (!persona) {
        console.log('No user persona available, attempting to extract again');
        persona = await extractUserPersona(sessionId);
        
        if (!persona) {
          console.error('Failed to extract user persona');
          setError('Unable to create your financial profile. Please try again.');
          return;
        }
      }
      
      console.log('Completing onboarding with persona:', persona);
      
      // Make sure persona is saved
      const result = await saveUserPersona(persona);
      
      if (result && result.success) {
        console.log('Successfully saved persona, navigating to dashboard');
        // Navigate to recommendations page
        navigate('/dashboard');
      } else {
        console.error('Failed to save persona:', result);
        setError('Failed to save your profile. Please try again.');
      }
    } catch (error) {
      console.error('Error completing onboarding:', error);
      setError('Failed to complete onboarding. Please try again.');
    }
  };

  // Handle key press (Enter to send)
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Handle retrying if there was an error
  const handleRetry = () => {
    setError('');
    // The last message would be the user's, so we try to resend it
    if (messages.length > 0 && messages[messages.length - 1].sender === 'user') {
      setInputMessage(messages[messages.length - 1].text);
      // Remove the last message since we're retrying it
      setMessages(prevMessages => prevMessages.slice(0, -1));
    }
  };

  // Reset the chat
  const handleResetChat = () => {
    // Clear session storage
    sessionStorage.removeItem(config.chat.sessionStorageKey);
    
    // Reinitialize chat
    initializeChat();
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar position="static">
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => navigate(-1)}
            sx={{ mr: 2 }}
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {isOnboarding ? 'Financial Profile Onboarding' : 'Financial Assistant Chat'}
          </Typography>
          {!isOnboarding && (
            <Button 
              color="inherit"
              onClick={() => navigate('/dashboard')}
            >
              Dashboard
            </Button>
          )}
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ flex: 1, display: 'flex', flexDirection: 'column', py: 4 }}>
        {/* Information card for onboarding */}
        {isOnboarding && (
          <Card sx={{ mb: 3, bgcolor: 'primary.light', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <AutoAwesomeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Welcome to Your Financial Profile Setup
              </Typography>
              <Typography variant="body2">
                I'll ask you a few questions to understand your financial situation and goals.
                This helps me provide personalized recommendations tailored to your needs.
                Your information is kept secure and will only be used to improve your experience.
              </Typography>
            </CardContent>
          </Card>
        )}

        {/* Chat area */}
        <Paper
          elevation={3}
          sx={{
            p: 2,
            display: 'flex',
            flexDirection: 'column',
            height: '60vh',
            overflow: 'hidden',
            flex: 1,
            mb: 2
          }}
        >
          {/* Messages container */}
          <Box
            sx={{
              flex: 1,
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              p: 1
            }}
          >
            {messages.map((message, index) => (
              <Box
                key={index}
                sx={{
                  maxWidth: '70%',
                  alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start',
                  mb: 2
                }}
              >
                <Paper
                  elevation={1}
                  sx={{
                    p: 2,
                    backgroundColor: message.sender === 'user' ? 'primary.main' : 'grey.100',
                    color: message.sender === 'user' ? 'white' : 'text.primary',
                    borderRadius: message.sender === 'user' ? '20px 20px 5px 20px' : '20px 20px 20px 5px'
                  }}
                >
                  <Typography variant="body1">{message.text}</Typography>
                </Paper>
                <Typography
                  variant="caption"
                  sx={{
                    display: 'block',
                    textAlign: message.sender === 'user' ? 'right' : 'left',
                    mt: 0.5,
                    color: 'text.secondary'
                  }}
                >
                  {message.sender === 'user' ? 'You' : 'Financial Assistant'} •{' '}
                  {new Date(message.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </Typography>
              </Box>
            ))}
            <div ref={messagesEndRef} />
            
            {/* Loading indicator */}
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                <CircularProgress size={24} />
              </Box>
            )}
          </Box>

          {/* Error message */}
          {error && (
            <Alert 
              severity="error" 
              sx={{ mb: 2 }}
              action={
                <Button color="inherit" size="small" onClick={handleRetry}>
                  Retry
                </Button>
              }
            >
              {error}
            </Alert>
          )}

          {/* Input area */}
          <Divider sx={{ my: 2 }} />
          {!isComplete ? (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Type your message..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={loading}
                sx={{ mr: 1 }}
              />
              <Button
                variant="contained"
                color="primary"
                endIcon={<SendIcon />}
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || loading}
              >
                Send
              </Button>
            </Box>
          ) : (
            // Onboarding complete actions
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                Thank you for sharing your financial information!
              </Typography>
              <Typography variant="body2" paragraph>
                I've analyzed your profile and have personalized recommendations ready for you.
              </Typography>
              <Grid container spacing={2} justifyContent="center">
                <Grid item>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleCompleteOnboarding}
                  >
                    View My Dashboard
                  </Button>
                </Grid>
                <Grid item>
                  <Button
                    variant="outlined"
                    onClick={handleResetChat}
                  >
                    Start Over
                  </Button>
                </Grid>
              </Grid>
            </Box>
          )}
        </Paper>
      </Container>
    </Box>
  );
};

export default ChatInterface;