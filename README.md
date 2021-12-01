# Trainerroad to Zwift

> Simple notebook that export specifics workouts and plans to Zwift.

## Installation

OS X & Linux:

_create your own environment with conda or virtualenv and then:_

```sh
pip install -r requirements.txt
```

## Usage example

Make sure to replace the following variables with your own values:

```sh
os.environ[TRAINERROAD_USER] = "your@username.com"
os.environ[TRAINERROAD_PASSWORD] = "yourpassword"

START_DATE = "12-12-2021"  # By default today's date
END_DATE = "12-12-2024"  # By default today's date plus 3 years
INCLUDE_DATE = False  # If True Download the whole calendar including daily workouts

```

## Contributing

1. Fork it (<https://github.com/yourname/yourproject/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## Credits

Credits to [stuwilkins](https://github.com/stuwilkins)
for [python-trainerroad](https://github.com/stuwilkins/python-trainerroad)

[npm-image]: https://img.shields.io/npm/v/datadog-metrics.svg?style=flat-square

[npm-url]: https://npmjs.org/package/datadog-metrics

[npm-downloads]: https://img.shields.io/npm/dm/datadog-metrics.svg?style=flat-square

[travis-image]: https://img.shields.io/travis/dbader/node-datadog-metrics/master.svg?style=flat-square

[travis-url]: https://travis-ci.org/dbader/node-datadog-metrics

[wiki]: https://github.com/yourname/yourproject/wiki
