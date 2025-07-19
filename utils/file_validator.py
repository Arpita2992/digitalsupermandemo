"""
File validation utility with MIME type checking and security validation
"""

import os
import logging
import magic
from typing import Dict, Tuple, Optional
import config

logger = logging.getLogger(__name__)


class FileValidator:
    def __init__(self):
        self.allowed_extensions = config.ALLOWED_EXTENSIONS
        self.allowed_mime_types = config.ALLOWED_MIME_TYPES
        self.max_file_size = config.MAX_CONTENT_LENGTH
        
    def validate_file(self, filepath: str, original_filename: str) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive file validation including MIME type checking
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            # 1. Check if file exists
            if not os.path.exists(filepath):
                return False, "File does not exist"
            
            # 2. Check file size
            file_size = os.path.getsize(filepath)
            if file_size == 0:
                return False, "File is empty"
            
            if file_size > self.max_file_size:
                return False, f"File too large: {file_size:,} bytes (max: {self.max_file_size:,} bytes)"
            
            # 3. Validate file extension
            file_ext = os.path.splitext(original_filename)[1].lower().lstrip('.')
            if file_ext not in self.allowed_extensions:
                return False, f"File extension '{file_ext}' not allowed. Allowed: {', '.join(self.allowed_extensions)}"
            
            # 4. MIME type validation
            try:
                mime_type = magic.from_file(filepath, mime=True)
                logger.info(f"Detected MIME type: {mime_type} for file: {original_filename}")
                
                # Check if MIME type matches allowed types for this extension
                allowed_mimes = self.allowed_mime_types.get(file_ext, [])
                if allowed_mimes and mime_type not in allowed_mimes:
                    return False, f"MIME type '{mime_type}' doesn't match extension '{file_ext}'. Expected: {', '.join(allowed_mimes)}"
                
            except Exception as e:
                logger.warning(f"Could not determine MIME type for {filepath}: {e}")
                # Continue without MIME validation if magic fails
            
            # 5. Basic file header validation
            if not self._validate_file_headers(filepath, file_ext):
                return False, f"File headers don't match extension '{file_ext}'"
            
            # 6. Security checks
            security_check, security_error = self._security_checks(filepath, original_filename)
            if not security_check:
                return False, security_error
            
            return True, None
            
        except Exception as e:
            logger.error(f"File validation error for {filepath}: {e}")
            return False, f"Validation error: {str(e)}"
    
    def _validate_file_headers(self, filepath: str, extension: str) -> bool:
        """Validate file headers match the extension"""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(512)  # Read first 512 bytes
            
            # File signature validation
            file_signatures = {
                'png': [b'\x89PNG\r\n\x1a\n'],
                'jpg': [b'\xff\xd8\xff\xe0', b'\xff\xd8\xff\xe1', b'\xff\xd8\xff\xdb'],
                'jpeg': [b'\xff\xd8\xff\xe0', b'\xff\xd8\xff\xe1', b'\xff\xd8\xff\xdb'],
                'pdf': [b'%PDF-'],
                'xml': [b'<?xml', b'<', b'\xef\xbb\xbf<?xml'],  # Including BOM
                'svg': [b'<svg', b'<?xml'],
                'vsdx': [b'PK\x03\x04'],  # ZIP signature
                'drawio': [b'PK\x03\x04', b'<']  # ZIP or XML
            }
            
            signatures = file_signatures.get(extension, [])
            if not signatures:
                return True  # No signature check for unknown extensions
            
            for signature in signatures:
                if header.startswith(signature):
                    return True
            
            # Special case for XML-based files that might have whitespace
            if extension in ['xml', 'svg', 'drawio']:
                header_str = header.decode('utf-8', errors='ignore').lstrip()
                if header_str.startswith('<?xml') or header_str.startswith('<'):
                    return True
            
            logger.warning(f"File header validation failed for {filepath} (extension: {extension})")
            return False
            
        except Exception as e:
            logger.error(f"Header validation error for {filepath}: {e}")
            return False
    
    def _security_checks(self, filepath: str, filename: str) -> Tuple[bool, Optional[str]]:
        """Additional security checks"""
        try:
            # 1. Check for suspicious filenames
            suspicious_patterns = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
            for pattern in suspicious_patterns:
                if pattern in filename:
                    return False, f"Suspicious filename pattern detected: '{pattern}'"
            
            # 2. Check for script injection in filename
            script_patterns = ['<script', 'javascript:', 'vbscript:', 'data:']
            filename_lower = filename.lower()
            for pattern in script_patterns:
                if pattern in filename_lower:
                    return False, f"Script injection attempt detected in filename"
            
            # 3. Check file content for potential malicious patterns (basic)
            with open(filepath, 'rb') as f:
                content_sample = f.read(8192)  # Read first 8KB
            
            # Look for suspicious patterns in content
            suspicious_content = [
                b'<script',
                b'javascript:',
                b'vbscript:',
                b'onclick=',
                b'onerror=',
                b'eval(',
                b'document.write'
            ]
            
            for pattern in suspicious_content:
                if pattern in content_sample.lower():
                    logger.warning(f"Suspicious content pattern detected in {filepath}: {pattern}")
                    # Don't fail immediately, just log warning
            
            return True, None
            
        except Exception as e:
            logger.error(f"Security check error for {filepath}: {e}")
            return False, f"Security validation error: {str(e)}"
    
    def get_file_info(self, filepath: str) -> Dict[str, any]:
        """Get detailed file information for logging"""
        try:
            stat = os.stat(filepath)
            info = {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'permissions': oct(stat.st_mode)[-3:],
            }
            
            # Add MIME type if available
            try:
                info['mime_type'] = magic.from_file(filepath, mime=True)
            except Exception:
                info['mime_type'] = 'unknown'
            
            return info
            
        except Exception as e:
            logger.error(f"Could not get file info for {filepath}: {e}")
            return {'error': str(e)}


# Global instance
file_validator = FileValidator()
