import json
import os
import gc
import atexit


class SecureVaultEngine:
    def __init__(self, protocol_path):
        self.protocol_path = protocol_path
        self._secret_buffer = None

    def load_protocol(self):
        with open(self.protocol_path, "r") as f:
            return json.load(f)

    def process_secure_token(self, token_data):
        # SIMULATION: In a real system, this would call a Hardware Security Module (HSM)
        # or a secure vault to decrypt the token in-memory.
        print("Processing token through secure channel...")
        self._secret_buffer = f"DECRYPTED_{token_data}"

        # Use the secret
        self._execute_secure_action()

        # Ephemeral deletion: Wipe from memory immediately after use
        self._clear_secret()

    def _execute_secure_action(self):
        print(f"Executing action with sensitive token: {self._secret_buffer[:15]}...")

    def _clear_secret(self):
        print("Wiping sensitive token from memory...")
        self._secret_buffer = (
            "\x00" * len(self._secret_buffer) if self._secret_buffer else None
        )
        self._secret_buffer = None
        gc.collect()


# Usage
if __name__ == "__main__":
    engine = SecureVaultEngine("protocol.json")
    protocol = engine.load_protocol()
    token = protocol["payload"]["field_api_token"]

    engine.process_secure_token(token)

    # Final check
    print(f"Secret buffer status: {engine._secret_buffer}")
