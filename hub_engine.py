import random
import json
import os

class HolographicHub:
    def __init__(self, storage_path='/mnt/h/ACTOR_DEV_ENV/storage'):
        self.storage = storage_path
        if not os.path.exists(self.storage):
            os.makedirs(self.storage)

    def generate_and_save(self, weights):
        entropy = random.random()
        slice_id = hex(random.getrandbits(128))
        slice_data = [w * entropy for w in weights]
        
        filepath = os.path.join(self.storage, f'{slice_id}.hologram')
        with open(filepath, 'w') as f:
            json.dump({'id': slice_id, 'data': slice_data}, f)
        return slice_id

if __name__ == "__main__":
    hub = HolographicHub()
    sid = hub.generate_and_save([0.1, 0.5, 0.9, 0.2, 0.8])
    print(f"Hologram snapshot created: {sid}")
