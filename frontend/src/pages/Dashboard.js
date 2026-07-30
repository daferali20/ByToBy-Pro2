import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  IconButton,
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  ShowChart,
  Timeline,
  Assessment,
  NotificationsActive,
  Refresh,
} from '@mui/icons-material';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
} from 'chart.js';
import { useQuery } from 'react-query';
import axios from 'axios';
import { format } from 'date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
);

const Dashboard = () => {
  const [marketData, setMarketData] = useState(null);
  const [portfolioData, setPortfolioData] = useState(null);
  const [watchlistData, setWatchlistData] = useState([]);
  const [alerts, setAlerts] = useState([]);

  // Fetch market data
  const { data: marketOverview, refetch: refetchMarket } = useQuery(
    'marketOverview',
    async () => {
      const response = await axios.get('/api/market/overview');
      return response.data;
    },
    {
      refetchInterval: 60000, // Refresh every minute
    }
  );

  // Fetch portfolio data
  const { data: portfolioOverview, refetch: refetchPortfolio } = useQuery(
    'portfolioOverview',
    async () => {
      const response = await axios.get('/api/portfolio/overview');
      return response.data;
    },
    {
      refetchInterval: 30000,
    }
  );

  // Fetch watchlist
  const { data: watchlist, refetch: refetchWatchlist } = useQuery(
    'watchlist',
    async () => {
      const response = await axios.get('/api/watchlist');
      return response.data;
    },
    {
      refetchInterval: 30000,
    }
  );

  // Fetch alerts
  const { data: recentAlerts, refetch: refetchAlerts } = useQuery(
    'recentAlerts',
    async () => {
      const response = await axios.get('/api/alerts/recent');
      return response.data;
    },
    {
      refetchInterval: 15000,
    }
  );

  // Chart configurations
  const portfolioChartData = {
    labels: ['Stocks', 'ETFs', 'Bonds', 'Crypto'],
    datasets: [
      {
        data: [40, 30, 20, 10],
        backgroundColor: ['#00b4d8', '#0077b6', '#00b894', '#fdcb6e'],
        borderWidth: 0,
      },
    ],
  };

  const performanceChartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Portfolio',
        data: [10000, 10500, 10200, 10800, 11200, 11500],
        borderColor: '#00b4d8',
        backgroundColor: 'rgba(0, 180, 216, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'S&P 500',
        data: [10000, 10200, 10100, 10500, 10700, 11000],
        borderColor: '#6c5ce7',
        backgroundColor: 'rgba(108, 92, 231, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const marketChartData = {
    labels: marketOverview?.indices?.map(i => i.symbol) || ['SPY', 'QQQ', 'DIA', 'IWM'],
    datasets: [
      {
        label: 'Performance',
        data: marketOverview?.indices?.map(i => i.change_percent) || [0.5, 1.2, -0.3, 0.8],
        backgroundColor: marketOverview?.indices?.map(i => 
          i.change_percent >= 0 ? '#00b894' : '#ff6b6b'
        ) || ['#00b894', '#00b894', '#ff6b6b', '#00b894'],
        borderRadius: 8,
      },
    ],
  };

  const StatCard = ({ title, value, change, icon, color }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 600 }}>
              {value}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
              {change && (
                <>
                  {change >= 0 ? (
                    <TrendingUp sx={{ color: 'success.main', fontSize: 16, mr: 0.5 }} />
                  ) : (
                    <TrendingDown sx={{ color: 'error.main', fontSize: 16, mr: 0.5 }} />
                  )}
                  <Typography
                    variant="body2"
                    sx={{
                      color: change >= 0 ? 'success.main' : 'error.main',
                      fontWeight: 600,
                    }}
                  >
                    {change >= 0 ? '+' : ''}{change}%
                  </Typography>
                </>
              )}
            </Box>
          </Box>
          <IconButton
            sx={{
              backgroundColor: `${color}20`,
              color: color,
              '&:hover': {
                backgroundColor: `${color}30`,
              },
            }}
          >
            {icon}
          </IconButton>
        </Box>
      </CardContent>
    </Card>
  );

  const WatchlistItem = ({ symbol, price, change }) => (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        py: 1,
        borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
        '&:last-child': {
          borderBottom: 'none',
        },
      }}
    >
      <Box>
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          {symbol}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          ${price?.toFixed(2) || '0.00'}
        </Typography>
      </Box>
      <Typography
        variant="body2"
        sx={{
          color: change >= 0 ? 'success.main' : 'error.main',
          fontWeight: 600,
        }}
      >
        {change >= 0 ? '+' : ''}{change?.toFixed(2) || '0.00'}%
      </Typography>
    </Box>
  );

  const AlertItem = ({ title, message, priority }) => (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        py: 1,
        borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
        '&:last-child': {
          borderBottom: 'none',
        },
      }}
    >
      <NotificationsActive
        sx={{
          color: priority === 'high' ? 'error.main' : 'warning.main',
          mr: 2,
          fontSize: 20,
        }}
      />
      <Box>
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
          {title}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {message}
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          Dashboard
        </Typography>
        <Box>
          <IconButton onClick={() => {
            refetchMarket();
            refetchPortfolio();
            refetchWatchlist();
            refetchAlerts();
          }}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Portfolio Value"
            value={`$${portfolioOverview?.total_value?.toLocaleString() || '0'}`}
            change={portfolioOverview?.daily_change || 0}
            icon={<AttachMoney />}
            color="#00b4d8"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Return"
            value={`${portfolioOverview?.total_return?.toFixed(1) || '0'}%`}
            change={portfolioOverview?.total_return || 0}
            icon={<TrendingUp />}
            color="#00b894"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Positions"
            value={portfolioOverview?.active_positions || 0}
            icon={<ShowChart />}
            color="#fdcb6e"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="AI Confidence Score"
            value={`${portfolioOverview?.ai_confidence?.toFixed(0) || 0}%`}
            icon={<Assessment />}
            color="#6c5ce7"
          />
        </Grid>
      </Grid>

      {/* Charts Grid */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Performance Overview
            </Typography>
            <Box sx={{ height: 300 }}>
              <Line
                data={performanceChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      labels: {
                        color: '#888',
                      },
                    },
                  },
                  scales: {
                    x: {
                      grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                      },
                      ticks: {
                        color: '#888',
                      },
                    },
                    y: {
                      grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                      },
                      ticks: {
                        color: '#888',
                      },
                    },
                  },
                }}
              />
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Portfolio Allocation
            </Typography>
            <Box sx={{ height: 250, display: 'flex', justifyContent: 'center' }}>
              <Doughnut
                data={portfolioChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom',
                      labels: {
                        color: '#888',
                        padding: 20,
                      },
                    },
                  },
                  cutout: '70%',
                }}
              />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Market and Watchlist Grid */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Market Overview
            </Typography>
            <Box sx={{ height: 200 }}>
              <Bar
                data={marketChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      display: false,
                    },
                  },
                  scales: {
                    x: {
                      grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                      },
                      ticks: {
                        color: '#888',
                      },
                    },
                    y: {
                      grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                      },
                      ticks: {
                        color: '#888',
                        callback: (value) => `${value}%`,
                      },
                    },
                  },
                }}
              />
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Watchlist
            </Typography>
            {watchlist?.slice(0, 5).map((stock) => (
              <WatchlistItem
                key={stock.symbol}
                symbol={stock.symbol}
                price={stock.price}
                change={stock.change_percent}
              />
            ))}
          </Paper>
        </Grid>
      </Grid>

      {/* Alerts */}
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
          Recent Alerts
        </Typography>
        {recentAlerts?.slice(0, 3).map((alert, index) => (
          <AlertItem
            key={index}
            title={alert.title}
            message={alert.message}
            priority={alert.priority}
          />
        ))}
      </Paper>
    </Box>
  );
};

export default Dashboard;
