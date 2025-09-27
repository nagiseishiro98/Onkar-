#!/usr/bin/env bash
# runpy.sh - list python scripts in pwd, auto-install missing modules, and run selected script
# Usage: chmod +x runpy.sh && ./runpy.sh

PYTHON_CMD=python3  # change to 'python' if needed
PIP_CMD="pip3"      # change to 'pip' if needed
PIP_INSTALL_OPTS="--user"  # use --user to avoid sudo; change if you want system-wide

# find py files in current dir
list_py_files() {
  mapfile -t files < <(ls -1 -- *.py 2>/dev/null)
  if [ ${#files[@]} -eq 0 ]; then
    echo "Koi .py file nahi mili is folder me."
    return 1
  fi
  echo "Python scripts in $(pwd):"
  for i in "${!files[@]}"; do
    printf "%3d) %s\n" $((i+1)) "${files[$i]}"
  done
  return 0
}

# extract top-level module names from a .py file
extract_modules() {
  local file="$1"
  # grep import/from lines, remove comments, extract module names, take top-level and uniq
  # handles: import a, b as c   and  from a.b import c
  grep -E '^\s*(import|from)\s+' "$file" 2>/dev/null \
    | sed -E 's/#.*//g' \
    | sed -E 's/^\s*import\s+//g; s/^\s*from\s+//g' \
    | awk '{print $1}' \
    | tr ',' '\n' \
    | sed -E 's/as\s+[[:alnum:]_]+$//g' \
    | sed -E 's/^([[:alnum:]_]+).*/\1/' \
    | awk '!/^$/ {print}' \
    | sort -u
}

# check if a module is importable
is_importable() {
  local mod="$1"
  $PYTHON_CMD - <<PYTEST >/dev/null 2>&1
try:
    import ${mod}
    print("OK")
except Exception as e:
    raise SystemExit(1)
PYTEST
  return $?
}

# try to install a single module via pip
try_pip_install() {
  local pkg="$1"
  echo "Installing package: $pkg ..."
  $PIP_CMD install $PIP_INSTALL_OPTS "$pkg"
  return $?
}

# install missing modules for a given file
install_missing_for_file() {
  local file="$1"
  echo "Checking imports in '$file'..."
  local mods
  mods=$(extract_modules "$file")
  if [ -z "$mods" ]; then
    echo "No obvious third-party imports detected."
    return 0
  fi

  local missing=()
  while IFS= read -r mod; do
    # skip builtins that are single letters or empty
    if [ -z "$mod" ]; then
      continue
    fi
    # some modules like __future__ or typing are stdlib; we'll test importability instead of maintaining stdlib list
    is_importable "$mod"
    if [ $? -ne 0 ]; then
      missing+=("$mod")
    fi
  done <<< "$mods"

  if [ ${#missing[@]} -eq 0 ]; then
    echo "Sari dependencies present."
    return 0
  fi

  echo "Missing modules detected: ${missing[*]}"
  echo "Attempting to install missing modules using $PIP_CMD $PIP_INSTALL_OPTS ..."
  for pkg in "${missing[@]}"; do
    try_pip_install "$pkg"
    if [ $? -ne 0 ]; then
      echo "Warning: pip install failed for package '$pkg'. You may need to install it manually (package name might differ from import name)."
    else
      echo "Installed: $pkg"
    fi
  done

  echo "Re-checking imports..."
  local still_missing=()
  for pkg in "${missing[@]}"; do
    is_importable "$pkg"
    if [ $? -ne 0 ]; then
      still_missing+=("$pkg")
    fi
  done

  if [ ${#still_missing[@]} -ne 0 ]; then
    echo "Ab bhi missing: ${still_missing[*]}"
    echo "Manual intervention may be needed (package name mismatch, system packages, or pip not available)."
  else
    echo "Saare imports ab importable hain."
  fi
}

# run selected file
run_file() {
  local file="$1"
  echo "Running: $file"
  # run in a subshell so Ctrl+C behaves locally to the script run
  $PYTHON_CMD "$file"
  local rc=$?
  echo "Process exited with code $rc"
  return $rc
}

# main menu loop
while true; do
  echo "=============================="
  list_py_files || exit 0
  echo "------------------------------"
  echo "Select number to run script, or:"
  echo "  r) refresh list"
  echo "  q) quit"
  read -p "Choice: " choice

  if [[ "$choice" =~ ^[Rr]$ ]]; then
    clear
    continue
  fi
  if [[ "$choice" =~ ^[Qq]$ ]]; then
    echo "Bye."
    exit 0
  fi

  if ! [[ "$choice" =~ ^[0-9]+$ ]]; then
    echo "Invalid input. Enter a number, r, or q."
    continue
  fi

  idx=$((choice-1))
  # reload files array (in case changed)
  mapfile -t files < <(ls -1 -- *.py 2>/dev/null)
  if [ -z "${files[$idx]}" ]; then
    echo "No file for that number. Refreshing list..."
    continue
  fi

  selected="${files[$idx]}"
  echo "You selected: $selected"

  # check for requirements.txt in same dir and install it first if present
  if [ -f "requirements.txt" ]; then
    echo "Found requirements.txt — installing packages from it (user scope)."
    $PIP_CMD install $PIP_INSTALL_OPTS -r requirements.txt
  fi

  # install missing modules detected from imports
  install_missing_for_file "$selected"

  # final prompt before running
  read -p "Run '$selected' now? [Y/n]: " run_choice
  if [[ "$run_choice" =~ ^([Nn])$ ]]; then
    echo "Not running."
    continue
  fi

  run_file "$selected"
  echo "Press Enter to return to menu..."
  read -r _
  clear
done
