import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

// Layout
import MainLayout from './components/Layout/MainLayout';
import ProtectedRoute from './components/Auth/ProtectedRoute';

// Pages
import Dashboard from './pages/Dashboard';
import Screener from './pages/Screener';
import Portfolio from './pages/Portfolio';
import Alerts from './pages/Alerts';
import AIAnalysis from './pages/AIAnalysis';
import Login from './pages/Login';
import Register from './pages/Register';
import StockDetail from './pages/StockDetail';

// Theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00b4d8',
    },
    secondary: {
      main: '#0077b6',
    },
    background: {
      default: '#0a0e17',
      paper: '#141b2d',
    },
    success: {
      main: '#00b894',
    },
    error: {
      main: '#ff6b6b',
    },
    warning: {
      main: '#fdcb6e',
    },
  },
  typography: {
    fontFamily: '"Inter", "Segoe UI", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          background: 'rgba(20, 27, 45, 0.8)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.05)',
        },
      },
    },
  },
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 300000, // 5 minutes
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            <Route path="/" element={<ProtectedRoute />}>
              <Route element={<MainLayout />}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/screener" element={<Screener />} />
                <Route path="/portfolio" element={<Portfolio />} />
                <Route path="/alerts" element={<Alerts />} />
                <Route path="/ai-analysis" element={<AIAnalysis />} />
                <Route path="/stocks/:symbol" element={<StockDetail />} />
              </Route>
            </Route>
          </Routes>
        </Router>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#141b2d',
              color: '#ffffff',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            },
            success: {
              iconTheme: {
                primary: '#00b894',
                secondary: '#ffffff',
              },
            },
            error: {
              iconTheme: {
                primary: '#ff6b6b',
                secondary: '#ffffff',
              },
            },
          }}
        />
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
