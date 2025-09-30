# ckanext-logs

A CKAN extension to view CKAN logs files in the CKAN web interface.

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.9 and earlier | no            |
| 2.10            | yes           |
| 2.11            | yes           |

## Installation

1. Install from source:

```
pip install -e .
```

2. Add `tables logs` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).



## Config settings

```yaml
- key: ckanext.logs.logs_path
description: Specify the path to the logs folder
default: /var/log/ckan

- key: ckanext.logs.log_filename
description: Specify the log file name to display in the logs viewer
default: ckan_default.error.log
```

## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
