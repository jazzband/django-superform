EXPECTED_EXPORTS = (
    "ForeignKeyFormField",
    "FormField",
    "FormSetField",
    "FormSetWidget",
    "FormWidget",
    "InlineFormSetField",
    "ModelFormField",
    "ModelFormSetField",
    "SuperForm",
    "SuperModelForm",
)


def test_all_exports_are_there():
    import django_superform

    for expected_export in EXPECTED_EXPORTS:
        assert hasattr(django_superform, expected_export)
