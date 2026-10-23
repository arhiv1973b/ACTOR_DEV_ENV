import os
import hashlib
import json
import subprocess
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
import csv
from datetime import datetime


class HubSyncedAuditorPipeline:
    def __init__(
        self,
        model_name: str = "prajjwal1/bert-tiny",
        audit_mode: str = "quantile",
        hub_repo_path: str = ".",
    ):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.audit_mode = audit_mode
        self.hub_repo_path = hub_repo_path
        self.log_path = os.path.join(hub_repo_path, "corpus_audit_hub_log.csv")
        self.manifest_path = os.path.join(hub_repo_path, "batch_manifest.json")

        self._init_storage()
        self._register_hooks()

    def _init_storage(self):
        if not os.path.exists(self.log_path):
            with open(self.log_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["timestamp", "layer_id", "mode", "anomaly_count", "threshold_used"]
                )

    def _register_hooks(self):
        encoder_layers = self.model.encoder.layer
        for idx, layer in enumerate(encoder_layers):
            hook = self._create_hook(idx)
            layer.register_forward_hook(hook)

    def _create_hook(self, layer_id: int):
        audit_mode = self.audit_mode
        log_path = self.log_path

        def hook_fn(
            module: nn.Module, input: tuple, output: torch.Tensor
        ) -> torch.Tensor:
            hidden_states = output[0] if isinstance(output, tuple) else output
            norm_dev = torch.norm(hidden_states, dim=-1)

            if audit_mode == "fixed":
                adaptive_threshold = torch.tensor(2.0, device=hidden_states.device)
            elif audit_mode == "median":
                adaptive_threshold = torch.median(norm_dev) * 1.5
            elif audit_mode == "quantile":
                adaptive_threshold = torch.quantile(norm_dev, 0.92)
            else:
                adaptive_threshold = torch.tensor(2.0, device=hidden_states.device)

            mask = norm_dev > adaptive_threshold
            anomaly_count = int(torch.sum(mask).detach().item())
            threshold_val = float(adaptive_threshold.detach().item())

            if anomaly_count > 0:
                scale = norm_dev.unsqueeze(-1) + 1e-8
                cleaned_states = hidden_states / scale * threshold_val

                if hidden_states.ndim == 3:
                    mask = mask.unsqueeze(-1)
                else:
                    mask = mask.unsqueeze(-1) if hidden_states.ndim == 2 else mask

                cleaned_states = torch.where(mask, cleaned_states, hidden_states)
                output = (
                    (cleaned_states,) + output[1:]
                    if isinstance(output, tuple)
                    else cleaned_states
                )

                timestamp = datetime.utcnow().isoformat()
                with open(log_path, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [timestamp, layer_id, audit_mode, anomaly_count, threshold_val]
                    )

            return output

        return hook_fn

    def compute_sha256(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def seal_and_sync_manifest(self, batch_meta: dict):
        """Создает криптографический манифест и подготавливает данные для пуша в хаб."""
        log_hash = self.compute_sha256(self.log_path)

        manifest = {
            "timestamp": datetime.utcnow().isoformat(),
            "batch_meta": batch_meta,
            "artifact": "corpus_audit_hub_log.csv",
            "sha256": log_hash,
            "status": "sealed",
        }

        with open(self.manifest_path, mode="w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=4, ensure_ascii=False)

        print(f"[Manifest Sealed] SHA-256 анкер сформирован: {log_hash[:16]}...")

    def push_to_github_hub(self, commit_msg: str = "Automated telemetry hub sync"):
        """Туннелирование состояния в GitHub репозиторий без потери целей."""
        try:
            subprocess.run(
                ["git", "add", self.log_path, self.manifest_path],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", commit_msg], check=True, capture_output=True
            )
            subprocess.run(["git", "push"], check=True, capture_output=True)
            print(
                "[Hub Sync] Артефакты успешно туннелированы и зафиксированы в GitHub хабе."
            )
        except subprocess.CalledProcessError as e:
            print(
                f"[Hub Sync Warning] Ошибка Git/GitHub синхронизации: {e.stderr.decode('utf-8') if e.stderr else e}"
            )

    def process_corpus(self, texts: list[str]) -> torch.Tensor:
        self.model.eval()
        encoded = self.tokenizer(
            texts, padding=True, truncation=True, return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**encoded)
            embeddings = outputs.last_hidden_state

        return embeddings


if __name__ == "__main__":
    corpus = [
        "Jus cogens and erga omnes obligations require absolute structural integrity.",
        "The telemetry socket tunnel bridges local latent audits with the central GitHub hub.",
        "Zero loss of objectives is guaranteed through cryptographic SHA-256 anchoring.",
    ]

    pipeline = HubSyncedAuditorPipeline(
        model_name="prajjwal1/bert-tiny", audit_mode="quantile"
    )
    embeddings = pipeline.process_corpus(corpus)

    pipeline.seal_and_sync_manifest(
        {"corpus_size": len(corpus), "d_model": embeddings.shape[-1]}
    )
    pipeline.push_to_github_hub(
        commit_msg="DAG Log: Sync telemetry and cryptographic manifest"
    )
