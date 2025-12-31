import sys
import time
import unittest

from peano.natural_number import NaturalNumber, natural_number, successor

sys.setrecursionlimit(1 << 16)


class TestNaturalNumber(unittest.TestCase):
    def setUp(self) -> None:
        self.startTime = time.time()

    def tearDown(self) -> None:
        t = time.time() - self.startTime
        print("{}: {}ms".format(self.id(), int(t * 1000)))

    def test_eq(self) -> None:
        for i in range(20):
            n = NaturalNumber()
            for _ in range(i):
                n = NaturalNumber(n)
            self.assertEqual(natural_number(i), n)

    def test_add(self) -> None:
        for i in range(5):
            for j in range(5):
                self.assertEqual(
                    natural_number(i) + natural_number(j), natural_number(i + j)
                )

    def test_add_axioms(self) -> None:
        for i in range(5):
            n = natural_number(i)
            self.assertEqual(n + natural_number(0), n)
        for i in range(4):
            for j in range(4):
                n = natural_number(i)
                m = natural_number(j)
                self.assertEqual(n + successor(m), successor(n + m))

    def test_mul(self) -> None:
        for i in range(5):
            for j in range(5):
                self.assertEqual(
                    natural_number(i) * natural_number(j), natural_number(i * j)
                )

    def test_mul_axioms(self) -> None:
        for i in range(5):
            n = natural_number(i)
            self.assertEqual(n * natural_number(0), natural_number(0))
        for i in range(4):
            for j in range(4):
                n = natural_number(i)
                m = natural_number(j)
                self.assertEqual(n * successor(m), n + (n * m))

    @unittest.skip("too slow")
    def test_bigmul(self) -> None:
        self.assertEqual(
            natural_number(100) * natural_number(100), natural_number(100 * 100)
        )

    def test_le(self) -> None:
        for i in range(10):
            for j in range(10):
                self.assertEqual(natural_number(i) <= natural_number(j), i <= j)

    def test_lt(self) -> None:
        for i in range(10):
            for j in range(10):
                self.assertEqual(natural_number(i) < natural_number(j), i < j)

    def test_sub(self) -> None:
        for i in range(10):
            for j in range(i):
                self.assertEqual(
                    natural_number(i) - natural_number(j), natural_number(i - j)
                )

    def test_sub_negative_result(self) -> None:
        with self.assertRaises(ValueError):
            natural_number(1) - natural_number(2)

    def test_mod(self) -> None:
        for i in range(10):
            for j in range(1, 10):
                self.assertEqual(
                    natural_number(i) % natural_number(j), natural_number(i % j)
                )

    def test_floordiv(self) -> None:
        for i in range(10):
            for j in range(1, 10):
                self.assertEqual(
                    natural_number(i) // natural_number(j), natural_number(i // j)
                )

    def test_bool(self) -> None:
        for i in range(20):
            self.assertEqual(bool(natural_number(i)), bool(i))

    def test_int(self) -> None:
        for i in range(20):
            self.assertEqual(int(natural_number(i)), int(i))

    def test_hash(self) -> None:
        for i in range(20):
            self.assertEqual(hash(natural_number(i)), hash(i))

    def test_str(self) -> None:
        for i in range(20):
            self.assertEqual(str(natural_number(i)), str(i))

    def test_set_repr(self) -> None:
        self.assertEqual(natural_number(0).set_repr(), frozenset())
        self.assertEqual(natural_number(1).set_repr(), frozenset((frozenset(),)))
        self.assertEqual(
            natural_number(2).set_repr(),
            frozenset((frozenset(), frozenset((frozenset(),)))),
        )

    def test_set_str(self) -> None:
        self.assertEqual(natural_number(0).set_str(), "{}")
        self.assertEqual(natural_number(1).set_str(), "{{}}")
        self.assertEqual(natural_number(2).set_str(), "{{}, {{}}}")
        self.assertEqual(natural_number(3).set_str(), "{{}, {{}, {{}}}, {{}}}")

    def test_iter(self) -> None:
        for i, n in enumerate(natural_number(30)):
            self.assertEqual(n, natural_number(i))

    def test_reversed(self) -> None:
        for i, n in enumerate(reversed((natural_number(30)))):
            self.assertEqual(n, natural_number(29 - i))

    def test_divmod(self) -> None:
        for i in range(5):
            for j in range(1, 5):
                self.assertEqual(
                    divmod(natural_number(i), natural_number(j)),
                    tuple(map(natural_number, divmod(i, j))),
                )

    def test_pow(self) -> None:
        for i in range(4):
            for j in range(4):
                self.assertEqual(
                    natural_number(i) ** natural_number(j), natural_number(i**j)
                )

    def test_pos(self) -> None:
        for i in range(30):
            self.assertEqual(+natural_number(i), natural_number(+i))

    def test_abs(self) -> None:
        for i in range(30):
            self.assertEqual(abs(natural_number(i)), natural_number(abs(i)))

    def test_negative_input(self) -> None:
        with self.assertRaises(ValueError):
            natural_number(-1)


if __name__ == "__main__":
    unittest.main()
