# infrahub-schema

## How to update a Schema

Generate the new schemas, using the invoke tool from the main [Infrahub repository](https://github.com/opsmill/infrahub).
```
invoke schema.generate-jsonschema
```

The command will create files under ./generated that needs to be copied to the corresponding location within this repository. The latest develop.json files can be copied as is and for released versions you would name them as [release-number].json and update the symlink to latest.json for the given schema.

Example:

- Copy the schema file to schemas/infrahub/schema/[version-number].json (i.e. 0.12.0.json)
- Navigate to the `schemas/infrahub/schema` and update the symbolic link

```
cd schemas/infrahub/schema
ln -f -s 0.12.0.json latest.json
```
