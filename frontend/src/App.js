import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import ChatInterface from './components/ChatInterface';
import RecommendationsPage from './pages/RecommendationsPage';
import { config } from './config';

// Create a custom theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#D41B2C', // Wells Fargo red
      light: '#FF4F5E',
      dark: '#A30000',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#FFCD34', // Wells Fargo yellow
      light: '#FFF176',
      dark: '#C79A00',
      contrastText: '#000000',
    },
    background: {
      default: '#F5F5F5',
    },
  },
  typography: {
    fontFamily: [
      'Open Sans',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontWeight: 600,
    },
    h2: {
      fontWeight: 600,
    },
    h3: {
      fontWeight: 600,
    },
    h4: {
      fontWeight: 500,
    },
    h5: {
      fontWeight: 500,
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* Protected Routes */}
            <Route element={<PrivateRoute />}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/recommendations" element={<RecommendationsPage />} />
              <Route 
                path="/chat" 
                element={<ChatInterface isOnboarding={true} />} 
              />
            </Route>
            
            {/* Redirect home to login or dashboard based on auth state */}
            <Route 
              path="/" 
              element={
                localStorage.getItem(config.auth.tokenKey) ? 
                <Navigate to="/dashboard" replace /> : 
                <Navigate to="/login" replace />
              } 
            />
            
            {/* Catch-all route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;