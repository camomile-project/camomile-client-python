

#### Step 1: setup Camomile API

```bash
$ git clone https://github.com/camomile-project/camomile-client-python.git
$ cd camomile-client-python/examples
$ docker-compose up -d
```

#### Step 2: install Camomile client

```bash
$ pip install -r requirements.txt
```

#### Step 3: edit `populate.py`

Use `docker ps` to know which port to use for SERVER.


#### Step 4: populate Camomile database

```bash
$ python populate.py
```

