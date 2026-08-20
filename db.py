import sqlite3
import aiosqlite
import asyncio

DB_PATH = "bot_users.db"

_db_connection: aiosqlite.Connection | None = None


async def get_db() -> aiosqlite.Connection:
    """Получение активного соединения"""
    global _db_connection
    if _db_connection is None:
        _db_connection = await aiosqlite.connect(DB_PATH)
    return _db_connection


async def init_db():
    """Инициализация базы данных и создание таблиц"""
    db = await get_db()
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            field TEXT DEFAULT '000000000',
            move INTEGER DEFAULT 0,
            difficulty TEXT DEFAULT 'easy',
            wins INTEGER DEFAULT 0,
            loses INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0
        )
    """)
    await db.commit()


async def close_db():
    """Закрытие соединения с БД при завершении работы бота"""
    global _db_connection
    if _db_connection is not None:
        await _db_connection.close()
        _db_connection = None


async def add_user(user_id: int) -> bool:
    """Добавить нового пользователя. Возвращает True, если добавлен, False — если существует."""
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO users (user_id) VALUES (?)",
            (user_id,)
        )
        await db.commit()
        return True
    except sqlite3.IntegrityError:
        return False


async def get_field(user_id: int) -> str:
    """Получить игровое поле"""
    db = await get_db()
    async with db.execute(
            "SELECT field FROM users WHERE user_id = ?",
            (user_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return row[0] if row else '000000000'


async def update_field(user_id: int, new_field: str) -> bool:
    """Обновить поле field"""
    db = await get_db()
    cursor = await db.execute(
        "UPDATE users SET field = ? WHERE user_id = ?",
        (new_field, user_id)
    )
    await db.commit()
    return cursor.rowcount > 0


async def reset_field(user_id: int) -> bool:
    """Сбросить поле до начального значения"""
    return await update_field(user_id, '000000000')


async def update_move(user_id: int) -> bool:
    """Переключить ход между 0 и 1"""
    db = await get_db()
    cursor = await db.execute(
        "UPDATE users SET move = 1 - move WHERE user_id = ?",
        (user_id,)
    )
    await db.commit()
    return cursor.rowcount > 0


async def set_start_move(user_id: int, move: int) -> bool:
    """Установить начальный ход"""
    db = await get_db()
    cursor = await db.execute(
        "UPDATE users SET move = ? WHERE user_id = ?",
        (move, user_id)
    )
    await db.commit()
    return cursor.rowcount > 0


async def get_move(user_id: int) -> int:
    """Получить текущий ход"""
    db = await get_db()
    async with db.execute(
            "SELECT move FROM users WHERE user_id = ?",
            (user_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return row[0] if row else 0


async def get_difficulty(user_id: int) -> str:
    """Получить уровень сложности"""
    db = await get_db()
    async with db.execute(
            "SELECT difficulty FROM users WHERE user_id = ?",
            (user_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return row[0] if row else 'easy'


async def update_difficulty(user_id: int, new_difficulty: str) -> bool:
    """Обновить сложность"""
    db = await get_db()
    cursor = await db.execute(
        "UPDATE users SET difficulty = ? WHERE user_id = ?",
        (new_difficulty, user_id)
    )
    await db.commit()
    return cursor.rowcount > 0


async def increment_stat(user_id: int, stat_type: str) -> bool:
    """Изменить статистику"""
    if stat_type not in ('wins', 'loses', 'draws'):
        raise ValueError(f"Недопустимый тип статистики: {stat_type}")

    db = await get_db()
    cursor = await db.execute(
        f"UPDATE users SET {stat_type} = {stat_type} + 1 WHERE user_id = ?",
        (user_id,)
    )
    await db.commit()
    return cursor.rowcount > 0


def format_field(field: list[int]) -> str:
    """Привести поле к формату базы данных"""
    return ''.join(map(str, field))


async def array_field(user_id: int) -> list[int]:
    """Привести поле к формату списка"""
    return [int(i) for i in await get_field(user_id)]


async def get_statistics(user_id: int) -> tuple[int, int, int]:
    """Получить статистику (победы, поражения, ничьи)"""
    db = await get_db()
    async with db.execute(
            "SELECT wins, loses, draws FROM users WHERE user_id = ?",
            (user_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return (row[0], row[1], row[2]) if row else (0, 0, 0)


async def show_all_users() -> list:
    """Вывести всех пользователей в консоль"""
    db = await get_db()
    async with db.execute(
            "SELECT user_id, field, move, difficulty, wins, loses, draws FROM users"
    ) as cursor:
        rows = await cursor.fetchall()
        print("=" * 100)
        print("Все пользователи в БД:")
        for row in rows:
            print(
                f"ID: {row[0]}, Field: {row[1]}, Move: {row[2]}, Difficulty: {row[3]}, Wins: {row[4]}, Loses: {row[5]}, Draws: {row[6]}"
            )
        print("=" * 100)
        return rows


if __name__ == '__main__':
    asyncio.run(show_all_users())
