"""
Blockchain connection module for the fun trading bot.
Handles connections to Solana and Base blockchains.
"""

import os
import logging
from solana.rpc.api import Client as SolanaClient
from web3 import Web3
from dotenv import load_dotenv
import sys
sys.path.append('/home/ubuntu/fun_bot')
from config.config import SOLANA_RPC_URL, BASE_RPC_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BlockchainConnection:
    """Class to manage blockchain connections for the trading bot."""
    
    def __init__(self):
        """Initialize blockchain connections."""
        self.solana_client = None
        self.base_client = None
        self.connected_solana = False
        self.connected_base = False
        
    def connect_solana(self):
        """Connect to Solana blockchain."""
        try:
            self.solana_client = SolanaClient(SOLANA_RPC_URL)
            # Test connection by getting latest blockhash
            response = self.solana_client.get_latest_blockhash()
            if response is not None:
                self.connected_solana = True
                logger.info(f"Successfully connected to Solana at {SOLANA_RPC_URL}")
                return True
            else:
                logger.error("Failed to connect to Solana: Invalid response")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Solana: {str(e)}")
            return False
    
    def connect_base(self):
        """Connect to Base blockchain."""
        try:
            self.base_client = Web3(Web3.HTTPProvider(BASE_RPC_URL))
            if self.base_client.is_connected():
                self.connected_base = True
                logger.info(f"Successfully connected to Base at {BASE_RPC_URL}")
                return True
            else:
                logger.error("Failed to connect to Base: Not connected")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Base: {str(e)}")
            return False
    
    def connect_all(self):
        """Connect to all supported blockchains."""
        solana_success = self.connect_solana()
        base_success = self.connect_base()
        return solana_success, base_success
    
    def get_solana_client(self):
        """Get Solana client instance."""
        if not self.connected_solana:
            self.connect_solana()
        return self.solana_client
    
    def get_base_client(self):
        """Get Base client instance."""
        if not self.connected_base:
            self.connect_base()
        return self.base_client
    
    def check_connections(self):
        """Check if connections are active."""
        solana_status = "Connected" if self.connected_solana else "Disconnected"
        base_status = "Connected" if self.connected_base else "Disconnected"
        logger.info(f"Solana: {solana_status}, Base: {base_status}")
        return {
            "solana": self.connected_solana,
            "base": self.connected_base
        }

# Example usage
if __name__ == "__main__":
    connection = BlockchainConnection()
    solana_success, base_success = connection.connect_all()
    connection.check_connections()
