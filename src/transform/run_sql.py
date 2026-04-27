import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "load"))
from database import run_sql_file

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def run_transforms() -> None:
    """
    Executes SQL transformation files in dependency order:
    1. Dimensions (truncate + reload)
    2. Facts
    """
    run_sql_file(os.path.join(ROOT, "sql", "transform_dimensions.sql"))
    run_sql_file(os.path.join(ROOT, "sql", "transform_facts.sql"))
    print("Transforms completed successfully.")


if __name__ == "__main__":
    run_transforms()