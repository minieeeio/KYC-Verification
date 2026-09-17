import os

from qrlib.QRBot import QRBot
from DefaultProcess import DefaultProcess

from dotenv import load_dotenv

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR,".env"))

class Bot(QRBot):
    """Entry point for the the bot."""

    def __init__(self) -> None:
        super().__init__()
        self.process = DefaultProcess()

    def start(self) -> None:
        """Set up platform components and run the process lifecycle."""
        self.setup_platform_components()
        self.process.before_run()
        self.process.execute_run()

    def teardown(self) -> None:
        """Global teardown — always runs after start() regardless of errors."""
        self.process.after_run()
        
