import os
import sys
from pathlib import Path

# Ensure the workspace root is on sys.path for imports
workspace_root = Path(r'H:/ACTOR_DEV_ENV')
if str(workspace_root) not in sys.path:
    sys.path.append(str(workspace_root))

import legal_agent

# Sample Jus Cogens statutes
data = [
    {
        'title': 'Prohibition of Genocide',
        'text': 'Genocide is an absolute crime under international law and is prohibited under all circumstances. It constitutes a violation of the fundamental right to life and security of persons.',
        'source': 'UN Convention on the Prevention and Punishment of the Crime of Genocide (1948)'
    },
    {
        'title': 'Prohibition of Torture',
        'text': 'No one shall be subjected to torture or to cruel, inhuman or degrading treatment or punishment. This norm is non‑derogable and applies in all situations, including armed conflict.',
        'source': 'UN Convention Against Torture (1984)'
    },
    {
        'title': 'Right to Life',
        'text': 'Every human being has the inherent right to life. This right shall be protected by law and no one shall be arbitrarily deprived of his life.',
        'source': 'Universal Declaration of Human Rights, Article 3'
    }
]

def populate():
    legal_agent.init_db()
    for entry in data:
        legal_agent.add_statute(entry['title'], entry['text'], entry['source'])
    print(f'Inserted {len(data)} Jus Cogens statutes into {legal_agent.DB_PATH}')

if __name__ == '__main__':
    populate()
