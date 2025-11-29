from typing import Any
from dataclasses import dataclass
import sqlite3
import yaml

YAML_SIZE_LIMIT = 524288  # 512 KB
APWORLD_SIZE_LIMIT = 1048576  # 1 MB


@dataclass
class Yaml:
    yaml_id: int
    creator_id: str
    slot_name: str
    data: bytes


@dataclass
class APWorld:
    apworld_id: int
    creator_id: str
    game_name: str
    data: bytes


def read_slot_name(data: bytes) -> str:
    try:
        return yaml.load(data, Loader=yaml.SafeLoader)["name"]
    except Exception as e:
        raise InvalidYamlException(e)


class FileTooBigException(Exception):
    pass


class InvalidYamlException(Exception):
    pass


class AlreadyExistsException(Exception):
    pass


class NotExistsException(Exception):
    pass


class APOrganizer:
    def __init__(self, *args: Any, **kwargs: dict[str, Any]):
        self.db: sqlite3.Connection = sqlite3.connect(*args, **kwargs)
        self.initialize_db()

    def initialize_db(self):
        cursor = self.db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS yaml (
                yaml_id INTEGER NOT NULL PRIMARY KEY,
                creator_id TEXT NOT NULL,
                slot_name TEXT NOT NULL UNIQUE,
                data BLOB NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS apworld (
                apworld_id INTEGER NOT NULL PRIMARY KEY,
                creator_id TEXT NOT NULL,
                game_name TEXT NOT NULL UNIQUE,
                data BLOB NOT NULL
            );
        """)
        self.db.commit()

    def add_yaml(self, creator_id: str, data: bytes):
        """Add a YAML to the database."""
        data_size = len(data)
        if data_size > YAML_SIZE_LIMIT:
            raise FileTooBigException(
                f"YAML provided is too large ({data_size} bytes; maximum {YAML_SIZE_LIMIT})"
            )
        slot_name = read_slot_name(data)
        cursor = self.db.cursor()
        # check if creator/slot has already been set. if so, delete it
        existing_yaml_id = self._yaml_exists(cursor, creator_id, slot_name)
        if existing_yaml_id is not None:
            cursor.execute("DELETE FROM yaml WHERE yaml_id = ?", (existing_yaml_id,))
        try:
            cursor.execute(
                "INSERT INTO yaml (creator_id, slot_name, data) VALUES (?,?,?)",
                (creator_id, slot_name, data),
            )
        except sqlite3.IntegrityError:
            raise AlreadyExistsException(f"Slot name {slot_name} already exists")
        self.db.commit()
        return Yaml(
            yaml_id=cursor.lastrowid,
            creator_id=creator_id,
            slot_name=slot_name,
            data=data,
        )

    def _yaml_exists(self, cursor: sqlite3.Cursor, creator_id: str, slot_name: str):
        result = cursor.execute(
            "SELECT yaml_id FROM yaml WHERE creator_id = ? AND slot_name = ?",
            (creator_id, slot_name),
        ).fetchone()
        if result is None:
            return None
        return result[0]

    def get_yamls(self, get_data: bool = True):
        if get_data:
            query = "SELECT yaml_id, creator_id, slot_name, data FROM yaml"
        else:
            query = "SELECT yaml_id, creator_id, slot_name, NULL as data FROM yaml"

        cursor = self.db.cursor()
        for row in cursor.execute(query):
            yaml_id, creator_id, slot_name, data = row
            yield Yaml(
                yaml_id=yaml_id,
                creator_id=creator_id,
                slot_name=slot_name,
                data=data,
            )

    def delete_yaml(self, slot_name: str):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM yaml WHERE slot_name = ?", (slot_name,))
        self.db.commit()
        if cursor.rowcount == 0:
            raise NotExistsException()

    def add_apworld(self, creator_id: str, game_name: str, data: bytes):
        data_size = len(data)
        if data_size > APWORLD_SIZE_LIMIT:
            raise FileTooBigException(
                f"APWorld provided is too large ({data_size} bytes; maximum {YAML_SIZE_LIMIT})"
            )
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "INSERT INTO apworld (creator_id, game_name, data) VALUES (?,?,?)",
                (creator_id, game_name, data),
            )
        except sqlite3.IntegrityError:
            raise AlreadyExistsException(f"APWorld for {game_name} already submitted")
        self.db.commit()
        return APWorld(
            apworld_id=cursor.lastrowid,
            creator_id=creator_id,
            game_name=game_name,
            data=data,
        )

    def get_apworlds(self, get_data: bool = True):
        if get_data:
            query = "SELECT apworld_id, creator_id, game_name, data FROM apworld"
        else:
            query = (
                "SELECT apworld_id, creator_id, game_name, NULL as data FROM apworld"
            )
        cursor = self.db.cursor()
        for row in cursor.execute(query):
            yield APWorld(
                apworld_id=row[0],
                creator_id=row[1],
                game_name=row[2],
                data=row[3],
            )

    def delete_apworld(self, game_name: str):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM apworld WHERE game_name = ?", (game_name,))
        self.db.commit()
        if cursor.rowcount == 0:
            raise NotExistsException()

    def clear(self):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM yaml")
        cursor.execute("DELETE FROM apworld")
        self.db.commit()
