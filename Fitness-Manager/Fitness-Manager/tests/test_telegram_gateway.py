import tempfile
import unittest
import sqlite3
from unittest.mock import patch
from pathlib import Path

from fitness_manager.db import initialize, session
from scripts.telegram_gateway import _command_payload, handle_message, process_updates


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
        self.assertEqual(_command_payload('/peso 72,4')['value'], 72.4)
        self.assertEqual(_command_payload('/corrida 4;42')['distance_km'], 4.0)
        self.assertEqual(_command_payload('/treino A;Supino;3;12;20')['sets'], 3)
        self.assertIsNone(_command_payload('/corrida 16;90'))

    def test_authorized_private_user_gets_pending_confirmation(self):
        import fitness_manager.db as db_module
        original = db_module.DB_PATH
        db_module.DB_PATH = self.db
        try:
            fake = FakeTelegram()
            handle_message(fake, {'message_id': 1, 'text': '/peso 72,4', 'from': {'id': 42}, 'chat': {'id': 42, 'type': 'private'}}, 42)
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
            message = {'message_id': 4, 'text': '/peso 72,4', 'from': {'id': 42}, 'chat': {'id': 42, 'type': 'private'}}
            handle_message(fake, message, 42)
            handle_message(fake, message, 42)
            with session(self.db) as conn:
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM integration_events').fetchone()[0], 1)
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM measurements').fetchone()[0], 0)
            self.assertIn('ja foi recebida', fake.messages[-1][1])
        finally:
            db_module.DB_PATH = original

    def test_invalid_zero_weight_is_not_queued(self):
        import fitness_manager.db as db_module
        original = db_module.DB_PATH
        db_module.DB_PATH = self.db
        try:
            fake = FakeTelegram()
            handle_message(fake, {'message_id': 60, 'text': '/peso 0', 'from': {'id': 42}, 'chat': {'id': 42, 'type': 'private'}}, 42)
            with session(self.db) as conn:
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM measurements').fetchone()[0], 0)
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM integration_events WHERE status='pending'").fetchone()[0], 0)
        finally:
            db_module.DB_PATH = original

    def test_integrity_error_on_confirmation_is_terminal_and_handled(self):
        import fitness_manager.db as db_module
        from fitness_manager.ingestion import create_inbound_event
        original = db_module.DB_PATH
        db_module.DB_PATH = self.db
        try:
            fake = FakeTelegram()
            with session(self.db) as conn:
                event_id, _ = create_inbound_event(conn, source='telegram', external_event_id='61', sender_id='42', chat_id='42', message_text='peso 0', payload={'type':'measurement','kind':'weight','value':0,'unit':'kg','date':'2026-11-25'})
            handle_message(fake, {'message_id': 62, 'text': f'/confirmar {event_id}', 'from': {'id': 42}, 'chat': {'id': 42, 'type': 'private'}}, 42)
            with session(self.db) as conn:
                status = conn.execute('SELECT status FROM integration_events WHERE id=?', (event_id,)).fetchone()[0]
                self.assertEqual(status, 'error')
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM measurements').fetchone()[0], 0)
            self.assertIn('estado de erro', fake.messages[-1][1])
        finally:
            db_module.DB_PATH = original

    def test_poison_update_does_not_block_following_updates_and_offset_advances(self):
        import fitness_manager.db as db_module
        from unittest.mock import patch
        original = db_module.DB_PATH
        db_module.DB_PATH = self.db
        try:
            fake = FakeTelegram()
            updates = [
                {'update_id': 100, 'message': {'message_id': 1, 'text': '/peso 70', 'from': {'id': 42}, 'chat': {'id': 42, 'type': 'private'}}},
                {'update_id': 101, 'message': {'message_id': 2, 'text': '/cintura 90', 'from': {'id': 42}, 'chat': {'id': 42, 'type': 'private'}}},
            ]
            real = handle_message
            calls = {'count': 0}
            def flaky(client, message, allowed):
                calls['count'] += 1
                if calls['count'] == 1:
                    raise sqlite3.IntegrityError('synthetic constraint failure')
                return real(client, message, allowed)
            with patch('scripts.telegram_gateway.handle_message', side_effect=flaky):
                final_offset = process_updates(fake, updates, 42, None)
            self.assertEqual(final_offset, 102)
            with session(self.db) as conn:
                stored = conn.execute("SELECT state_value FROM integration_state WHERE state_key='telegram_update_offset'").fetchone()[0]
                self.assertEqual(stored, '102')
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM integration_events WHERE status='pending'").fetchone()[0], 1)
        finally:
            db_module.DB_PATH = original

    def test_unauthorized_sender_is_ignored(self):
        fake = FakeTelegram()
        handle_message(fake, {'message_id': 2, 'text': '/peso 72', 'from': {'id': 99}, 'chat': {'id': 99, 'type': 'private'}}, 42)
        self.assertEqual(fake.messages, [])

    def test_group_messages_are_ignored(self):
        fake = FakeTelegram()
        handle_message(fake, {'message_id': 3, 'text': '/peso 72', 'from': {'id': 42}, 'chat': {'id': -100, 'type': 'group'}}, 42)
        self.assertEqual(fake.messages, [])


    def test_voice_transcript_is_previewed_and_requires_confirmation(self):
        import fitness_manager.db as db_module
        original = db_module.DB_PATH
        db_module.DB_PATH = self.db
        try:
            class VoiceTelegram(FakeTelegram):
                def download_audio(self, file_id, max_bytes):
                    return b"fake-audio-bytes"

            fake = VoiceTelegram()
            message = {
                'message_id': 50,
                'voice': {'file_id': 'voice-file', 'file_size': 128, 'duration': 4, 'mime_type': 'audio/ogg'},
                'from': {'id': 42},
                'chat': {'id': 42, 'type': 'private'},
            }
            transcribed_paths = []
            def fake_transcribe(path, language="pt"):
                transcribed_paths.append(Path(path))
                return {
                    'text': 'meu peso atual e 72,4 kg', 'language': 'pt', 'duration_sec': 4,
                    'engine': 'faster-whisper-local', 'model': 'base'
                }
            with patch('scripts.telegram_gateway.transcribe_audio_local', side_effect=fake_transcribe):
                handle_message(fake, message, 42)
            self.assertEqual(len(transcribed_paths), 1)
            self.assertFalse(transcribed_paths[0].exists(), 'temporary audio must be deleted after transcription')
            self.assertIn('Transcricao local', fake.messages[-1][1])
            self.assertIn('/confirmar', fake.messages[-1][1])
            with session(self.db) as conn:
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM measurements').fetchone()[0], 0)
                event = conn.execute("SELECT id,source,status FROM integration_events").fetchone()
                self.assertEqual(event['source'], 'telegram_voice')
                self.assertEqual(event['status'], 'pending')
            with session(self.db) as conn:
                from fitness_manager.ingestion import confirm_event
                confirm_event(conn, event['id'])
            with session(self.db) as conn:
                row = conn.execute("SELECT value,source FROM measurements").fetchone()
                self.assertEqual(row['value'], 72.4)
                self.assertEqual(row['source'], 'telegram_voice')
        finally:
            db_module.DB_PATH = original

    def test_voice_unknown_transcript_does_not_create_health_record(self):
        import fitness_manager.db as db_module
        original = db_module.DB_PATH
        db_module.DB_PATH = self.db
        try:
            class VoiceTelegram(FakeTelegram):
                def download_audio(self, file_id, max_bytes):
                    return b"fake-audio-bytes"

            fake = VoiceTelegram()
            message = {
                'message_id': 51,
                'voice': {'file_id': 'voice-file', 'file_size': 128, 'duration': 4},
                'from': {'id': 42},
                'chat': {'id': 42, 'type': 'private'},
            }
            with patch('scripts.telegram_gateway.transcribe_audio_local', return_value={
                'text': 'amanha talvez eu treine', 'language': 'pt', 'duration_sec': 4,
                'engine': 'faster-whisper-local', 'model': 'base'
            }):
                handle_message(fake, message, 42)
            self.assertIn('Nada foi gravado', fake.messages[-1][1])
            with session(self.db) as conn:
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM measurements').fetchone()[0], 0)
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM integration_events').fetchone()[0], 1)
                self.assertEqual(conn.execute('SELECT status FROM integration_events').fetchone()[0], 'unsupported')
        finally:
            db_module.DB_PATH = original

    def test_unauthorized_voice_is_ignored_before_download(self):
        class VoiceTelegram(FakeTelegram):
            def download_audio(self, file_id, max_bytes):
                raise AssertionError('unauthorized sender must not trigger download')
        fake = VoiceTelegram()
        message = {
            'message_id': 52,
            'voice': {'file_id': 'voice-file', 'file_size': 128, 'duration': 4},
            'from': {'id': 99},
            'chat': {'id': 99, 'type': 'private'},
        }
        handle_message(fake, message, 42)
        self.assertEqual(fake.messages, [])



if __name__ == '__main__':
    unittest.main()
