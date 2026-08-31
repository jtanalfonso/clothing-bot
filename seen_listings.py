import json

def load_seen(path):
  """
  Loads the set of listing IDs already posted to Discord.

  Args:
    path: Path to the site's seen-listings JSON file.

  Returns:
    Dict mapping listing ID strings to True. Returns an empty dict if the file doens't exist yet (first run).
  """
  try:
    with open(path, "r", encoding="utf-8") as f:
      return json.load(f)
  except FileNotFoundError:
    return {}

def save_seen(path, seen):
  """
  Overwrites the current set of posted listing IDs to the given file, overwriting its contents.

  Args:
    path: Path to the site's seen-listings JSON file.
    seen: Dict mapping listing ID strings to TRue, as returned by load_seen().
  """
  with open(path, "w", encoding="utf-8") as f:
    json.dump(seen, f, indent=2)