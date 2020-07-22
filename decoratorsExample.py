def my_decorator(function):
    print('Я обычная функция')
    def wrapper():
        print("HELLO")
    
    return wrapper

def lazy_function():
    print("привет я ленивая функция")

if __name__ == "__main__":
    decorated_function = my_decorator(lazy_function)

    decorated_function()