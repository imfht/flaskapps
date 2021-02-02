import argparse

def my_const_fun(*args, **kwargs):
    print('const', args, kwargs)
    
def my_default_fun(*args, **kwargs):
    print('default', args, kwargs)

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("integers", type=int, nargs="+")
    parser.add_argument("--sum", dest='accumulate', action='store_const', const=sum, default=max)
    parser.add_argument("--math", dest='math_is_fun', action='store_const', const=my_const_fun, default=my_default_fun)
    args = parser.parse_args()
    print(args.accumulate(args.integers))
    # print(args.math_is_fun(args.integers))
