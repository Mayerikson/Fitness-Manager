import tempfile
import unittest
from pathlib import Path

from fitness_manager.db import initialize, session
from scripts.telegram_gateway import _command_payload, handle_message


class FakeTelegram:
    def __init__(self):
        self.messages = []
    def send(self, chat_id, text):
        self.messages.append((chat_id, text))


class TelegramGatewayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / 'fitness.sqlite'
        initialize(self.db)
        self.old_db_path = None

    def tearDown(self):
        self.temp.cleanup()

    def test_command_parser(self):
        self.assertEqual(_command_payload('/peso 111,4')['value'], 111.4)
        self.assertEqual(_command_payload('/corrida 4;42')['distance_km'], 4.0)
        self.assertEqual(_command_payload('/treino A;Supino;3;12;20')['sets'], 3)
        self.assertIsNone(_command_payload('/corrida 16;90'))

    def test_authorized_private_user_gets_pending_confirmation(self):
        import fitness_manager.db as db_module
        original = db_module.DB_PATH
        db_module.DB_PATH = self.db
        try:
            fake = FakeTelegram()
            handle_message(fake, {'message_id': 1, 'text': '/peso 111,4', 'from': {'id': 42}, 'chat': {'id': 42, 'type': 'private'}}, 42)
            self.assertEqual(len(fake.messages), 1)
            self.assertIn('/confirmar', fake.messages[0][1])
            with session(self.db) as conn:
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM measurements').fetchone()[0], 0)
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM integration_events WHERE status='pending'").fetchone()[0], 1)
        finally:
            db_module.DB_PATH = original

    def test_duplicate_message_is_not_created_twice(self):
        import fitness_manager.db as db_module
        original = db_module.DB_PATH
        db_module.DB_PATH = self.db
        try:
            fake = FakeTelegram()
            message = {'message_id': 4, 'text': '/peso 111,4', 'from': {'id': 42}, 'chat': {'id': 42, 'type': 'private'}}
            handle_message(fake, message, 42)
            handle_message(fake, message, 42)
            with session(self.db) as conn:
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM integration_events').fetchone()[0], 1)
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM measurements').fetchone()[0], 0)
            self.assertIn('ja foi recebida', fake.messages[-1][1])
        finally:
            db_module.DB_PATH = original

    def test_unauthorized_sender_is_ignored(self):
        fake = FakeTelegram()
        handle_message(fake, {'message_id': 2, 'text': '/peso 111', 'from': {'id': 99}, 'chat': {'id': 99, 'type': 'private'}}, 42)
        self.assertEqual(fake.messages, [])

    def test_group_messages_are_ignored(self):
        fake = FakeTelegram()
        handle_message(fake, {'message_id': 3, 'text': '/peso 111', 'from': {'id': 42}, 'chat': {'id': -100, 'type': 'group'}}, 42)
        self.assertEqual(fake.messages, [])


if __name__ == '__main__':
    unittest.main()
