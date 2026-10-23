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

// Создаем файлы документов претензии и ответов на основе полученных данных
const CLAIM_DOCS_DIR = path.join(ROOT_DIR, "evidence", "fincombank-billing-traces", "claims_2026");

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
  console.log("📥 Сохранение новых документов досудебной претензии и переписки с FinComBank (октябрь 2026)...");
  
  await fs.mkdir(CLAIM_DOCS_DIR, { recursive: true });

  const claimText = `ДОСУДЕБНАЯ ПРЕТЕНЗИЯ
о разблокировании и зачислении денежных средств (09.10.2026)
Адресат: FinComBank S.A., Юридический департамент, ул. Пушкина, 26, Кишинёв
Заявитель: Мачерет Алексей (Maceret Alexei), IDNP: 2000001159655
Адрес: мун. Кишинёв, ул. А. Дога, 30, кв. 38

Сумма спора: 25 210 256,15 MDL на счетах FinComPay / FinComBank.
Основания:
1. Определение ВСП РМ по делу № 1ra-834/09 о полной реабилитации.
2. Научное заключение Института филологии (Aviz № 269 от 01.10.2026), подтверждающее тождественность написания фамилии (Macheret / Мачерет).
3. Документы ASP об отсутствии ограничений.

ТРЕБУЮ:
1. Незамедлительно снять блокировку, зачислить и обеспечить беспрепятственный доступ к сумме 25 210 256,15 MDL.
2. Предоставить детальную выписку и письменное обоснование причин блокировки.
3. В случае отказа в течение 10 дней — обращение в судебные инстанции и международные суды.
`;

  const avizText = `AVIZ 
ştiinţific privind etimologizarea şi identificarea numelui/prenumelui
Institutul de Filologie Română „Bogdan Petriceicu-Hasdeu” (Nr. 269 din 01.10.2026)
Numele de familie MACERET (ALEXEI) / MACHERET (ARTUR) / МАЧЕРЕТ sunt variante echivalente antroponimic, purtate de membrii uneia şi aceleiaşi familii.
Titularul este cetăţean al Republicii Moldova, IDNP 2000001159655.
Secretar al Comisiei / Cercetător ştiinţific Lidia Vieru.
`;

  const bankResponseText = `FinComBank S.A. Răspuns nr. 7614/Out din 07.10.2026
Semnat de Preşedinte interimar al Comitetului de Conducere Elena Stovbun.
Răspuns la notificarea din 25.09.2026, anexând extrase de cont pentru perioada 01.04.2026 - 28.09.2026 (conturi nr. 225920600348117/498 și nr. 225930100319987/498).
`;

  await fs.writeFile(path.join(CLAIM_DOCS_DIR, "pre_trial_claim_20261009.txt"), claimText, "utf-8");
  await fs.writeFile(path.join(CLAIM_DOCS_DIR, "aviz_institute_philology_20261001.txt"), avizText, "utf-8");
  await fs.writeFile(path.join(CLAIM_DOCS_DIR, "fincombank_response_7614_out_20261007.txt"), bankResponseText, "utf-8");

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
    description: "Comprehensive FinComBank billing statements, pre-trial claims, Philology Aviz No. 269, bank responses, and scanner evidence crypto-manifest",
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
    `git diff-index --quiet HEAD || git commit -m "chore(crypto): add pre-trial claim 09.10.2026, Aviz No. 269, and bank responses to Ed25519 signed FinComBank manifest [Core-Node]"`,
    `git push origin evidence/fincombank-billing-traces`
  ].join(" && ");

  const { stdout, stderr } = await execAsync(gitCmds);
  console.log(stdout);
  if (stderr) console.error(stderr);
  console.log(`🎉 Претензия, Авиз филологии и ответы банка успешно зафиксированы в крипто-манифесте и отправлены в репозиторий!`);
}

main().catch(err => {
  console.error(`❌ Критическая ошибка:`, err);
  process.exit(1);
});
