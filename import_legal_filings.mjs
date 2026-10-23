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

const LEGAL_DIR = path.join(ROOT_DIR, "evidence", "fincombank-billing-traces", "legal_filings_2026");

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
  console.log("📥 Сохранение новых процессуальных документов и заявлений (октябрь 2026)...");
  
  await fs.mkdir(LEGAL_DIR, { recursive: true });

  const cerereRevizuiereText = `CĂTRE: CURTEA DE APEL CHIŞINĂU (Colegiul civil)
Dosar nr.: 2r-1026/26
Petent: Macheret Alexei Artur (A©tor), IDNP: 2000001159655
Obiect: CERERE DE REVIZUIRE împotriva deciziei Colegiului civil (judecător-raportor Elena Bolocan, Ana Panov, Svetlana Vişeu), art. 449 CPC (conflict de interese, lipsă de imparţialitate). Solicitare recuzare Elena Bolocan, casarea încheierilor ilegale privind taxa de timbru, acordarea scutirii totale pentru persoana cu dizabilitate gradul I şi victimă a torturii.
Data: 19 octombrie 2026. Semnătura: A©TOR_KEY="#[A©tor Declaration]"
`;

  const criminalComplaintText = `ОФИЦИАЛЬНОЕ ЗАЯВЛЕНИЕ О ПРЕСТУПЛЕНИИ И ТРЕБОВАНИИ РЕСТИТУЦИИ
В Генеральную прокуратуру Республики Молдова / Антикоррупционную прокуратуру
Дата: 26 сентября 2026 г.
Дело / Кейс: CASE-MACHERET-1997-2026 / CCL-39 (Квартира № 64, ул. М. Костин / К. Маркса 13/3)
Заявитель: Мачерет Алексей Артурович, IDNP 2000001159655
Merkle Root: 'CFC9a2465bde77' (SHA-256 Verified, от 25.04.2026)
Требования: возбуждение уголовного дела по фактам служебного подлога, мошенничества, фальсификации судебных решений (по делам № 2-1642/08 и № 1-568/98), расследование подмены IDNP Нантой Л.И., полная реституция квартиры № 64 (CCL-39) и взыскание материального и морального ущерба в размере 25 210 256,15 MDL.
`;

  const sesizareArt313Text = `CĂTRE: Judecătoria Chişinău, Sediul Ciocana (Judecător Sergiu Ciobanu)
În dosarul penal nr. 1-26114218-12-10-09092026-1 (10-2071/2026)
Petent / Parte vătămată: Maceret Alexei. Avocat: Kebeş Alexei.
SESIZARE şi cerere privind excepția de neconstituţionalitate a art. 313 CPP (examinarea plângerilor în absenţa părților), solicitarea de amânare a ședinței din 07.10.2026 și sesizarea Curții Constituționale. Abuzurile organelor de urmărire penală (oficiul Râșcani) în mușamalizarea furturilor bancare (FinComBank și Moldindconbank).
Data: 03.10.2026.
`;

  await fs.writeFile(path.join(LEGAL_DIR, "cerere_revizuiere_2r_1026_26.txt"), cerereRevizuiereText, "utf-8");
  await fs.writeFile(path.join(LEGAL_DIR, "criminal_complaint_26092026.txt"), criminalComplaintText, "utf-8");
  await fs.writeFile(path.join(LEGAL_DIR, "sesizare_art_313_cpp_03102026.txt"), sesizareArt313Text, "utf-8");

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
           name.includes('criminal_complaint') ||
           name.includes('sesizare') ||
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
    description: "Comprehensive FinComBank billing statements, pre-trial claims, revision requests (2r-1026/26), criminal complaints, Art. 313 CPP objections, and evidence crypto-manifest",
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
    `git diff-index --quiet HEAD || git commit -m "chore(crypto): add revision request 2r-1026/26, criminal complaint 26.09.2026, and Art. 313 CPP objection to Ed25519 signed FinComBank manifest [Core-Node]"`,
    `git push origin evidence/fincombank-billing-traces`
  ].join(" && ");

  const { stdout, stderr } = await execAsync(gitCmds);
  console.log(stdout);
  if (stderr) console.error(stderr);
  console.log(`🎉 Заявления о пересмотре, жалобы и процессуальные документы успешно зафиксированы в крипто-манифесте и отправлены в репозиторий!`);
}

main().catch(err => {
  console.error(`❌ Критическая ошибка:`, err);
  process.exit(1);
});
