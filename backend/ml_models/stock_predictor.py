import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from typing import Dict, Any, Optional
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from loguru import logger

class StockPredictor:
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.load_models()
    
    def load_models(self):
        """Load pre-trained models"""
        try:
            # Load ML models
            self.models['random_forest'] = joblib.load('models/random_forest.pkl')
            self.models['gradient_boost'] = joblib.load('models/gradient_boost.pkl')
            self.models['neural_net'] = joblib.load('models/neural_net.pkl')
            
            # Load PyTorch model
            self.models['lstm'] = self.load_lstm_model()
            
            logger.info("Models loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load models: {e}")
            # Initialize models if not loaded
            self.initialize_models()
    
    def initialize_models(self):
        """Initialize new models"""
        self.models['random_forest'] = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.models['gradient_boost'] = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.models['neural_net'] = MLPRegressor(
            hidden_layer_sizes=(100, 50),
            activation='relu',
            solver='adam',
            max_iter=1000,
            random_state=42
        )
        self.models['lstm'] = self.create_lstm_model()
    
    def create_lstm_model(self):
        """Create LSTM model for time series prediction"""
        class LSTMPredictor(nn.Module):
            def __init__(self, input_size=60, hidden_size=128, num_layers=2, output_size=1):
                super(LSTMPredictor, self).__init__()
                self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
                self.fc = nn.Linear(hidden_size, output_size)
                
            def forward(self, x):
                out, _ = self.lstm(x)
                out = self.fc(out[:, -1, :])
                return out
        
        return LSTMPredictor().to(self.device)
    
    def train(self, X, y):
        """Train all models"""
        try:
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Train Random Forest
            self.models['random_forest'].fit(X_train, y_train)
            
            # Train Gradient Boost
            self.models['gradient_boost'].fit(X_train, y_train)
            
            # Train Neural Network
            self.models['neural_net'].fit(X_train, y_train)
            
            # Train LSTM
            self.train_lstm(X_train, y_train, X_test, y_test)
            
            # Save models
            self.save_models()
            
            logger.info("Models trained successfully")
        except Exception as e:
            logger.error(f"Error training models: {e}")
    
    def train_lstm(self, X_train, y_train, X_test, y_test, epochs=100):
        """Train LSTM model"""
        X_train_tensor = torch.FloatTensor(X_train).to(self.device)
        y_train_tensor = torch.FloatTensor(y_train).to(self.device)
        X_test_tensor = torch.FloatTensor(X_test).to(self.device)
        y_test_tensor = torch.FloatTensor(y_test).to(self.device)
        
        # Reshape for LSTM
        X_train_tensor = X_train_tensor.view(X_train_tensor.size(0), 1, -1)
        X_test_tensor = X_test_tensor.view(X_test_tensor.size(0), 1, -1)
        
        train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
        
        model = self.models['lstm']
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        model.train()
        for epoch in range(epochs):
            for batch_x, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = model(batch_x)
                loss = criterion(outputs.squeeze(), batch_y)
                loss.backward()
                optimizer.step()
            
            if epoch % 10 == 0:
                model.eval()
                with torch.no_grad():
                    test_outputs = model(X_test_tensor)
                    test_loss = criterion(test_outputs.squeeze(), y_test_tensor)
                    logger.info(f'Epoch {epoch}, Test Loss: {test_loss.item():.4f}')
                model.train()
    
    def save_models(self):
        """Save trained models"""
        try:
            joblib.dump(self.models['random_forest'], 'models/random_forest.pkl')
            joblib.dump(self.models['gradient_boost'], 'models/gradient_boost.pkl')
            joblib.dump(self.models['neural_net'], 'models/neural_net.pkl')
            torch.save(self.models['lstm'].state_dict(), 'models/lstm.pth')
            logger.info("Models saved successfully")
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """Make predictions using ensemble of models"""
        try:
            # Ensure features are 2D
            if len(features.shape) == 1:
                features = features.reshape(1, -1)
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Get predictions from each model
            predictions = {}
            
            # ML models
            for name, model in self.models.items():
                if name != 'lstm':
                    try:
                        pred = model.predict(features_scaled)
                        predictions[name] = pred[0] if len(pred) > 0 else 0
                    except Exception as e:
                        logger.warning(f"Error predicting with {name}: {e}")
                        predictions[name] = 0
            
            # LSTM prediction
            try:
                features_tensor = torch.FloatTensor(features_scaled).to(self.device)
                features_tensor = features_tensor.view(features_tensor.size(0), 1, -1)
                self.models['lstm'].eval()
                with torch.no_grad():
                    lstm_pred = self.models['lstm'](features_tensor)
                predictions['lstm'] = lstm_pred.cpu().numpy()[0][0]
            except Exception as e:
                logger.warning(f"Error predicting with LSTM: {e}")
                predictions['lstm'] = 0
            
            # Ensemble prediction (weighted average)
            weights = {
                'random_forest': 0.25,
                'gradient_boost': 0.25,
                'neural_net': 0.25,
                'lstm': 0.25
            }
            
            weighted_pred = sum(predictions.get(name, 0) * weights.get(name, 0.25) 
                              for name in weights.keys())
            
            # Calculate confidence based on model agreement
            values = [predictions.get(name, 0) for name in weights.keys()]
            confidence = 1 - (np.std(values) / (np.mean(values) + 1e-8))
            confidence = min(max(confidence, 0), 1)  # Clip to [0, 1]
            
            return {
                'price': weighted_pred,
                'confidence': float(confidence),
                'predictions': predictions,
                'target_low': weighted_pred * 0.95,
                'target_high': weighted_pred * 1.05,
                'recommendation': self.get_recommendation(weighted_pred, confidence)
            }
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return {
                'price': 0,
                'confidence': 0,
                'predictions': {},
                'target_low': 0,
                'target_high': 0,
                'recommendation': 'NEUTRAL'
            }
    
    def get_recommendation(self, predicted_price: float, confidence: float) -> str:
        """Get recommendation based on prediction and confidence"""
        # This would normally compare with current price
        # For now, return based on confidence and predicted price
        if confidence > 0.8:
            if predicted_price > 0:
                return "STRONG BUY"
            else:
                return "STRONG SELL"
        elif confidence > 0.6:
            if predicted_price > 0:
                return "BUY"
            else:
                return "SELL"
        else:
            return "HOLD"
