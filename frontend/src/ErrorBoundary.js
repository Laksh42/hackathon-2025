import React, { Component } from 'react';
import { Box, Typography, Button, Alert } from '@mui/material';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // You can also log the error to an error reporting service
    console.error("React Error Boundary caught an error:", error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReset = () => {
    // Reset the error state
    this.setState({ hasError: false, error: null, errorInfo: null });
    
    // Reload the page as a last resort
    window.location.reload();
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <Alert severity="error" sx={{ mb: 3 }}>
            Something went wrong with the application.
          </Alert>

          <Typography variant="h5" sx={{ mb: 2 }}>
            We apologize for the inconvenience
          </Typography>
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            The application encountered an unexpected error. You can try reloading the page.
          </Typography>
          
          <Button 
            variant="contained" 
            color="primary" 
            onClick={this.handleReset}
            sx={{ mr: 2 }}
          >
            Reload Application
          </Button>
          
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <Box sx={{ mt: 4, textAlign: 'left', bgcolor: '#f5f5f5', p: 2, borderRadius: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Error Details (Development Only):
              </Typography>
              <Typography variant="body2" component="pre" sx={{ overflow: 'auto' }}>
                {this.state.error.toString()}
              </Typography>
              {this.state.errorInfo && (
                <Typography variant="body2" component="pre" sx={{ overflow: 'auto', mt: 2 }}>
                  {this.state.errorInfo.componentStack}
                </Typography>
              )}
            </Box>
          )}
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;