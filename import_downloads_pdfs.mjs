import crypto from "crypto";
import fs from "fs/promises";
import fsSync from "fs";
import path from "path";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);
const ROOT_DIR = "H:\\ACTOR_DEV_ENV";
const PRIVATE_KEY_PATH = path.join(ROOT_DIR, "keys", "ti_ula_ed25519.pem");

const OUTPUT_MANIFEST_1 = path.join(ROOT_DIR, "evidence", "fincombank-billing-traces", "fincombank_billing_crypto_manifest.json");
const OUTPUT_MANIFEST_2 = path.join(ROOT_DIR, "fincombank_billing_crypto_manifest.json");

const DOWNLOADS_DIR = path.join(ROOT_DIR, "evidence", "fincombank-billing-traces", "downloads_2026");

async function calculateFileSha256(filePath) {
  return new Promise((resolve, reject) => {
    const hash = crypto.createHash("sha256");
    const stream = fsSync.createReadStream(filePath);
    stream.on("data", (chunk) => hash.update(chunk));
    stream.on("end", () => resolve(hash.digest("hex").toLowerCase()));
    stream.on("error", (err) => reject(err));
  });
}

async function getFilesRecursive(dir) {
  const dirents = await fs.readdir(dir, { withFileTypes: true });
  const files = await Promise.all(dirents.map((dirent) => {
    const res = path.resolve(dir, dirent.name);
    return dirent.isDirectory() ? getFilesRecursive(res) : res;
  }));
  return Array.prototype.concat(...files);
}

async function main() {
  console.log("📥 Импорт файлов Cerere_de_Revizuire_Macheret_PRINT.pdf и Документ (232).pdf...");
  
  await fs.mkdir(DOWNLOADS_DIR, { recursive: true });

  const sourceFiles = [
    { src: "H:\\Загрузки\\Cerere_de_Revizuire_Macheret_PRINT.pdf", dest: "Cerere_de_Revizuire_Macheret_PRINT.pdf" },
    { src: "H:\\Загрузки\\Документ (232).pdf", dest: "Document_232.pdf" }
  ];

  for (const item of sourceFiles) {
    try {
      if (fsSync.existsSync(item.src)) {
        await fs.copyFile(item.src, path.join(DOWNLOADS_DIR, item.dest));
        console.log(`  [COPIED] ${item.src} -> evidence/fincombank-billing-traces/downloads_2026/${item.dest}`);
      } else {
        console.log(`  [WARNING] Источник не найден: ${item.src}`);
      }
    } catch (err) {
      console.error(`  [ERROR] Не удалось скопировать ${item.src}: ${err.message}`);
    }
  }

  console.log("🔍 Сканирование репозитория для обновления крипто-манифеста...");
  const allFiles = await getFilesRecursive(ROOT_DIR);
  
  const targetFiles = allFiles.filter(file => {
    const lower = file.toLowerCase();
    const isTargetExt = lower.endsWith('.pdf') || lower.endsWith('.png') || lower.endsWith('.jpg') || lower.endsWith('.jpeg') || lower.endsWith('.json') || lower.endsWith('.txt');
    if (!isTargetExt) return false;
    
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
           name.includes('claim') ||
           name.includes('aviz') ||
           name.includes('revizuiere') ||
           name.includes('cerere_de_revizuire') ||
           name.includes('criminal_complaint') ||
           name.includes('sesizare') ||
           name.includes('decizie_21r') ||
           name.includes('document_232') ||
           name.includes('scanner_x_2026-10-20') ||
           name.includes('legal_reply_fincombank') ||
           name.includes('legal_submission_fincombank');
  });

  console.log(`📦 Всего релевантных файлов в манифесте: ${targetFiles.length}`);

  const fileEntries = [];
  for (const filePath of targetFiles) {
    try {
      const hash = await calculateFileSha256(filePath);
      const relativePath = path.relative(ROOT_DIR, filePath).replace(/\\/g, '/');
      fileEntries.push({
        path: relativePath,
        hash: hash
      });
    } catch (err) {
      console.error(`  [ERROR] ${filePath}: ${err.message}`);
    }
  }

  fileEntries.sort((a, b) => a.path.localeCompare(b.path));

  const manifestData = {
    version: "1.0",
    case_id: "CASE-MACHERET-1997-2026",
    timestamp: new Date().toISOString(),
    description: "Comprehensive FinComBank billing statements, Cerere de Revizuire PRINT PDF, Document 232 PDF, and evidence crypto-manifest",
    algorithm: "SHA-256",
    files: fileEntries
  };

  console.log(`🔑 Подписание обновленного манифеста ключом Ed25519...`);
  const privateKeyPem = await fs.readFile(PRIVATE_KEY_PATH, "utf-8");
  const privKeyObject = crypto.createPrivateKey(privateKeyPem);

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

  await fs.writeFile(OUTPUT_MANIFEST_1, JSON.stringify(signedManifest, null, 2), "utf-8");
  await fs.writeFile(OUTPUT_MANIFEST_2, JSON.stringify(signedManifest, null, 2), "utf-8");

  console.log(`✅ Манифест успешно обновлен и подписан!`);
  console.log(`   Public Key: ${rawPubKeyHex}`);
  console.log(`   Signature: ${sigHex}`);

  console.log(`🚀 Выполнение Git Commit & Push...`);
  const gitCmds = [
    `git config --global --add safe.directory "${ROOT_DIR}"`,
    `git add "evidence/fincombank-billing-traces/" "fincombank_billing_crypto_manifest.json"`,
    `git diff-index --quiet HEAD || git commit -m "chore(crypto): import Cerere_de_Revizuire_Macheret_PRINT.pdf and Document 232 to Ed25519 signed FinComBank manifest [Core-Node]"`,
    `git push origin evidence/fincombank-billing-traces`
  ].join(" && ");

  const { stdout, stderr } = await execAsync(gitCmds);
  console.log(stdout);
  if (stderr) console.error(stderr);
  console.log(`🎉 Файлы успешно импортированы, зафиксированы в крипто-манифесте и отправлены в репозиторий!`);
}

main().catch(err => {
  console.error(`❌ Критическая ошибка:`, err);
  process.exit(1);
});
