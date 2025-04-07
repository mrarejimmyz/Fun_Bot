"""
Main controller for the fun trading bot.
Integrates all components and manages the overall bot operation.
"""

import logging
import asyncio
import time
import sys
sys.path.append('/home/ubuntu/pump_fun_bot')
from src.blockchain_connection import BlockchainConnection
from src.market_analyzer import MarketAnalyzer
from src.trading_strategy import TradingStrategy
from src.transaction_executor import TransactionExecutor
from src.risk_manager import RiskManager
from config.config import SOLANA_RPC_URL, MONITORING_INTERVAL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pump_fun_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PumpFunBot:
    """Main controller class for the fun trading bot."""
    
    def __init__(self):
        """Initialize the fun trading bot."""
        logger.info("Initializing fun trading bot...")
        
        # Initialize blockchain connection
        self.blockchain_connection = BlockchainConnection()
        
        # Initialize components
        self.solana_client = None
        self.market_analyzer = None
        self.trading_strategy = None
        self.transaction_executor = None
        self.risk_manager = None
        
        # Bot state
        self.running = False
        self.initial_balance = 0
        self.current_balance = 0
        
    async def initialize(self):
        """Initialize all bot components."""
        try:
            # Connect to blockchains
            solana_success, base_success = self.blockchain_connection.connect_all()
            
            if not solana_success:
                logger.error("Failed to connect to Solana blockchain")
                return False
                
            # Get Solana client
            self.solana_client = self.blockchain_connection.get_solana_client()
            
            # Initialize components
            self.transaction_executor = TransactionExecutor(self.solana_client)
            self.initial_balance = await self.transaction_executor.get_wallet_balance()
            self.current_balance = self.initial_balance
            
            self.trading_strategy = TradingStrategy(self.initial_balance)
            self.market_analyzer = MarketAnalyzer(self.solana_client)
            self.risk_manager = RiskManager(self.trading_strategy, self.transaction_executor)
            
            logger.info(f"Bot initialized with wallet balance: {self.initial_balance} SOL")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing bot: {str(e)}")
            return False
    
    async def start(self):
        """Start the trading bot."""
        if self.running:
            logger.warning("Bot is already running")
            return
            
        if not await self.initialize():
            logger.error("Failed to initialize bot")
            return
            
        self.running = True
        logger.info("Starting fun trading bot...")
        
        # Start monitoring and trading tasks
        monitoring_task = asyncio.create_task(self._monitoring_loop())
        market_task = asyncio.create_task(self._market_monitoring_loop())
        
        # Wait for tasks to complete (they run indefinitely until bot is stopped)
        await asyncio.gather(monitoring_task, market_task)
    
    async def stop(self):
        """Stop the trading bot."""
        if not self.running:
            logger.warning("Bot is not running")
            return
            
        self.running = False
        logger.info("Stopping fun trading bot...")
        
        # Perform cleanup
        # Close any open connections, etc.
        
        logger.info("Bot stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop for portfolio management."""
        logger.info("Starting monitoring loop...")
        
        while self.running:
            try:
                # Update wallet balance
                self.current_balance = await self.transaction_executor.get_wallet_balance()
                self.trading_strategy.set_wallet_balance(self.current_balance)
                
                # Check wallet health
                self.risk_manager.check_wallet_health(self.initial_balance, self.current_balance)
                
                # Monitor active trades for stop loss/take profit
                tokens_to_sell = await self.risk_manager.monitor_active_trades()
                
                # Sell tokens that triggered stop loss/take profit
                for token_address in tokens_to_sell:
                    await self._sell_token(token_address)
                
                # Calculate and log performance
                performance = self.trading_strategy.calculate_performance()
                if performance["total_trades"] > 0:
                    logger.info(f"Performance: {performance['profitable_trades']}/{performance['total_trades']} profitable trades ({performance['win_rate']:.2%})")
                    logger.info(f"Total P/L: {performance['total_profit_loss']:.2%}")
                
                # Sleep for monitoring interval
                await asyncio.sleep(MONITORING_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(10)  # Sleep and retry
    
    async def _market_monitoring_loop(self):
        """Loop for monitoring new token creations."""
        logger.info("Starting market monitoring loop...")
        
        while self.running:
            try:
                # Monitor for new tokens
                # This is a placeholder for the actual implementation
                # In a real implementation, this would use the market_analyzer.monitor_new_tokens method
                
                # Simulate receiving a new token
                # In a real implementation, this would be triggered by the market_analyzer
                # when it detects a new token creation
                
                # For testing purposes, we'll simulate a new token every 60 seconds
                await asyncio.sleep(60)
                
                # Example token data (in a real implementation, this would come from the market_analyzer)
                token_data = {
                    "mint": f"simulated_token_{int(time.time())}",
                    "name": "Simulated Token",
                    "symbol": "SIM",
                    "bondingCurve": "simulated_bonding_curve",
                    "associatedBondingCurve": "simulated_associated_bonding_curve",
                    "creator": "simulated_creator",
                    "timestamp": time.time()
                }
                
                # Process the new token
                await self._process_new_token(token_data)
                
            except Exception as e:
                logger.error(f"Error in market monitoring loop: {str(e)}")
                await asyncio.sleep(10)  # Sleep and retry
    
    async def _process_new_token(self, token_data):
        """Process a new token and decide whether to buy it."""
        try:
            logger.info(f"Processing new token: {token_data['name']} ({token_data['symbol']})")
            
            # Analyze token
            success, token_data, score = await self._analyze_token(token_data)
            
            if not success:
                logger.info(f"Token analysis failed or token does not meet criteria: {token_data['symbol']}")
                return
                
            # Perform safety checks
            if not await self.risk_manager.perform_safety_checks(token_data):
                logger.warning(f"Token failed safety checks: {token_data['symbol']}")
                return
                
            # Decide whether to buy
            should_buy, sol_amount, reason = self.trading_strategy.should_buy(token_data, score)
            
            if not should_buy:
                logger.info(f"Decision not to buy token: {token_data['symbol']} - {reason}")
                return
                
            # Buy token
            await self._buy_token(token_data, sol_amount)
            
        except Exception as e:
            logger.error(f"Error processing new token: {str(e)}")
    
    async def _analyze_token(self, token_data):
        """Analyze a token to determine if it's a good trading opportunity."""
        # This is a simplified version of what would be in the market_analyzer
        # In a real implementation, this would use more sophisticated analysis
        
        # Simulate token analysis
        score = 85  # Example score
        
        # Determine if this is a good trading opportunity
        if score >= 70:  # Threshold for "good" opportunity
            logger.info(f"High potential token detected: {token_data['name']} (Score: {score})")
            return True, token_data, score
        else:
            logger.info(f"Token does not meet criteria: {token_data['name']} (Score: {score})")
            return False, token_data, score
    
    async def _buy_token(self, token_data, sol_amount):
        """Buy a token."""
        try:
            logger.info(f"Buying {sol_amount} SOL of {token_data['symbol']}")
            
            # Execute buy transaction
            success, tx_id, price = await self.transaction_executor.buy_token(token_data, sol_amount)
            
            if not success:
                logger.error(f"Failed to buy token: {token_data['symbol']}")
                return
                
            # Record buy in trading strategy
            self.trading_strategy.record_buy(token_data, sol_amount, price)
            
            logger.info(f"Successfully bought {sol_amount} SOL of {token_data['symbol']} at {price} SOL per token")
            logger.info(f"Transaction ID: {tx_id}")
            
        except Exception as e:
            logger.error(f"Error buying token: {str(e)}")
    
    async def _sell_token(self, token_address):
        """Sell a token."""
        try:
            # Get token data from active trades
            active_trades = self.trading_strategy.get_active_trades()
            
            if token_address not in active_trades:
                logger.error(f"Token not found in active trades: {token_address}")
                return
                
            token_data = active_trades[token_address]
            
            logger.info(f"Selling token: {token_data['token_symbol']}")
            
            # Execute sell transaction
            success, tx_id, price = await self.transaction_executor.sell_token(
                token_address, 
                token_data["bondingCurve"]
            )
            
            if not success:
                logger.error(f"Failed to sell token: {token_data['token_symbol']}")
                return
                
            # Record sell in trading strategy
            self.trading_strategy.record_sell(token_address, token_data["sol_amount"], price)
            
            logger.info(f"Successfully sold {token_data['token_symbol']} at {price} SOL per token")
            logger.info(f"Transaction ID: {tx_id}")
            
        except Exception as e:
            logger.error(f"Error selling token: {str(e)}")

# Example usage
if __name__ == "__main__":
    async def main():
        bot = PumpFunBot()
        try:
            await bot.start()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, stopping bot...")
            await bot.stop()
    
    asyncio.run(main())
