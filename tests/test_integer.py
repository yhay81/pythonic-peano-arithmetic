import sys
import time
import unittest

from peano.integer import Integer, integer
from peano.natural_number import natural_number

sys.setrecursionlimit(1 << 16)


class TestInteger(unittest.TestCase):
    def setUp(self) -> None:
        self.startTime = time.time()

    def tearDown(self) -> None:
        t = time.time() - self.startTime
        print("{}: {}ms".format(self.id(), int(t * 1000)))

    def test_eq(self) -> None:
        for i in range(-10, 10):
            for j in range(abs(i), 10):
                self.assertEqual(
                    integer(i), Integer(natural_number(i + j), natural_number(j))
                )

    def test_add(self) -> None:
        for i in range(-5, 5):
            for j in range(-5, 5):
                self.assertEqual(integer(i) + integer(j), integer(i + j))

    def test_mul(self) -> None:
        for i in range(-5, 5):
            for j in range(-5, 5):
                self.assertEqual(integer(i) * integer(j), integer(i * j))

    @unittest.skip("too slow")
    def test_bigmul(self) -> None:
        self.assertEqual(integer(100) * integer(100), integer(100 * 100))

    def test_le(self) -> None:
        for i in range(-5, 5):
            for j in range(-5, 5):
                self.assertEqual(integer(i) <= integer(j), i <= j)

    def test_lt(self) -> None:
        for i in range(-5, 5):
            for j in range(-5, 5):
                self.assertEqual(integer(i) < integer(j), i < j)

    def test_sub(self) -> None:
        for i in range(-5, 5):
            for j in range(-5, 5):
                self.assertEqual(integer(i) - integer(j), integer(i - j))

    def test_mod(self) -> None:
        for i in range(-3, 3):
            for j in range(-3, 3):
                if j == 0:
                    continue
                self.assertEqual(integer(i) % integer(j), integer(i % j))

    def test_floordiv(self) -> None:
        for i in range(-3, 3):
            for j in range(-3, 3):
                if j == 0:
                    continue
                self.assertEqual(integer(i) // integer(j), integer(i // j))

    def test_bool(self) -> None:
        for i in range(-30, 30):
            self.assertEqual(bool(integer(i)), bool(i))

    def test_int(self) -> None:
        for i in range(-30, 30):
            self.assertEqual(int(integer(i)), int(i))

    def test_hash(self) -> None:
        for i in range(-30, 30):
            self.assertEqual(hash(integer(i)), hash(i))

    def test_str(self) -> None:
        for i in range(-30, 30):
            self.assertEqual(str(integer(i)), str(i))

    def test_divmod(self) -> None:
        for i in range(-3, 3):
            for j in range(-3, 3):
                if j == 0:
                    continue
                self.assertEqual(
                    divmod(integer(i), integer(j)),
                    tuple(map(integer, divmod(i, j))),
                )

    def test_pow(self) -> None:
        for i in range(-4, 4):
            for j in range(4):
                self.assertEqual(integer(i) ** natural_number(j), integer(i**j))

    def test_pos(self) -> None:
        for i in range(-30, 30):
            self.assertEqual(+integer(i), integer(+i))

    def test_abs(self) -> None:
        for i in range(-30, 30):
            self.assertEqual(abs(integer(i)), natural_number(abs(i)))


if __name__ == "__main__":
    unittest.main()
