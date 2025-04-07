"""
Trading strategy module for the fun trading bot.
Implements various strategies for token selection and trading execution.
"""

import logging
import time
import asyncio
from decimal import Decimal
import sys
sys.path.append('/home/ubuntu/pump_fun_bot')
from config.config import (
    DEFAULT_SLIPPAGE, MAX_ALLOCATION_PER_TOKEN, 
    STOP_LOSS_PERCENTAGE, TAKE_PROFIT_PERCENTAGE
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TradingStrategy:
    """Class to implement trading strategies for the fun bot."""
    
    def __init__(self, wallet_balance=0):
        """Initialize trading strategy with wallet balance."""
        self.wallet_balance = wallet_balance
        self.active_trades = {}  # Track active trades
        self.trade_history = []  # Track historical trades
        self.slippage = DEFAULT_SLIPPAGE
        self.max_allocation = MAX_ALLOCATION_PER_TOKEN
        self.stop_loss = STOP_LOSS_PERCENTAGE
        self.take_profit = TAKE_PROFIT_PERCENTAGE
        
    def set_wallet_balance(self, balance):
        """Update wallet balance."""
        self.wallet_balance = balance
        logger.info(f"Wallet balance updated: {balance} SOL")
        
    def calculate_position_size(self, token_data, score):
        """
        Calculate position size based on token score and wallet balance.
        Higher scores result in larger position sizes, up to the maximum allocation.
        """
        # Base allocation is proportional to score
        base_allocation = (score / 100) * self.max_allocation
        
        # Calculate SOL amount based on wallet balance
        sol_amount = self.wallet_balance * base_allocation
        
        # Ensure minimum trade size
        min_trade = 0.01  # Minimum 0.01 SOL
        if sol_amount < min_trade:
            sol_amount = min_trade
            
        # Ensure maximum allocation is not exceeded
        max_sol = self.wallet_balance * self.max_allocation
        if sol_amount > max_sol:
            sol_amount = max_sol
            
        logger.info(f"Calculated position size: {sol_amount} SOL (Score: {score}, Allocation: {base_allocation:.2%})")
        return sol_amount
        
    def should_buy(self, token_data, score):
        """
        Determine if a token should be bought based on analysis score and strategy rules.
        Returns a tuple of (should_buy, sol_amount, reason).
        """
        # Check if score meets minimum threshold
        if score < 70:
            return False, 0, f"Score too low: {score}"
            
        # Check if wallet has sufficient balance
        if self.wallet_balance <= 0:
            return False, 0, "Insufficient wallet balance"
            
        # Calculate position size
        sol_amount = self.calculate_position_size(token_data, score)
        
        # Check if position size meets minimum requirements
        if sol_amount < 0.01:
            return False, 0, f"Position size too small: {sol_amount} SOL"
            
        return True, sol_amount, "Token meets buying criteria"
        
    def should_sell(self, token_address, current_price, purchase_price):
        """
        Determine if a token should be sold based on price movement and strategy rules.
        Returns a tuple of (should_sell, reason).
        """
        if token_address not in self.active_trades:
            return False, "Token not in active trades"
            
        # Calculate price change percentage
        price_change = (current_price - purchase_price) / purchase_price
        
        # Check stop loss
        if price_change <= -self.stop_loss:
            return True, f"Stop loss triggered: {price_change:.2%}"
            
        # Check take profit
        if price_change >= self.take_profit:
            return True, f"Take profit triggered: {price_change:.2%}"
            
        # Time-based exit (hold for maximum of 24 hours)
        purchase_time = self.active_trades[token_address]["timestamp"]
        current_time = time.time()
        hours_held = (current_time - purchase_time) / 3600
        
        if hours_held >= 24:
            return True, f"Maximum hold time reached: {hours_held:.1f} hours"
            
        return False, "Holding position"
        
    def record_buy(self, token_data, sol_amount, price):
        """Record a buy transaction."""
        trade = {
            "token_address": token_data["mint"],
            "token_name": token_data["name"],
            "token_symbol": token_data["symbol"],
            "action": "buy",
            "sol_amount": sol_amount,
            "price": price,
            "timestamp": time.time()
        }
        
        # Add to active trades
        self.active_trades[token_data["mint"]] = trade
        
        # Add to trade history
        self.trade_history.append(trade)
        
        logger.info(f"Buy recorded: {sol_amount} SOL of {token_data['symbol']} at {price}")
        
    def record_sell(self, token_address, sol_amount, price):
        """Record a sell transaction."""
        if token_address not in self.active_trades:
            logger.error(f"Cannot record sell: Token {token_address} not in active trades")
            return
            
        buy_trade = self.active_trades[token_address]
        
        trade = {
            "token_address": token_address,
            "token_name": buy_trade["token_name"],
            "token_symbol": buy_trade["token_symbol"],
            "action": "sell",
            "sol_amount": sol_amount,
            "price": price,
            "timestamp": time.time(),
            "profit_loss": (price - buy_trade["price"]) / buy_trade["price"]
        }
        
        # Remove from active trades
        del self.active_trades[token_address]
        
        # Add to trade history
        self.trade_history.append(trade)
        
        logger.info(f"Sell recorded: {sol_amount} SOL of {trade['token_symbol']} at {price} (P/L: {trade['profit_loss']:.2%})")
        
    def get_active_trades(self):
        """Get list of active trades."""
        return self.active_trades
        
    def get_trade_history(self):
        """Get trade history."""
        return self.trade_history
        
    def calculate_performance(self):
        """Calculate overall trading performance."""
        if not self.trade_history:
            return {
                "total_trades": 0,
                "profitable_trades": 0,
                "win_rate": 0,
                "average_profit": 0,
                "total_profit_loss": 0
            }
            
        # Filter completed trades (buy and sell pairs)
        completed_trades = [t for t in self.trade_history if t["action"] == "sell"]
        
        if not completed_trades:
            return {
                "total_trades": 0,
                "profitable_trades": 0,
                "win_rate": 0,
                "average_profit": 0,
                "total_profit_loss": 0
            }
            
        # Calculate metrics
        total_trades = len(completed_trades)
        profitable_trades = sum(1 for t in completed_trades if t["profit_loss"] > 0)
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0
        
        # Calculate average and total profit/loss
        total_profit_loss = sum(t["profit_loss"] for t in completed_trades)
        average_profit = total_profit_loss / total_trades if total_trades > 0 else 0
        
        return {
            "total_trades": total_trades,
            "profitable_trades": profitable_trades,
            "win_rate": win_rate,
            "average_profit": average_profit,
            "total_profit_loss": total_profit_loss
        }

# Example usage
if __name__ == "__main__":
    # Example token data
    token_data = {
        "mint": "example_token_address",
        "name": "Example Token",
        "symbol": "EX",
        "bondingCurve": "bonding_curve_address",
        "associatedBondingCurve": "associated_bonding_curve_address",
        "creator": "creator_address",
        "timestamp": time.time()
    }
    
    # Initialize strategy with 10 SOL balance
    strategy = TradingStrategy(10)
    
    # Test buy decision
    should_buy, sol_amount, reason = strategy.should_buy(token_data, 85)
    print(f"Should buy: {should_buy}, Amount: {sol_amount} SOL, Reason: {reason}")
    
    if should_buy:
        # Record buy
        strategy.record_buy(token_data, sol_amount, 0.001)
        
        # Test sell decision
        should_sell, reason = strategy.should_sell(token_data["mint"], 0.0015, 0.001)
        print(f"Should sell: {should_sell}, Reason: {reason}")
        
        if should_sell:
            # Record sell
            strategy.record_sell(token_data["mint"], sol_amount, 0.0015)
            
    # Print performance
    performance = strategy.calculate_performance()
    print(f"Performance: {performance}")
