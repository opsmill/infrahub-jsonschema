# infrahub-jsonschema

Infrahub JSON Schema is the home of various [JSON Schema](https://json-schema.org/) files related to [Infrahub](https://github.com/opsmill/infrahub)

> A JSON Schema file is a standard specification that describes the structure and validation rules for various data (YAML, JSON). It provides a way to define what a valid document should look like, including the types of values, required fields, default values, and other constraints.

Currently we maintain JSON Schema files for:
- [Infrahub Schema definition file](https://docs.infrahub.app/topics/schema) Schema file for Infrahub, usually defined in Yaml
- [Infrahub repository configuration file](https://docs.infrahub.app/topics/infrahub-yml) (`.infrahub.yml`)


## Integration with standard IDE via yaml-language-server

In most IDE it's be possible to get inline format validation of a YAML file by providing the address of a JSON Schema file at the top of the file, using the syntax below

```yaml
# yaml-language-server: $schema=https://schema.infrahub.app/infrahub/schema/latest.json
---
version: '1.0'
```

## Public URL

Everything under the `schemas/` directory is automatically published to `https://schema.infrahub.app` to simplify the integration with external tools that requires a public URL

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
