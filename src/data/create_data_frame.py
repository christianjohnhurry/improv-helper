# Script to interactively build a dataframe of scenes and save to JSON
# Columns: scene name, timestamp (seconds), level, tag, tag_type
# Usage: python3 src/data/create_data_frame.py

import json
from pathlib import Path
import pandas as pd
import sys

DATA_DIR = Path(__file__).resolve().parents[2] / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)


def parse_timestamp_to_seconds(ts: str) -> int:
    """Parse a timestamp in MM:SS or total seconds (integer string).
    Returns total seconds as int. Raises ValueError on bad format.
    """
    ts = ts.strip()
    if ts == '':
        raise ValueError('Empty timestamp')
    if ':' in ts:
        parts = ts.split(':')
        if len(parts) != 2:
            raise ValueError('Timestamp must be MM:SS')
        m, s = parts
        return int(m) * 60 + int(s)
    # allow integer seconds
    return int(float(ts))


def format_seconds_mmss(seconds: int) -> str:
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"


def prompt(prompt_text: str, default: str | None = None) -> str:
    if default is None:
        return input(prompt_text).strip()
    raw = input(f"{prompt_text} [{default}] ").strip()
    return raw if raw != '' else default


def yesno_prompt(prompt_text: str, default: bool = True) -> bool:
    yn = 'Y/n' if default else 'y/N'
    resp = input(f"{prompt_text} ({yn}): ").strip().lower()
    if resp == '':
        return default
    return resp[0] == 'y'


def collect_rows():
    rows = []
    print('\nEnter scene rows. For timestamp use MM:SS or total seconds (e.g. 75).')
    try:
        while True:
            scene = input('\nScene name: ').strip()
            if scene == '':
                print('Scene name cannot be empty. Try again.')
                continue

            # timestamp
            while True:
                ts_in = input('Timestamp (MM:SS or seconds): ').strip()
                try:
                    ts_seconds = parse_timestamp_to_seconds(ts_in)
                    break
                except Exception as e:
                    print('Invalid timestamp:', e)

            # level
            while True:
                lvl_in = input('Level (integer): ').strip()
                try:
                    level = int(lvl_in)
                    break
                except Exception:
                    print('Level must be an integer. Try again.')

            tag = input('Tag (optional): ').strip()
            tag_type = input('Tag type (optional): ').strip()

            rows.append({
                'description': scene,
                'timestamp': ts_seconds,
                'level': level,
                'tag': tag,
                'tag_type': tag_type,
            })

            more = yesno_prompt('Add another scene?', default=True)
            if not more:
                break
    except KeyboardInterrupt:
        print('\nInterrupted by user. Proceeding with collected rows...')
    return rows


def main():
    print('Create a dataframe interactively and save to JSON file in the data/ folder.')

    # file name
    while True:
        fname = input('Enter file name (without extension, e.g. scamps-new): ').strip()
        if fname == '':
            print('File name cannot be empty.')
            continue
        # sanitize
        if any(c in fname for c in ('/', '\\')):
            print('Do not include path separators in file name. Just a base name.')
            continue
        break

    rows = collect_rows()
    if len(rows) == 0:
        print('No rows collected. Exiting.')
        sys.exit(0)

    df = pd.DataFrame(rows)
    # add human friendly column for MM:SS (optional)
    df['timestamp_mmss'] = df['timestamp'].apply(format_seconds_mmss)

    print('\nCollected dataframe:')
    print(df.to_string(index=False))

    if yesno_prompt('Save to JSON now?', default=True):
        out_path = DATA_DIR / f"{fname}.json"
        # save pretty JSON
        with open(out_path, 'w', encoding='utf-8') as fh:
            json.dump(df.to_dict(orient='records'), fh, indent=2, ensure_ascii=False)
        print(f'Saved {len(df)} rows to {out_path}')
    else:
        print('Not saved. You can write the dataframe manually or run again.')


if __name__ == '__main__':
    main()
