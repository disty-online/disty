# disty

Disty is a file transfer system geared towards organizations.

## Use case

### From inside to outside

As a company you need to make files available to customers, vendors and partners. Could be debug logs, temporary licenses, quick fixes or any other kind of artifacts.
You don't want or can't use external cloud solutions like Dropbox, Google Drive or One Drive due to company policies or lack of fine-grained control.

### From outside to inside

You need to receive large files from 3rd parties, which certainly exceed the limit of email attachments. Your counter-part also can't use any vendor or 3rd party tool to upload you the files, so you find yourself in a situation where the file exchange cannot happen easily.

Disty allows internal users to upload files and create download restrictions based on number of downloads of expiry date for the link.
It also allows internal users to create unique URLs where 3rd parties are able to upload files for them.

Access to files are registered and can be audited later.

### Planned features

1. Password support for downloadable files
1. Additional types of backend storage (currently only local disk supported)

### Out of scope features

1. End-to-end encryption

Disty is a tool for organizations. Individual users cannot expect privacy on the files they share. Encryption at rest and over the wire need to be implemented by the operations team. Administrators will have full visibility of the files contents - which is also a pre-req for auditability.

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
