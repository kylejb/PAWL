# PAWL: Python API Wrapper for LinkedIn

OAuth flow will be added in the next revision.

## Installation

PAWL is supported on Python 3.9+. The recommended way to install PAWL is with pip.

`pip install pawl`

## Quickstart

You can instantiate an instance like so:

```python
import pawl

>>> linkedin = pawl.Linkedin(
    access_token="ACCESS_TOKEN_VALUE",
)

>>> linkedin
<pawl.linkedin.Linkedin at 0x10ea46af0>
```

#### get_basic_profile()
```python
>>> response = linkedin.me.get_basic_profile()

>>> response
{
    'localizedLastName': 'LAST_NAME',
    'profilePicture': {
        'displayImage': 'urn:li:digitalmediaAsset:PHOTO_ID_VALUE'
    },
    'firstName': {
        'localized': {
            'language_code_value_and_country_code_value': 'FIRST_NAME_VALUE'
        },
        'preferredLocale': {
            'country': 'country_code_value', 'language': 'language_code_value'
        }
    },
    'lastName': {
        'localized': {
            'language_code_value_and_country_code_value':
            'LAST_NAME_VALUE'
        },
        'preferredLocale': {
            'country': 'country_code_value',
            'language': 'language_value'
        }
    },
    'id': 'USER_ID_VALUE',
    'localizedFirstName': 'localized_first_name_value'
}
```

## License

PAWL's source is provided under the MIT License.

- Copyright © 2021 Kyle J. Burda
