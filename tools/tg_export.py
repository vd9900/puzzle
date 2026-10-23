#!/usr/bin/env python3
"""Read-only Telegram group export for puzzle research (Telethon, your own account).

Run it YOURSELF in a terminal; it asks for your phone number and login code interactively.
Never paste the login code or 2FA password anywhere else. The script only reads history;
it never sends, edits or deletes anything.

Setup (once): create an API ID/hash at https://my.telegram.org -> "API development tools".

  export TG_API_ID=123456 TG_API_HASH=abcdef...
  .venv/bin/python tools/tg_export.py --list GSMG            # find the group and its id
  .venv/bin/python tools/tg_export.py --chat <id> --since 2026-05-01 --photos creator
  .venv/bin/python tools/tg_export.py --chat <id> --photos none   # full text history

Output (git-ignored): data/user_supplied/telegram/
  messages.jsonl   one JSON object per message (resumable: re-running continues after the last id)
  media/           downloaded photos (<message id>.jpg)
The session file (gsmg.session) in the same folder keeps you logged in; delete it when done
(and/or end the session in Telegram -> Settings -> Devices).
"""
import argparse, asyncio, datetime as dt, json, os, sys
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto

OUT = Path(__file__).resolve().parent.parent / 'data' / 'user_supplied' / 'telegram'
CREATOR_USERNAMES = {'sowut'}  # the puzzle creator's public handle (@SoWut)


def sender_info(m):
    s = m.sender
    if s is None:
        return None, None
    name = ' '.join(x for x in (getattr(s, 'first_name', None), getattr(s, 'last_name', None)) if x) or getattr(s, 'title', None)
    return name, getattr(s, 'username', None)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', metavar='FILTER', help='list dialogs whose title contains FILTER')
    ap.add_argument('--chat', help='chat id (from --list) or exact title')
    ap.add_argument('--since', help='YYYY-MM-DD: only messages on/after this date (default: all)')
    ap.add_argument('--photos', choices=['none', 'creator', 'all'], default='creator')
    args = ap.parse_args()

    api_id, api_hash = os.environ.get('TG_API_ID'), os.environ.get('TG_API_HASH')
    if not api_id or not api_hash:
        sys.exit('Set TG_API_ID and TG_API_HASH (from https://my.telegram.org) first.')
    OUT.mkdir(parents=True, exist_ok=True)
    client = TelegramClient(str(OUT / 'gsmg'), int(api_id), api_hash, flood_sleep_threshold=120)
    await client.start()  # prompts for phone, code (and 2FA password) in THIS terminal

    if args.list is not None:
        async for d in client.iter_dialogs():
            if args.list.lower() in (d.title or '').lower():
                print(f'{d.id}\t{d.title}')
        return

    if not args.chat:
        sys.exit('Give --chat <id or title> (use --list first).')
    target = int(args.chat) if args.chat.lstrip('-').isdigit() else args.chat
    entity = await client.get_entity(target)

    out_file = OUT / 'messages.jsonl'
    last_id = 0
    if out_file.exists():
        for line in out_file.open():
            last_id = max(last_id, json.loads(line)['id'])
    since = dt.datetime.fromisoformat(args.since).replace(tzinfo=dt.timezone.utc) if args.since else None
    (OUT / 'media').mkdir(exist_ok=True)

    n = 0
    with out_file.open('a') as fh:
        async for m in client.iter_messages(entity, reverse=True, min_id=last_id,
                                            offset_date=since if (since and not last_id) else None):
            name, username = sender_info(m)
            rec = {
                'id': m.id, 'date': m.date.isoformat(), 'sender_id': m.sender_id,
                'sender_name': name, 'sender_username': username, 'text': m.message or '',
                'reply_to': m.reply_to.reply_to_msg_id if m.reply_to else None,
                'forward': bool(m.fwd_from), 'media': type(m.media).__name__ if m.media else None,
                'edit_date': m.edit_date.isoformat() if m.edit_date else None,
            }
            is_creator = (username or '').lower() in CREATOR_USERNAMES
            if isinstance(m.media, MessageMediaPhoto) and (args.photos == 'all' or (args.photos == 'creator' and is_creator)):
                path = await m.download_media(file=str(OUT / 'media' / f'{m.id}.jpg'))
                rec['media_file'] = os.path.relpath(path, OUT) if path else None
            fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
            n += 1
            if n % 2000 == 0:
                print(f'{n} messages ... (last {m.date:%Y-%m-%d})', flush=True)
    print(f'done: {n} new messages -> {out_file}')


if __name__ == '__main__':
    asyncio.run(main())
