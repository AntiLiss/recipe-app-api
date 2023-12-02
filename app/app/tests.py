from django.test import SimpleTestCase
from . import calculator


class CalculatorTests(SimpleTestCase):
    def test_get_sum_of_numbers(self):
        res = calculator.get_sum(1, 9)
        self.assertEqual(res, 10)

    def test_get_square_of_number(self):
        res = calculator.get_square(2)
        self.assertEqual(res, 4)

    def test_subtract_numbers(self):
        res = calculator.subtract(6, 10)
        self.assertEqual(res, 4)