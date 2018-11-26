import unittest
import time
from peano.integer import Integer, integer
from peano.natural_number import natural_number
import sys

sys.setrecursionlimit(1 << 16)


class TestInteger(unittest.TestCase):
    def setUp(self):
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("{}: {}ms".format(self.id(), int(t * 1000)))

    def test_eq(self):
        for i in range(-10, 10):
            for j in range(abs(i), 20):
                self.assertEqual(integer(i), Integer(natural_number(i + j), natural_number(j)))

    def test_add(self):
        for i in range(-10, 10):
            for j in range(-10, 10):
                self.assertEqual(integer(i) + integer(j), integer(i + j))

    def test_mul(self):
        for i in range(-5, 5):
            for j in range(-5, 5):
                self.assertEqual(integer(i) * integer(j), integer(i * j))

    # def test_bigmul(self):
    #     self.assertEqual(Z(100) * Z(100), Z(100 * 100))

    def test_le(self):
        for i in range(-10, 10):
            for j in range(-10, 10):
                self.assertEqual(integer(i) <= integer(j), i <= j)

    def test_lt(self):
        for i in range(-10, 10):
            for j in range(-10, 10):
                self.assertEqual(integer(i) < integer(j), i < j)

    def test_sub(self):
        for i in range(-10, 10):
            for j in range(-10, 10):
                self.assertEqual(integer(i) - integer(j), integer(i - j))

    # def test_mod(self):
    #     for i in range(-10, 10):
    #         for j in range(-10, 10):
    #             if j == 0:
    #                 continue
    #             self.assertEqual(Z(i) % Z(j), Z(i % j))

    # def test_floordiv(self):
    #     for i in range(-10, 10):
    #         for j in range(-10, 10):
    #             if j == 0:
    #                 continue
    #             self.assertEqual(Z(i) // Z(j), Z(i // j))

    def test_bool(self):
        for i in range(-100, 100):
            self.assertEqual(bool(integer(i)), bool(i))

    def test_int(self):
        for i in range(-100, 100):
            self.assertEqual(int(integer(i)), int(i))

    def test_hash(self):
        for i in range(-100, 100):
            self.assertEqual(hash(integer(i)), hash(i))

    def test_str(self):
        for i in range(-100, 100):
            self.assertEqual(str(integer(i)), str(i))

    # def test_divmod(self):
    #     for i in range(20):
    #         for j in range(1, 10):
    #             self.assertEqual(divmod(Z(i), Z(j)),
    #                              tuple(map(N, divmod(i, j))))

    def test_pow(self):
        for i in range(-5, 5):
            for j in range(5):
                self.assertEqual(integer(i) ** natural_number(j), integer(i ** j))

    def test_pos(self):
        for i in range(100):
            self.assertEqual(+integer(i), integer(+i))

    def test_abs(self):
        for i in range(100):
            self.assertEqual(abs(integer(i)), natural_number(abs(i)))


if __name__ == '__main__':
    unittest.main()
