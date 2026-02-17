"""Unit tests for the filename utilities in utils.filename module."""

from src.utils.filename import sanitize_filename


class TestSanitizeFilenameBasic:
    """Tests for basic sanitize_filename functionality."""

    def test_sanitize_simple_string(self):
        """Test sanitization of a simple string."""
        result = sanitize_filename("test")
        assert result == "test"

    def test_sanitize_with_spaces(self):
        """Test that spaces are replaced with underscores."""
        result = sanitize_filename("Sea Kayak Pro")
        assert result == "sea_kayak_pro"

    def test_sanitize_multiple_spaces(self):
        """Test that multiple spaces are replaced."""
        result = sanitize_filename("Test  With   Spaces")
        assert result == "test_with_spaces"

    def test_sanitize_leading_trailing_spaces(self):
        """Test that leading and trailing spaces are removed."""
        result = sanitize_filename("  Test String  ")
        assert result == "test_string"

    def test_sanitize_empty_string(self):
        """Test that empty string becomes 'unnamed'."""
        result = sanitize_filename("")
        assert result == "unnamed"

    def test_sanitize_whitespace_only(self):
        """Test that whitespace-only string becomes 'unnamed'."""
        result = sanitize_filename("   ")
        assert result == "unnamed"


class TestSanitizeFilenameSpecialCharacters:
    """Tests for sanitizing special characters."""

    def test_sanitize_removes_slashes(self):
        """Test that forward slashes are removed."""
        result = sanitize_filename("My/Kayak/Design")
        assert result == "mykayakdesign"

    def test_sanitize_removes_backslashes(self):
        """Test that backslashes are removed."""
        result = sanitize_filename("My\\Kayak\\Design")
        assert result == "mykayakdesign"

    def test_sanitize_removes_special_chars(self):
        """Test that various special characters are removed."""
        result = sanitize_filename("Test@#$%^&*()Design")
        assert result == "testdesign"

    def test_sanitize_keeps_hyphens(self):
        """Test that hyphens are preserved."""
        result = sanitize_filename("Test-Kayak-01")
        assert result == "test-kayak-01"

    def test_sanitize_keeps_underscores(self):
        """Test that underscores are preserved."""
        result = sanitize_filename("Test_Kayak_01")
        assert result == "test_kayak_01"

    def test_sanitize_keeps_numbers(self):
        """Test that numbers are preserved."""
        result = sanitize_filename("Kayak 123")
        assert result == "kayak_123"

    def test_sanitize_mixed_valid_invalid(self):
        """Test sanitization with mix of valid and invalid characters."""
        result = sanitize_filename("Kayak-2024!@#")
        assert result == "kayak-2024"


class TestSanitizeFilenameCustomReplacement:
    """Tests for custom replacement character."""

    def test_sanitize_with_hyphen_replacement(self):
        """Test using hyphen as replacement for spaces."""
        result = sanitize_filename("Sea Kayak Pro", replacement="-")
        assert result == "sea-kayak-pro"

    def test_sanitize_with_empty_replacement(self):
        """Test using empty string as replacement."""
        result = sanitize_filename("Sea Kayak Pro", replacement="")
        assert result == "seakayakpro"

    def test_sanitize_with_dot_replacement(self):
        """Test using dot as replacement for spaces."""
        result = sanitize_filename("Sea Kayak Pro", replacement=".")
        assert result == "sea.kayak.pro"


class TestSanitizeFilenameCaseConversion:
    """Tests for case conversion."""

    def test_sanitize_converts_to_lowercase(self):
        """Test that result is in lowercase."""
        result = sanitize_filename("UPPERCASE")
        assert result == "uppercase"

    def test_sanitize_mixed_case(self):
        """Test sanitization with mixed case."""
        result = sanitize_filename("MiXeD CaSe")
        assert result == "mixed_case"


class TestSanitizeFilenameRealWorldExamples:
    """Tests with real-world filename examples."""

    def test_sanitize_kayak_model_name(self):
        """Test with typical kayak model name."""
        result = sanitize_filename("Sea Kayak Pro v2.1")
        assert result == "sea_kayak_pro_v21"

    def test_sanitize_with_parentheses(self):
        """Test with parentheses in name."""
        result = sanitize_filename("Kayak Design (Final)")
        assert result == "kayak_design_final"

    def test_sanitize_with_brackets(self):
        """Test with brackets in name."""
        result = sanitize_filename("Kayak [2024]")
        assert result == "kayak_2024"

    def test_sanitize_with_quotes(self):
        """Test with quotes in name."""
        result = sanitize_filename('"My Kayak"')
        assert result == "my_kayak"

    def test_sanitize_with_apostrophe(self):
        """Test with apostrophe in name."""
        result = sanitize_filename("John's Kayak")
        assert result == "johns_kayak"

    def test_sanitize_with_comma(self):
        """Test with comma in name."""
        result = sanitize_filename("Kayak, Model A")
        assert result == "kayak_model_a"

    def test_sanitize_with_period(self):
        """Test with period in name."""
        result = sanitize_filename("Kayak.Design")
        assert result == "kayakdesign"

    def test_sanitize_complex_filename(self):
        """Test with complex real-world filename."""
        result = sanitize_filename("My Awesome Kayak (v2.0) - Final [2024]!")
        assert result == "my_awesome_kayak_v20_-_final_2024"


class TestSanitizeFilenameEdgeCases:
    """Tests for edge cases."""

    def test_sanitize_only_special_chars(self):
        """Test string with only special characters becomes 'unnamed'."""
        result = sanitize_filename("!@#$%^&*()")
        assert result == "unnamed"

    def test_sanitize_unicode_characters(self):
        """Test handling of unicode characters."""
        # Unicode characters should be removed if not alphanumeric
        result = sanitize_filename("Kayak™")
        assert result == "kayak"

    def test_sanitize_very_long_string(self):
        """Test with a very long string."""
        long_name = "A" * 200 + " Kayak"
        result = sanitize_filename(long_name)
        # Should still work and convert properly
        assert "kayak" in result
        assert "_" in result

    def test_sanitize_single_character(self):
        """Test with single character."""
        result = sanitize_filename("A")
        assert result == "a"

    def test_sanitize_numbers_only(self):
        """Test with only numbers."""
        result = sanitize_filename("123456")
        assert result == "123456"

    def test_sanitize_hyphen_and_underscore_only(self):
        """Test with only hyphens and underscores."""
        result = sanitize_filename("_-_-_")
        assert result == "_-_-_"
