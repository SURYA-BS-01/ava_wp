Why __new__?
The __new__ method is responsible for creating a new instance.

By overriding __new__, you can control the instantiation process.

If an instance already exists (cls._instance is not None), the method simply returns that instance.

Otherwise, it creates a new one and stores it in cls._instance.