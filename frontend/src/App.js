import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ChatPage from './pages/ChatPage';
import RecommendationsPage from './pages/RecommendationsPage';
import Layout from './components/Layout';
import ErrorBoundary from './ErrorBoundary';

// Create a custom theme with Wells Fargo colors
const theme = createTheme({
  palette: {
    primary: {
      main: '#D71E28', // Wells Fargo red
    },
    secondary: {
      main: '#FFBF3F', // Wells Fargo gold
    },
    background: {
      default: '#FFFFFF',
    },
  },
  typography: {
    fontFamily: '"Helvetica Neue", Arial, sans-serif',
    h4: {
      fontWeight: 700,
    },
    h5: {
      fontWeight: 600,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ErrorBoundary>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<ChatPage />} />
              <Route path="/recommendations" element={<RecommendationsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </ErrorBoundary>
    </ThemeProvider>
  );
}

export default App;