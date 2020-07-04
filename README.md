# disty

File transfer system.

## Development

This quick start assumes an Unix environment. Tested under Linux, but should work on MacOS.

### Pre-req

Make sure you have poetry installed:
`pip install poetry`

### Development environment

1. Start the poetry shell and install all dependencies:

```
poetry shell
poetry install
```

2. Configure your environment variables as per `development.env`

3. Source from the file: `source development.env`

4. Run the Django application:
   `python manage.py runserver`

## Production

1. Customise your `production.env`

```
docker build . --name disty
docker run -d --env-file production.env -p 8000:8000 -v /documents/volume/path:/app/documents/ distyonline/disty
```

If you changed the _UPLOAD_FOLDER_ in your production.env make sure you map the volume accordingly.
