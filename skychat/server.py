# SkyChat
# Copyright (C) 2026  dw with opencode
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import argparse
import asyncio
import collections
import hashlib
import json
import os
import re
import secrets
import sqlite3
import time
from typing import cast
from urllib.parse import parse_qs

JSONObj = dict[str, object]

MAX_BODY_SIZE = 65536  # 64KB max HTTP body

db_path_value = 'chat.db'

RoomRow = tuple[str, str, str | None, int, int]
MemberRow = tuple[str, str, str, str, str, str, int, int]
MessageRow = tuple[int, str, str, str, str, str, int]
RoomIdRow = tuple[str]

ROOM_ID_PATTERN = re.compile(r'^[A-Za-z0-9-]{30,100}$')


class RateLimiter:
    def __init__(self) -> None:
        self.requests: collections.defaultdict[str, list[float]] = collections.defaultdict(list)

    def check(self, ip: str, limit: int, window_seconds: int, action: str = '') -> bool:
        now = time.time()
        key = f'{ip}:{action}'
        self.requests[key] = [t for t in self.requests[key] if now - t < window_seconds]
        if len(self.requests[key]) >= limit:
            return False
        self.requests[key].append(now)
        return True


rate_limiter = RateLimiter()


HTTP_STATUS_TEXT = {
    200: 'OK',
    201: 'Created',
    400: 'Bad Request',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    408: 'Request Timeout',
    429: 'Too Many Requests',
    500: 'Internal Server Error',
}


class HTTPError(Exception):
    status: int
    message: str

    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def _connect() -> sqlite3.Connection:
    db_file = db_path_value
    if not os.path.isabs(db_file):
        db_file = os.path.join(os.getcwd(), db_file)
    return sqlite3.connect(db_file)


def init_db() -> None:
    with _connect() as conn:
        _ = conn.execute('PRAGMA journal_mode=WAL')
        _ = conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS rooms (
                room_id TEXT PRIMARY KEY,
                admin_public_key TEXT NOT NULL,
                admin_member_id TEXT,
                created_at INTEGER NOT NULL,
                ttl_seconds INTEGER NOT NULL
            )
            '''
        )
        _ = conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS members (
                room_id TEXT NOT NULL,
                member_id TEXT NOT NULL,
                public_key TEXT NOT NULL,
                nickname_encrypted TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                joined_at INTEGER NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (room_id, member_id)
            )
            '''
        )
        _ = conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id TEXT NOT NULL,
                sender_id TEXT NOT NULL,
                ciphertext TEXT NOT NULL,
                iv TEXT NOT NULL,
                signature TEXT NOT NULL,
                created_at INTEGER NOT NULL
            )
            '''
        )

        _ = conn.execute(
            'CREATE INDEX IF NOT EXISTS idx_rooms_created_ttl ON rooms(created_at, ttl_seconds)'
        )
        _ = conn.execute(
            'CREATE INDEX IF NOT EXISTS idx_members_room_active ON members(room_id, is_active)'
        )
        _ = conn.execute(
            'CREATE INDEX IF NOT EXISTS idx_messages_room_created ON messages(room_id, created_at)'
        )


def create_room(room_id: str, admin_public_key: str, admin_member_id: str, ttl_seconds: int) -> None:
    now = int(time.time())
    with _connect() as conn:
        _ = conn.execute(
            '''
            INSERT INTO rooms (room_id, admin_public_key, admin_member_id, created_at, ttl_seconds)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (room_id, admin_public_key, admin_member_id, now, int(ttl_seconds)),
        )


def hash_password_client_hash(password_hash: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        'sha256',
        password_hash.encode('utf-8'),
        salt.encode('utf-8'),
        iterations=600_000,
    ).hex()


def get_room(room_id: str) -> dict[str, str | int | None] | None:
    with _connect() as conn:
        row = cast(
            RoomRow | None,
            conn.execute(
                '''
                SELECT room_id, admin_public_key, admin_member_id, created_at, ttl_seconds
                FROM rooms
                WHERE room_id = ?
                ''',
                (room_id,),
            ).fetchone(),
        )

    if row is None:
        return None

    now = int(time.time())
    if row[3] + row[4] < now:
        return None

    return {
        'room_id': row[0],
        'admin_public_key': row[1],
        'admin_member_id': row[2],
        'created_at': row[3],
        'ttl_seconds': row[4],
    }


