import sys
import time
import unittest

from peano.integer import integer
from peano.natural_number import natural_number
from peano.rational import Rational, rational

sys.setrecursionlimit(1 << 16)


class TestRational(unittest.TestCase):
    def setUp(self) -> None:
        self.startTime = time.time()

    def tearDown(self) -> None:
        t = time.time() - self.startTime
        print("{}: {}ms".format(self.id(), int(t * 1000)))

    def test_eq(self) -> None:
        for i in range(-4, 4):
            for j in range(-4, 4):
                self.assertEqual(rational(i, j), Rational(integer(i), integer(j)))

    def test_add(self) -> None:
        for i in range(-2, 2):
            for j in range(-2, 2):
                for k in range(-2, 2):
                    for m in range(-2, 2):
                        # if j * m == 0:
                        #     continue
                        self.assertEqual(
                            rational(i, j) + rational(k, m),
                            rational(i * m + j * k, j * m),
                        )

    def test_mul(self) -> None:
        for i in range(-2, 2):
            for j in range(-2, 2):
                for k in range(-2, 2):
                    for m in range(-2, 2):
                        self.assertEqual(
                            rational(i, j) * rational(k, m), rational(i * k, j * m)
                        )

    @unittest.skip("too slow")
    def test_bigmul(self) -> None:
        self.assertEqual(rational(9, 2) * rational(9, 2), rational(9 * 9, 2 * 2))

    def test_le(self) -> None:
        for i in range(-2, 2):
            for j in range(-2, 2):
                for k in range(-2, 2):
                    for m in range(-2, 2):
                        # if j * m == 0:
                        #     continue
                        self.assertEqual(
                            rational(i, j) < rational(k, m), (i * m) < (k * j)
                        )

    def test_lt(self) -> None:
        for i in range(-2, 2):
            for j in range(-2, 2):
                for k in range(-2, 2):
                    for m in range(-2, 2):
                        # if j * m == 0:
                        #     continue
                        self.assertEqual(
                            rational(i, j) <= rational(k, m), (i * m) <= (k * j)
                        )

    def test_sub(self) -> None:
        for i in range(-2, 2):
            for j in range(-2, 2):
                for k in range(-2, 2):
                    for m in range(-2, 2):
                        # if j * m == 0:
                        #     continue
                        self.assertEqual(
                            rational(i, j) - rational(k, m),
                            rational(i * m - j * k, j * m),
                        )

    def test_truediv(self) -> None:
        for i in range(-2, 2):
            for j in range(-2, 2):
                for k in range(-2, 2):
                    for m in range(-2, 2):
                        self.assertEqual(
                            rational(i, j) / rational(k, m), rational(i * m, j * k)
                        )

    def test_bool(self) -> None:
        for i in range(-5, 5):
            for j in range(-5, 5):
                self.assertEqual(bool(rational(i, j)), bool(i))

    def test_hash(self) -> None:
        self.assertEqual(
            len(set(hash(rational(i, j)) for j in range(-5, 5) for i in range(-5, 5))),
            100,
        )

    def test_str(self) -> None:
        for i in range(-5, 5):
            for j in range(-5, 5):
                self.assertEqual(str(rational(i, j)), f"{str(i)}/{str(j)}")

    def test_pow(self) -> None:
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    self.assertEqual(
                        rational(i, j) ** natural_number(k), rational(i**k, j**k)
                    )

    def test_pos(self) -> None:
        for i in range(5):
            for j in range(5):
                self.assertEqual(+rational(i, j), rational(+i, +j))

    def test_abs(self) -> None:
        for i in range(5):
            for j in range(5):
                self.assertEqual(abs(rational(i, j)), rational(abs(i), abs(j)))


if __name__ == "__main__":
    unittest.main()
