import sqlite3
import tempfile
import unittest
from pathlib import Path

from fitness_manager.db import initialize, session
from fitness_manager.ingestion import create_inbound_event, confirm_event, parse_message, reject_event


class IngestionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / 'fitness.sqlite'
        initialize(self.db)

    def tearDown(self):
        self.temp.cleanup()

    def test_parse_measurements_with_decimal_comma(self):
        self.assertEqual(parse_message('peso 111,4 kg')['value'], 111.4)
        self.assertEqual(parse_message('cintura 108 cm')['kind'], 'waist')

    def test_run_scope_rejects_over_15_km(self):
        self.assertIsNone(parse_message('corrida 16 km em 90 min'))
        self.assertEqual(parse_message('corrida 4 km em 42 min')['distance_km'], 4.0)

    def test_ambiguous_message_is_not_parsed(self):
        self.assertIsNone(parse_message('hoje fiz um treino muito bom'))

    def test_inbound_event_is_idempotent(self):
        payload = parse_message('peso 111,4 kg')
        with session(self.db) as conn:
            first, inserted1 = create_inbound_event(conn, source='telegram', external_event_id='100', sender_id='1', chat_id='1', message_text='peso 111,4 kg', payload=payload)
            second, inserted2 = create_inbound_event(conn, source='telegram', external_event_id='100', sender_id='1', chat_id='1', message_text='peso 111,4 kg', payload=payload)
            self.assertTrue(inserted1)
            self.assertFalse(inserted2)
            self.assertEqual(first, second)

    def test_confirmation_writes_once(self):
        payload = parse_message('cintura 108 cm')
        with session(self.db) as conn:
            event_id, _ = create_inbound_event(conn, source='telegram', external_event_id='101', sender_id='1', chat_id='1', message_text='cintura 108 cm', payload=payload)
            summary = confirm_event(conn, event_id)
            self.assertIn('waist', summary)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM measurements WHERE kind='waist'").fetchone()[0], 1)
            with self.assertRaises(ValueError):
                confirm_event(conn, event_id)

    def test_cancel_does_not_write_health_data(self):
        payload = parse_message('peso 110 kg')
        with session(self.db) as conn:
            event_id, _ = create_inbound_event(conn, source='telegram', external_event_id='102', sender_id='1', chat_id='1', message_text='peso 110 kg', payload=payload)
            reject_event(conn, event_id)
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM measurements').fetchone()[0], 0)

    def test_unsupported_text_is_not_retained(self):
        with session(self.db) as conn:
            event_id, _ = create_inbound_event(conn, source='telegram', external_event_id='104', sender_id='1', chat_id='1', message_text='private unrelated text', payload=None)
            row = conn.execute('SELECT message_text,payload_json,status FROM integration_events WHERE id=?', (event_id,)).fetchone()
            self.assertNotIn('private unrelated text', row['message_text'])
            self.assertIsNone(row['payload_json'])
            self.assertEqual(row['status'], 'unsupported')

    def test_food_does_not_invent_macros(self):
        payload = parse_message('alimento almoco;arroz;150')
        with session(self.db) as conn:
            event_id, _ = create_inbound_event(conn, source='telegram', external_event_id='103', sender_id='1', chat_id='1', message_text='alimento almoco;arroz;150', payload=payload)
            confirm_event(conn, event_id)
            row = conn.execute('SELECT quantity_g,kcal,protein_g FROM food_logs').fetchone()
            self.assertEqual(row['quantity_g'], 150)
            self.assertIsNone(row['kcal'])
            self.assertIsNone(row['protein_g'])


if __name__ == '__main__':
    unittest.main()