def add_member(
    room_id: str,
    member_id: str,
    public_key: str,
    nickname_encrypted: str,
    password_hash: str,
) -> None:
    now = int(time.time())
    password_salt = secrets.token_hex(16)
    stored_password_hash = hash_password_client_hash(password_hash, password_salt)
    with _connect() as conn:
        _ = conn.execute(
            '''
            INSERT INTO members (
                room_id,
                member_id,
                public_key,
                nickname_encrypted,
                password_hash,
                password_salt,
                joined_at,
                is_active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ''',
            (room_id, member_id, public_key, nickname_encrypted, stored_password_hash, password_salt, now),
        )


def get_members(room_id: str) -> list[dict[str, str | int]]:
    with _connect() as conn:
        rows = cast(
            list[MemberRow],
            conn.execute(
                '''
                SELECT room_id, member_id, public_key, nickname_encrypted, password_hash, password_salt, joined_at, is_active
                FROM members
                WHERE room_id = ? AND is_active = 1
                ORDER BY joined_at ASC
                ''',
                (room_id,),
            ).fetchall(),
        )

    members: list[dict[str, str | int]] = []
    for row in rows:
        members.append(
            {
                'room_id': row[0],
                'member_id': row[1],
                'public_key': row[2],
                'nickname_encrypted': row[3],
                'password_hash': row[4],
                'password_salt': row[5],
                'joined_at': row[6],
                'is_active': row[7],
            }
        )
    return members


def get_member_by_id(room_id: str, member_id: str) -> dict[str, str | int] | None:
    with _connect() as conn:
        row = cast(
            MemberRow | None,
            conn.execute(
                '''
                SELECT room_id, member_id, public_key, nickname_encrypted, password_hash, password_salt, joined_at, is_active
                FROM members
                WHERE room_id = ? AND member_id = ?
                ''',
                (room_id, member_id),
            ).fetchone(),
        )
    if row is None:
        return None
    return {
        'room_id': row[0],
        'member_id': row[1],
        'public_key': row[2],
        'nickname_encrypted': row[3],
        'password_hash': row[4],
        'password_salt': row[5],
        'joined_at': row[6],
        'is_active': row[7],
    }


def update_member_identity(room_id: str, member_id: str, public_key: str, nickname_encrypted: str) -> None:
    with _connect() as conn:
        _ = conn.execute(
            '''
            UPDATE members
            SET public_key = ?, nickname_encrypted = ?, is_active = 1
            WHERE room_id = ? AND member_id = ?
            ''',
            (public_key, nickname_encrypted, room_id, member_id),
        )


def remove_member(room_id: str, member_id: str) -> None:
    with _connect() as conn:
        _ = conn.execute(
            '''
            UPDATE members
            SET is_active = 0
            WHERE room_id = ? AND member_id = ?
            ''',
            (room_id, member_id),
        )


