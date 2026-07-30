import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import yfinance as yf
import ta
from loguru import logger
import warnings
import os
import pickle
warnings.filterwarnings('ignore')

class AIService:
    def __init__(self):
        """Initialize the AI Service with model and scaler"""
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = None
        self.model_path = 'models/stock_predictor.pkl'
        self.scaler_path = 'models/scaler.pkl'
        self.features_path = 'models/features.pkl'
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        self.load_model()
    
    def load_model(self):
        """Load pre-trained model or initialize new one"""
        try:
            # Try to load model, scaler, and features
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                
                if os.path.exists(self.features_path):
                    with open(self.features_path, 'rb') as f:
                        self.feature_columns = pickle.load(f)
                
                self.is_trained = True
                logger.info("✅ AI model loaded successfully")
            else:
                logger.warning("⚠️ No pre-trained model found, initializing new model")
                self._initialize_model()
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize a new model"""
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1  # Use all CPU cores
        )
        self.is_trained = False
        logger.info("🆕 New model initialized (untrained)")
    
    def _calculate_features(self, data: pd.DataFrame) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Calculate technical features for prediction"""
        try:
            if data.empty or len(data) < 50:
                logger.warning("⚠️ Insufficient data for feature calculation")
                return None
            
            features = pd.DataFrame(index=data.index)
            
            # === PRICE FEATURES ===
            features['close'] = data['Close']
            features['high'] = data['High']
            features['low'] = data['Low']
            features['volume'] = data['Volume']
            
            # Price ratios
            features['high_low_ratio'] = data['High'] / data['Low']
            features['close_high_ratio'] = data['Close'] / data['High']
            features['close_low_ratio'] = data['Close'] / data['Low']
            
            # === RETURNS ===
            for period in [1, 5, 10, 20]:
                features[f'return_{period}d'] = data['Close'].pct_change(periods=period) * 100
            
            # === TECHNICAL INDICATORS ===
            
            # RSI
            try:
                features['rsi'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
            except Exception as e:
                logger.debug(f"RSI calculation error: {e}")
                features['rsi'] = 50
            
            # MACD
            try:
                macd = ta.trend.MACD(data['Close'])
                features['macd'] = macd.macd()
                features['macd_signal'] = macd.macd_signal()
                features['macd_diff'] = macd.macd_diff()
            except Exception as e:
                logger.debug(f"MACD calculation error: {e}")
                features['macd'] = 0
                features['macd_signal'] = 0
                features['macd_diff'] = 0
            
            # Moving Averages
            try:
                for period in [20, 50, 200]:
                    if len(data) >= period:
                        features[f'sma_{period}'] = ta.trend.sma_indicator(data['Close'], window=period)
                    else:
                        features[f'sma_{period}'] = data['Close'].mean()
            except Exception as e:
                logger.debug(f"SMA calculation error: {e}")
                for period in [20, 50, 200]:
                    features[f'sma_{period}'] = data['Close'].mean()
            
            # Exponential Moving Averages
            try:
                for period in [12, 26]:
                    features[f'ema_{period}'] = ta.trend.ema_indicator(data['Close'], window=period)
            except Exception as e:
                logger.debug(f"EMA calculation error: {e}")
                for period in [12, 26]:
                    features[f'ema_{period}'] = data['Close'].mean()
            
            # Bollinger Bands
            try:
                bb = ta.volatility.BollingerBands(data['Close'], window=20, window_dev=2)
                features['bb_high'] = bb.bollinger_hband()
                features['bb_low'] = bb.bollinger_lband()
                features['bb_mid'] = bb.bollinger_mavg()
                features['bb_width'] = bb.bollinger_wband()
                features['bb_position'] = (data['Close'] - features['bb_low']) / (features['bb_high'] - features['bb_low'] + 1e-8)
            except Exception as e:
                logger.debug(f"Bollinger Bands calculation error: {e}")
                features['bb_high'] = data['Close'].max()
                features['bb_low'] = data['Close'].min()
                features['bb_mid'] = data['Close'].mean()
                features['bb_width'] = 0
                features['bb_position'] = 0.5
            
            # Volume indicators
            try:
                features['volume_sma'] = data['Volume'].rolling(window=20).mean()
                features['volume_ratio'] = data['Volume'] / (features['volume_sma'] + 1e-8)
                features['volume_trend'] = data['Volume'].rolling(window=10).mean() / (data['Volume'].rolling(window=30).mean() + 1e-8)
            except Exception as e:
                logger.debug(f"Volume indicators calculation error: {e}")
                features['volume_sma'] = data['Volume'].mean()
                features['volume_ratio'] = 1
                features['volume_trend'] = 1
            
            # Momentum
            try:
                features['momentum'] = ta.momentum.roc(data['Close'], window=12)
                features['stoch_k'] = ta.momentum.stochrsi_k(data['Close'], window=14, smooth1=3)
                features['stoch_d'] = ta.momentum.stochrsi_d(data['Close'], window=14, smooth1=3, smooth2=3)
            except Exception as e:
                logger.debug(f"Momentum indicators calculation error: {e}")
                features['momentum'] = 0
                features['stoch_k'] = 50
                features['stoch_d'] = 50
            
            # Volatility
            try:
                features['volatility'] = data['Close'].rolling(window=20).std()
                features['volatility_ratio'] = features['volatility'] / (features['volatility'].rolling(window=60).mean() + 1e-8)
            except Exception as e:
                logger.debug(f"Volatility calculation error: {e}")
                features['volatility'] = data['Close'].std()
                features['volatility_ratio'] = 1
            
            # Average True Range (ATR)
            try:
                features['atr'] = ta.volatility.average_true_range(data['High'], data['Low'], data['Close'], window=14)
            except Exception as e:
                logger.debug(f"ATR calculation error: {e}")
                features['atr'] = data['Close'].std()
            
            # Price position relative to moving averages
            for period in [20, 50]:
                if f'sma_{period}' in features.columns:
                    features[f'price_to_sma_{period}'] = data['Close'] / (features[f'sma_{period}'] + 1e-8)
            
            # Trend strength
            features['trend_strength'] = abs(features['macd'] - features['macd_signal']) / (features['volatility'] + 1e-8)
            
            # === TARGET VARIABLE ===
            # Next day return
            features['target'] = data['Close'].shift(-1) / data['Close'] - 1
            
            # Drop NaN values
            features = features.dropna()
            
            if features.empty:
                logger.warning("⚠️ All features dropped (NaN values)")
                return None
            
            # Store feature columns for consistency
            if self.feature_columns is None:
                self.feature_columns = [col for col in features.columns if col != 'target']
            
            # Separate features and target
            X = features[self.feature_columns].values
            y = features['target'].values
            
            # Check if we have enough data
            if len(X) < 10:
                logger.warning("⚠️ Insufficient data after cleaning")
                return None
            
            return X, y
            
        except Exception as e:
            logger.error(f"❌ Error calculating features: {e}")
            return None
    
    def train_model(self, symbols: List[str] = None, force_retrain: bool = False) -> bool:
        """Train the model on historical data"""
        if symbols is None:
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'VTI', 'SPY']
        
        if self.is_trained and not force_retrain:
            logger.info("ℹ️ Model already trained, use force_retrain=True to retrain")
            return True
        
        logger.info(f"🔄 Training AI model on {len(symbols)} stocks...")
        
        all_features = []
        all_targets = []
        
        for symbol in symbols:
            try:
                logger.info(f"  📊 Processing {symbol}...")
                stock = yf.Ticker(symbol)
                data = stock.history(period="2y")
                
                if data.empty:
                    logger.warning(f"  ⚠️ No data for {symbol}")
                    continue
                
                result = self._calculate_features(data)
                if result is None:
                    continue
                
                X, y = result
                all_features.append(X)
                all_targets.append(y)
                
            except Exception as e:
                logger.error(f"  ❌ Error processing {symbol}: {e}")
                continue
        
        if not all_features:
            logger.error("❌ No training data available")
            return False
        
        # Combine all data
        X_combined = np.vstack(all_features)
        y_combined = np.concatenate(all_targets)
        
        logger.info(f"📊 Training data shape: {X_combined.shape}")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_combined)
        
        # Train model
        try:
            self.model.fit(X_scaled, y_combined)
            self.is_trained = True
            
            # Save model and scaler
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            # Save feature columns
            with open(self.features_path, 'wb') as f:
                pickle.dump(self.feature_columns, f)
            
            # Calculate and log model performance
            train_score = self.model.score(X_scaled, y_combined)
            logger.info(f"✅ Model trained successfully! R² Score: {train_score:.4f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error training model: {e}")
            return False
    
    def predict(self, symbol: str) -> Dict[str, Any]:
        """Make AI prediction for a stock"""
        try:
            # Check if model is trained
            if not self.is_trained:
                logger.warning("⚠️ Model not trained, training now...")
                self.train_model()
                if not self.is_trained:
                    return self._get_default_prediction()
            
            # Get historical data
            stock = yf.Ticker(symbol)
            data = stock.history(period="2y")
            
            if data.empty or len(data) < 50:
                logger.warning(f"⚠️ Insufficient data for {symbol}")
                return self._get_default_prediction()
            
            # Calculate features
            result = self._calculate_features(data)
            if result is None:
                return self._get_default_prediction()
            
            X, _ = result
            
            # Check if we have features
            if len(X) == 0:
                return self._get_default_prediction()
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Get predictions for each time step
            predictions = self.model.predict(X_scaled)
            
            # Use the most recent prediction
            latest_prediction = predictions[-1] if len(predictions) > 0 else 0
            
            # Calculate confidence
            confidence = self._calculate_confidence(X_scaled[-1:])
            
            current_price = data['Close'].iloc[-1]
            predicted_price = current_price * (1 + latest_prediction)
            predicted_return = latest_prediction * 100
            
            # Get price targets
            target_low = predicted_price * 0.95
            target_high = predicted_price * 1.05
            
            # Determine time horizon
            time_horizon = "1 Day"
            if abs(predicted_return) < 2:
                time_horizon = "1 Week"
            
            # Get recommendation
            recommendation = self._get_recommendation(predicted_return, confidence)
            
            # Get score
            score = self._calculate_score(predicted_return, confidence, recommendation)
            
            return {
                'price': float(predicted_price),
                'current_price': float(current_price),
                'predicted_return': float(predicted_return),
                'confidence': float(confidence),
                'score': float(score),
                'recommendation': recommendation,
                'target_low': float(target_low),
                'target_high': float(target_high),
                'time_horizon': time_horizon,
                'model_version': '2.0.0',
                'symbol': symbol,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error making prediction for {symbol}: {e}")
            return self._get_default_prediction()
    
    def _get_default_prediction(self) -> Dict[str, Any]:
        """Return default prediction when data is insufficient"""
        return {
            'price': 0,
            'current_price': 0,
            'predicted_return': 0,
            'confidence': 0,
            'score': 50,
            'recommendation': 'HOLD',
            'target_low': 0,
            'target_high': 0,
            'time_horizon': 'N/A',
            'model_version': '2.0.0',
            'symbol': 'N/A',
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_confidence(self, features: np.ndarray) -> float:
        """Calculate confidence score for prediction"""
        try:
            if not hasattr(self.model, 'estimators_'):
                return 0.5
            
            # Get predictions from all trees
            predictions = []
            for estimator in self.model.estimators_[:20]:  # Use 20 trees
                try:
                    pred = estimator.predict(features)
                    predictions.append(pred[0])
                except:
                    continue
            
            if not predictions:
                return 0.5
            
            # Calculate confidence based on prediction consistency
            mean_pred = np.mean(predictions)
            std_pred = np.std(predictions)
            
            # Higher confidence when predictions are consistent (low std)
            if abs(mean_pred) > 0.01:
                confidence = 1 - (std_pred / (abs(mean_pred) + 0.01))
            else:
                confidence = 1 - std_pred
            
            confidence = np.clip(confidence, 0, 1)
            
            # Additional confidence factors
            # 1. Number of trees used
            tree_factor = min(len(predictions) / 20, 1)
            
            # 2. Out-of-bag score if available
            if hasattr(self.model, 'oob_score_'):
                oob_factor = self.model.oob_score_
            else:
                oob_factor = 0.5
            
            # Combine factors
            final_confidence = confidence * 0.6 + tree_factor * 0.2 + oob_factor * 0.2
            
            return float(np.clip(final_confidence, 0, 1))
            
        except Exception as e:
            logger.error(f"❌ Error calculating confidence: {e}")
            return 0.5
    
    def _get_recommendation(self, predicted_return: float, confidence: float) -> str:
        """Get recommendation based on prediction and confidence"""
        # Strong signals with high confidence
        if confidence > 0.8:
            if predicted_return > 15:
                return "STRONG BUY"
            elif predicted_return > 8:
                return "BUY"
            elif predicted_return < -15:
                return "STRONG SELL"
            elif predicted_return < -8:
                return "SELL"
            elif predicted_return > 3:
                return "OUTPERFORM"
            elif predicted_return < -3:
                return "UNDERPERFORM"
        
        # Moderate signals
        if confidence > 0.6:
            if predicted_return > 12:
                return "BUY"
            elif predicted_return < -12:
                return "SELL"
            elif predicted_return > 5:
                return "OUTPERFORM"
            elif predicted_return < -5:
                return "UNDERPERFORM"
        
        # Neutral
        return "HOLD"
    
    def _calculate_score(self, predicted_return: float, confidence: float, recommendation: str) -> float:
        """Calculate AI score (0-100)"""
        try:
            # Base score from confidence
            score = confidence * 100
            
            # Adjust based on prediction
            if predicted_return > 0:
                score += min(predicted_return * 2, 20)
            else:
                score += max(predicted_return * 2, -20)
            
            # Recommendation bonus
            rec_bonus = {
                'STRONG BUY': 15,
                'BUY': 10,
                'OUTPERFORM': 5,
                'HOLD': 0,
                'UNDERPERFORM': -5,
                'SELL': -10,
                'STRONG SELL': -15
            }
            score += rec_bonus.get(recommendation, 0)
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"❌ Error calculating score: {e}")
            return 50
    
    def get_score(self, symbol: str) -> float:
        """Get AI score for a stock (0-100)"""
        try:
            prediction = self.predict(symbol)
            return prediction.get('score', 50)
        except Exception as e:
            logger.error(f"❌ Error getting score for {symbol}: {e}")
            return 50
    
    def get_recommendations(self, symbols: Optional[List[str]] = None) -> List[Dict]:
        """Get recommendations for multiple stocks"""
        if symbols is None:
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'VTI', 'SPY']
        
        recommendations = []
        for symbol in symbols:
            try:
                pred = self.predict(symbol)
                if pred['price'] > 0:
                    recommendations.append({
                        'Symbol': symbol,
                        'Price': pred.get('current_price', 0),
                        'Target': pred.get('price', 0),
                        'Return %': pred.get('predicted_return', 0),
                        'Confidence': pred.get('confidence', 0) * 100,
                        'Score': pred.get('score', 50),
                        'Action': pred.get('recommendation', 'HOLD'),
                        'Time Horizon': pred.get('time_horizon', 'N/A')
                    })
            except Exception as e:
                logger.error(f"❌ Error getting recommendation for {symbol}: {e}")
                continue
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x['Confidence'], reverse=True)
        return recommendations
    
    def get_overall_confidence(self) -> float:
        """Get overall AI confidence across all stocks"""
        try:
            recommendations = self.get_recommendations()
            if recommendations:
                confidences = [r['Confidence'] for r in recommendations if r['Confidence'] > 0]
                if confidences:
                    avg_confidence = np.mean(confidences)
                    return float(avg_confidence)
            return 50.0
        except Exception as e:
            logger.error(f"❌ Error getting overall confidence: {e}")
            return 50.0
    
    def get_best_picks(self, limit: int = 5) -> List[Dict]:
        """Get the best AI picks"""
        try:
            recommendations = self.get_recommendations()
            # Filter for BUY recommendations
            buys = [r for r in recommendations if 'BUY' in r['Action']]
            # Sort by score
            buys.sort(key=lambda x: x['Score'], reverse=True)
            return buys[:limit]
        except Exception as e:
            logger.error(f"❌ Error getting best picks: {e}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        info = {
            'is_trained': self.is_trained,
            'model_type': 'RandomForestRegressor',
            'feature_count': len(self.feature_columns) if self.feature_columns else 0,
            'model_path': self.model_path,
            'scaler_path': self.scaler_path,
            'features_path': self.features_path
        }
        
        if self.is_trained and hasattr(self.model, 'n_estimators'):
            info.update({
                'n_estimators': self.model.n_estimators,
                'max_depth': self.model.max_depth,
                'min_samples_split': self.model.min_samples_split,
                'n_features': self.model.n_features_in_ if hasattr(self.model, 'n_features_in_') else 0
            })
            
            # Calculate feature importance if available
            if hasattr(self.model, 'feature_importances_') and self.feature_columns:
                importances = self.model.feature_importances_
                top_features = sorted(
                    zip(self.feature_columns[:len(importances)], importances),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
                info['top_features'] = top_features
        
        return info
    
    def save_model(self, path: str = None) -> bool:
        """Save the current model to disk"""
        try:
            if path is None:
                path = self.model_path
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            joblib.dump(self.model, path)
            joblib.dump(self.scaler, self.scaler_path)
            
            if self.feature_columns is not None:
                with open(self.features_path, 'wb') as f:
                    pickle.dump(self.feature_columns, f)
            
            logger.info(f"✅ Model saved to {path}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving model: {e}")
            return False
    
    def load_model_from_path(self, model_path: str, scaler_path: str = None, features_path: str = None) -> bool:
        """Load model from custom paths"""
        try:
            self.model = joblib.load(model_path)
            
            if scaler_path and os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
            
            if features_path and os.path.exists(features_path):
                with open(features_path, 'rb') as f:
                    self.feature_columns = pickle.load(f)
            
            self.is_trained = True
            logger.info(f"✅ Model loaded from {model_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Error loading model from path: {e}")
            return False
    
    def evaluate_model(self, test_symbols: List[str] = None) -> Dict[str, Any]:
        """Evaluate model performance on test data"""
        if test_symbols is None:
            test_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
        
        if not self.is_trained:
            logger.warning("⚠️ Model not trained, cannot evaluate")
            return {'error': 'Model not trained'}
        
        results = {
            'predictions': [],
            'accuracy': 0,
            'mean_error': 0,
            'rmse': 0
        }
        
        errors = []
        directions_correct = 0
        total = 0
        
        for symbol in test_symbols:
            try:
                stock = yf.Ticker(symbol)
                data = stock.history(period="1y")
                
                if data.empty:
                    continue
                
                # Split into train and test
                train_data = data.iloc[:-30]  # Last 30 days for testing
                test_data = data.iloc[-30:]
                
                # Train on historical data
                train_result = self._calculate_features(train_data)
                if train_result is None:
                    continue
                
                X_train, y_train = train_result
                X_train_scaled = self.scaler.fit_transform(X_train)
                self.model.fit(X_train_scaled, y_train)
                
                # Test on recent data
                test_result = self._calculate_features(test_data)
                if test_result is None:
                    continue
                
                X_test, y_test = test_result
                X_test_scaled = self.scaler.transform(X_test)
                predictions = self.model.predict(X_test_scaled)
                
                # Calculate metrics
                for i, (pred, actual) in enumerate(zip(predictions, y_test)):
                    errors.append(abs(pred - actual))
                    if (pred > 0 and actual > 0) or (pred < 0 and actual < 0):
                        directions_correct += 1
                    total += 1
                
            except Exception as e:
                logger.error(f"❌ Error evaluating {symbol}: {e}")
                continue
        
        if total > 0:
            results['accuracy'] = directions_correct / total
            results['mean_error'] = np.mean(errors)
            results['rmse'] = np.sqrt(np.mean(np.array(errors)**2))
        
        return results


# === SINGLETON INSTANCE ===
_ai_service_instance = None

def get_ai_service() -> AIService:
    """Get or create the AI service singleton"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance


# === TEST FUNCTIONS ===
def test_ai_service():
    """Test the AI service functionality"""
    logger.info("🧪 Testing AI Service...")
    
    # Get service
    ai_service = get_ai_service()
    
    # Train model
    logger.info("Training model...")
    ai_service.train_model()
    
    # Test prediction
    logger.info("Testing prediction...")
    prediction = ai_service.predict('AAPL')
    logger.info(f"Prediction: {prediction}")
    
    # Test recommendations
    logger.info("Testing recommendations...")
    recommendations = ai_service.get_recommendations(['AAPL', 'GOOGL', 'MSFT'])
    logger.info(f"Recommendations: {recommendations}")
    
    # Get model info
    logger.info("Getting model info...")
    info = ai_service.get_model_info()
    logger.info(f"Model info: {info}")
    
    # Evaluate model
    logger.info("Evaluating model...")
    evaluation = ai_service.evaluate_model()
    logger.info(f"Evaluation: {evaluation}")
    
    logger.info("✅ AI Service test complete")


if __name__ == "__main__":
    # Run test if executed directly
    test_ai_service()
