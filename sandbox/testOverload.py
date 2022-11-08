class A:
    def __init__(self, a) -> None:
        self.a = a

    def __and__(self, other):
        return A(self.a * other.a)

    def __rshit__(self, other: 'A'):
        return A(self.a - other.a * self.a)

omega = A(12)
delta = A(25)
charlie = omega >> delta
print(charlie.a)