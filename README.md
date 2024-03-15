# infrahub-schema

## How to update a Schema

Generate the new schema, using the Infrahub cli tool
```
infrahub generate-schema schema
```

- Copy the schema file to schemas/infrahub/schema/[version-number].json (i.e. 0.12.0.json)
- Navigate to the `schemas/infrahub/schema` and update the symbolic link

```
cd schemas/infrahub/schema
ln -f -s 0.12.0.json latest.json
```