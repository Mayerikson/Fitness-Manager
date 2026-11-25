import os
import unittest
from unittest.mock import patch

from fitness_manager.local_llm import ask_local_model


class LocalLlmTests(unittest.TestCase):
    def test_missing_local_configuration_is_rejected(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'Modelo local nao configurado'):
                ask_local_model('Como estou evoluindo?')

    def test_remote_endpoint_is_rejected(self):
        env = {
            'FITNESS_MANAGER_LOCAL_LLM_URL': 'https://example.com/v1',
            'FITNESS_MANAGER_LOCAL_LLM_MODEL': 'model',
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'somente endpoints locais|endpoint local'):
                ask_local_model('Como estou evoluindo?')

    def test_endpoint_credentials_are_rejected(self):
        env = {
            'FITNESS_MANAGER_LOCAL_LLM_URL': 'http://user:pass@127.0.0.1:11434/v1',
            'FITNESS_MANAGER_LOCAL_LLM_MODEL': 'model',
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(RuntimeError):
                ask_local_model('Como estou evoluindo?')


if __name__ == '__main__':
    unittest.main()
