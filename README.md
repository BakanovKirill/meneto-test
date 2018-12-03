# Meneto shopping cart app

The inital Flask skeleton was taken from the following boilerplate:

```sh
https://github.com/realpython/cookiecutter-flask-skeleton.git
```

### Development thoughts

This is my first Flask experience after years working with Django.

Firstly i was searching for ready-to-use boilerplate, after several attempts i stopped at the current realpython version mentioned above. This one had used several builtin libs and had set up User, homepage and Auth (except TokenAuth for api).

Then i added models, struggled a bit with deciding which library to use for API and stopped on `Flask-API`. Looking into the code now, i'd rather use `flask-restful` in future to make Django-like class based views to group API endpoints.

Application has homepage with products and a cart, so you can access and use the functionality from a browser once you log in.
If logged in using browser, app uses `flask_login` session based user. If you want to test application using `curl` or `PostMan`, you have to include `Authorization: Token admin_auth_token` header. Token is hardcoded in the codebase to avoid spending time for the auth part. I make use of token based auth in tests. 

You can do following in the front-end:

1. Add product to cart from products list
2. Increment or decrement quantity of the product in the cart. (if quantity reaches zero - cart item is removed automatically)
3. Remove the whole cart item from the cart.
4. Toggle loyalty card with a button near the cart to check the discount working.


# Installation

Clone the repository to your local machine into the folder for ex. "meneto-test".

Run the following to setup the environment and the project.

```sh
$ cd ./meneto-test
$ ./setup.sh
```


> [setup.sh](https://github.com/BakanovKirill/meneto-test/blob/master/setup.sh) is intended to be used in Linux systems. It installs `python3.6` and `pipenv` into the system and then makes the project in local virtualenv. Check the file contents in case you want to know what's in it.


# Usage

If virtualenv is not activated, activate it using pipenv command:

```sh
$ pipenv shell
```

To run the local development server in the activated environment use one of the following commands:


```sh
$ ./entrypoint.sh
```

### Testing

Without coverage:

```sh
$ python manage.py test
```

With coverage:

```sh
$ python manage.py cov
```

