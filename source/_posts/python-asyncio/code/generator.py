def foo_generator():
    data = yield "bar"
    while data:
        print(f"Received: {data}")
        data = yield f"Echo: {data}"


gen = foo_generator()
print(next(gen))
print(gen.send("baz"))
print(gen.send("foo-bar-baz"))
try:
    print(gen.send(None))
except StopIteration as e:
    print(e.value)
