import argparse
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import os

# Local imports – assuming legal_agent.py is in same directory
import legal_agent

DB_PATH = Path(r'H:/ACTOR_DEV_ENV/legal_cases.db')

def delete_statute(statute_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM statutes WHERE id = ?', (statute_id,))
    conn.commit()
    conn.close()
    print(f'Deleted statute with id {statute_id}')

def export_statutes(output_path: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute('SELECT id, title, text, source, created_at FROM statutes')
    rows = cursor.fetchall()
    conn.close()
    data = [
        {'id': r[0], 'title': r[1], 'text': r[2], 'source': r[3], 'created_at': r[4]}
        for r in rows
    ]
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'Exported {len(data)} statutes to {output_path}')

def main():
    parser = argparse.ArgumentParser(description='Legal agent CLI')
    subparsers = parser.add_subparsers(dest='command')

    # add
    add_parser = subparsers.add_parser('add', help='Add a new statute')
    add_parser.add_argument('--title', required=True, help='Title of the statute')
    add_parser.add_argument('--text', required=True, help='Full text of the statute')
    add_parser.add_argument('--source', required=True, help='Source citation')

    # list
    list_parser = subparsers.add_parser('list', help='List statutes')
    list_parser.add_argument('--keyword', help='Keyword to search in title or text')

    # delete
    del_parser = subparsers.add_parser('delete', help='Delete a statute by id')
    del_parser.add_argument('id', type=int, help='ID of the statute to delete')

    # export
    export_parser = subparsers.add_parser('export', help='Export all statutes to JSON')
    export_parser.add_argument('output', help='Output JSON file path')

    # query
    query_parser = subparsers.add_parser('query', help='Ask a legal question using LLM')
    query_parser.add_argument('question', help='Question to ask the LLM')

    args = parser.parse_args()

    if args.command == 'add':
        legal_agent.add_statute(args.title, args.text, args.source)
        print('Statute added.')
    elif args.command == 'list':
        statutes = legal_agent.find_statutes(args.keyword) if args.keyword else legal_agent.find_statutes('')
        for s in statutes:
            print(f'[{s[0]}] {s[1]} – {s[3]}')
    elif args.command == 'delete':
        delete_statute(args.id)
    elif args.command == 'export':
        export_statutes(args.output)
    elif args.command == 'query':
        answer = legal_agent.query_with_llm(args.question)
        print('LLM answer:\n', answer)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
