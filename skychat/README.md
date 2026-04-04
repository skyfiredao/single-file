# SkyChat / 天聊

Self-hosted encrypted web chat with no external dependencies.

**[中文文档](README_zh.md)**

License: GPL v3

## Features

- **Encrypted Chat**: All messages are encrypted using AES-256-GCM. The server only stores ciphertext.
- **URL-Based Key Distribution**: The room key is shared via the URL hash fragment, meaning it's never sent to the server.
- **Three-Layer Key System**:
    - **Room Key**: AES-256-GCM symmetric key for message encryption.
    - **Identity Key**: ECDSA P-256 key pair for each member to sign messages.
    - **Admin Key**: ECDSA P-256 key pair for the room creator to manage the room.
- **Zero Dependencies**:
    - **Backend**: Pure Python 3.10+ using only the standard library (`asyncio` and `sqlite3`). No Flask, Django, or other frameworks.
    - **Frontend**: Single `index.html` file using vanilla HTML, CSS, and JavaScript. No React, Vue, npm, or Node.js required.
- **Bilingual Interface**: Full support for both English and Chinese.
- **Telegram-Style UI**: Modern chat bubbles with circular avatars. Avatar colors are deterministically generated from nickname hashes.
- **Temporary Accounts**: Quick access using a nickname and password. No formal registration process.
- **Auto-Expiring Rooms**: Configurable room durations (1h, 6h, 24h, 72h).
- **Admin Controls**: Room creators can clear all messages or close the room entirely.
- **Polling Architecture**: Efficient HTTP polling (3s interval) with timestamp anchors for incremental updates. Does not use WebSockets.
- **Security Hardened**: Includes per-IP rate limiting, SHA-256 double-hashing for passwords, CSP with per-request nonces, AES-GCM authenticated data binding, and tamper-proof message signatures.
- **Session Recovery**: Identities are stored in `localStorage` and protected by a PBKDF2-derived key.
- **Mobile Responsive**: Works across desktop and mobile browsers.
- **Easy Sharing**: Invite others directly via shareable URLs.

## Screenshots / Demo

<!-- Screenshots coming soon -->

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd skychat
   ```
2. Start the server:
   ```bash
   python3 server.py
   ```
3. Open `http://<your-server-ip>:8080` in your browser.

## Usage

- **Create a Room**: Click "Create Room", enter your nickname and password, and select the room duration.
- **Invite Others**: Click the "Link" button to copy the invite URL and share it.
- **Join a Room**: Open an invite URL, then enter your nickname and password.
- **Chat**: Type your message and click "Send" or press Enter.
- **Refresh**: Click the 🔄 button to manually update the message and member list.
- **Exit**: Click the "Exit" button to leave.
- **Admin**: If you created the room, you will see "Clear" and "Close" buttons for management.

## CLI Options

```bash
python3 server.py [--host HOST] [--port PORT] [--db DB_PATH]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `0.0.0.0` | Bind address |
| `--port` | `8080` | Listen port |
| `--db` | `chat.db` | SQLite database path |

For local-only debugging:
```bash
python3 server.py --host 127.0.0.1
```

## Architecture

- **Minimalist Design**: The project consists of just two main files: `server.py` (~855 lines) and `index.html` (~1370 lines).
- **Data Storage**: Uses SQLite (WAL mode) for message persistence. The database is auto-generated on the first run.
- **No Dependencies**: Relies strictly on the Python 3.10+ standard library.
- **Encryption**: All cryptographic operations occur in the browser via the Web Crypto API. The server never sees plaintext messages, nicknames, or room keys.
- **Syncing**: Clients poll the server every 3 seconds using a timestamp anchor to fetch only new messages.

## Security Model

SkyChat employs a three-layer key system:
- **Room Key (AES-256-GCM)**: A shared symmetric key used to encrypt all messages in a room. It is distributed via the URL hash and never touches the server.
- **Identity Key (ECDSA P-256)**: Each member generates a key pair for signing messages. The private key is protected by PBKDF2 using the user's password.
- **Admin Key (ECDSA P-256)**: The room creator's key pair used to authorize administrative actions.

**Security Hardening**:
- **CSP Nonce**: Each page load generates a unique `nonce` for the Content-Security-Policy `script-src` directive, preventing injected script execution.
- **AES-GCM AAD**: Message encryption uses the sender's member ID as Additional Authenticated Data (AAD), binding ciphertext to its sender and preventing message reattribution.
- **Signature Binding**: Digital signatures cover `ciphertext + IV + senderId` (not plaintext), ensuring tamper detection on the wire without exposing message content.
- **No innerHTML**: All DOM updates use safe APIs (`textContent`, `createElement`, `removeChild`) to eliminate XSS vectors.
- **Rate Limiting**: Per-IP, per-action rate limits protect against brute-force and abuse.
- **Password Hashing**: Passwords are SHA-256 hashed client-side, then double-hashed with a random salt server-side. The server never sees plaintext passwords.
- **Security Headers**: X-Frame-Options (DENY), X-Content-Type-Options (nosniff), Referrer-Policy (no-referrer), Permissions-Policy.

**Visibility**:
- **Server sees**: Room IDs, member counts, message counts, timestamps, and member public keys.
- **Server DOES NOT see**: Message content, nicknames, room keys, passwords, or private keys.

**Limitations & Notes**:
- **URL = Key**: Anyone with the invite URL has the room key. Share it only through trusted channels.
- **No Forward Secrecy**: If a room key is compromised, the entire message history can be decrypted. There is no per-message key rotation.
- **Single Room Key**: All members share one symmetric key. A compromised member can decrypt all messages in the room.
- **localStorage Identity**: User identities are stored in `localStorage`. Clearing browser data will permanently lose your identity for that room; there is no recovery mechanism.
- **Same Browser Limitation**: Two users cannot be simulated in the same browser because they share `localStorage`. Use separate browsers or incognito/private windows for testing.
- **No File/Image Support**: Only plain text messages are supported. No file uploads, images, or rich media.
- **Room Capacity**: Maximum 50 members per room.
- **Message Length**: Maximum 10,000 characters per message.
- **Polling, Not Real-Time**: Messages are fetched via HTTP polling every 3 seconds. This is not instant delivery; expect up to a 3-second delay.
- **No Offline Messages**: If the server restarts, the database persists, but client sessions need to rejoin (page refresh is sufficient).
- **Server Trust**: While the server cannot read message content, a malicious server operator could tamper with public keys, block messages, or log metadata (IPs, timestamps, room activity patterns).
- **No TLS Built-In**: The server does not provide HTTPS. For production use, place it behind a reverse proxy (e.g., Nginx, Caddy) with TLS enabled.
- **SQLite Concurrency**: SQLite WAL mode handles moderate concurrency, but is not designed for high-throughput production workloads with hundreds of simultaneous users.
- **Browser Crypto Dependency**: All encryption relies on the Web Crypto API. Older browsers without Web Crypto support will not work.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3 stdlib (asyncio + sqlite3) |
| Frontend | HTML + CSS + JavaScript (single file) |
| Crypto | Web Crypto API (AES-256-GCM, ECDSA P-256, PBKDF2) |
| Storage | SQLite (WAL mode) |
| Dependencies | None |

## Project Structure

```
skychat/
├── server.py          # Python HTTP server + SQLite backend
├── index.html         # Complete frontend (HTML + CSS + JS)
├── chat.db            # SQLite database (auto-generated)
├── README.md          # English documentation
└── README_zh.md       # Chinese documentation
```

## License

GPL v3. See the [LICENSE](https://www.gnu.org/licenses/gpl-3.0.html) for details.