def save_message(room_id: str, sender_id: str, ciphertext: str, iv: str, signature: str) -> None:
    now = int(time.time())
    with _connect() as conn:
        _ = conn.execute(
            '''
            INSERT INTO messages (room_id, sender_id, ciphertext, iv, signature, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (room_id, sender_id, ciphertext, iv, signature, now),
        )


def get_messages(room_id: str, since_timestamp: int = 0, limit: int = 200) -> list[dict[str, str | int]]:
    with _connect() as conn:
        rows = cast(
            list[MessageRow],
            conn.execute(
                '''
                SELECT id, room_id, sender_id, ciphertext, iv, signature, created_at
                FROM messages
                WHERE room_id = ? AND created_at >= ?
                ORDER BY created_at ASC
                LIMIT ?
                ''',
                (room_id, int(since_timestamp), int(limit)),
            ).fetchall(),
        )

    messages: list[dict[str, str | int]] = []
    for row in rows:
        messages.append(
            {
                'id': row[0],
                'room_id': row[1],
                'sender_id': row[2],
                'ciphertext': row[3],
                'iv': row[4],
                'signature': row[5],
                'created_at': row[6],
            }
        )
    return messages


def delete_room(room_id: str) -> None:
    with _connect() as conn:
        _ = conn.execute('DELETE FROM messages WHERE room_id = ?', (room_id,))
        _ = conn.execute('DELETE FROM members WHERE room_id = ?', (room_id,))
        _ = conn.execute('DELETE FROM rooms WHERE room_id = ?', (room_id,))


def cleanup_expired_rooms() -> int:
    now = int(time.time())

    with _connect() as conn:
        rows = cast(
            list[RoomIdRow],
            conn.execute(
                '''
                SELECT room_id
                FROM rooms
                WHERE created_at + ttl_seconds < ?
                ''',
                (now,),
            ).fetchall(),
        )

        room_ids = [row[0] for row in rows]
        for room_id in room_ids:
            _ = conn.execute('DELETE FROM messages WHERE room_id = ?', (room_id,))
            _ = conn.execute('DELETE FROM members WHERE room_id = ?', (room_id,))
            _ = conn.execute('DELETE FROM rooms WHERE room_id = ?', (room_id,))

    return len(room_ids)


def clear_messages(room_id: str) -> None:
    with _connect() as conn:
        _ = conn.execute('DELETE FROM messages WHERE room_id = ?', (room_id,))


def _status_text(status: int) -> str:
    return HTTP_STATUS_TEXT.get(status, 'OK')


def _build_response(status: int, body: bytes, content_type: str, csp_override: str = '') -> bytes:
    csp = csp_override if csp_override else "default-src 'self'; img-src 'self' data:"
    headers = {
        'Content-Type': content_type,
        'Content-Length': str(len(body)),
        'Connection': 'close',
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'Referrer-Policy': 'no-referrer',
        'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
        'Content-Security-Policy': csp,
    }
    lines = [f'HTTP/1.1 {status} {_status_text(status)}']
    for key, value in headers.items():
        lines.append(f'{key}: {value}')
    lines.append('')
    head = '\r\n'.join(lines).encode('utf-8') + b'\r\n'
    return head + body


async def send_json(writer: asyncio.StreamWriter, status: int, data: object) -> None:
    body = json.dumps(data).encode('utf-8')
    writer.write(_build_response(status, body, 'application/json'))
    await writer.drain()


async def send_html(writer: asyncio.StreamWriter, status: int, content: str, csp_override: str = '') -> None:
    body = content.encode('utf-8')
    writer.write(_build_response(status, body, 'text/html; charset=utf-8', csp_override))
    await writer.drain()


async def send_error(writer: asyncio.StreamWriter, status: int, message: str) -> None:
    await send_json(writer, status, {'error': message})


async def send_empty(writer: asyncio.StreamWriter, status: int) -> None:
    writer.write(_build_response(status, b'', 'application/json'))
    await writer.drain()


def _normalize_headers(headers: dict[str, str]) -> dict[str, str]:
    return {k.lower(): v for k, v in headers.items()}


async def read_request(reader: asyncio.StreamReader) -> tuple[str, str, str, dict[str, str], bytes]:
    request_line = await reader.readline()
    if not request_line:
        raise HTTPError(400, 'Empty request')

    try:
        method, target, version = request_line.decode('utf-8').strip().split(' ')
    except ValueError as exc:
        raise HTTPError(400, 'Malformed request line') from exc

    headers: dict[str, str] = {}
    while True:
        line = await reader.readline()
        if not line:
            break
        if line in (b'\r\n', b'\n'):
            break
        if b':' not in line:
            raise HTTPError(400, 'Malformed header')
        key, value = line.decode('utf-8').split(':', 1)
        headers[key.strip()] = value.strip()

    normalized_headers = _normalize_headers(headers)
    content_length = int(normalized_headers.get('content-length', '0') or '0')
    if content_length < 0:
        raise HTTPError(400, 'Invalid Content-Length')
    if content_length > MAX_BODY_SIZE:
        raise HTTPError(400, 'Request body too large')

    body = b''
    if content_length > 0:
        body = await reader.readexactly(content_length)

    return method, target, version, normalized_headers, body


def parse_json_body(body: bytes) -> JSONObj:
    if not body:
        return {}
    try:
        parsed: object = json.loads(body.decode('utf-8'))  # pyright: ignore[reportAny]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPError(400, 'Invalid JSON body') from exc

    if not isinstance(parsed, dict):
        raise HTTPError(400, 'JSON body must be an object')

    return cast(JSONObj, parsed)


def require_str(data: JSONObj, key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise HTTPError(400, f'Missing or invalid field: {key}')
    return value


def require_int(data: JSONObj, key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise HTTPError(400, f'Missing or invalid field: {key}')
    return value


def split_target(target: str) -> tuple[str, dict[str, list[str]]]:
    if '?' in target:
        path, query = target.split('?', 1)
        return path, parse_qs(query)
    return target, {}


def validate_max_length(value: str, field: str, max_length: int) -> None:
    if len(value) > max_length:
        raise HTTPError(400, f'Field too long: {field}')


def validate_room_id(room_id: str) -> None:
    if not ROOM_ID_PATTERN.match(room_id):
        raise HTTPError(400, 'Invalid roomId format')


def validate_sha256_hex(value: str, field: str) -> None:
    if len(value) != 64 or any(ch not in '0123456789abcdef' for ch in value):
        raise HTTPError(400, f'Invalid field: {field}')


def enforce_rate_limit(client_ip: str, limit: int, window_seconds: int, action: str) -> None:
    if not rate_limiter.check(client_ip, limit, window_seconds, action):
        raise HTTPError(429, f'Too many requests for {action}')


async def handle_get_root(writer: asyncio.StreamWriter) -> None:
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
    if not os.path.exists(index_path):
        raise HTTPError(404, 'index.html not found')
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    nonce = secrets.token_urlsafe(32)
    content = content.replace('<style>', f'<style nonce="{nonce}">')
    content = content.replace('<script>', f'<script nonce="{nonce}">')
    csp = f"default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'nonce-{nonce}'; img-src 'self' data:"
    await send_html(writer, 200, content, csp)


async def handle_get_room(writer: asyncio.StreamWriter, room_id: str) -> None:
    room = get_room(room_id)
    if room is None:
        raise HTTPError(404, 'Room not found')

    members = get_members(room_id)
    member_public_keys = [
        {
            'memberId': str(member['member_id']),
            'publicKey': str(member['public_key']),
            'nicknameEncrypted': str(member['nickname_encrypted']),
        }
        for member in members
    ]
    await send_json(
        writer,
        200,
        {
            'room': room,
            'memberPublicKeys': member_public_keys,
        },
    )


async def handle_post_rooms(writer: asyncio.StreamWriter, body: bytes, client_ip: str) -> None:
    enforce_rate_limit(client_ip, 5, 60, 'room creation')

    data = parse_json_body(body)
    room_id = require_str(data, 'roomId')
    admin_public_key = require_str(data, 'adminPublicKey')
    admin_member_id = require_str(data, 'adminMemberId')
    password_hash = require_str(data, 'passwordHash')
    ttl = require_int(data, 'ttl')

    nickname_encrypted_value = data.get('nicknameEncrypted', '')
    if not isinstance(nickname_encrypted_value, str):
        raise HTTPError(400, 'Invalid field: nicknameEncrypted')

    validate_room_id(room_id)
    validate_sha256_hex(admin_member_id, 'adminMemberId')
    validate_sha256_hex(password_hash, 'passwordHash')
    validate_max_length(admin_public_key, 'publicKey', 2048)
    validate_max_length(nickname_encrypted_value, 'nicknameEncrypted', 2048)

    try:
        create_room(room_id, admin_public_key, admin_member_id, ttl)
        add_member(room_id, admin_member_id, admin_public_key, nickname_encrypted_value, password_hash)
    except sqlite3.IntegrityError as exc:
        raise HTTPError(400, 'Room or member already exists') from exc

    room = get_room(room_id)
    await send_json(writer, 201, {'room': room})


async def handle_post_join(writer: asyncio.StreamWriter, room_id: str, body: bytes, client_ip: str) -> None:
    enforce_rate_limit(client_ip, 10, 60, 'join')

    if get_room(room_id) is None:
        raise HTTPError(404, 'Room not found')

    members = get_members(room_id)
    if len(members) >= 50:
        raise HTTPError(400, 'Room is full (max 50 members)')

    data = parse_json_body(body)
    member_id = require_str(data, 'memberId')
    public_key = require_str(data, 'publicKey')
    nickname_encrypted = require_str(data, 'nicknameEncrypted')
    password_hash = require_str(data, 'passwordHash')

    validate_sha256_hex(member_id, 'memberId')
    validate_sha256_hex(password_hash, 'passwordHash')
    validate_max_length(public_key, 'publicKey', 2048)
    validate_max_length(nickname_encrypted, 'nicknameEncrypted', 2048)

    try:
        add_member(room_id, member_id, public_key, nickname_encrypted, password_hash)
    except sqlite3.IntegrityError as exc:
        raise HTTPError(400, 'Member already exists') from exc

    await send_json(writer, 201, {'status': 'joined'})


async def handle_get_messages(writer: asyncio.StreamWriter, room_id: str, query: dict[str, list[str]]) -> None:
    if get_room(room_id) is None:
        raise HTTPError(404, 'Room not found')

    since = 0
    since_values = query.get('since', [])
    if since_values:
        try:
            since = int(since_values[0])
        except ValueError as exc:
            raise HTTPError(400, 'Invalid since parameter') from exc

    messages = get_messages(room_id, since)
    await send_json(writer, 200, messages)


async def handle_post_messages(writer: asyncio.StreamWriter, room_id: str, body: bytes, client_ip: str) -> None:
    enforce_rate_limit(client_ip, 30, 60, 'message send')

    if get_room(room_id) is None:
        raise HTTPError(404, 'Room not found')

    data = parse_json_body(body)
    sender_id = require_str(data, 'senderId')
    ciphertext = require_str(data, 'ciphertext')
    iv = require_str(data, 'iv')
    signature = require_str(data, 'signature')

    validate_sha256_hex(sender_id, 'senderId')
    validate_max_length(ciphertext, 'ciphertext', 32768)
    validate_max_length(iv, 'iv', 64)
    validate_max_length(signature, 'signature', 512)

    # Verify sender is an active member
    members = get_members(room_id)
    member_row = next((m for m in members if m['member_id'] == sender_id), None)
    if member_row is None:
        raise HTTPError(403, 'Not a member of this room')

    save_message(room_id, sender_id, ciphertext, iv, signature)
    await send_json(writer, 201, {'status': 'sent'})


async def handle_post_login(writer: asyncio.StreamWriter, room_id: str, body: bytes, client_ip: str) -> None:
    enforce_rate_limit(client_ip, 10, 60, 'join')

    if get_room(room_id) is None:
        raise HTTPError(404, 'Room not found')

    data = parse_json_body(body)
    member_id = require_str(data, 'memberId')
    password_hash = require_str(data, 'passwordHash')
    validate_sha256_hex(member_id, 'memberId')
    validate_sha256_hex(password_hash, 'passwordHash')

    member = get_member_by_id(room_id, member_id)
    if member is None:
        raise HTTPError(404, 'Member not found')

    expected_hash = str(member['password_hash'])
    password_salt = str(member['password_salt'])
    computed_hash = hash_password_client_hash(password_hash, password_salt)
    if computed_hash != expected_hash:
        raise HTTPError(403, 'Invalid credentials')

    public_key_value = data.get('publicKey')
    nickname_encrypted_value = data.get('nicknameEncrypted')
    if isinstance(public_key_value, str) and isinstance(nickname_encrypted_value, str):
        validate_max_length(public_key_value, 'publicKey', 2048)
        validate_max_length(nickname_encrypted_value, 'nicknameEncrypted', 2048)
        update_member_identity(room_id, member_id, public_key_value, nickname_encrypted_value)
        member = get_member_by_id(room_id, member_id)
        if member is None:
            raise HTTPError(404, 'Member not found')

    await send_json(
        writer,
        200,
        {
            'status': 'ok',
            'member': {
                'memberId': str(member['member_id']),
                'publicKey': str(member['public_key']),
                'nicknameEncrypted': str(member['nickname_encrypted']),
            },
        },
    )


async def handle_post_admin(writer: asyncio.StreamWriter, room_id: str, body: bytes, _client_ip: str) -> None:
    room = get_room(room_id)
    if room is None:
        raise HTTPError(404, 'Room not found')

    data = parse_json_body(body)
    requester_member_id = data.get('requesterMemberId')
    if not isinstance(requester_member_id, str) or not requester_member_id:
        requester_member_id = data.get('memberId')

    if not isinstance(requester_member_id, str) or not requester_member_id:
        raise HTTPError(400, 'Missing or invalid field: requesterMemberId')

    if room.get('admin_member_id') != requester_member_id:
        raise HTTPError(405, 'Only admin can execute this command')

    command = data.get('command')
    if not isinstance(command, str) or command not in {'kick', 'close', 'clear'}:
        raise HTTPError(400, 'Invalid admin command')

    if command == 'kick':
        target_member_id = data.get('targetMemberId')
        if not isinstance(target_member_id, str) or not target_member_id:
            raise HTTPError(400, 'Missing or invalid field: targetMemberId')
        remove_member(room_id, target_member_id)
        await send_json(writer, 200, {'status': 'kicked', 'memberId': target_member_id})
        return

    if command == 'close':
        delete_room(room_id)
        await send_json(writer, 200, {'status': 'closed'})
        return

    clear_messages(room_id)
    await send_json(writer, 200, {'status': 'cleared'})


async def route_request(
    writer: asyncio.StreamWriter,
    method: str,
    target: str,
    body: bytes,
    client_ip: str,
) -> None:
    path, query = split_target(target)
    segments = [segment for segment in path.split('/') if segment]

    enforce_rate_limit(client_ip, 600, 60, 'general')

    if method == 'OPTIONS':
        await send_empty(writer, 200)
        return

    if method == 'GET' and path == '/':
        await handle_get_root(writer)
        return

    if method == 'POST' and path == '/api/rooms':
        await handle_post_rooms(writer, body, client_ip)
        return

    if len(segments) >= 3 and segments[0] == 'api' and segments[1] == 'rooms':
        room_id = segments[2]

        if len(segments) == 3 and method == 'GET':
            await handle_get_room(writer, room_id)
            return

        if len(segments) == 4 and segments[3] == 'join' and method == 'POST':
            await handle_post_join(writer, room_id, body, client_ip)
            return

        if len(segments) == 4 and segments[3] == 'messages' and method == 'GET':
            await handle_get_messages(writer, room_id, query)
            return

        if len(segments) == 4 and segments[3] == 'messages' and method == 'POST':
            await handle_post_messages(writer, room_id, body, client_ip)
            return

        if len(segments) == 4 and segments[3] == 'admin' and method == 'POST':
            await handle_post_admin(writer, room_id, body, client_ip)
            return

        if len(segments) == 4 and segments[3] == 'login' and method == 'POST':
            await handle_post_login(writer, room_id, body, client_ip)
            return

        if len(segments) == 4 and segments[3] in {'join', 'admin', 'login'} and method != 'POST':
            raise HTTPError(405, 'Method not allowed')

        if len(segments) == 4 and segments[3] == 'messages' and method not in {'GET', 'POST'}:
            raise HTTPError(405, 'Method not allowed')

        if len(segments) == 3 and method != 'GET':
            raise HTTPError(405, 'Method not allowed')

    raise HTTPError(404, 'Not found')


async def _close_writer(writer: asyncio.StreamWriter) -> None:
    writer.close()
    await writer.wait_closed()


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    peername_obj = cast(tuple[object, ...] | None, writer.get_extra_info('peername'))
    client_ip = 'unknown'
    if isinstance(peername_obj, tuple) and peername_obj:
        first = peername_obj[0]
        if isinstance(first, str):
            client_ip = first
        elif isinstance(first, bytes):
            client_ip = first.decode('utf-8', errors='ignore')

    try:
        method, target, _version, _headers, body = await asyncio.wait_for(read_request(reader), timeout=30)
        await route_request(writer, method, target, body, client_ip)
    except asyncio.TimeoutError:
        await send_error(writer, 408, 'Request timeout')
    except HTTPError as exc:
        await send_error(writer, exc.status, exc.message)
    except asyncio.IncompleteReadError:
        await send_error(writer, 400, 'Incomplete request body')
    except Exception:
        await send_error(writer, 500, 'Internal server error')
    finally:
        await _close_writer(writer)


async def periodic_cleanup() -> None:
    while True:
        await asyncio.sleep(60)
        _ = cleanup_expired_rooms()


async def start_server(host: str, port: int, db_path: str) -> None:
    global db_path_value
    db_path_value = db_path

    print('数据库结构已更新；如启动失败请删除旧 chat.db 后重试 / Schema updated; delete old chat.db if needed.')
    server = await asyncio.start_server(handle_client, host, port)
    print(f'Server running on http://{host}:{port}')
    async with server:
        _ = asyncio.create_task(periodic_cleanup())
        await server.serve_forever()


class CLIArgs(argparse.Namespace):
    host: str = '0.0.0.0'
    port: int = 8080
    db: str = 'chat.db'


def parse_args() -> CLIArgs:
    parser = argparse.ArgumentParser(description='SkyChat — E2E Encrypted Web Chat')
    _ = parser.add_argument('--host', default='0.0.0.0', help='Bind address (default: 0.0.0.0)')
    _ = parser.add_argument('--port', type=int, default=8080, help='Listen port (default: 8080)')
    _ = parser.add_argument('--db', default='chat.db', help='SQLite database path (default: chat.db)')
    return parser.parse_args(namespace=CLIArgs())


if __name__ == '__main__':
    args = parse_args()
    db_path_value = args.db
    init_db()
    asyncio.run(start_server(args.host, args.port, args.db))
