"""
Risk management module for the fun trading bot.
Implements safeguards and monitoring to prevent losses.
"""

import logging
import time
import asyncio
import sys
sys.path.append('/home/ubuntu/pump_fun_bot')
from config.config import (
    MAX_TOKENS_HELD, MINIMUM_LIQUIDITY, 
    STOP_LOSS_PERCENTAGE, TAKE_PROFIT_PERCENTAGE
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RiskManager:
    """Class to manage risk and prevent losses in the trading bot."""
    
    def __init__(self, trading_strategy=None, transaction_executor=None):
        """Initialize risk manager with trading strategy and transaction executor."""
        self.trading_strategy = trading_strategy
        self.transaction_executor = transaction_executor
        self.max_tokens = MAX_TOKENS_HELD
        self.min_liquidity = MINIMUM_LIQUIDITY
        self.stop_loss = STOP_LOSS_PERCENTAGE
        self.take_profit = TAKE_PROFIT_PERCENTAGE
        self.emergency_stop = False
        self.suspicious_tokens = set()
        
    def set_trading_strategy(self, trading_strategy):
        """Set trading strategy reference."""
        self.trading_strategy = trading_strategy
        
    def set_transaction_executor(self, transaction_executor):
        """Set transaction executor reference."""
        self.transaction_executor = transaction_executor
        
    def check_portfolio_diversification(self):
        """
        Check if portfolio is properly diversified.
        Returns True if diversification is acceptable, False otherwise.
        """
        if not self.trading_strategy:
            logger.error("Trading strategy not set")
            return False
            
        active_trades = self.trading_strategy.get_active_trades()
        
        # Check number of tokens held
        if len(active_trades) >= self.max_tokens:
            logger.warning(f"Maximum number of tokens held: {len(active_trades)}/{self.max_tokens}")
            return False
            
        return True
        
    async def check_token_liquidity(self, bonding_curve_address):
        """
        Check if token has sufficient liquidity.
        Returns True if liquidity is acceptable, False otherwise.
        """
        if not self.transaction_executor:
            logger.error("Transaction executor not set")
            return False
            
        try:
            # This would query the bonding curve account to determine liquidity
            # For now, return a simulated result
            liquidity = 2000  # Example liquidity in SOL
            
            if liquidity < self.min_liquidity:
                logger.warning(f"Insufficient liquidity: {liquidity} SOL (minimum: {self.min_liquidity} SOL)")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking token liquidity: {str(e)}")
            return False
            
    def check_token_creator(self, creator_address):
        """
        Check if token creator is suspicious.
        Returns True if creator is acceptable, False otherwise.
        """
        # This would check against a database of known scammers
        # For now, use a simple check against suspicious_tokens set
        if creator_address in self.suspicious_tokens:
            logger.warning(f"Suspicious creator detected: {creator_address}")
            return False
            
        return True
        
    def validate_token_data(self, token_data):
        """
        Validate token data for suspicious patterns.
        Returns True if token data is acceptable, False otherwise.
        """
        # Check for missing fields
        required_fields = ["mint", "bondingCurve", "associatedBondingCurve", "name", "symbol", "creator"]
        for field in required_fields:
            if field not in token_data or not token_data[field]:
                logger.warning(f"Missing required field in token data: {field}")
                return False
                
        # Check for suspicious names
        suspicious_patterns = ["scam", "rug", "fake", "steal", "ponzi"]
        for pattern in suspicious_patterns:
            if pattern.lower() in token_data["name"].lower() or pattern.lower() in token_data["symbol"].lower():
                logger.warning(f"Suspicious pattern in token name/symbol: {pattern}")
                return False
                
        return True
        
    async def monitor_active_trades(self):
        """
        Monitor active trades for stop loss and take profit conditions.
        Returns list of tokens that should be sold.
        """
        if not self.trading_strategy or not self.transaction_executor:
            logger.error("Trading strategy or transaction executor not set")
            return []
            
        active_trades = self.trading_strategy.get_active_trades()
        tokens_to_sell = []
        
        for token_address, trade_data in active_trades.items():
            try:
                # Get current price
                current_price = await self.transaction_executor.fetch_token_price(trade_data["bondingCurve"])
                
                if current_price is None:
                    logger.warning(f"Could not fetch current price for {token_address}")
                    continue
                    
                purchase_price = trade_data["price"]
                
                # Calculate price change
                price_change = (current_price - purchase_price) / purchase_price
                
                # Check stop loss
                if price_change <= -self.stop_loss:
                    logger.warning(f"Stop loss triggered for {token_address}: {price_change:.2%}")
                    tokens_to_sell.append(token_address)
                    continue
                    
                # Check take profit
                if price_change >= self.take_profit:
                    logger.info(f"Take profit triggered for {token_address}: {price_change:.2%}")
                    tokens_to_sell.append(token_address)
                    continue
                    
            except Exception as e:
                logger.error(f"Error monitoring trade for {token_address}: {str(e)}")
                
        return tokens_to_sell
        
    def emergency_stop_trading(self, reason):
        """
        Trigger emergency stop of all trading.
        """
        self.emergency_stop = True
        logger.critical(f"EMERGENCY STOP TRIGGERED: {reason}")
        
    def resume_trading(self):
        """
        Resume trading after emergency stop.
        """
        self.emergency_stop = False
        logger.info("Trading resumed")
        
    def is_trading_allowed(self):
        """
        Check if trading is currently allowed.
        """
        return not self.emergency_stop
        
    def add_suspicious_token(self, token_address):
        """
        Add token to suspicious list.
        """
        self.suspicious_tokens.add(token_address)
        logger.warning(f"Added token to suspicious list: {token_address}")
        
    def check_wallet_health(self, initial_balance, current_balance):
        """
        Check wallet health by comparing current balance to initial balance.
        Triggers emergency stop if balance drops too much.
        """
        if initial_balance <= 0:
            return True
            
        balance_change = (current_balance - initial_balance) / initial_balance
        
        # If balance drops by more than 20%, trigger emergency stop
        if balance_change <= -0.2:
            self.emergency_stop_trading(f"Wallet balance dropped by {-balance_change:.2%}")
            return False
            
        return True
        
    async def perform_safety_checks(self, token_data):
        """
        Perform all safety checks before buying a token.
        Returns True if all checks pass, False otherwise.
        """
        # Check if trading is allowed
        if not self.is_trading_allowed():
            logger.warning("Trading is currently stopped")
            return False
            
        # Check portfolio diversification
        if not self.check_portfolio_diversification():
            logger.warning("Failed portfolio diversification check")
            return False
            
        # Validate token data
        if not self.validate_token_data(token_data):
            logger.warning("Failed token data validation")
            return False
            
        # Check token creator
        if not self.check_token_creator(token_data["creator"]):
            logger.warning("Failed token creator check")
            return False
            
        # Check token liquidity
        if not await self.check_token_liquidity(token_data["bondingCurve"]):
            logger.warning("Failed token liquidity check")
            return False
            
        logger.info(f"All safety checks passed for token: {token_data['symbol']}")
        return True

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        risk_manager = RiskManager()
        
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
        
        # Test safety checks
        result = await risk_manager.perform_safety_checks(token_data)
        print(f"Safety checks passed: {result}")
        
        # Test emergency stop
        risk_manager.emergency_stop_trading("Testing emergency stop")
        print(f"Trading allowed: {risk_manager.is_trading_allowed()}")
        
        # Test resume
        risk_manager.resume_trading()
        print(f"Trading allowed: {risk_manager.is_trading_allowed()}")
    
    asyncio.run(main())
