import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import yfinance as yf
import ta
from loguru import logger

class AIService:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.load_model()
    
    def load_model(self):
        """Load pre-trained model or initialize new one"""
        try:
            self.model = joblib.load('models/stock_predictor.pkl')
            logger.info("AI model loaded successfully")
        except:
            logger.warning("No pre-trained model found, initializing new model")
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
    
    def predict(self, symbol: str) -> Dict[str, Any]:
        """Make AI prediction for a stock"""
        try:
            # Get historical data
            stock = yf.Ticker(symbol)
            data = stock.history(period="2y")
            
            if data.empty:
                return {'price': 0, 'confidence': 0, 'recommendation': 'HOLD'}
            
            # Calculate features
            features = self._calculate_features(data)
            
            if features is None or len(features) == 0:
                return {'price': 0, 'confidence': 0, 'recommendation': 'HOLD'}
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Make prediction
            if self.model:
                prediction = self.model.predict(features_scaled[-1:])
                confidence = self._calculate_confidence(features_scaled)
                
                current_price = data['Close'].iloc[-1]
                predicted_return = (prediction[0] / current_price - 1) * 100
                
                return {
                    'price': float(prediction[0]),
                    'current_price': float(current_price),
                    'predicted_return': float(predicted_return),
                    'confidence': float(confidence),
                    'recommendation': self._get_recommendation(predicted_return, confidence),
                    'target_low': float(prediction[0] * 0.95),
                    'target_high': float(prediction[0] * 1.05)
                }
            
            return {'price': 0, 'confidence': 0, 'recommendation': 'HOLD'}
        except Exception as e:
            logger.error(f"Error making prediction for {symbol}: {e}")
            return {'price': 0, 'confidence': 0, 'recommendation': 'HOLD'}
    
    def _calculate_features(self, data: pd.DataFrame) -> np.ndarray:
        """Calculate technical features for prediction"""
        try:
            features = pd.DataFrame()
            
            # Price features
            features['close'] = data['Close']
            features['volume'] = data['Volume']
            
            # Returns
            features['return_1d'] = data['Close'].pct_change()
            features['return_5d'] = data['Close'].pct_change(periods=5)
            features['return_20d'] = data['Close'].pct_change(periods=20)
            
            # Technical indicators
            features['rsi'] = ta.momentum.rsi(data['Close'], window=14)
            features['macd'] = ta.trend.MACD(data['Close']).macd()
            features['sma_20'] = ta.trend.sma_indicator(data['Close'], window=20)
            features['sma_50'] = ta.trend.sma_indicator(data['Close'], window=50)
            
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(data['Close'], window=20)
            features['bb_high'] = bb.bollinger_hband()
            features['bb_low'] = bb.bollinger_lband()
            features['bb_mid'] = bb.bollinger_mavg()
            
            # Volume features
            features['volume_sma'] = data['Volume'].rolling(20).mean()
            features['volume_ratio'] = data['Volume'] / features['volume_sma']
            
            # Drop NaN values
            features = features.dropna()
            
            return features.values
        except Exception as e:
            logger.error(f"Error calculating features: {e}")
            return None
    
    def _calculate_confidence(self, features: np.ndarray) -> float:
        """Calculate confidence score for prediction"""
        try:
            # Use ensemble of estimators for confidence
            if hasattr(self.model, 'estimators_'):
                predictions = []
                for estimator in self.model.estimators_[:10]:  # Use 10 trees
                    pred = estimator.predict(features[-1:])
                    predictions.append(pred[0])
                
                # Confidence based on standard deviation of predictions
                if predictions:
                    mean_pred = np.mean(predictions)
                    std_pred = np.std(predictions)
                    confidence = 1 - (std_pred / (abs(mean_pred) + 0.01))
                    confidence = min(max(confidence, 0), 1)
                    return float(confidence)
            
            return 0.5
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _get_recommendation(self, predicted_return: float, confidence: float) -> str:
        """Get recommendation based on prediction and confidence"""
        if confidence > 0.8:
            if predicted_return > 10:
                return "STRONG BUY"
            elif predicted_return > 5:
                return "BUY"
            elif predicted_return < -10:
                return "STRONG SELL"
            elif predicted_return < -5:
                return "SELL"
        elif confidence > 0.6:
            if predicted_return > 10:
                return "BUY"
            elif predicted_return < -10:
                return "SELL"
        
        return "HOLD"
    
    def get_score(self, symbol: str) -> float:
        """Get AI score for a stock (0-100)"""
        try:
            prediction = self.predict(symbol)
            if prediction['confidence'] > 0.5:
                # Combine confidence and predicted return
                score = prediction['confidence'] * 100
                if prediction['predicted_return'] > 0:
                    score += min(prediction['predicted_return'] * 2, 20)
                else:
                    score += max(prediction['predicted_return'] * 2, -20)
                return max(0, min(score, 100))
            return 0
        except:
            return 0
    
    def get_recommendations(self, symbols: Optional[List[str]] = None) -> List[Dict]:
        """Get recommendations for multiple stocks"""
        if symbols is None:
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM']
        
        recommendations = []
        for symbol in symbols:
            pred = self.predict(symbol)
            recommendations.append({
                'Symbol': symbol,
                'Price': pred.get('current_price', 0),
                'Target': pred.get('price', 0),
                'Return %': pred.get('predicted_return', 0),
                'Confidence': pred.get('confidence', 0) * 100,
                'Action': pred.get('recommendation', 'HOLD')
            })
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x['Confidence'], reverse=True)
        return recommendations
    
    def get_overall_confidence(self) -> float:
        """Get overall AI confidence across all stocks"""
        try:
            recommendations = self.get_recommendations()
            if recommendations:
                avg_confidence = np.mean([r['Confidence'] for r in recommendations])
                return avg_confidence
            return 50
        except:
            return 50
