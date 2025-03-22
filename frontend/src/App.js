import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Box, AppBar, Toolbar, Typography, Container } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import ChatInterface from './ChatInterface';
import RecommendationsPage from './RecommendationsPage';

// Wells Fargo theme colors
const theme = createTheme({
  palette: {
    primary: {
      main: '#d71e28', // Wells Fargo red
    },
    secondary: {
      main: '#ffff00', // Wells Fargo yellow
    },
  },
  typography: {
    fontFamily: [
      'Helvetica Neue',
      'Arial',
      'sans-serif'
    ].join(','),
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Box sx={{ flexGrow: 1 }}>
          <AppBar position="static">
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Wells Fargo Financial Assistant
              </Typography>
            </Toolbar>
          </AppBar>
          <Container>
            <Routes>
              <Route path="/" element={<ChatInterface />} />
              <Route path="/recommendations" element={<RecommendationsPage />} />
            </Routes>
          </Container>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;