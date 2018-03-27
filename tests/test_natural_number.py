import unittest
import time
from numbers.natural_number import NaturalNumber, N
import sys
sys.setrecursionlimit(1 << 16)


class TestNaturalNumber(unittest.TestCase):
    def setUp(self):
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("{}: {}ms".format(self.id(), int(t * 1000)))

    def test_eq(self):
        for i in range(20):
            n = NaturalNumber()
            for _ in range(i):
                n = NaturalNumber(n)
            self.assertEqual(N(i), n)

    def test_add(self):
        for i in range(10):
            for j in range(10):
                self.assertEqual(N(i) + N(j), N(i + j))

    def test_mul(self):
        for i in range(10):
            for j in range(10):
                self.assertEqual(N(i) * N(j), N(i * j))

    # def test_bigmul(self):
    #     self.assertEqual(N(100) * N(100), N(100 * 100))

    def test_le(self):
        for i in range(10):
            for j in range(10):
                self.assertEqual(N(i) <= N(j), i <= j)

    def test_lt(self):
        for i in range(10):
            for j in range(10):
                self.assertEqual(N(i) < N(j), i < j)

    def test_sub(self):
        for i in range(10):
            for j in range(i):
                self.assertEqual(N(i) - N(j), N(i - j))

    def test_mod(self):
        for i in range(20):
            for j in range(1, 10):
                self.assertEqual(N(i) % N(j), N(i % j))

    def test_floordiv(self):
        for i in range(20):
            for j in range(1, 10):
                self.assertEqual(N(i) // N(j), N(i // j))

    def test_bool(self):
        for i in range(100):
            self.assertEqual(bool(N(i)), bool(i))

    def test_int(self):
        for i in range(20):
            self.assertEqual(int(N(i)), int(i))

    def test_hash(self):
        for i in range(20):
            self.assertEqual(hash(N(i)), hash(i))

    def test_str(self):
        for i in range(20):
            self.assertEqual(str(N(i)), str(i))

    def test_set_repr(self):
        self.assertEqual(N(0).set_repr(), frozenset())
        self.assertEqual(N(1).set_repr(), frozenset((frozenset(),)))

    def test_set_str(self):
        self.assertEqual(N(0).set_str(), "{}")
        self.assertEqual(N(1).set_str(), "{{}}")
        self.assertEqual(N(2).set_str(), "{{{}}, {}}")

    def test_iter(self):
        for i, n in enumerate(N(100)):
            self.assertEqual(n, N(i))

    def test_reversed(self):
        for i, n in enumerate(reversed((N(100)))):
            self.assertEqual(n, N(99 - i))

    def test_divmod(self):
        for i in range(20):
            for j in range(1, 10):
                self.assertEqual(divmod(N(i), N(j)),
                                 tuple(map(N, divmod(i, j))))

    def test_pow(self):
        for i in range(8):
            for j in range(4):
                self.assertEqual(N(i) ** N(j), N(i**j))

    def test_pos(self):
        for i in range(100):
            self.assertEqual(+N(i), N(+i))

    def test_abs(self):
        for i in range(100):
            self.assertEqual(abs(N(i)), N(abs(i)))


if __name__ == '__main__':
    unittest.main()
