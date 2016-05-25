# Python client for Camomile REST API

## Installation

```bash
pip install camomile
```

## Usage

```python
from camomile import Camomile
client = Camomile('http://camomile.fr/api')
client.login('username', 'password')
client.logout()
client.getCorpora()
client.createCorpus(...)
```

## Documentation

Available at http://camomile-project.github.io
