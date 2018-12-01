# Meneto shopping cart app

The inital Flask skeleton was taken from the following boilerplate:

```sh
https://github.com/realpython/cookiecutter-flask-skeleton.git
```

# Installation

Clone the repository to your local machine into the folder for ex. "meneto-test".

Run the following to setup the environment and the project.

```sh
$ cs ./meneto-test
$ ./setup.sh
```

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

