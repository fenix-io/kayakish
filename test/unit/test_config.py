"""Unit tests for the config module."""

import pytest
from pathlib import Path
from src.config import Settings, settings


class TestSettingsDefaults:
    """Tests for Settings default values."""

    def test_default_data_path(self):
        """Test that default data_path is Path('data')."""
        s = Settings()
        assert isinstance(s.data_path, Path)
        assert s.data_path == Path("data")

    def test_default_api_host(self):
        """Test that default api_host is '0.0.0.0'."""
        s = Settings()
        assert s.api_host == "0.0.0.0"

    def test_default_api_port(self):
        """Test that default api_port is 8000."""
        s = Settings()
        assert s.api_port == 8000

    def test_default_app_name(self):
        """Test that default app_name is set."""
        s = Settings()
        assert s.app_name == "Kayakish - Hull Analysis Tool"

    def test_default_debug(self):
        """Test that default debug is False."""
        s = Settings()
        assert s.debug == False


class TestSettingsTypes:
    """Tests for Settings attribute types."""

    def test_data_path_is_path(self):
        """Test that data_path is a Path object."""
        s = Settings()
        assert isinstance(s.data_path, Path)

    def test_api_host_is_string(self):
        """Test that api_host is a string."""
        s = Settings()
        assert isinstance(s.api_host, str)

    def test_api_port_is_int(self):
        """Test that api_port is an integer."""
        s = Settings()
        assert isinstance(s.api_port, int)

    def test_app_name_is_string(self):
        """Test that app_name is a string."""
        s = Settings()
        assert isinstance(s.app_name, str)

    def test_debug_is_bool(self):
        """Test that debug is a boolean."""
        s = Settings()
        assert isinstance(s.debug, bool)


class TestGlobalSettings:
    """Tests for global settings instance."""

    def test_global_settings_exists(self):
        """Test that global settings instance exists."""
        assert settings is not None

    def test_global_settings_is_settings_instance(self):
        """Test that global settings is a Settings instance."""
        assert isinstance(settings, Settings)

    def test_global_settings_has_data_path(self):
        """Test that global settings has data_path."""
        assert hasattr(settings, "data_path")
        assert isinstance(settings.data_path, Path)

    def test_global_settings_has_api_host(self):
        """Test that global settings has api_host."""
        assert hasattr(settings, "api_host")

    def test_global_settings_has_api_port(self):
        """Test that global settings has api_port."""
        assert hasattr(settings, "api_port")


class TestSettingsConfiguration:
    """Tests for Settings configuration."""

    def test_settings_uses_pydantic_base_settings(self):
        """Test that Settings uses Pydantic BaseSettings."""
        from pydantic_settings import BaseSettings

        assert issubclass(Settings, BaseSettings)

    def test_settings_has_model_config(self):
        """Test that Settings has model_config."""
        assert hasattr(Settings, "model_config")

    def test_model_config_env_file(self):
        """Test that model_config specifies .env file."""
        config = Settings.model_config
        assert "env_file" in config
        assert config["env_file"] == ".env"

    def test_model_config_encoding(self):
        """Test that model_config specifies UTF-8 encoding."""
        config = Settings.model_config
        assert "env_file_encoding" in config
        assert config["env_file_encoding"] == "utf-8"


class TestSettingsValidation:
    """Tests for Settings validation."""

    def test_can_create_settings_with_custom_port(self):
        """Test creating Settings with custom port."""
        # Use model_validate to create with custom values
        s = Settings(api_port=9000)
        assert s.api_port == 9000

    def test_can_create_settings_with_custom_host(self):
        """Test creating Settings with custom host."""
        s = Settings(api_host="127.0.0.1")
        assert s.api_host == "127.0.0.1"

    def test_can_create_settings_with_debug_true(self):
        """Test creating Settings with debug=True."""
        s = Settings(debug=True)
        assert s.debug == True

    def test_can_create_settings_with_custom_data_path(self):
        """Test creating Settings with custom data_path."""
        custom_path = Path("/custom/data")
        s = Settings(data_path=custom_path)
        assert s.data_path == custom_path


class TestSettingsEdgeCases:
    """Tests for edge cases."""

    def test_settings_port_accepts_valid_range(self):
        """Test that api_port accepts valid port numbers."""
        s = Settings(api_port=8080)
        assert s.api_port == 8080

        s2 = Settings(api_port=3000)
        assert s2.api_port == 3000

    def test_settings_accepts_localhost(self):
        """Test that api_host accepts localhost."""
        s = Settings(api_host="localhost")
        assert s.api_host == "localhost"

    def test_settings_app_name_can_be_customized(self):
        """Test that app_name can be customized."""
        custom_name = "Custom Kayak Tool"
        s = Settings(app_name=custom_name)
        assert s.app_name == custom_name

    def test_multiple_settings_instances_independent(self):
        """Test that multiple Settings instances are independent."""
        s1 = Settings(api_port=8000)
        s2 = Settings(api_port=9000)

        assert s1.api_port == 8000
        assert s2.api_port == 9000
        assert s1.api_port != s2.api_port
