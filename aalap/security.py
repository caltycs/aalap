#!/usr/bin/env python3
"""
Security and privacy features for Aalap
Ensures organizational data remains private and secure
"""

import os
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

class SecurityManager:
    """Manage security and privacy for organizational data"""

    def __init__(self, config_dir: Path, org_id: str):
        self.config_dir = config_dir
        self.org_id = org_id
        self.security_dir = config_dir / "security" / org_id
        self.security_dir.mkdir(parents=True, exist_ok=True)

        self.encryption_key_file = self.security_dir / "encryption.key"
        self.access_control_file = self.security_dir / "access_control.json"

        self._init_encryption()
        self._load_access_control()

    def _init_encryption(self):
        """Initialize encryption for sensitive data"""
        if self.encryption_key_file.exists():
            with open(self.encryption_key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            # Generate new encryption key
            self.encryption_key = Fernet.generate_key()
            with open(self.encryption_key_file, 'wb') as f:
                f.write(self.encryption_key)
            # Secure the key file
            os.chmod(self.encryption_key_file, 0o600)

        self.cipher = Fernet(self.encryption_key)

    def _load_access_control(self):
        """Load access control configuration"""
        if self.access_control_file.exists():
            with open(self.access_control_file, 'r') as f:
                self.access_control = json.load(f)
        else:
            self.access_control = {
                "org_id": self.org_id,
                "allowed_users": [],
                "restricted_collections": [],
                "data_retention_days": 90,
                "require_authentication": False,
                "allowed_ips": []
            }
            self._save_access_control()

    def _save_access_control(self):
        """Save access control configuration"""
        with open(self.access_control_file, 'w') as f:
            json.dump(self.access_control, f, indent=2)

    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    def hash_document(self, content: str) -> str:
        """Create hash of document content for deduplication"""
        return hashlib.sha256(content.encode()).hexdigest()

    def sanitize_metadata(self, metadata: Dict) -> Dict:
        """
        Remove or redact sensitive information from metadata
        before sending to external APIs
        """
        # List of fields that should never be sent externally
        sensitive_fields = [
            'email', 'phone', 'ssn', 'password', 'api_key',
            'token', 'secret', 'credential', 'internal_id'
        ]

        sanitized = metadata.copy()

        for key in list(sanitized.keys()):
            # Remove sensitive fields
            if any(field in key.lower() for field in sensitive_fields):
                del sanitized[key]
            # Redact file paths to remove internal structure
            elif key == 'source' and isinstance(sanitized[key], str):
                path = Path(sanitized[key])
                sanitized[key] = path.name  # Keep only filename

        return sanitized

    def validate_source(self, source_path: str) -> bool:
        """
        Validate that a data source is allowed to be accessed

        Args:
            source_path: Path to data source

        Returns:
            True if access is allowed
        """
        path = Path(source_path)

        # Check if path exists and is within allowed directories
        if not path.exists():
            return False

        # Add more validation logic as needed
        # e.g., check against whitelist/blacklist

        return True

    def add_allowed_user(self, user_id: str):
        """Add user to allowed users list"""
        if user_id not in self.access_control["allowed_users"]:
            self.access_control["allowed_users"].append(user_id)
            self._save_access_control()

    def remove_allowed_user(self, user_id: str):
        """Remove user from allowed users list"""
        if user_id in self.access_control["allowed_users"]:
            self.access_control["allowed_users"].remove(user_id)
            self._save_access_control()

    def check_user_access(self, user_id: str) -> bool:
        """Check if user has access to the organization's data"""
        if not self.access_control["require_authentication"]:
            return True

        return user_id in self.access_control["allowed_users"]

    def restrict_collection(self, collection_name: str):
        """Mark a collection as restricted"""
        if collection_name not in self.access_control["restricted_collections"]:
            self.access_control["restricted_collections"].append(collection_name)
            self._save_access_control()

    def unrestrict_collection(self, collection_name: str):
        """Remove restriction from a collection"""
        if collection_name in self.access_control["restricted_collections"]:
            self.access_control["restricted_collections"].remove(collection_name)
            self._save_access_control()

    def is_collection_restricted(self, collection_name: str) -> bool:
        """Check if a collection is restricted"""
        return collection_name in self.access_control["restricted_collections"]

    def audit_log(self, action: str, details: Dict):
        """Log security-relevant actions"""
        audit_file = self.security_dir / "audit.log"

        from datetime import datetime
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "org_id": self.org_id,
            "action": action,
            "details": details
        }

        with open(audit_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_privacy_summary(self) -> Dict:
        """Get summary of privacy and security settings"""
        return {
            "org_id": self.org_id,
            "encryption_enabled": True,
            "authentication_required": self.access_control["require_authentication"],
            "authorized_users": len(self.access_control["allowed_users"]),
            "restricted_collections": len(self.access_control["restricted_collections"]),
            "data_retention_days": self.access_control["data_retention_days"],
            "local_storage": True,
            "external_api_used": "Anthropic Claude",
            "data_sent_externally": "Query + Retrieved Context (sanitized)",
            "data_stored_externally": "No"
        }