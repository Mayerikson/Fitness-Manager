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
        self.assertEqual(parse_message('peso 72,4 kg')['value'], 72.4)
        self.assertEqual(parse_message('cintura 83 cm')['kind'], 'waist')

    def test_natural_language_weight_and_waist(self):
        self.assertEqual(parse_message('hoje estou com 72,4 kg')['value'], 72.4)
        self.assertEqual(parse_message('minha cintura esta 83 cm')['kind'], 'waist')

    def test_natural_language_workout(self):
        payload = parse_message('Hoje fiz supino com halteres, três séries de doze, usando vinte quilos em cada mão')
        self.assertIsNotNone(payload)
        self.assertEqual(payload['exercise'], 'supino com halteres')
        self.assertEqual(payload['sets'], 3)
        self.assertEqual(payload['reps'], 12)
        self.assertEqual(payload['load_kg'], 20.0)

    def test_spoken_weight_and_run_numbers(self):
        self.assertEqual(parse_message('hoje estou com cento e dezessete quilos')['value'], 117.0)
        run = parse_message('hoje corri quatro quilometros em quarenta e dois minutos')
        self.assertEqual(run['distance_km'], 4.0)
        self.assertEqual(run['duration_min'], 42.0)

    def test_regression_common_spoken_phrases_from_user_report(self):
        cases = [
            ("estou com 72 quilos", "measurement"),
            ("Peso 72 quilos.", "measurement"),
            ("peso 72 kg.", "measurement"),
            ("meu peso e cento e quinze quilos", "measurement"),
            ("corri 4 quilômetros em 30 minutos", "run"),
            ("fiz uma corrida de quatro quilômetros em trinta minutos", "run"),
            ("fiz supino reto, três séries de doze repetições com vinte quilos.", "workout"),
        ]
        for phrase, expected_type in cases:
            with self.subTest(phrase=phrase):
                payload = parse_message(phrase)
                self.assertIsNotNone(payload)
                self.assertEqual(payload["type"], expected_type)

    def test_spoken_number_range_101_to_199_is_generated(self):
        self.assertEqual(parse_message("meu peso e cento e um quilos")["value"], 101.0)
        self.assertEqual(parse_message("meu peso e cento e quinze quilos")["value"], 115.0)
        self.assertEqual(parse_message("meu peso e cento e noventa e nove quilos")["value"], 199.0)

    def test_number_word_does_not_mutate_exercise_name(self):
        payload = parse_message("fiz rosca com um braco, tres series de doze repeticoes com dez quilos")
        self.assertIsNotNone(payload)
        self.assertEqual(payload["exercise"], "rosca com um braco")

    def test_run_scope_rejects_over_15_km(self):
        self.assertIsNone(parse_message('corrida 16 km em 90 min'))
        self.assertEqual(parse_message('corrida 4 km em 42 min')['distance_km'], 4.0)

    def test_ambiguous_message_is_not_parsed(self):
        self.assertIsNone(parse_message('hoje fiz um treino muito bom'))

    def test_inbound_event_is_idempotent(self):
        payload = parse_message('peso 72,4 kg')
        with session(self.db) as conn:
            first, inserted1 = create_inbound_event(conn, source='telegram', external_event_id='100', sender_id='1', chat_id='1', message_text='peso 72,4 kg', payload=payload)
            second, inserted2 = create_inbound_event(conn, source='telegram', external_event_id='100', sender_id='1', chat_id='1', message_text='peso 72,4 kg', payload=payload)
            self.assertTrue(inserted1)
            self.assertFalse(inserted2)
            self.assertEqual(first, second)

    def test_confirmation_writes_once(self):
        payload = parse_message('cintura 83 cm')
        with session(self.db) as conn:
            event_id, _ = create_inbound_event(conn, source='telegram', external_event_id='101', sender_id='1', chat_id='1', message_text='cintura 83 cm', payload=payload)
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



    def test_user_reported_common_phrases_with_punctuation_and_accents(self):
        cases = [
            ("estou com 72 quilos", "measurement"),
            ("Peso 72 quilos.", "measurement"),
            ("peso 72 kg.", "measurement"),
            ("meu peso é cento e quinze quilos", "measurement"),
            ("corri 4 quilômetros em 30 minutos", "run"),
            ("fiz uma corrida de quatro quilômetros em trinta minutos", "run"),
            ("fiz supino reto, três séries de doze repetições com vinte quilos.", "workout"),
        ]
        for phrase, expected_type in cases:
            with self.subTest(phrase=phrase):
                payload = parse_message(phrase)
                self.assertIsNotNone(payload)
                self.assertEqual(payload["type"], expected_type)

    def test_spoken_numbers_from_101_to_199(self):
        expected = {
            "cento e um": 101.0,
            "cento e sete": 107.0,
            "cento e quinze": 115.0,
            "cento e noventa e nove": 199.0,
        }
        for words, value in expected.items():
            with self.subTest(words=words):
                self.assertEqual(parse_message(f"meu peso é {words} quilos")["value"], value)

    def test_accented_exercise_name_is_preserved_after_normalization(self):
        payload = parse_message("fiz elevação pélvica, três séries de doze repetições com vinte quilos.")
        self.assertIsNotNone(payload)
        self.assertEqual(payload["exercise"], "elevação pélvica")

    def test_one_in_exercise_name_is_not_converted_to_digit(self):
        payload = parse_message("fiz rosca com um braço, três séries de doze repetições com dez quilos.")
        self.assertIsNotNone(payload)
        self.assertEqual(payload["exercise"], "rosca com um braço")

    def test_zero_weight_and_waist_are_rejected(self):
        self.assertIsNone(parse_message("peso 0"))
        self.assertIsNone(parse_message("cintura 0"))
        self.assertIsNone(parse_message("meu peso atual e zero kg"))

    def test_zero_sets_reps_and_food_quantity_are_rejected(self):
        self.assertIsNone(parse_message("treino A;Supino;0;12;20"))
        self.assertIsNone(parse_message("treino A;Supino;3;0;20"))
        self.assertIsNone(parse_message("alimento almoco;arroz;0"))

class SpokenDecimalAndOriginalTextTests(unittest.TestCase):
    def test_spoken_decimal_weight(self):
        for text in ("peso setenta e dois vírgula quatro",
                     "Peso 72 vírgula 4 quilos.",
                     "estou com setenta e dois virgula quatro quilos"):
            with self.subTest(text=text):
                self.assertEqual(parse_message(text)["value"], 72.4)

    def test_decimal_keeps_leading_zero(self):
        self.assertEqual(parse_message("peso 72 vírgula 05")["value"], 72.05)

    def test_commands_keep_accents_and_case(self):
        food = parse_message("alimento Almoço;Pão francês;50")
        self.assertEqual((food["meal"], food["food"]), ("Almoço", "Pão francês"))
        workout = parse_message("treino A;Elevação pélvica (barra);3;12;20")
        self.assertEqual((workout["session"], workout["exercise"]), ("A", "Elevação pélvica (barra)"))


if __name__ == '__main__':
    unittest.main()
