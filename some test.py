class SomeClass:
    def __enter__(self):
        print("enter")
        return "hey"

    def __exit__(self, *_):
        print("exit")
        return "boo"


with SomeClass() as something:
    print(something)
