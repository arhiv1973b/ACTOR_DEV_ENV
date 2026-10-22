import crypto from "crypto";
import fs from "fs/promises";
import fsSync from "fs";
import path from "path";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);
const ROOT_DIR = "H:\\ACTOR_DEV_ENV";
const OUTPUT_MANIFEST_1 = path.join(ROOT_DIR, "evidence", "fincombank-billing-traces", "fincombank_billing_crypto_manifest.json");
const OUTPUT_MANIFEST_2 = path.join(ROOT_DIR, "fincombank_billing_crypto_manifest.json");
const PRIVATE_KEY_PATH = path.join(ROOT_DIR, "keys", "ti_ula_ed25519.pem");

// Потоковое вычисление SHA-256 хеша файла
function calculateFileSha256(filePath) {
  return new Promise((resolve, reject) => {
    const hash = crypto.createHash("sha256");
    const stream = fsSync.createReadStream(filePath);
    stream.on("data", (chunk) => hash.update(chunk));
    stream.on("end", () => resolve(hash.digest("hex").toLowerCase()));
    stream.on("error", (err) => reject(err));
  });
}

// Рекурсивный сбор файлов
async function getFilesRecursive(dir) {
  const dirents = await fs.readdir(dir, { withFileTypes: true });
  const files = await Promise.all(dirents.map((dirent) => {
    const res = path.resolve(dir, dirent.name);
    return dirent.isDirectory() ? getFilesRecursive(res) : res;
  }));
  return Array.prototype.concat(...files);
}

async function main() {
  console.log("🔍 Сканирование директории для извлечения PDF и изображений выписок FinComBank...");
  
  const allFiles = await getFilesRecursive(ROOT_DIR);
  
  // Фильтрация файлов FinComBank, биллинга, выписок, квитанций (PDF, PNG, JPG, JSON)
  const targetFiles = allFiles.filter(file => {
    const lower = file.toLowerCase();
    const isTargetExt = lower.endsWith('.pdf') || lower.endsWith('.png') || lower.endsWith('.jpg') || lower.endsWith('.jpeg') || lower.endsWith('.json');
    if (!isTargetExt) return false;
    
    // Исключаем системные папки node_modules, .git, keys, reports, etc.
    if (lower.includes('\\.git\\') || lower.includes('\\node_modules\\') || lower.includes('\\keys\\') || lower.includes('\\run\\')) {
      return false;
    }

    const name = path.basename(lower);
    return name.includes('fincom') || 
           name.includes('финком') || 
           name.includes('billing') || 
           name.includes('receipt') || 
           name.includes('extract') || 
           name.includes('extras') || 
           name.includes('legal_reply_fincombank') ||
           name.includes('legal_submission_fincombank');
  });

  console.log(`📦 Найдено релевантных файлов выписок и биллинга: ${targetFiles.length}`);
  
  const fileEntries = [];
  for (const filePath of targetFiles) {
    try {
      const hash = await calculateFileSha256(filePath);
      const relativePath = path.relative(ROOT_DIR, filePath).replace(/\\/g, '/');
      fileEntries.push({
        path: relativePath,
        hash: hash
      });
      console.log(`  [SHA-256] ${relativePath} -> ${hash}`);
    } catch (err) {
      console.error(`  [ERROR] Не удалось обработать файл ${filePath}: ${err.message}`);
    }
  }

  // Сортируем файлы по пути для детерминизма
  fileEntries.sort((a, b) => a.path.localeCompare(b.path));

  const manifestData = {
    version: "1.0",
    case_id: "CASE-MACHERET-1997-2026",
    timestamp: new Date().toISOString(),
    description: "Local crypto-manifest for FinComBank billing statements, PDF extracts, and payment traces",
    algorithm: "SHA-256",
    files: fileEntries
  };

  // Чтение закрытого ключа Ed25519
  console.log(`🔑 Загрузка закрытого ключа Ed25519 с Core-узла: ${PRIVATE_KEY_PATH}`);
  const privateKeyPem = await fs.readFile(PRIVATE_KEY_PATH, "utf-8");
  const privKeyObject = crypto.createPrivateKey(privateKeyPem);

  // Каноническое подписание (сортировка ключей объекта)
  const { signature, public_key, ...dataToSign } = manifestData;
  const sortedKeys = Object.keys(dataToSign).sort();
  const canonicalJson = JSON.stringify(dataToSign, sortedKeys);
  const dataBuffer = Buffer.from(canonicalJson, "utf-8");

  const pubKeyObject = crypto.createPublicKey(privKeyObject);
  const pubKeyDer = pubKeyObject.export({ format: "der", type: "spki" });
  const rawPubKeyHex = pubKeyDer.subarray(-32).toString("hex");

  const sigBuffer = crypto.sign(null, dataBuffer, privKeyObject);
  const sigHex = sigBuffer.toString("hex");

  const signedManifest = {
    ...dataToSign,
    public_key: rawPubKeyHex,
    signature: sigHex
  };

  // Создаем директории при необходимости
  await fs.mkdir(path.dirname(OUTPUT_MANIFEST_1), { recursive: true });

  // Записываем манифесты
  await fs.writeFile(OUTPUT_MANIFEST_1, JSON.stringify(signedManifest, null, 2), "utf-8");
  await fs.writeFile(OUTPUT_MANIFEST_2, JSON.stringify(signedManifest, null, 2), "utf-8");

  console.log(`✅ Крипто-манифест успешно сгенерирован и подписан Ed25519!`);
  console.log(`   Public Key: ${rawPubKeyHex}`);
  console.log(`   Signature: ${sigHex}`);
  console.log(`   Saved to: ${OUTPUT_MANIFEST_1}`);
  console.log(`   Saved to: ${OUTPUT_MANIFEST_2}`);

  // Git add, commit, push
  console.log(`🚀 Выполнение Git Commit & Push в текущую ветку (evidence/fincombank-billing-traces)...`);
  const gitCmds = [
    `git -C "${ROOT_DIR}" add "evidence/fincombank-billing-traces/fincombank_billing_crypto_manifest.json" "fincombank_billing_crypto_manifest.json"`,
    `git -C "${ROOT_DIR}" diff-index --quiet HEAD || git -C "${ROOT_DIR}" commit -m "chore(crypto): generate and Ed25519 sign FinComBank billing crypto-manifest [Core-Node]"`,
    `git -C "${ROOT_DIR}" push origin evidence/fincombank-billing-traces`
  ].join(" && ");

  const { stdout, stderr } = await execAsync(gitCmds);
  console.log(stdout);
  if (stderr) console.error(stderr);
  console.log(`🎉 Пайплайн успешно завершен!`);
}

main().catch(err => {
  console.error(`❌ Критическая ошибка:`, err);
  process.exit(1);
});
