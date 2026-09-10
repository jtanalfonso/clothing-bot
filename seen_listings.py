import json
import re

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

def seen_file(prefix, brand_name):
  """
  Builds the seen-listings file path for a given site and brand. 
  seen_file("grailed", "Isamu Katayama Backlash") -> "seen_grailed_isamu_katayama_backlash.json"

  Args:
    prefix: Site identifier used as a filename prefix
    brand_name: Brand name

  Returns:
    Path string for that site+brand's seen-listings file.
  """
  slug = re.sub(r"[^a-z0-9]+", "_", brand_name.lower()).strip("_")
  return f"seen_{prefix}_{slug}.json"