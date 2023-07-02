# infrahub-schema


## How to update a Schema

Generate the new schema, using the Infrahub cli tool
```
infrahub generate-schema schema
```

- Create a new directory in the `schemas/versions` with the appropriate version number
- Copy the schema file in the new directory
- Navigate to the `schemas/develop` and update the symbolic link

```
cd schemas/develop
ln -f -s ../versions/0.6.0/infrahub_schema.schema.json schema.schema.json
```

