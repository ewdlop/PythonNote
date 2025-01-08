def partial_class(cls):
   """Decorator to make a class partial"""
   # Track unimplemented abstract methods
   cls.__abstract_methods__ = {name for name, value in vars(cls).items() 
                             if getattr(value, "__isabstractmethod__", False)}
   
   # Allow partial instantiation
   original_new = cls.__new__
   def __new__(cls, *args, **kwargs):
       instance = original_new(cls)
       for name in cls.__abstract_methods__:
           setattr(instance, name, lambda *a, **kw: NotImplemented)
       return instance
   
   cls.__new__ = __new__
   return cls
