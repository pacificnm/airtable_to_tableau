def airtable_type_to_json_type(airtable_type):
    # Map Airtable types to your config schema types
    mapping = {
        "singleLineText": "str",
        "multilineText": "str",
        "number": "float",
        "checkbox": "bool",
        "date": "str",
        "email": "str",
        "url": "str",
        "phoneNumber": "str",
        "singleSelect": "str",
        "multipleSelects": "str",
        "formula": "str",
        "rollup": "str",
        "lookup": "str",
        "count": "int",
        "createdTime": "str",
        "lastModifiedTime": "str",
        # Add more mappings as needed
    }
    return mapping.get(airtable_type, "str")