import unittest
import time
import sys

from peano.natural_number import NaturalNumber, natural_number

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
            self.assertEqual(natural_number(i), n)

    def test_add(self):
        for i in range(5):
            for j in range(5):
                self.assertEqual(natural_number(i) + natural_number(j), natural_number(i + j))

    def test_mul(self):
        for i in range(5):
            for j in range(5):
                self.assertEqual(natural_number(i) * natural_number(j), natural_number(i * j))

    # def test_bigmul(self):
    #     self.assertEqual(N(100) * N(100), N(100 * 100))

    def test_le(self):
        for i in range(10):
            for j in range(10):
                self.assertEqual(natural_number(i) <= natural_number(j), i <= j)

    def test_lt(self):
        for i in range(10):
            for j in range(10):
                self.assertEqual(natural_number(i) < natural_number(j), i < j)

    def test_sub(self):
        for i in range(10):
            for j in range(i):
                self.assertEqual(natural_number(i) - natural_number(j), natural_number(i - j))

    def test_mod(self):
        for i in range(10):
            for j in range(1, 10):
                self.assertEqual(natural_number(i) % natural_number(j), natural_number(i % j))

    def test_floordiv(self):
        for i in range(10):
            for j in range(1, 10):
                self.assertEqual(natural_number(i) // natural_number(j), natural_number(i // j))

    def test_bool(self):
        for i in range(20):
            self.assertEqual(bool(natural_number(i)), bool(i))

    def test_int(self):
        for i in range(20):
            self.assertEqual(int(natural_number(i)), int(i))

    def test_hash(self):
        for i in range(20):
            self.assertEqual(hash(natural_number(i)), hash(i))

    def test_str(self):
        for i in range(20):
            self.assertEqual(str(natural_number(i)), str(i))

    def test_set_repr(self):
        self.assertEqual(natural_number(0).set_repr(), frozenset())
        self.assertEqual(natural_number(1).set_repr(), frozenset((frozenset(),)))
        self.assertEqual(natural_number(2).set_repr(), frozenset((frozenset(),frozenset((frozenset(),)))))

    def test_set_str(self):
        self.assertEqual(natural_number(0).set_str(), "{}")
        self.assertEqual(natural_number(1).set_str(), "{{}}")
        self.assertEqual(natural_number(2).set_str(), "{{}, {{}}}")
        self.assertEqual(natural_number(3).set_str(), "{{}, {{}, {{}}}, {{}}}")

    def test_iter(self):
        for i, n in enumerate(natural_number(30)):
            self.assertEqual(n, natural_number(i))

    def test_reversed(self):
        for i, n in enumerate(reversed((natural_number(30)))):
            self.assertEqual(n, natural_number(29 - i))

    def test_divmod(self):
        for i in range(5):
            for j in range(1, 5):
                self.assertEqual(divmod(natural_number(i), natural_number(j)),
                                 tuple(map(natural_number, divmod(i, j))))

    def test_pow(self):
        for i in range(4):
            for j in range(4):
                self.assertEqual(natural_number(i) ** natural_number(j), natural_number(i ** j))

    def test_pos(self):
        for i in range(30):
            self.assertEqual(+natural_number(i), natural_number(+i))

    def test_abs(self):
        for i in range(30):
            self.assertEqual(abs(natural_number(i)), natural_number(abs(i)))


if __name__ == '__main__':
    unittest.main()
