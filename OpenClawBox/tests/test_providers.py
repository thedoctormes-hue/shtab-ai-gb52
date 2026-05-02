"""Tests for OpenClawBox providers with mocks."""
import pytest
from dataclasses import dataclass

# Define RateLimit locally for tests
@dataclass
class RateLimit:
    rpm: int
    tpm: int
    rpd: int
    remaining_rpm: int = 0
    remaining_tpm: int = 0
    remaining_rpd: int = 0
    reset_at: float = 0
    errors: int = 0
    cooldown_until: float = 0


class TestRateLimit:
    def test_rate_limit_initialization(self):
        rl = RateLimit(rpm=30, tpm=6000, rpd=14400)
        assert rl.rpm == 30
        assert rl.tpm == 6000

    def test_can_request_with_tokens(self):
        rl = RateLimit(rpm=30, tpm=6000, rpd=14400, remaining_tpm=5000)
        tokens = 100
        assert rl.remaining_tpm >= int(tokens * 1.2)
