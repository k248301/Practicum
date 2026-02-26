import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import os
import glob
import joblib

class CryptoDataProcessor:
    """Handles data loading from multiple symbols, feature engineering, and sequence creation."""
    def __init__(self, sequence_length=24, horizon=5, threshold=0.01):
        self.sequence_length = sequence_length
        self.horizon = horizon
        self.threshold = threshold
        self.scaler = StandardScaler()
        # Features available in user CSVs
        self.features = ['Open', 'High', 'Low', 'Close', 'Volume', 'Marketcap', 'SMA_20', 'SMA_50', 'RSI', 'vol_change']

    def add_indicators(self, df):
        """Adds common technical indicators to a single symbol's dataframe."""
        df = df.copy()
        # Ensure Date is datetime and sorted
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.sort_values('Date')
        
        # Convert numeric columns to float to avoid object type issues
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Marketcap']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Simple Moving Averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Relative Strength Index (RSI)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        # Handle division by zero for RS
        rs = gain / loss.replace(0, np.nan)
        df['RSI'] = 100 - (100 / (1 + rs.fillna(100))) # loss=0 implies RSI=100
        
        # Volume Change - replace infinity if volume was 0
        df['vol_change'] = df['Volume'].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0)
        
        # Final cleanup: Replace any remaining inf with NaN and drop them
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        return df

    def generate_signals(self, df):
        """Generate Buy (1), Sell (2), Hold (0) signals based on future price change."""
        df = df.copy()
        df['future_return'] = df['Close'].shift(-self.horizon) / df['Close'] - 1
        
        def label_func(ret):
            if ret > self.threshold: return 1 # Buy
            if ret < -self.threshold: return 2 # Sell
            return 0 # Hold
            
        df['signal'] = df['future_return'].apply(label_func)
        return df.dropna()

    def process_all_symbols(self, data_dir):
        """Loads and processes all CSV files in the directory."""
        all_X_train = []
        all_y_train = []
        all_X_test = []
        all_y_test = []
        
        csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {data_dir}")
            
        print(f"Found {len(csv_files)} symbols in {data_dir}")
        
        train_dfs = []
        test_dfs = []
        
        for file in csv_files:
            df = pd.read_csv(file)
            df = self.add_indicators(df)
            df = self.generate_signals(df)
            
            # Use 80% per symbol for training to preserve temporal order
            split = int(0.8 * len(df))
            train_dfs.append(df.iloc[:split])
            test_dfs.append(df.iloc[split:])
            
        # Fit scaler on all aggregated training data
        full_train_agg = pd.concat(train_dfs)
        self.scaler.fit(full_train_agg[self.features].values)
        
        # Second pass: Create sequences per symbol
        for train_df, test_df in zip(train_dfs, test_dfs):
            X_train_scaled = self.scaler.transform(train_df[self.features].values)
            y_train = train_df['signal'].values
            X_seq_tr, y_seq_tr = self._create_sequences(X_train_scaled, y_train)
            if len(X_seq_tr) > 0:
                all_X_train.append(X_seq_tr)
                all_y_train.append(y_seq_tr)
                
            X_test_scaled = self.scaler.transform(test_df[self.features].values)
            y_test = test_df['signal'].values
            X_seq_ts, y_seq_ts = self._create_sequences(X_test_scaled, y_test)
            if len(X_seq_ts) > 0:
                all_X_test.append(X_seq_ts)
                all_y_test.append(y_seq_ts)
                
        return (np.concatenate(all_X_train), np.concatenate(all_y_train)), \
               (np.concatenate(all_X_test), np.concatenate(all_y_test))

    def _create_sequences(self, X, y):
        X_seq, y_seq = [], []
        if len(X) <= self.sequence_length:
            return np.array([]), np.array([])
        for i in range(len(X) - self.sequence_length):
            X_seq.append(X[i : i + self.sequence_length])
            y_seq.append(y[i + self.sequence_length])
        return np.array(X_seq), np.array(y_seq)

    def save_scaler(self, path):
        joblib.dump(self.scaler, path)
        print(f"Scaler saved to {path}")

class CryptoRNNModel:
    """Encapsulates the LSTM model architecture and lifecycle."""
    def __init__(self, input_shape, num_classes=3):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential([
            Input(shape=self.input_shape),
            LSTM(256, return_sequences=True),
            Dropout(0.4),
            BatchNormalization(),
            LSTM(128, return_sequences=False),
            Dropout(0.4),
            BatchNormalization(),
            Dense(64, activation='relu'),
            Dropout(0.2),
            Dense(self.num_classes, activation='softmax')
        ])
        model.compile(optimizer=Adam(learning_rate=0.0001), 
                      loss='sparse_categorical_crossentropy', 
                      metrics=['accuracy'])
        return model

    def train(self, X_train, y_train, epochs=30, batch_size=32, validation_split=0.2, model_path='multi_crypto_rnn.keras'):
        # Restore best weights at the end of training
        early_stop = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss', 
            patience=7, 
            restore_best_weights=True
        )
        
        # Save the best model locally during training
        checkpoint = tf.keras.callbacks.ModelCheckpoint(
            model_path,
            monitor='val_loss',
            save_best_only=True,
            mode='min',
            verbose=1
        )
        
        return self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[early_stop, checkpoint],
            verbose=1
        )

    def evaluate(self, X_test, y_test):
        y_pred_probs = self.model.predict(X_test)
        y_pred = np.argmax(y_pred_probs, axis=1)
        print("\n--- Aggregated Classification Report ---")
        print(classification_report(y_test, y_pred, target_names=['Hold', 'Buy', 'Sell']))
        return y_pred

    def save(self, path):
        self.model.save(path)
        print(f"Model saved to {path}")

class MultiSymbolPipeline:
    """Orchestrator for the training workflow across multiple symbols."""
    def __init__(self, processor, model_path='multi_crypto_rnn.keras', scaler_path='scaler.pkl'):
        self.processor = processor
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None

    def run(self, data_dir):
        print(f"Starting pipeline using data from: {data_dir}")
        (X_train, y_train), (X_test, y_test) = self.processor.process_all_symbols(data_dir)
        
        print(f"Aggregated Training Samples: {X_train.shape}")
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        base_model, ext_model = os.path.splitext(self.model_path)
        base_scaler, ext_scaler = os.path.splitext(self.scaler_path)
        
        current_model_path = f"{base_model}_{timestamp}{ext_model}"
        current_scaler_path = f"{base_scaler}_{timestamp}{ext_scaler}"

        self.model = CryptoRNNModel(input_shape=(X_train.shape[1], X_train.shape[2]))
        self.model.train(X_train, y_train, model_path=current_model_path)
        
        print("Evaluating on aggregated test set...")
        self.model.evaluate(X_test, y_test)
        
        # Save artifacts with timestamp
        self.model.save(current_model_path)
        self.processor.save_scaler(current_scaler_path)

if __name__ == "__main__":
    DATA_DIRECTORY = '.\\CryptoTradingModel\\RawData'
    MODEL_FILE = '.\\CryptoTradingModel\\Artifacts\\crypto_predictor.keras'
    SCALER_FILE = '.\\CryptoTradingModel\\Artifacts\\data_scaler.pkl'
    
    if os.path.exists(DATA_DIRECTORY):
        cryptoDataProcessor = CryptoDataProcessor(sequence_length=30)
        dataPipeline = MultiSymbolPipeline(cryptoDataProcessor, model_path=MODEL_FILE, scaler_path=SCALER_FILE)
        dataPipeline.run(DATA_DIRECTORY)
    else:
        print(f"Directory not found: {DATA_DIRECTORY}")
