# PAWL: Python API Wrapper for LinkedIn

---

![PyPI - Version](https://img.shields.io/pypi/v/pawl?color=blue)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pawl)
![PyPI - Monthly Downloads](https://img.shields.io/pypi/dm/pawl)

PAWL (an acronym for `Python API Wrapper - LinkedIn`) allows for simple access to LinkedIn's API with only a single dependency.

## Installation

PAWL is supported on Python 3.9+. The recommended way to install PAWL is with pip.

`pip install pawl`

## Quickstart

The depicted implementation of `access_token` below will be replaced by OAuth2 flow in **v0.0.2**.

```python
# Demo in python/ipython shell
# Don't forget to install pawl first

>>> import pawl

>>> linkedin = pawl.Linkedin(
    access_token="ACCESS_TOKEN_VALUE"
)

>>> linkedin
<pawl.linkedin.Linkedin at 0x10ea46af0>
```

#### GET PROFILE:

```python
# Demo in python/ipython shell

>>> linkedin
<pawl.linkedin.Linkedin at 0x10ea46af0>

>>> response = linkedin.me.get_basic_profile()

>>> response
{
    'localizedLastName': 'LAST_NAME',
    'profilePicture': {
        'displayImage': 'PHOTO_ID'
    },
    'firstName': {
        'localized': {
            'LANG_CODE_COUNTRY_CODE': 'FIRST_NAME'
        },
        'preferredLocale': {
            'country': 'COUNTRY_CODE_VALUE',
            'language': 'LANGUAGE_CODE'
        }
    },
    'lastName': {
        'localized': {
            'LANG_CODE_COUNTRY_CODE':
            'LAST_NAME'
        },
        'preferredLocale': {
            'country': 'COUNTRY_CODE',
            'language': 'LANGUAGE_CODE'
        }
    },
    'id': 'USER_ID',
    'localizedFirstName': 'LOCALIZED_FIRST_NAME'
}
```

## Sources

The work that went into PAWL is not entirely my own. I learned a lot from open-sourced code written by [many incredible developers](docs/CREDITS.md).

## License

PAWL's source is provided under the MIT License.

- Copyright © 2021 Kyle J. Burda
