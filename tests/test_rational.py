import unittest
import time
from peano.rational import Rational, rational
from peano.integer import integer
from peano.natural_number import natural_number
import sys

sys.setrecursionlimit(1 << 16)


class TestRational(unittest.TestCase):
    def setUp(self):
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("{}: {}ms".format(self.id(), int(t * 1000)))

    def test_eq(self):
        for i in range(-4, 4):
            for j in range(-4, 4):
                self.assertEqual(rational(i, j), Rational(integer(i), integer(j)))

    def test_add(self):
        for i in range(-2, 2):
            for j in range(-2, 2):
                for k in range(-2, 2):
                    for l in range(-2, 2):
                        # if j * l == 0:
                        #     continue
                        self.assertEqual(rational(i, j) + rational(k, l), rational(i * l + j * k, j * l))

    def test_mul(self):
        for i in range(-2, 2):
            for j in range(-2, 2):
                for k in range(-2, 2):
                    for l in range(-2, 2):
                        self.assertEqual(rational(i, j) * rational(k, l), rational(i * k, j * l))

    # def test_bigmul(self):
    #     self.assertEqual(rational(50) * rational(50), rational(50 * 50))

    def test_le(self):
        for i in range(-2, 2):
            for j in range(-2, 2):
                for k in range(-2, 2):
                    for l in range(-2, 2):
                        # if j * l == 0:
                        #     continue
                        self.assertEqual(rational(i, j) < rational(k, l), (i * l) < (k * j))

    def test_lt(self):
        for i in range(-2, 2):
            for j in range(-2, 2):
                for k in range(-2, 2):
                    for l in range(-2, 2):
                        # if j * l == 0:
                        #     continue
                        self.assertEqual(rational(i, j) <= rational(k, l), (i * l) <= (k * j))

    def test_sub(self):
        for i in range(-2, 2):
            for j in range(-2, 2):
                for k in range(-2, 2):
                    for l in range(-2, 2):
                        # if j * l == 0:
                        #     continue
                        self.assertEqual(rational(i, j) - rational(k, l), rational(i * l - j * k, j * l))

    def test_truediv(self):
        for i in range(-2, 2):
            for j in range(-2, 2):
                for k in range(-2, 2):
                    for l in range(-2, 2):
                        self.assertEqual(rational(i, j) / rational(k, l), rational(i * l, j * k))

    def test_bool(self):
        for i in range(-5, 5):
            for j in range(-5, 5):
                self.assertEqual(bool(rational(i, j)), bool(i))

    # def test_int(self):
    #     for i in range(20):
    #         self.assertEqual(int(rational(i, integer(1))), int(i))

    def test_hash(self):
        self.assertEqual(len(set(
            hash(rational(i, j)) for j in range(-5, 5) for i in range(-5, 5)
        )), 100)

    def test_str(self):
        for i in range(-5, 5):
            for j in range(-5, 5):
                self.assertEqual(str(rational(i, j)), f"{str(i)}/{str(j)}")

    def test_pow(self):
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    self.assertEqual(rational(i, j) ** natural_number(k), rational(i ** k, j ** k))

    def test_pos(self):
        for i in range(5):
            for j in range(5):
                self.assertEqual(+rational(i, j), rational(+i, +j))

    def test_abs(self):
        for i in range(5):
            for j in range(5):
                self.assertEqual(abs(rational(i, j)), rational(abs(i), abs(j)))


if __name__ == '__main__':
    unittest.main()
