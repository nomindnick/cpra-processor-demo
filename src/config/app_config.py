"""
Application configuration for CPRA Processing Application.

Sprint 7 Implementation: Configuration Management
- Centralized configuration for all application settings
- Environment variable support for deployment flexibility
- Default values optimized for demo presentation
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class ModelConfig:
    """Configuration for AI model settings."""
    default_model: str = "gemma3:latest"
    responsiveness_model: str = "gemma3:latest"
    exemption_model: str = "gemma3:latest"
    temperature: float = 0.2
    max_tokens: int = 800
    timeout_seconds: int = 60
    retry_attempts: int = 3
    retry_delay: float = 2.0
    
    @classmethod
    def from_env(cls) -> 'ModelConfig':
        """Create configuration from environment variables."""
        return cls(
            default_model=os.getenv('CPRA_DEFAULT_MODEL', cls.default_model),
            responsiveness_model=os.getenv('CPRA_RESPONSIVENESS_MODEL', cls.responsiveness_model),
            exemption_model=os.getenv('CPRA_EXEMPTION_MODEL', cls.exemption_model),
            temperature=float(os.getenv('CPRA_MODEL_TEMPERATURE', str(cls.temperature))),
            max_tokens=int(os.getenv('CPRA_MAX_TOKENS', str(cls.max_tokens))),
            timeout_seconds=int(os.getenv('CPRA_TIMEOUT_SECONDS', str(cls.timeout_seconds))),
            retry_attempts=int(os.getenv('CPRA_RETRY_ATTEMPTS', str(cls.retry_attempts))),
            retry_delay=float(os.getenv('CPRA_RETRY_DELAY', str(cls.retry_delay)))
        )


@dataclass
class ProcessingConfig:
    """Configuration for document processing settings."""
    batch_size: int = 5
    enable_parallel_processing: bool = False
    max_concurrent_requests: int = 2
    processing_timeout_minutes: int = 10
    auto_save_interval: int = 10  # Save session every N documents
    enable_progress_callbacks: bool = True
    
    @classmethod
    def from_env(cls) -> 'ProcessingConfig':
        """Create configuration from environment variables."""
        return cls(
            batch_size=int(os.getenv('CPRA_BATCH_SIZE', str(cls.batch_size))),
            enable_parallel_processing=os.getenv('CPRA_ENABLE_PARALLEL', 'false').lower() == 'true',
            max_concurrent_requests=int(os.getenv('CPRA_MAX_CONCURRENT', str(cls.max_concurrent_requests))),
            processing_timeout_minutes=int(os.getenv('CPRA_PROCESSING_TIMEOUT', str(cls.processing_timeout_minutes))),
            auto_save_interval=int(os.getenv('CPRA_AUTO_SAVE_INTERVAL', str(cls.auto_save_interval))),
            enable_progress_callbacks=os.getenv('CPRA_ENABLE_CALLBACKS', 'true').lower() == 'true'
        )


@dataclass
class DemoConfig:
    """Configuration for demo mode settings."""
    enable_by_default: bool = False
    default_speed: float = 1.0
    show_animations: bool = True
    show_resource_monitor: bool = True
    typewriter_effect: bool = False
    celebration_animations: bool = True
    ai_thinking_indicator: bool = True
    
    # Demo data paths
    demo_emails_path: str = "demo-files/synthetic_emails.txt"
    demo_requests_path: str = "demo-files/cpra_requests.txt"
    demo_guide_path: str = "demo-files/demo_cpra_requests.md"
    
    @classmethod
    def from_env(cls) -> 'DemoConfig':
        """Create configuration from environment variables."""
        return cls(
            enable_by_default=os.getenv('CPRA_DEMO_MODE', 'false').lower() == 'true',
            default_speed=float(os.getenv('CPRA_DEMO_SPEED', str(cls.default_speed))),
            show_animations=os.getenv('CPRA_SHOW_ANIMATIONS', 'true').lower() == 'true',
            show_resource_monitor=os.getenv('CPRA_SHOW_RESOURCES', 'true').lower() == 'true',
            typewriter_effect=os.getenv('CPRA_TYPEWRITER_EFFECT', 'false').lower() == 'true',
            celebration_animations=os.getenv('CPRA_CELEBRATIONS', 'true').lower() == 'true',
            ai_thinking_indicator=os.getenv('CPRA_AI_INDICATOR', 'true').lower() == 'true'
        )


@dataclass
class ExportConfig:
    """Configuration for export settings."""
    export_directory: str = "exports"
    pdf_page_size: str = "letter"
    pdf_font_family: str = "Helvetica"
    pdf_font_size: int = 11
    include_headers: bool = True
    include_footers: bool = True
    include_page_numbers: bool = True
    privilege_log_format: str = "both"  # "csv", "pdf", or "both"
    
    @classmethod
    def from_env(cls) -> 'ExportConfig':
        """Create configuration from environment variables."""
        return cls(
            export_directory=os.getenv('CPRA_EXPORT_DIR', cls.export_directory),
            pdf_page_size=os.getenv('CPRA_PDF_PAGE_SIZE', cls.pdf_page_size),
            pdf_font_family=os.getenv('CPRA_PDF_FONT', cls.pdf_font_family),
            pdf_font_size=int(os.getenv('CPRA_PDF_FONT_SIZE', str(cls.pdf_font_size))),
            include_headers=os.getenv('CPRA_PDF_HEADERS', 'true').lower() == 'true',
            include_footers=os.getenv('CPRA_PDF_FOOTERS', 'true').lower() == 'true',
            include_page_numbers=os.getenv('CPRA_PDF_PAGE_NUMBERS', 'true').lower() == 'true',
            privilege_log_format=os.getenv('CPRA_PRIVILEGE_LOG_FORMAT', cls.privilege_log_format)
        )


@dataclass
class SessionConfig:
    """Configuration for session management."""
    session_directory: str = "sessions"
    enable_auto_save: bool = True
    session_timeout_hours: int = 24
    max_session_size_mb: int = 100
    compression_enabled: bool = False
    
    @classmethod
    def from_env(cls) -> 'SessionConfig':
        """Create configuration from environment variables."""
        return cls(
            session_directory=os.getenv('CPRA_SESSION_DIR', cls.session_directory),
            enable_auto_save=os.getenv('CPRA_AUTO_SAVE', 'true').lower() == 'true',
            session_timeout_hours=int(os.getenv('CPRA_SESSION_TIMEOUT', str(cls.session_timeout_hours))),
            max_session_size_mb=int(os.getenv('CPRA_MAX_SESSION_SIZE', str(cls.max_session_size_mb))),
            compression_enabled=os.getenv('CPRA_COMPRESSION', 'false').lower() == 'true'
        )


@dataclass
class LoggingConfig:
    """Configuration for logging settings."""
    log_level: str = "INFO"
    log_directory: str = "logs"
    enable_file_logging: bool = False
    log_rotation: str = "daily"
    max_log_size_mb: int = 10
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """Create configuration from environment variables."""
        return cls(
            log_level=os.getenv('CPRA_LOG_LEVEL', cls.log_level),
            log_directory=os.getenv('CPRA_LOG_DIR', cls.log_directory),
            enable_file_logging=os.getenv('CPRA_FILE_LOGGING', 'false').lower() == 'true',
            log_rotation=os.getenv('CPRA_LOG_ROTATION', cls.log_rotation),
            max_log_size_mb=int(os.getenv('CPRA_MAX_LOG_SIZE', str(cls.max_log_size_mb))),
            log_format=os.getenv('CPRA_LOG_FORMAT', cls.log_format)
        )


class AppConfig:
    """Main application configuration."""
    
    def __init__(self):
        """Initialize application configuration."""
        self.model = ModelConfig.from_env()
        self.processing = ProcessingConfig.from_env()
        self.demo = DemoConfig.from_env()
        self.export = ExportConfig.from_env()
        self.session = SessionConfig.from_env()
        self.logging = LoggingConfig.from_env()
        
        # Create necessary directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary application directories."""
        directories = [
            self.export.export_directory,
            self.session.session_directory,
        ]
        
        if self.logging.enable_file_logging:
            directories.append(self.logging.log_directory)
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'model': self.model.__dict__,
            'processing': self.processing.__dict__,
            'demo': self.demo.__dict__,
            'export': self.export.__dict__,
            'session': self.session.__dict__,
            'logging': self.logging.__dict__
        }
    
    def update_from_dict(self, config_dict: Dict[str, Any]):
        """Update configuration from dictionary."""
        if 'model' in config_dict:
            for key, value in config_dict['model'].items():
                setattr(self.model, key, value)
        if 'processing' in config_dict:
            for key, value in config_dict['processing'].items():
                setattr(self.processing, key, value)
        if 'demo' in config_dict:
            for key, value in config_dict['demo'].items():
                setattr(self.demo, key, value)
        if 'export' in config_dict:
            for key, value in config_dict['export'].items():
                setattr(self.export, key, value)
        if 'session' in config_dict:
            for key, value in config_dict['session'].items():
                setattr(self.session, key, value)
        if 'logging' in config_dict:
            for key, value in config_dict['logging'].items():
                setattr(self.logging, key, value)
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        # Check model settings
        if self.model.temperature < 0 or self.model.temperature > 1:
            raise ValueError(f"Invalid temperature: {self.model.temperature}")
        if self.model.max_tokens < 1:
            raise ValueError(f"Invalid max_tokens: {self.model.max_tokens}")
        if self.model.timeout_seconds < 1:
            raise ValueError(f"Invalid timeout: {self.model.timeout_seconds}")
        
        # Check processing settings
        if self.processing.batch_size < 1:
            raise ValueError(f"Invalid batch_size: {self.processing.batch_size}")
        
        # Check demo data paths exist
        if self.demo.enable_by_default:
            demo_files = [
                self.demo.demo_emails_path,
                self.demo.demo_requests_path
            ]
            for file_path in demo_files:
                if not Path(file_path).exists():
                    raise FileNotFoundError(f"Demo file not found: {file_path}")
        
        return True


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = AppConfig()
        _config.validate()
    return _config


def reset_config():
    """Reset the global configuration instance."""
    global _config
    _config = None