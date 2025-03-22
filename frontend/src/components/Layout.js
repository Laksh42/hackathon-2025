import React from 'react';
import { AppBar, Toolbar, Typography, Box, Button, Container } from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import { useTheme } from '@mui/material/styles';

const Layout = ({ children }) => {
  const theme = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  
  const isRecommendationsPage = location.pathname === '/recommendations';

  return (
    <div className="App">
      <AppBar position="static" color="default" elevation={0}>
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
            <Typography 
              variant="h6" 
              component="div" 
              sx={{ 
                color: theme.palette.primary.main,
                fontWeight: 'bold',
                mr: 2,
                cursor: 'pointer'
              }}
              onClick={() => navigate('/')}
            >
              WELLS FARGO
            </Typography>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
              Financial Assistant
            </Typography>
            {isRecommendationsPage && (
              <Button 
                color="primary" 
                variant="outlined"
                onClick={() => navigate('/')}
              >
                New Recommendation
              </Button>
            )}
          </Box>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
        {children}
      </Container>
      
      <Box 
        component="footer" 
        sx={{ 
          py: 3, 
          bgcolor: '#f5f5f5', 
          textAlign: 'center',
          mt: 'auto',
          position: 'fixed',
          bottom: 0,
          width: '100%'
        }}
      >
        <Typography variant="body2" color="text.secondary">
          © {new Date().getFullYear()} Wells Fargo. All rights reserved.
        </Typography>
      </Box>
    </div>
  );
};

export default Layout;