"""
Market analysis module for the fun trading bot.
Monitors for new token creations and analyzes trading opportunities.
"""

import logging
import time
import json
from solana.rpc.api import Client as SolanaClient
from solana.rpc.websocket_api import connect
import sys
sys.path.append('/home/ubuntu/pump_fun_bot')
from config.config import PUMP_FUN_PROGRAM_ID, SOLANA_RPC_URL, BLACKLISTED_TERMS, COOLDOWN_PERIOD

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """Class to monitor and analyze fun market for trading opportunities."""
    
    def __init__(self, solana_client):
        """Initialize market analyzer with Solana client."""
        self.solana_client = solana_client
        self.monitored_tokens = {}
        self.blacklisted_terms = BLACKLISTED_TERMS
        
    async def monitor_new_tokens(self):
        """
        Monitor for new token creations on fun.
        Uses Solana websocket subscription to listen for program transactions.
        """
        logger.info(f"Starting to monitor for new tokens on fun (Program ID: {PUMP_FUN_PROGRAM_ID})")
        
        async with connect(SOLANA_RPC_URL) as websocket:
            await websocket.logs_subscribe(
                {"mentions": [PUMP_FUN_PROGRAM_ID]},
                commitment="confirmed"
            )
            
            first_resp = await websocket.recv()
            subscription_id = first_resp.result
            
            logger.info(f"Successfully subscribed to fun program logs (Subscription ID: {subscription_id})")
            
            while True:
                try:
                    msg = await websocket.recv()
                    if msg.result is not None and hasattr(msg.result, 'value'):
                        transaction = msg.result.value
                        await self._process_transaction(transaction)
                except Exception as e:
                    logger.error(f"Error processing transaction: {str(e)}")
    
    async def _process_transaction(self, transaction):
        """Process a transaction to extract token creation data."""
        try:
            # Extract transaction signature
            signature = transaction.signature
            
            # Get transaction details
            tx_details = await self.solana_client.get_transaction(
                signature, 
                encoding="jsonParsed"
            )
            
            # Check if this is a token creation transaction
            if self._is_token_creation(tx_details):
                token_data = self._extract_token_data(tx_details)
                if token_data:
                    await self._analyze_token(token_data)
        except Exception as e:
            logger.error(f"Error processing transaction {signature if 'signature' in locals() else 'unknown'}: {str(e)}")
    
    def _is_token_creation(self, tx_details):
        """
        Determine if a transaction is a token creation on fun.
        Looks for specific instruction signatures in the transaction.
        """
        try:
            if not tx_details or not tx_details.get("result"):
                return False
                
            # Check for the create instruction discriminator
            # This would need to be updated with the actual discriminator for token creation
            instructions = tx_details["result"]["transaction"]["message"]["instructions"]
            for instruction in instructions:
                if instruction.get("programId") == PUMP_FUN_PROGRAM_ID:
                    # Check for create instruction data pattern
                    # This is a simplified check and would need to be refined based on actual data format
                    data = instruction.get("data")
                    if data and data.startswith("create"):
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking if transaction is token creation: {str(e)}")
            return False
    
    def _extract_token_data(self, tx_details):
        """
        Extract token data from a creation transaction.
        Returns a dictionary with token details.
        """
        try:
            # This is a placeholder for the actual extraction logic
            # In a real implementation, this would parse the transaction data to extract:
            # - Token mint address
            # - Bonding curve address
            # - Associated bonding curve address
            # - Token name and symbol
            # - Creator address
            
            # Example structure of returned data:
            token_data = {
                "mint": "token_mint_address",
                "bondingCurve": "bonding_curve_address",
                "associatedBondingCurve": "associated_bonding_curve_address",
                "name": "token_name",
                "symbol": "token_symbol",
                "creator": "creator_address",
                "timestamp": time.time()
            }
            
            return token_data
        except Exception as e:
            logger.error(f"Error extracting token data: {str(e)}")
            return None
    
    async def _analyze_token(self, token_data):
        """
        Analyze a new token to determine if it's a good trading opportunity.
        Implements filtering and scoring based on various criteria.
        """
        try:
            # Skip tokens with blacklisted terms in name
            if any(term.lower() in token_data["name"].lower() for term in self.blacklisted_terms):
                logger.info(f"Skipping token with blacklisted term: {token_data['name']}")
                return
            
            # Add token to monitored list
            self.monitored_tokens[token_data["mint"]] = token_data
            
            # Log the new token
            logger.info(f"New token detected: {token_data['name']} ({token_data['symbol']})")
            logger.info(f"Mint address: {token_data['mint']}")
            
            # Wait for cooldown period before analyzing further
            # This allows the token to stabilize and gather initial trading data
            logger.info(f"Waiting {COOLDOWN_PERIOD} seconds for token to stabilize...")
            import asyncio
            await asyncio.sleep(COOLDOWN_PERIOD)
            
            # Perform deeper analysis
            score = await self._score_token(token_data)
            
            # Determine if this is a good trading opportunity
            if score >= 70:  # Threshold for "good" opportunity
                logger.info(f"High potential token detected: {token_data['name']} (Score: {score})")
                # Signal to trading module that this is a good opportunity
                return True, token_data, score
            else:
                logger.info(f"Token does not meet criteria: {token_data['name']} (Score: {score})")
                return False, token_data, score
                
        except Exception as e:
            logger.error(f"Error analyzing token: {str(e)}")
            return False, token_data, 0
    
    async def _score_token(self, token_data):
        """
        Score a token based on various criteria to determine trading potential.
        Returns a score from 0-100, with higher scores indicating better opportunities.
        """
        try:
            score = 0
            
            # Check creator reputation
            creator_score = await self._check_creator_reputation(token_data["creator"])
            score += creator_score * 0.3  # 30% weight
            
            # Check initial liquidity
            liquidity_score = await self._check_initial_liquidity(token_data["bondingCurve"])
            score += liquidity_score * 0.3  # 30% weight
            
            # Check token name and symbol quality
            name_score = self._evaluate_token_name(token_data["name"], token_data["symbol"])
            score += name_score * 0.2  # 20% weight
            
            # Check market conditions
            market_score = await self._check_market_conditions()
            score += market_score * 0.2  # 20% weight
            
            return min(round(score), 100)  # Cap at 100
            
        except Exception as e:
            logger.error(f"Error scoring token: {str(e)}")
            return 0
    
    async def _check_creator_reputation(self, creator_address):
        """Check reputation of token creator based on past tokens."""
        # This would query historical data to see if this creator has launched successful tokens before
        # For now, return a placeholder score
        return 50  # Neutral score for unknown creators
    
    async def _check_initial_liquidity(self, bonding_curve_address):
        """Check initial liquidity provided for the token."""
        # This would query the bonding curve account to determine initial liquidity
        # For now, return a placeholder score
        return 60  # Slightly above average liquidity
    
    def _evaluate_token_name(self, name, symbol):
        """Evaluate token name and symbol for quality and appeal."""
        # Simple heuristic: longer names tend to be more legitimate
        length_score = min(len(name) / 20 * 100, 100)
        
        # Check for common meme patterns that tend to perform well
        meme_patterns = ["dog", "cat", "pepe", "elon", "moon", "rocket", "inu", "shib"]
        meme_score = 0
        for pattern in meme_patterns:
            if pattern.lower() in name.lower() or pattern.lower() in symbol.lower():
                meme_score += 20
        
        meme_score = min(meme_score, 100)
        
        # Combine scores with weights
        return length_score * 0.4 + meme_score * 0.6
    
    async def _check_market_conditions(self):
        """Check overall market conditions for favorable trading."""
        # This would analyze overall market sentiment, volume, etc.
        # For now, return a placeholder score
        return 70  # Generally favorable market conditions

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        solana_client = SolanaClient(SOLANA_RPC_URL)
        analyzer = MarketAnalyzer(solana_client)
        await analyzer.monitor_new_tokens()
    
    asyncio.run(main())
