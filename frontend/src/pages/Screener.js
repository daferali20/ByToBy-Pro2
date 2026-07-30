import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Slider,
  Switch,
  FormControlLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  LinearProgress,
  Card,
  CardContent,
} from '@mui/material';
import {
  Search,
  FilterList,
  Download,
  Save,
  TrendingUp,
  TrendingDown,
  Star,
  StarBorder,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import axios from 'axios';

const Screener = () => {
  const [filters, setFilters] = useState({
    sector: '',
    marketCap: [0, 1000000000000],
    peRatio: [0, 100],
    dividendYield: [0, 10],
    priceChange: [0, 100],
    rsi: [0, 100],
    volume: 0,
    aiScore: [0, 100],
  });
  const [sortBy, setSortBy] = useState('marketCap');
  const [sortOrder, setSortOrder] = useState('desc');
  const [watchlist, setWatchlist] = useState(['AAPL', 'GOOGL']);

  // Fetch screener results
  const { data: screenerResults, isLoading } = useQuery(
    ['screener', filters, sortBy, sortOrder],
    async () => {
      const response = await axios.post('/api/screener/scan', {
        filters,
        sort_by: sortBy,
        sort_order: sortOrder,
        limit: 50,
      });
      return response.data;
    },
    {
      refetchInterval: 60000,
    }
  );

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };

  const toggleWatchlist = (symbol) => {
    if (watchlist.includes(symbol)) {
      setWatchlist(watchlist.filter(s => s !== symbol));
    } else {
      setWatchlist([...watchlist, symbol]);
    }
  };

  const getPriceColor = (change) => {
    if (change > 0) return 'success.main';
    if (change < 0) return 'error.main';
    return 'textSecondary';
  };

  const getRecommendationColor = (rec) => {
    if (rec === 'STRONG BUY') return 'success.main';
    if (rec === 'BUY') return 'success.light';
    if (rec === 'HOLD') return 'warning.main';
    if (rec === 'SELL') return 'error.light';
    if (rec === 'STRONG SELL') return 'error.main';
    return 'textSecondary';
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700 }}>
        Stock Screener
      </Typography>

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              placeholder="Search symbols..."
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'textSecondary' }} />,
              }}
              onChange={(e) => handleFilterChange('search', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Sector</InputLabel>
              <Select
                value={filters.sector}
                onChange={(e) => handleFilterChange('sector', e.target.value)}
              >
                <MenuItem value="">All Sectors</MenuItem>
                <MenuItem value="Technology">Technology</MenuItem>
                <MenuItem value="Healthcare">Healthcare</MenuItem>
                <MenuItem value="Finance">Finance</MenuItem>
                <MenuItem value="Energy">Energy</MenuItem>
                <MenuItem value="Consumer">Consumer</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <Typography variant="body2" gutterBottom>
              Market Cap (${filters.marketCap[0] / 1000000000}B - ${filters.marketCap[1] / 1000000000}B)
            </Typography>
            <Slider
              value={filters.marketCap}
              onChange={(e, value) => handleFilterChange('marketCap', value)}
              valueLabelDisplay="auto"
              min={0}
              max={1000000000000}
              step={1000000000}
              valueLabelFormat={(value) => `$${value / 1000000000}B`}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControlLabel
              control={
                <Switch
                  checked={filters.aiOptimized}
                  onChange={(e) => handleFilterChange('aiOptimized', e.target.checked)}
                />
              }
              label="AI Optimized"
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              variant="contained"
              fullWidth
              startIcon={<FilterList />}
              onClick={() => console.log('Apply filters')}
            >
              Apply Filters
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Results */}
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">
            Results: {screenerResults?.length || 0} stocks
          </Typography>
          <Box>
            <IconButton>
              <Save />
            </IconButton>
            <IconButton>
              <Download />
            </IconButton>
          </Box>
        </Box>

        {isLoading && <LinearProgress />}

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Watchlist</TableCell>
                <TableCell sortDirection={sortBy === 'symbol' ? sortOrder : false}>
                  <TableSortLabel
                    active={sortBy === 'symbol'}
                    direction={sortBy === 'symbol' ? sortOrder : 'asc'}
                    onClick={() => handleSort('symbol')}
                  >
                    Symbol
                  </TableSortLabel>
                </TableCell>
                <TableCell sortDirection={sortBy === 'name' ? sortOrder : false}>
                  <TableSortLabel
                    active={sortBy === 'name'}
                    direction={sortBy === 'name' ? sortOrder : 'asc'}
                    onClick={() => handleSort('name')}
                  >
                    Name
                  </TableSortLabel>
                </TableCell>
                <TableCell sortDirection={sortBy === 'price' ? sortOrder : false}>
                  <TableSortLabel
                    active={sortBy === 'price'}
                    direction={sortBy === 'price' ? sortOrder : 'asc'}
                    onClick={() => handleSort('price')}
                  >
                    Price
                  </TableSortLabel>
                </TableCell>
                <TableCell sortDirection={sortBy === 'change' ? sortOrder : false}>
                  <TableSortLabel
                    active={sortBy === 'change'}
                    direction={sortBy === 'change' ? sortOrder : 'asc'}
                    onClick={() => handleSort('change')}
                  >
                    Change
                  </TableSortLabel>
                </TableCell>
                <TableCell>Market Cap</TableCell>
                <TableCell>PE Ratio</TableCell>
                <TableCell>Dividend Yield</TableCell>
                <TableCell>RSI</TableCell>
                <TableCell>AI Score</TableCell>
                <TableCell>Recommendation</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {screenerResults?.map((stock) => (
                <TableRow
                  key={stock.symbol}
                  sx={{
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    },
                    cursor: 'pointer',
                  }}
                  onClick={() => window.location.href = `/stocks/${stock.symbol}`}
                >
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleWatchlist(stock.symbol);
                      }}
                    >
                      {watchlist.includes(stock.symbol) ? (
                        <Star sx={{ color: '#fdcb6e' }} />
                      ) : (
                        <StarBorder />
                      )}
                    </IconButton>
                  </TableCell>
                  <TableCell>
                    <Typography sx={{ fontWeight: 600 }}>
                      {stock.symbol}
                    </Typography>
                  </TableCell>
                  <TableCell>{stock.name}</TableCell>
                  <TableCell>
                    <Typography sx={{ fontWeight: 600 }}>
                      ${stock.price?.toFixed(2)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography sx={{ color: getPriceColor(stock.change) }}>
                      {stock.change > 0 ? '+' : ''}{stock.change?.toFixed(2)}%
                    </Typography>
                  </TableCell>
                  <TableCell>
                    ${(stock.marketCap / 1000000000)?.toFixed(1)}B
                  </TableCell>
                  <TableCell>{stock.peRatio?.toFixed(2)}</TableCell>
                  <TableCell>
                    {stock.dividendYield?.toFixed(2)}%
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={stock.rsi?.toFixed(0)}
                      size="small"
                      color={stock.rsi > 70 ? 'error' : stock.rsi < 30 ? 'success' : 'default'}
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <LinearProgress
                        variant="determinate"
                        value={stock.aiScore * 100}
                        sx={{
                          width: 60,
                          mr: 1,
                          height: 8,
                          borderRadius: 4,
                        }}
                      />
                      <Typography>
                        {(stock.aiScore * 100)?.toFixed(0)}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={stock.recommendation}
                      size="small"
                      sx={{
                        color: getRecommendationColor(stock.recommendation),
                        borderColor: getRecommendationColor(stock.recommendation),
                      }}
                      variant="outlined"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default Screener;
