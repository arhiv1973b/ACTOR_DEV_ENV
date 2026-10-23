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
  console.log("📥 Сохранение консолидированной и окончательной Cerere de Revizuire (21.10.2026)...");
  
  await fs.mkdir(LEGAL_DIR, { recursive: true });

  const consolidatedText = `CERERE DE REVIZUIRE (Forma consolidată și definitivată pentru depunere)
Către: Curtea de Apel Chișinău (prin intermediul instanței care a pronunțat hotărârea atacată, cu adresare ulterioară către Curtea Supremă de Justiție)
Reclamant (Revizuent): MACHEREȚ ALEXEI (A©tor) IDNP: 2000001159655 Domiciliu: mun. Chișinău, str. Andrei Doga 30, ap. 38 Statut: persoană cu dizabilitate severă (gradul I, pe viață), victimă oficial recunoscută a torturii. În nume propriu (autoreprezentare)
Obiect: Cerere de revizuire a Încheierii Colegiului penal al Curții de Apel Chișinău din 01.10.2026 (judecători Băbălău Denis, Schibin Vladislav, Buzu Elisaveta), prin care s-a legiferat menținerea efectelor actelor de tortură și a consecințelor continue ale acestora, cu încălcarea normelor imperative jus cogens și a obligațiilor erga omnes.

I. TEMEIUL JURIDIC AL CERERII
Art. 4 și 8 din Constituția Republicii Moldova, art. 8 din Declarația Universală a Drepturilor Omului (1948), normele imperative jus cogens (interdicția absolută a torturii).

II. CIRCUMSTANȚELE DE FAPT
1. Legalizarea directă a consecințelor torturii prin Încheierea din 01.10.2026.
2. Ascunderea și sabotarea Deciziei CSJ nr. 1ra-834/09 din 21.07.2009.
3. Consecințe continue și complicitate judiciară în confiscarea proprietății (imobilul din str. M. Costin 13/3, ap. 64 / CCL-39).

III. SOLICITĂRI
1. Admiterea prezentei cereri de revizuire și constatarea unui viciu fundamental.
2. Anularea (casarea) integrală a Încheierii Colegiului penal al Curții de Apel Chișinău din 01.10.2026 (dosar nr. 21r-10/26).
3. Pronunțarea unei noi hotărâri (nulitatea absolută ab initio a acuzațiilor fabricate, restitutio in integrum).
4. Înlăturarea consecințelor patrimoniale, inclusiv deblocarea sumei de 25.210.256,15 MDL.
5. Interdicție absolută privind reprezentarea de stat (autoreprezentare exclusivă).

IV. PROBE ȘI ANEXE
1. Extras din baza de date criptografică a probatoriului (Manifest JSON securizat prin semnătura Ed25519) – reprezentând Registrul Apostilelor și baza probatorie (Merkle Root hash-secol: CFC9a2465bde77).
2. Demers Suplimentar.
3. Încheierea Curții de Apel Centru din 01.10.2026.
4. Avizul științific al Institutului de Filologie nr. 269 din 01.10.2026.
5. Adeverința de dizabilitate (gradul I, pe viață).

Data: 21 octombrie 2026
Semnătura: MACHEREȚ ALEXEI (A©tor) (în nume propriu / autoreprezentare)
A©TOR_KEY="#[⚖ A©tor Declaration]"
`;

  await fs.writeFile(path.join(LEGAL_DIR, "cerere_revizuiere_consolidata_21102026.txt"), consolidatedText, "utf-8");

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
           name.includes('consolidata') ||
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
    description: "Comprehensive FinComBank billing statements, consolidated Cerere de Revizuire (21.10.2026), and evidence crypto-manifest",
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
    `git diff-index --quiet HEAD || git commit -m "chore(crypto): add consolidated Cerere de Revizuire (21.10.2026) to Ed25519 signed FinComBank manifest [Core-Node]"`,
    `git push origin evidence/fincombank-billing-traces`
  ].join(" && ");

  const { stdout, stderr } = await execAsync(gitCmds);
  console.log(stdout);
  if (stderr) console.error(stderr);
  console.log(`🎉 Консолидированная ревизия успешно зафиксирована в крипто-манифесте и отправлена в репозиторий!`);
}

main().catch(err => {
  console.error(`❌ Критическая ошибка:`, err);
  process.exit(1);
});
