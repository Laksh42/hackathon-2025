import React, { useState, useRef, useEffect } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Paper, 
  List, 
  ListItem, 
  Divider, 
  Grid,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Alert,
  Checkbox,
  FormControlLabel
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import axios from 'axios';
import { mockRecommendations, mockNews } from './mockData';

// API URL (would be set in .env in production)
const API_URL = 'http://localhost:5050/api';

// Pre-defined bot questions for onboarding
const BOT_QUESTIONS = [
  {
    id: 'welcome',
    content: "Welcome to Wells Fargo's Financial Assistant! I'll help you discover personalized financial products based on your needs. Let's start with a few questions about your financial situation.",
    required: false
  },
  {
    id: 'income',
    content: "What's your approximate annual income?",
    required: true
  },
  {
    id: 'expenses',
    content: "How much do you typically spend per month on expenses?",
    required: true
  },
  {
    id: 'savings',
    content: "How much do you have in savings currently?",
    required: true
  },
  {
    id: 'financial_goals',
    content: "What are your main financial goals? (e.g., retirement, home purchase, education, etc.)",
    required: true
  },
  {
    id: 'risk_appetite',
    content: "How would you describe your risk tolerance for investments? (conservative, moderate, or aggressive)",
    required: true
  },
  {
    id: 'debt',
    content: "Do you have any outstanding debt such as student loans, credit cards, or mortgages?",
    required: true
  },
  {
    id: 'final',
    content: "Thank you for sharing that information. I'll analyze your financial profile to find the best product recommendations for you.",
    required: false
  }
];

const steps = ['Basic Info', 'Financial Goals', 'Risk Profile', 'Analysis'];

