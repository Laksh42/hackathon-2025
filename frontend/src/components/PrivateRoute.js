import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { CircularProgress, Box } from '@mui/material';

// Component for routes that require authentication
const PrivateRoute = ({ redirectPath = '/login' }) => {
  const { isAuthenticated, loading } = useAuth();

  // Show loading spinner while checking authentication status
  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to={redirectPath} replace />;
  }

  // Render the protected component
  return <Outlet />;
};

export default PrivateRoute;