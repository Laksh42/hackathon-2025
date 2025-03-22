import React from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  CardActions, 
  Button, 
  Grid, 
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import LocalOfferIcon from '@mui/icons-material/LocalOffer';
import NewspaperIcon from '@mui/icons-material/Newspaper';

const RecommendationDisplay = ({ recommendationData, onReset }) => {
  // Add debugging to see what data we're receiving
  console.log('RecommendationDisplay received data structure:', {
    hasData: !!recommendationData,
    hasRecommendations: recommendationData?.recommendations ? true : false,
    recommendationsCount: recommendationData?.recommendations?.length || 0,
    hasNews: recommendationData?.relevant_news ? true : false,
    newsCount: recommendationData?.relevant_news?.length || 0,
    dataKeys: recommendationData ? Object.keys(recommendationData) : []
  });

  if (recommendationData) {
    console.log('First recommendation (if exists):', 
      recommendationData.recommendations && recommendationData.recommendations[0] 
        ? recommendationData.recommendations[0] : 'None available');
  }

  // Handle null or undefined data
  if (!recommendationData) {
    return (
      <Box sx={{ mt: 4, p: 3, textAlign: 'center' }}>
        <Alert severity="warning" sx={{ mb: 3 }}>
          No recommendation data was received. Please try again or contact support.
        </Alert>
        <Button variant="contained" color="primary" onClick={onReset}>
          Start New Assessment
        </Button>
      </Box>
    );
  }

  // Fix the destructuring to handle different data structures
  // Check both convention styles: recommendations vs recommendation (singular)
  const recommendations = recommendationData.recommendations || 
                         recommendationData.recommendation || 
                         [];
  
  const relevant_news = recommendationData.relevant_news || 
                        recommendationData.relevantNews || 
                        recommendationData.news || 
                        [];

  // Handle empty recommendations
  if (!recommendations || recommendations.length === 0) {
    return (
      <Box sx={{ mt: 4, p: 3, textAlign: 'center' }}>
        <Alert severity="info" sx={{ mb: 3 }}>
          Based on your profile, we couldn't find any recommendations at this time. Please update your information or speak with a financial advisor.
        </Alert>
        <Button variant="contained" color="primary" onClick={onReset}>
          Start New Assessment
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom align="center" color="primary" fontWeight="bold">
        Your Personalized Recommendations
      </Typography>
      
      <Typography variant="subtitle1" gutterBottom align="center" color="text.secondary" sx={{ mb: 4 }}>
        Based on your financial profile, we recommend the following products:
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 5 }}>
        {recommendations.map((recommendation, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Card 
              elevation={3} 
              sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: 6,
                },
                border: index === 0 ? '2px solid #2e7d32' : 'none',
                position: 'relative'
              }}
            >
              {index === 0 && (
                <Chip 
                  icon={<CheckCircleIcon />} 
                  label="Best Match" 
                  color="success" 
                  sx={{ 
                    position: 'absolute',
                    top: 10,
                    right: 10,
                  }}
                />
              )}
              
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h5" component="div" gutterBottom color="primary">
                  {recommendation.product?.name || 'Product Name Missing'}
                </Typography>
                
                <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                  Match Score: {Math.round((recommendation.confidence || recommendation.confidence_score) * 100)}%
                </Typography>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {recommendation.product?.description || 'No description available'}
                </Typography>
                
                <Typography variant="h6" gutterBottom sx={{ mt: 3, fontWeight: 'bold' }}>
                  <LocalOfferIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                  Features
                </Typography>
                
                <List dense>
                  {recommendation.product?.features ? 
                    recommendation.product.features.map((feature, idx) => (
                      <ListItem key={idx} disablePadding>
                        <ListItemText primary={feature} />
                      </ListItem>
                    )) : 
                    <ListItem disablePadding>
                      <ListItemText primary="Feature information not available" />
                    </ListItem>
                  }
                </List>
                
                <Typography variant="h6" gutterBottom sx={{ mt: 3, fontWeight: 'bold' }}>
                  <InfoIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                  Why This Recommendation
                </Typography>
                
                <Typography variant="body2" color="text.secondary">
                  {recommendation.explanation || 'No explanation available'}
                </Typography>
              </CardContent>
              
              <CardActions sx={{ p: 2, pt: 0 }}>
                <Button 
                  variant="contained" 
                  color="primary" 
                  fullWidth
                  onClick={() => window.open('https://www.wellsfargo.com', '_blank')}
                >
                  Learn More
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      {relevant_news && relevant_news.length > 0 && (
        <Box sx={{ mt: 5, mb: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <NewspaperIcon sx={{ mr: 1 }} />
            Relevant Financial News
          </Typography>
          <Divider sx={{ mb: 3 }} />
          
          <Grid container spacing={3}>
            {relevant_news.map((news, index) => (
              <Grid item xs={12} sm={6} key={index}>
                <Card elevation={2}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {news.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {news.summary}
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button 
                      size="small" 
                      color="primary"
                      onClick={() => window.open('https://www.reuters.com/finance', '_blank')}
                    >
                      Read Full Article
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
      
      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Button variant="outlined" color="primary" onClick={onReset} size="large">
          Start New Assessment
        </Button>
        <Typography variant="caption" display="block" sx={{ mt: 2, color: 'text.secondary' }}>
          These recommendations are based on the information you provided and are not financial advice.
          Please consult with a Wells Fargo financial advisor for personalized guidance.
        </Typography>
      </Box>
    </Box>
  );
};

export default RecommendationDisplay;