# Config Validation Changes

## Summary

Added validation for required fields in `core/utils/config_loader.py` to prevent loading invalid or incomplete configurations.

## Changes Made

### 1. Empty File Validation

**Before**: Empty YAML/JSON files would be loaded as empty configs and could cause runtime errors.

**After**: Empty files raise `ValueError: Config file is empty: {path}` immediately.

```python
# In ProjectConfig.load()
if path.suffix.lower() in {".yml", ".yaml"}:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        raise ValueError(f"Config file is empty: {path}")
```

### 2. Required Field Validation

**Before**: Configs could be loaded without `project.name`, causing issues downstream.

**After**: Configs without `project.name` raise `ValueError: Project name is required in {path}`.

```python
# In ProjectConfig.load()
config = cls(raw)

# Validate required fields
project_section = config.get("project", {})
if not project_section or not project_section.get("name"):
    raise ValueError(f"Project name is required in {path}")

return config
```

## Test Coverage

Added comprehensive test suite in `tests/test_config_loader.py`:

- **26 tests** covering:
  - `ConfigNode` functionality (10 tests)
  - `_deep_merge` helper (3 tests)
  - `ProjectConfig.load()` validation (8 tests)
  - Module-level `load()` function (2 tests)
  - Backward compatibility (3 tests)

### Key Test Cases

1. ✅ `test_load_empty_file` - Empty YAML files are rejected
2. ✅ `test_load_missing_project_name` - Configs without `project.name` are rejected
3. ✅ `test_load_valid_yaml` - Valid configs still load correctly
4. ✅ `test_load_valid_json` - JSON configs work the same way

## Error Messages

### Empty File
```
ValueError: Config file is empty: /path/to/config.yaml
```

### Missing Project Name
```
ValueError: Project name is required in /path/to/config.yaml
```

### Invalid Format
```
ValueError: Config root must be a mapping
```

## Backward Compatibility

✅ **Fully backward compatible** - All existing valid configs continue to work.

❌ **Breaking for invalid configs** - Intentionally breaks for:
- Empty config files
- Configs without `project.name`

This is a **security/safety improvement** - better to fail fast than to crash later.

## Validation Summary

| Validation | Before | After |
|------------|--------|-------|
| Empty files | ❌ Loaded as `{}` | ✅ Raises error |
| Missing `project.name` | ❌ Loaded with empty name | ✅ Raises error |
| Non-dict root | ❌ Unclear error | ✅ Clear error message |
| Valid configs | ✅ Works | ✅ Still works |

## Next Steps

Future validation improvements could include:

1. **Schema validation** - Validate against a JSON schema
2. **Type checking** - Ensure `temperature` is float, etc.
3. **Range validation** - Ensure `temperature` is 0-1, etc.
4. **Required sections** - Ensure `generation`, `tts`, etc. exist

For now, we focus on the **most critical validation**: ensuring configs are non-empty and have a project name.
