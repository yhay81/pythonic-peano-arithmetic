import unittest
import time
from numbers.rational import Rational, Q
from numbers.integer import Z
from numbers.natural_number import N
import sys
sys.setrecursionlimit(1 << 16)


class TestNaturalNumber(unittest.TestCase):
    def setUp(self):
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("{}: {}ms".format(self.id(), int(t * 1000)))

    def test_eq(self):
        for i in range(-10, 10):
            for j in range(-10, 10):
                self.assertEqual(Q(i, j), Rational(Z(i), Z(j)))

    def test_add(self):
        for i in range(-3, 3):
            for j in range(-3, 3):
                for k in range(-3, 3):
                    for l in range(-3, 3):
                        # if j * l == 0:
                        #     continue
                        self.assertEqual(Q(i, j) + Q(k, l),
                                         Q(i * l + j * k, j * l))

    def test_mul(self):
        for i in range(-3, 3):
            for j in range(-3, 3):
                for k in range(-3, 3):
                    for l in range(-3, 3):
                        self.assertEqual(Q(i, j) * Q(k, l), Q(i * k, j * l))

    # def test_bigmul(self):
    #     self.assertEqual(Q(100) * Q(100), Q(100 * 100))

    # def test_le(self):
    #     for i in range(-10, 10):
    #         for j in range(-10, 10):
    #             for k in range(-10, 10):
    #                 for l in range(-10, 10):

    # def test_lt(self):
    #     for i in range(-10, 10):
    #         for j in range(-10, 10):
    #             for k in range(-10, 10):
    #                 for l in range(-10, 10):

    def test_sub(self):
        for i in range(-3, 3):
            for j in range(-3, 3):
                for k in range(-3, 3):
                    for l in range(-3, 3):
                        if j * l == 0:
                            continue
                        self.assertEqual(Q(i, j) - Q(k, l),
                                         Q(i * l - j * k, j * l))

    def test_truediv(self):
        for i in range(-3, 3):
            for j in range(-3, 3):
                for k in range(-3, 3):
                    for l in range(-3, 3):
                        self.assertEqual(Q(i, j) / Q(k, l), Q(i * l, j * k))

    def test_bool(self):
        for i in range(-10, 10):
            for j in range(-10, 10):
                self.assertEqual(bool(Q(i, j)), bool(i))

    # def test_int(self):
    #     for i in range(20):
    #         self.assertEqual(int(Q(i)), int(i))

    def test_hash(self):
        self.assertEqual(len(set(
            hash(Q(i, j)) for j in range(-10, 10) for i in range(-10, 10)
        )), 400)

    def test_str(self):
        for i in range(-10, 10):
            for j in range(-10, 10):
                self.assertEqual(str(Q(i, j)), f"{str(i)}/{str(j)}")

    def test_pow(self):
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    self.assertEqual(Q(i, j) ** N(k), Q(i ** k, j ** k))

    def test_pos(self):
        for i in range(10):
            for j in range(10):
                self.assertEqual(+Q(i, j), Q(+i, +j))

    def test_abs(self):
        for i in range(10):
            for j in range(10):
                self.assertEqual(abs(Q(i, j)), Q(abs(i), abs(j)))


if __name__ == '__main__':
    unittest.main()
