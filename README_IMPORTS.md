# Import Update Tool

This tool helps update module imports across the codebase. It's particularly useful when refactoring or renaming modules.

## Usage

```bash
./update_imports_consolidated.py [directory] [options]
```

### Arguments

- `directory`: Directory to process (default: economic_model_py)

### Options

- `--old-module`: Old module name to replace (default: china_growth_game)
- `--new-module`: New module name (default: economic_model_py)
- `--extensions`: Comma-separated list of file extensions to process (default: .py)
- `--verbose`, `-v`: Print verbose output

### Examples

Update imports in the economic_model_py directory:
```bash
./update_imports_consolidated.py
```

Update imports in a specific directory:
```bash
./update_imports_consolidated.py frontend/src
```

Update imports with custom module names:
```bash
./update_imports_consolidated.py --old-module old_name --new-module new_name
```

Process multiple file extensions:
```bash
./update_imports_consolidated.py --extensions .py,.js,.jsx
```

## How It Works

The script uses two methods to update imports:

1. **Regex-based replacement** for specific import patterns:
   - `from old_module.xxx import yyy` → `from new_module.xxx import yyy`
   - `import old_module.xxx` → `import new_module.xxx`
   - `@patch('old_module.xxx')` → `@patch('new_module.xxx')`

2. **Simple string replacement** for any remaining occurrences of the old module name.

This combined approach ensures thorough replacement while maintaining the structure of import statements.
