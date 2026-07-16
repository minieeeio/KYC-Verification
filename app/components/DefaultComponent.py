from qrlib.QRComponent import QRComponent
from qrlib.QREnv import QREnv


class DefaultComponent(QRComponent):
    
    def __init__(self):
        super().__init__()

    def load_vault(self):
        self.qrvault = QREnv.VAULTS[QREnv.VAULT_NAMES[0]]
        self.user = self.qrvault.get("user")
        self.password = self.qrvault.get("password")

    def login(self):
        try:
            self.logger.info("Logging in...")
        except Exception as e:
            self.run_item.logger.error("Failed to login")
            self.run_item.notification.data = {"reason": "Login failed"}
            raise e
            
    def logout(self):
        try:
            self.logger.info("Logging out...")
        except Exception as e:
            self.logger.error("Failed to logout")
            raise e

    def test(self):
        try:
            self.logger.info("Test task")
        except Exception as e:
            self.logger.error("Test task failed")
            raise e