const ChatInterface = ({ onChatComplete }) => {
  const [messages, setMessages] = useState([]);
  const [currentInput, setCurrentInput] = useState('');
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [error, setError] = useState(null);
  const [useMockData, setUseMockData] = useState(false);
  
  const messagesEndRef = useRef(null);

  // Initialize with the first bot message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([{
        role: 'bot',
        content: BOT_QUESTIONS[0].content
      }]);
      setCurrentQuestion(1); // Move to first actual question
    }
  }, [messages]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleInputChange = (e) => {
    setCurrentInput(e.target.value);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!currentInput.trim()) return;
    
    // Add user message to chat
    const newUserMessage = {
      role: 'user',
      content: currentInput
    };
    
    console.log(`DEBUG: Adding user message. Current question: ${currentQuestion}/${BOT_QUESTIONS.length}`);
    
    setMessages(prevMessages => [...prevMessages, newUserMessage]);
    setCurrentInput('');
    
    // Important: For the last actual question (debt), we need to show the final message and then process
    if (currentQuestion === 7) { // This is the debt question (index 6) + 1
      console.log(`DEBUG: This was the last question with user input needed`);
      
      // Add final message
      const finalMessage = {
        role: 'bot',
        content: BOT_QUESTIONS[7].content // Final thank you message
      };
      
      // Add the final message and then process the chat
      setMessages(prevMessages => {
        const updatedMessages = [...prevMessages, finalMessage];
        console.log(`DEBUG: Added final thank you message, now processing chat...`);
        
        // Schedule chat processing after state update
        setTimeout(() => {
          processCompletedChat();
        }, 1000);
        
        return updatedMessages;
      });
      
      setActiveStep(3); // Final step
      setCurrentQuestion(8); // Move past the end of questions
      
    } 
    // For other questions, continue the normal flow
    else if (currentQuestion < BOT_QUESTIONS.length) {
      // Add next bot question
      const nextBotMessage = {
        role: 'bot',
        content: BOT_QUESTIONS[currentQuestion].content
      };
      
      setTimeout(() => {
        console.log(`DEBUG: Adding bot question ${currentQuestion}: "${BOT_QUESTIONS[currentQuestion].content}"`);
        setMessages(prevMessages => [...prevMessages, nextBotMessage]);
        
        // Update stepper
        if (currentQuestion === 1) setActiveStep(1);
        else if (currentQuestion === 4) setActiveStep(2);
        else if (currentQuestion === 6) setActiveStep(3);
        
        console.log(`DEBUG: Incrementing question from ${currentQuestion} to ${currentQuestion + 1}`);
        setCurrentQuestion(currentQuestion + 1);
        
        // IMPORTANT: Check if this was the second-to-last question, and if so, log that the next one will be the final
        if (currentQuestion + 1 === BOT_QUESTIONS.length - 1) {
          console.log(`DEBUG: Next question will be the final one. After that, processCompletedChat should run.`);
        }
      }, 500);
    } else {
      // This should rarely be reached with the new logic above
      console.log(`DEBUG: Reached final question. currentQuestion=${currentQuestion}, BOT_QUESTIONS.length=${BOT_QUESTIONS.length}`);
      console.log(`DEBUG: Processing completed chat now...`);
      await processCompletedChat();
    }
  };

  const processCompletedChat = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Add a loading message
      setMessages(prevMessages => [
        ...prevMessages, 
        { 
          role: 'bot', 
          content: 'Analyzing your financial profile and generating recommendations...' 
        }
      ]);
      
      // If using mock data, simulate a delay and return mock recommendations
      if (useMockData) {
        console.log('Using mock data instead of API call');
        
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Import the ready-to-use mock response
        const mockResponse = {
          recommendations: mockRecommendations,
          relevant_news: mockNews
        };
        
        console.log('Mock API Response:', mockResponse);
        
        // Add a final message indicating redirect is about to happen
        setMessages(prevMessages => [
          ...prevMessages, 
          { 
            role: 'bot', 
            content: 'Great! I have your personalized recommendations ready. Redirecting you now...' 
          }
        ]);
        
        // Short delay before redirect
        setTimeout(() => {
          console.log("REDIRECTING with mock data:", mockResponse);
          onChatComplete(mockResponse);
          // Add fallback direct navigation after a brief delay
          setTimeout(() => {
            console.log("Checking if still on same page, attempting direct redirect");
            if (window.location.pathname !== '/recommendations') {
              window.location.href = '/recommendations';
            }
          }, 1500);
        }, 1000);
        
        return;
      }
      
      // Debug: Log all messages being sent to API
      console.log('Sending messages to API:', messages);
      
      // Create a complete set of messages including the last user input
      const completeMessages = messages;
      
      // Send the entire conversation to the API with a timeout
      console.log('Sending POST request to:', `${API_URL}/chat`);
      try {
        const response = await axios.post(`${API_URL}/chat`, {
          messages: completeMessages
        }, {
          timeout: 10000 // 10 second timeout
        });
        
        // Debug: Log API response
        console.log('API Response received:', response.data);
        
        // Check if response contains expected data
        if (!response.data) {
          throw new Error('Empty response from server');
        }
        
        // Add a final message indicating redirect is about to happen
        setMessages(prevMessages => [
          ...prevMessages, 
          { 
            role: 'bot', 
            content: 'Great! I have your personalized recommendations ready. Redirecting you to the results page...' 
          }
        ]);
        
        // Short delay before redirect
        setTimeout(() => {
          console.log("REDIRECTING with API data:", response.data);
          onChatComplete(response.data);
          // Add fallback direct navigation after a brief delay
          setTimeout(() => {
            console.log("Checking if still on same page, attempting direct redirect");
            if (window.location.pathname !== '/recommendations') {
              window.location.href = '/recommendations';
            }
          }, 1500);
        }, 1000);
        
      } catch (axiosError) {
        console.error('Axios error details:', axiosError);
        if (axiosError.response) {
          console.error('Response status:', axiosError.response.status);
          console.error('Response data:', axiosError.response.data);
        }
        throw axiosError; // rethrow to be caught by outer try/catch
      }
      
    } catch (error) {
      console.error('Error processing chat:', error);
      
      let errorMessage = 'Sorry, there was an error processing your information. Please try again.';
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'The request timed out. Please ensure all backend services are running.';
      } else if (error.response && error.response.data && error.response.data.error) {
        errorMessage = `Error: ${error.response.data.error}`;
      }
      
      setError(errorMessage);
      
      // Add error message to chat
      setMessages(prevMessages => [
        ...prevMessages, 
        { 
          role: 'bot', 
          content: errorMessage
        }
      ]);
      
      // Allow retry
      setCurrentQuestion(BOT_QUESTIONS.length - 1);
      
    } finally {
      setIsLoading(false);
    }
  };

  // Function to handle a manual retry
  const handleRetry = async () => {
    await processCompletedChat();
  };
  
  // Function to use mock data instead
  const handleUseMockData = () => {
    setUseMockData(!useMockData);
  };

  return (
    <Box>
      <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
          <Box sx={{ mt: 1 }}>
            <FormControlLabel
              control={
                <Checkbox 
                  checked={useMockData}
                  onChange={handleUseMockData}
                  size="small"
                />
              }
              label="Use sample data instead (Demo mode)"
            />
          </Box>
        </Alert>
      )}
      
      <Box sx={{ height: 400, overflow: 'auto', mb: 2, p: 2, bgcolor: '#f9f9f9', borderRadius: 1 }}>
        <List>
          {messages.map((message, index) => (
            <React.Fragment key={index}>
              <ListItem alignItems="flex-start" sx={{ 
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                mb: 1 
              }}>
                <Paper 
                  elevation={1} 
                  sx={{ 
                    p: 2, 
                    maxWidth: '75%',
                    bgcolor: message.role === 'user' ? '#e3f2fd' : '#ffffff',
                    borderRadius: message.role === 'user' ? '20px 20px 0 20px' : '20px 20px 20px 0',
                  }}
                >
                  <Typography variant="body1">
                    {message.content}
                  </Typography>
                </Paper>
              </ListItem>
              {index < messages.length - 1 && <Divider component="li" />}
            </React.Fragment>
          ))}
          <div ref={messagesEndRef} />
        </List>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        {!error && (
          <FormControlLabel
            control={
              <Checkbox 
                checked={useMockData}
                onChange={handleUseMockData}
                size="small"
              />
            }
            label="Use sample data (Demo mode)"
          />
        )}
        
        {currentQuestion >= 7 && (
          <Button 
            color="secondary" 
            variant="contained" 
            onClick={() => {
              console.log("DEBUG: Mock data button clicked");
              setUseMockData(true);
              processCompletedChat();
            }}
            sx={{ ml: 'auto' }}
          >
            Generate Sample Recommendations
          </Button>
        )}
      </Box>

      <Box component="form" onSubmit={handleSendMessage} sx={{ display: 'flex' }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your response here..."
          value={currentInput}
          onChange={handleInputChange}
          disabled={isLoading || currentQuestion >= BOT_QUESTIONS.length}
          sx={{ mr: 1 }}
        />
        <Button 
          variant="contained" 
          color="primary" 
          type="submit"
          disabled={isLoading || currentQuestion >= BOT_QUESTIONS.length || !currentInput.trim()}
          endIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
        >
          Send
        </Button>
        
        {currentQuestion >= BOT_QUESTIONS.length && error && (
          <Button 
            variant="outlined" 
            color="secondary"
            onClick={handleRetry}
            disabled={isLoading}
            sx={{ ml: 1 }}
          >
            Retry
          </Button>
        )}
      </Box>
    </Box>
  );
};

export default ChatInterface;