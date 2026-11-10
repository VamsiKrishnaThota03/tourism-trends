"""
Tests for the deployment security posture.

`manage.py check --deploy` reported SECURE_HSTS_SECONDS and
SECURE_SSL_REDIRECT as missing (W004, W008). They are now set, and these tests
keep them set — a settings file is exactly the kind of thing that gets edited
without anyone re-running the deploy check.

The settings are applied under `if not DEBUG`, so each test re-imports the
module with DEBUG forced off rather than relying on the test runner's
configuration (which runs with DEBUG on).
"""

import importlib
import os
import sys
import unittest
from unittest import mock


def production_settings():
    """Import tourism_analyzer.settings with DEBUG off, and return the module."""
    env = {
        'DJANGO_DEBUG': 'false',
        'DJANGO_SECRET_KEY': 'test-only-key-' + 'x' * 60,
    }
    with mock.patch.dict(os.environ, env, clear=False):
        # Drop any cached copy so the module-level `if not DEBUG` block re-runs.
        sys.modules.pop('tourism_analyzer.settings', None)
        module = importlib.import_module('tourism_analyzer.settings')
        importlib.reload(module)
        return module


class ProductionSecuritySettings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = production_settings()

    @classmethod
    def tearDownClass(cls):
        # Leave the import cache as the test runner expects to find it.
        sys.modules.pop('tourism_analyzer.settings', None)

    def test_debug_is_off(self):
        self.assertFalse(self.settings.DEBUG)

    def test_ssl_redirect_is_enabled(self):
        # security.W008
        self.assertTrue(self.settings.SECURE_SSL_REDIRECT)

    def test_hsts_is_enabled_for_a_year(self):
        # security.W004
        self.assertGreaterEqual(self.settings.SECURE_HSTS_SECONDS, 31536000)
        self.assertTrue(self.settings.SECURE_HSTS_INCLUDE_SUBDOMAINS)

    def test_hsts_preload_is_off_by_default(self):
        # Deliberate: submitting a domain to the browser preload list is
        # permanent, so it must be an explicit choice rather than a default.
        self.assertFalse(self.settings.SECURE_HSTS_PRELOAD)

    def test_the_preload_check_is_silenced_only_while_preload_is_off(self):
        # Acknowledging W021 keeps `check --deploy` clean, so a genuinely new
        # warning stands out instead of being lost in standing noise. The
        # silence must be scoped to that one check and must disappear when
        # someone opts in — otherwise it is a blanket suppression.
        self.assertEqual(self.settings.SILENCED_SYSTEM_CHECKS, ['security.W021'])

        env = {
            'DJANGO_DEBUG': 'false',
            'DJANGO_SECRET_KEY': 'test-only-key-' + 'x' * 60,
            'DJANGO_HSTS_PRELOAD': 'true',
        }
        with mock.patch.dict(os.environ, env, clear=False):
            sys.modules.pop('tourism_analyzer.settings', None)
            opted_in = importlib.import_module('tourism_analyzer.settings')
            importlib.reload(opted_in)
            self.assertTrue(opted_in.SECURE_HSTS_PRELOAD)
            self.assertFalse(getattr(opted_in, 'SILENCED_SYSTEM_CHECKS', []))
        sys.modules.pop('tourism_analyzer.settings', None)

    def test_cookies_are_secure_httponly_and_samesite(self):
        self.assertTrue(self.settings.SESSION_COOKIE_SECURE)
        self.assertTrue(self.settings.CSRF_COOKIE_SECURE)
        self.assertTrue(self.settings.SESSION_COOKIE_HTTPONLY)
        self.assertEqual(self.settings.SESSION_COOKIE_SAMESITE, 'Lax')
        self.assertEqual(self.settings.CSRF_COOKIE_SAMESITE, 'Lax')

    def test_content_sniffing_framing_and_referrer_are_locked_down(self):
        self.assertTrue(self.settings.SECURE_CONTENT_TYPE_NOSNIFF)
        self.assertEqual(self.settings.X_FRAME_OPTIONS, 'DENY')
        self.assertEqual(self.settings.SECURE_REFERRER_POLICY, 'strict-origin-when-cross-origin')

    def test_allowed_hosts_is_not_a_wildcard_by_default(self):
        # '*' would let the app serve any Host header, which enables cache
        # poisoning and password-reset link forgery.
        self.assertNotIn('*', self.settings.ALLOWED_HOSTS)

    def test_secret_key_has_no_insecure_default_in_production(self):
        # The local-dev fallback must only apply when DEBUG is on.
        self.assertFalse(self.settings.SECRET_KEY.startswith('django-insecure-'))


class SecretKeyEnforcement(unittest.TestCase):
    def test_missing_secret_key_raises_when_debug_is_off(self):
        from django.core.exceptions import ImproperlyConfigured

        env = {'DJANGO_DEBUG': 'false', 'DJANGO_SECRET_KEY': ''}
        with mock.patch.dict(os.environ, env, clear=False):
            sys.modules.pop('tourism_analyzer.settings', None)
            with self.assertRaises(ImproperlyConfigured):
                importlib.import_module('tourism_analyzer.settings')
        sys.modules.pop('tourism_analyzer.settings', None)

    def test_debug_allows_the_local_fallback_key(self):
        env = {'DJANGO_DEBUG': 'true', 'DJANGO_SECRET_KEY': ''}
        with mock.patch.dict(os.environ, env, clear=False):
            sys.modules.pop('tourism_analyzer.settings', None)
            module = importlib.import_module('tourism_analyzer.settings')
            importlib.reload(module)
            self.assertTrue(module.SECRET_KEY.startswith('django-insecure-'))
        sys.modules.pop('tourism_analyzer.settings', None)
