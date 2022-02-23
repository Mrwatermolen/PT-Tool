import time
from manager import SimpleToolSql
from datetime import datetime


if __name__ == "__main__":

    def update(columns: list[str], keys: list[str]) -> bool:
        com_str = "UPDATE subscription set "
