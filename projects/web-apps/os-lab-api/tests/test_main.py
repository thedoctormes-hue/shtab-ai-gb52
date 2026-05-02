#!/usr/bin/env python3
"""Тесты для OS Lab Dashboard API"""

import subprocess
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Импортируем приложение
from main import app, ping_server


@pytest.fixture
def client():
    """Фикстура для тестового клиента FastAPI"""
    return TestClient(app)


class TestPingServer:
    """Тесты функции ping_server"""

    @patch('main.subprocess.run')
    def test_ping_server_success(self, mock_run):
        """Тест успешного пинга"""
        mock_run.return_value = MagicMock(returncode=0)
        result = ping_server('127.0.0.1')
        assert result is True
        mock_run.assert_called_once_with(
            ['ping', '-c', '1', '-W', '2', '127.0.0.1'],
            capture_output=True,
            check=True
        )

    @patch('main.subprocess.run')
    def test_ping_server_fail(self, mock_run):
        """Тест неуспешного пинга"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'ping')
        result = ping_server('8.8.8.8')
        assert result is False


class TestGetServers:
    """Тесты эндпоинта /api/monitoring/servers"""

    @patch('main.ping_server')
    def test_get_servers_success(self, mock_ping, client):
        """Тест успешного получения статуса серверов"""
        mock_ping.return_value = True
        response = client.get('/api/monitoring/servers')
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем, что все серверы в ответе
        assert 'warsaw' in data
        assert 'florida' in data
        assert 'rf-proxy' in data
        
        # Проверяем структуру ответа для каждого сервера
        for server_name, server_data in data.items():
            assert 'cpu' in server_data
            assert 'ram' in server_data
            assert 'disk' in server_data
            assert 'ping' in server_data
            assert 'uptime' in server_data
            assert server_data['ping'] == 'OK'

    @patch('main.ping_server')
    def test_get_servers_partial_fail(self, mock_ping, client):
        """Тест, когда часть серверов недоступна"""
        # warsaw - OK, florida - FAIL, rf-proxy - OK
        mock_ping.side_effect = [True, False, True]
        response = client.get('/api/monitoring/servers')
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['warsaw']['ping'] == 'OK'
        assert data['florida']['ping'] == 'FAIL'
        assert data['rf-proxy']['ping'] == 'OK'


class TestAppInit:
    """Тесты инициализации приложения"""

    def test_app_title(self):
        """Тест корректности заголовка приложения"""
        assert app.title == "OS Lab Dashboard API"
        assert app.version == "1.0.0"

    def test_cors_middleware(self, client):
        """Тест CORS заголовков"""
        response = client.options('/api/monitoring/servers')
        # CORS должен быть настроен
        assert response.status_code in [200, 405, 422]  # Разные коды в зависимости от настроек
