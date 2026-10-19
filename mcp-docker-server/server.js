import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import crypto from "crypto";
import fs from "fs/promises";
import fsSync from "fs";
import { constants } from "fs";
import path from "path";
import { z } from "zod";
import { exec } from "child_process";
import { promisify } from "util";
import "dotenv/config";

// Проверка прав доступа к файлу .env при старте
const envPath = path.resolve(process.cwd(), ".env");
try {
  if (fsSync.existsSync(envPath)) {
    const stats = fsSync.statSync(envPath);
    const permissions = stats.mode & 0o777;
    if ((permissions & 0o077) !== 0) {
      console.error(`🚨 ОШИБКА БЕЗОПАСНОСТИ: Файл .env имеет слишком широкие права доступа (${permissions.toString(8)})!`);
      console.error(`💡 Исправьте права в терминале WSL командой: chmod 600 .env`);
      process.exit(1);
    } else {
      console.error(`[Security] Права файла .env безопасны (${permissions.toString(8)} - rw-------).`);
    }
  }
} catch (err) {
  console.error(`[Security] Предупреждение: Не удалось проверить права файла .env: ${err.message}`);
}

const execAsync = promisify(exec);

const CryptoManifestSchema = z.object({
  version: z.string().optional(),
  timestamp: z.string().optional(),
  public_key: z.string().optional().describe("Публичный ключ Ed25519 (HEX 64 символа или PEM)"),
  signature: z.string().optional().describe("Цифровая подпись Ed25519 (HEX 128 символов)"),
  algorithm: z.string().default("SHA-256"),
  files: z.array(z.object({
    path: z.string(),
    hash: z.string().length(64)
  }))
}).passthrough();

// 1. Загрузка реестра доверенных ключей при старте
let trustedKeys = [];
try {
  const keyringData = await fs.readFile("/app/trusted_keys.json", "utf-8");
  trustedKeys = JSON.parse(keyringData).trusted_keys;
  console.error(`[Keyring] Загружено ${trustedKeys.length} доверенных ключей Ed25519.`);
} catch (err) {
  console.error("[Keyring] Внимание: trusted_keys.json не найден. Аутентификация авторов отключена.");
}

// 2. Вспомогательная функция поиска автора
function getAuthorIdentity(publicKeyHex) {
  if (!publicKeyHex) return null;
  const match = trustedKeys.find(
    k => k.public_key.toLowerCase() === publicKeyHex.toLowerCase()
  );
  return match ? match : null;
}

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

// Верификация подписи Ed25519 манифеста
function verifyEd25519Manifest(manifestData) {
  const { signature, public_key, ...dataToVerify } = manifestData;

  if (!signature || !public_key) {
    return { valid: false, reason: "Отсутствует signature или public_key в манифесте" };
  }

  try {
    const sortedKeys = Object.keys(dataToVerify).sort();
    const canonicalJson = JSON.stringify(dataToVerify, sortedKeys);
    const dataBuffer = Buffer.from(canonicalJson, "utf-8");
    const sigBuffer = Buffer.from(signature, "hex");

    let keyObject;
    if (public_key.includes("-----BEGIN PUBLIC KEY-----")) {
      keyObject = crypto.createPublicKey(public_key);
    } else {
      const rawKeyBuffer = Buffer.from(public_key, "hex");
      const spkiHeader = Buffer.from("302a300506032b6570032100", "hex");
      keyObject = crypto.createPublicKey({
        key: Buffer.concat([spkiHeader, rawKeyBuffer]),
        format: "der",
        type: "spki"
      });
    }

    const isValid = crypto.verify(null, dataBuffer, keyObject, sigBuffer);
    return {
      valid: isValid,
      reason: isValid ? "Подпись действительна" : "Подпись недействительна (содержимое манифеста было изменено)"
    };
  } catch (err) {
    return { valid: false, reason: `Ошибка криптографии: ${err.message}` };
  }
}

// Подписание манифеста приватным ключом Ed25519
function signEd25519Manifest(manifestData, privateKeyInput) {
  const { signature, public_key, ...dataToSign } = manifestData;

  const sortedKeys = Object.keys(dataToSign).sort();
  const canonicalJson = JSON.stringify(dataToSign, sortedKeys);
  const dataBuffer = Buffer.from(canonicalJson, "utf-8");

  let privKeyObject;
  if (privateKeyInput.includes("-----BEGIN PRIVATE KEY-----")) {
    privKeyObject = crypto.createPrivateKey(privateKeyInput);
  } else {
    const rawPrivBuffer = Buffer.from(privateKeyInput, "hex");
    const pkcs8Header = Buffer.from("302e020100300506032b657004220420", "hex");
    privKeyObject = crypto.createPrivateKey({
      key: Buffer.concat([pkcs8Header, rawPrivBuffer]),
      format: "der",
      type: "pkcs8"
    });
  }

  const pubKeyObject = crypto.createPublicKey(privKeyObject);
  const pubKeyDer = pubKeyObject.export({ format: "der", type: "spki" });
  const rawPubKeyHex = pubKeyDer.subarray(-32).toString("hex");

  const sigBuffer = crypto.sign(null, dataBuffer, privKeyObject);
  const sigHex = sigBuffer.toString("hex");

  return {
    signedManifest: {
      ...dataToSign,
      public_key: rawPubKeyHex,
      signature: sigHex
    },
    publicKeyHex: rawPubKeyHex,
    signatureHex: sigHex
  };
}

// Вспомогательная функция для рекурсивного сбора файлов
async function getFilesRecursive(dir) {
  const dirents = await fs.readdir(dir, { withFileTypes: true });
  const files = await Promise.all(dirents.map((dirent) => {
    const res = path.resolve(dir, dirent.name);
    return dirent.isDirectory() ? getFilesRecursive(res) : res;
  }));
  return Array.prototype.concat(...files);
}

const server = new Server(
  { name: "custom-crypto-mcp", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "calculate_sha256",
      description: "Вычисляет SHA-256 хеш для переданного текста",
      inputSchema: {
        type: "object",
        properties: {
          text: { type: "string", description: "Текст для хеширования" }
        },
        required: ["text"]
      }
    },
    {
      name: "run_forensic_audit",
      description: "Запускает air-gapped проверку SHA-256 хешей для указанной директории",
      inputSchema: {
        type: "object",
        properties: {
          targetDirectory: { type: "string", default: "/audit_data", description: "Путь к проверяемой директории внутри контейнера" }
        }
      }
    },
    {
      name: "validate_crypto_manifest",
      description: "Читает JSON крипто-манифест, проверяет Ed25519 подпись, аутентифицирует автора по реестру доверенных ключей (учитывая статусы отзыва), выполняет потоковый SHA-256 аудит файлов и сохраняет подробный CSV-отчет",
      inputSchema: {
        type: "object",
        properties: {
          file_path: { type: "string", description: "Абсолютный путь к JSON файлу (например, H:\\ACTOR_DEV_ENV\\manifest.json)" }
        },
        required: ["file_path"]
      }
    },
    {
      name: "run_gdpr_cookie_audit",
      description: "Запускает скрипт GDPR Cookie & Storage Forensic Audit для проверки локальных артефактов и формирования SHA-256 манифеста",
      inputSchema: {
        type: "object",
        properties: {
          input_file: { type: "string", description: "Путь к файлу артефактов (например, C:\\Users\\arhiv\\Downloads\\Downolde\\Анализ файлов cookie Truth Social.json)" },
          output_report: { type: "string", description: "Путь для сохранения JSON-отчета (например, H:\\ACTOR_DEV_ENV\\reports\\truth_social_cookie_audit.json)" }
        },
        required: ["input_file"]
      }
    },
    {
      name: "sign_crypto_manifest",
      description: "Подписывает JSON-манифест приватным ключом Ed25519 (берет ключ из .env по умолчанию, если не указан) и вшивает подпись в файл",
      inputSchema: {
        type: "object",
        properties: {
          manifest_path: { type: "string", description: "Путь к JSON-манифесту (H:\\ACTOR_DEV_ENV\\manifest.json)" },
          private_key: { type: "string", description: "Приватный ключ Ed25519 (опционально, по умолчанию из .env)" }
        },
        required: ["manifest_path"]
      }
    },
    {
      name: "re_sign_manifest",
      description: "Переподписывает существующий JSON-манифест при ротации (берет ключ из .env по умолчанию, если не указан) и обновляет файл на диске H:\\ in-place",
      inputSchema: {
        type: "object",
        properties: {
          manifest_path: { type: "string", description: "Путь к JSON-манифесту (H:\\ACTOR_DEV_ENV\\manifest.json)" },
          new_private_key: { type: "string", description: "Новый приватный ключ Ed25519 (опционально, по умолчанию из .env)" }
        },
        required: ["manifest_path"]
      }
    },
    {
      name: "re_sign_all_manifests",
      description: "Рекурсивно сканирует директорию на диске H:\\, находит все JSON-манифесты и массово переподписывает их новым приватным ключом Ed25519",
      inputSchema: {
        type: "object",
        properties: {
          root_dir: { type: "string", description: "Корневая директория для поиска (например, H:\\ACTOR_DEV_ENV)" },
          new_private_key: { type: "string", description: "Новый приватный ключ Ed25519 (HEX 64 символа или PEM)" }
        },
        required: ["root_dir", "new_private_key"]
      }
    },
    {
      name: "add_trusted_key",
      description: "Регистрирует новый публичный ключ Ed25519 и данные автора в реестре доверенных ключей (trusted_keys.json)",
      inputSchema: {
        type: "object",
        properties: {
          identity: { type: "string", description: "Имя автора или название системы (например, Alexei Macheret (A©tor))" },
          public_key: { type: "string", description: "Публичный ключ Ed25519 (HEX 64 символа)" },
          role: { type: "string", description: "Роль или уровень доступа (например, Owner, Auditor, CI/CD Bot)" }
        },
        required: ["identity", "public_key", "role"]
      }
    },
    {
      name: "list_trusted_keys",
      description: "Выводит список всех зарегистрированных в системе ключей Ed25519 с фильтрацией по статусу (активные / отозванные)",
      inputSchema: {
        type: "object",
        properties: {
          status_filter: { 
            type: "string", 
            enum: ["all", "active", "revoked"], 
            default: "active", 
            description: "Фильтр ключей: только активные (active), только отозванные (revoked) или все (all)" 
          }
        }
      }
    },
    {
      name: "export_trusted_keys_for_pages",
      description: "Экспортирует публичную часть реестра доверенных ключей (без секретных данных) в публичную директорию для публикации на GitHub Pages",
      inputSchema: {
        type: "object",
        properties: {
          output_dir: { type: "string", description: "Путь к публичной директории сайта (например, H:\\ACTOR_DEV_ENV\\docs)" },
          file_name: { type: "string", default: "keys.json", description: "Имя результирующего файла (например, keys.json)" }
        },
        required: ["output_dir"]
      }
    },
    {
      name: "export_trusted_keys_html",
      description: "Генерирует и сохраняет стилизованную HTML-страницу со списком доверенных ключей Ed25519 для публикации на GitHub Pages",
      inputSchema: {
        type: "object",
        properties: {
          output_dir: { type: "string", description: "Путь к публичной директории сайта (например, H:\\ACTOR_DEV_ENV\\docs)" },
          file_name: { type: "string", default: "keys.html", description: "Имя HTML файла (например, index.html или keys.html)" }
        },
        required: ["output_dir"]
      }
    },
    {
      name: "revoke_trusted_key",
      description: "Отозывает скомпрометированный публичный ключ Ed25519 в реестре и опционально связывает его с новым ключом замены",
      inputSchema: {
        type: "object",
        properties: {
          public_key: { type: "string", description: "Отозываемый публичный ключ Ed25519 (HEX 64 символа)" },
          reason: { type: "string", description: "Причина отзыва (например, Compromised key, Scheduled rotation)" },
          replacement_public_key: { type: "string", description: "Новый публичный ключ Ed25519 для ротации (опционально)" }
        },
        required: ["public_key", "reason"]
      }
    },
    {
      name: "generate_ed25519_keypair",
      description: "Генерирует новую пару ключей Ed25519, сохраняет их на диск H:\\ и автоматически регистрирует публичный ключ в trusted_keys.json",
      inputSchema: {
        type: "object",
        properties: {
          output_dir: { type: "string", description: "Директория для сохранения ключей (например, H:\\ACTOR_DEV_ENV\\keys)" },
          key_name: { type: "string", description: "Префикс имён файлов (например, ed25519_actor)" },
          format: { 
            type: "string", 
            enum: ["hex", "pem"], 
            default: "hex", 
            description: "Формат сохранения ключей: hex или pem" 
          },
          auto_register: { 
            type: "boolean", 
            default: true, 
            description: "Автоматически добавить публичный ключ в реестр доверенных подписисантов" 
          },
          identity: { type: "string", description: "Имя автора (например, Alexei Macheret (A©tor))" },
          role: { type: "string", description: "Роль подписисанта (например, Primary Signer, Auditor)" }
        },
        required: ["output_dir", "key_name"]
      }
    },
    {
      name: "generate_rclone_recovery_script",
      description: "Генерирует оптимизированные Rclone скрипты для восстановления отсутствующих и поврежденных файлов (MISSING, HASH_MISMATCH)",
      inputSchema: {
        type: "object",
        properties: {
          csv_path: { type: "string", description: "Путь к CSV отчету аудита (например, H:\\ACTOR_DEV_ENV\\missing_evidence_audit_report.csv)" },
          remote_name: { type: "string", description: "Имя удаленного remote в Rclone (например, 'remote:backup')" }
        },
        required: ["csv_path", "remote_name"]
      }
    },
    {
      name: "generate_rclone_backup_script",
      description: "Находит файлы на диске, которых нет в крипто-манифесте, и генерирует скрипт для их бэкапа через Rclone",
      inputSchema: {
        type: "object",
        properties: {
          manifest_path: { type: "string", description: "Путь к JSON-манифесту (H:\\ACTOR_DEV_ENV\\manifest.json)" },
          scan_dir: { type: "string", description: "Директория для поиска новых файлов (H:\\ACTOR_DEV_ENV)" },
          remote_name: { type: "string", description: "Имя Rclone remote назначения (например, my_drive:Backup/ACTOR_DEV_ENV)" }
        },
        required: ["manifest_path", "scan_dir", "remote_name"]
      }
    },
    {
      name: "execute_rclone_recovery",
      description: "Автономно запускает Rclone внутри контейнера для скачивания недостающих файлов по списку",
      inputSchema: {
        type: "object",
        properties: {
          remote_name: { type: "string", description: "Имя remote в rclone (например, my_drive:Backup)" },
          list_file_path: { type: "string", description: "Путь к txt-файлу со списком файлов (например, H:\\ACTOR_DEV_ENV\\rclone_missing_files.txt)" }
        },
        required: ["remote_name", "list_file_path"]
      }
    },
    {
      name: "git_commit_and_push_manifests",
      description: "Автоматически добавляет измененные файлы и манифесты в Git, делает коммит и отправляет изменения (push) в репозиторий",
      inputSchema: {
        type: "object",
        properties: {
          repo_dir: { type: "string", description: "Путь к корню репозитория (например, H:\\ACTOR_DEV_ENV)" },
          commit_message: { type: "string", description: "Сообщение коммита (например, 'chore: update crypto manifests and signatures')" },
          branch: { type: "string", default: "main", description: "Целевая ветка для пуша" }
        },
        required: ["repo_dir", "commit_message"]
      }
    },
    {
      name: "full_sync_and_publish",
      description: "Комплексный контур: рекурсивно проверяет манифесты, переподписывает их новым ключом Ed25519, коммитит изменения и пушит в Git за один вызов",
      inputSchema: {
        type: "object",
        properties: {
          root_dir: { type: "string", description: "Корневая директория репозитория (например, H:\\ACTOR_DEV_ENV)" },
          new_private_key: { type: "string", description: "Новый приватный ключ Ed25519 (HEX или PEM) для переподписания" },
          commit_message: { type: "string", default: "chore: auto-sign and sync manifests", description: "Сообщение для Git коммита" },
          branch: { type: "string", default: "main", description: "Целевая ветка Git" }
        },
        required: ["root_dir", "new_private_key"]
      }
    }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "calculate_sha256") {
    const text = String(request.params.arguments.text);
    const hash = crypto.createHash('sha256').update(text).digest('hex');
    
    return {
      content: [{ type: "text", text: hash }]
    };
  }

  if (request.params.name === "run_forensic_audit") {
    const targetDirectory = String(request.params.arguments?.targetDirectory || "/audit_data");
    try {
      const { stdout, stderr } = await execAsync(`python3 /app/forensic_air_gapped_audit.py ${targetDirectory}`);
      
      return {
        content: [{ 
          type: "text", 
          text: stdout || stderr 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Критическая ошибка аудита: ${error.message}\n${error.stderr || ''}` 
        }],
        isError: true
      };
    }
  }

  if (request.params.name === "run_gdpr_cookie_audit") {
    const rawInput = String(request.params.arguments.input_file);
    const rawOutput = String(request.params.arguments.output_report || "H:\\ACTOR_DEV_ENV\\reports\\truth_social_cookie_audit.json");

    const containerInput = rawInput.replace(/^([a-zA-Z]):\\/i, (_, drv) => `/mnt/${drv.toLowerCase()}/`).replace(/\\/g, '/');
    const containerOutput = rawOutput.replace(/^([a-zA-Z]):\\/i, (_, drv) => `/mnt/${drv.toLowerCase()}/`).replace(/\\/g, '/');

    const cmd = `python /mnt/h/ACTOR_DEV_ENV/scripts/gdpr_cookie_forensic_audit.py -i "${containerInput}" -o "${containerOutput}"`;

    try {
      console.error(`Executing: ${cmd}`);
      const { stdout, stderr } = await execAsync(cmd, { maxBuffer: 1024 * 1024 * 10 });

      let reportContent = "";
      try {
        reportContent = await fs.readFile(containerOutput, "utf-8");
      } catch {}

      return {
        content: [{ 
          type: "text", 
          text: `✅ GDPR Forensic Audit успешно выполнен!\n\nSTDOUT:\n${stdout}\n\nОтчет сохранен в: ${rawOutput}\n\nСодержимое отчета:\n${reportContent.substring(0, 1500)}` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `❌ Ошибка GDPR аудита (Код ${error.code}):\n${error.message}\n\nSTDERR:\n${error.stderr || 'отсутствует'}` 
        }],
        isError: true
      };
    }
  }

  if (request.params.name === "validate_crypto_manifest") {
    const rawPath = String(request.params.arguments.file_path);
    const containerPath = rawPath.replace(/^H:\\/i, '/mnt/h/').replace(/\\/g, '/');

    try {
      const fileContent = await fs.readFile(containerPath, "utf-8");
      const jsonData = JSON.parse(fileContent);
      const validationResult = CryptoManifestSchema.safeParse(jsonData);
      
      if (!validationResult.success) {
        return {
          content: [{ 
            type: "text", 
            text: `❌ Ошибка валидации схемы Zod:\n${JSON.stringify(validationResult.error.format(), null, 2)}` 
          }],
          isError: true
        };
      }

      // Валидация цифровой подписи Ed25519
      const sigCheck = verifyEd25519Manifest(validationResult.data);
      if (!sigCheck.valid) {
        return {
          content: [{ 
            type: "text", 
            text: `❌ Ошибка аутентификации манифеста!\nПричина: ${sigCheck.reason}` 
          }],
          isError: true
        };
      }

      // Проверка автора по Trusted Keyring
      const author = getAuthorIdentity(validationResult.data.public_key);
      if (!author) {
        return {
          content: [{ 
            type: "text", 
            text: `⚠️ ПОДПИСЬ ВАЛИДНА, НО АВТОР НЕИЗВЕСТЕН!\nПубличный ключ ${validationResult.data.public_key} отсутствует в trusted_keys.json.` 
          }],
          isError: true
        };
      }

      if (author.status === "REVOKED") {
        let warning = `🚨 ОШИБКА БЕЗОПАСНОСТИ: Манифест подписан ОТОЗВАННЫМ ключом!\n`;
        warning += `👤 Автор: ${author.identity}\n`;
        warning += `⛔ Дата отзыва: ${author.revoked_at}\n`;
        warning += `📝 Причина: ${author.revocation_reason}\n`;
        if (author.rotated_to) {
          warning += `🔄 Рекомендуется переподписать манифест новым ключом: ${author.rotated_to}`;
        }
        return {
          content: [{ type: "text", text: warning }],
          isError: true
        };
      }

      const manifestDir = path.dirname(containerPath);
      const auditResults = [];

      await Promise.all(validationResult.data.files.map(async (fileObj) => {
        let targetPath = fileObj.path;
        
        if (/^[a-zA-Z]:\\/.test(targetPath)) {
          targetPath = targetPath.replace(/^H:\\/i, '/mnt/h/').replace(/\\/g, '/');
        } else {
          targetPath = path.resolve(manifestDir, targetPath);
        }

        try {
          await fs.access(targetPath, constants.F_OK);
          
          const actualHash = await calculateFileSha256(targetPath);
          const expectedHash = fileObj.hash.toLowerCase();

          if (actualHash === expectedHash) {
            auditResults.push({ path: fileObj.path, status: "VALID", actualHash, expectedHash });
          } else {
            auditResults.push({ path: fileObj.path, status: "HASH_MISMATCH", actualHash, expectedHash });
          }
        } catch {
          auditResults.push({ path: fileObj.path, status: "MISSING", actualHash: "N/A", expectedHash: fileObj.hash });
        }
      }));

      const invalidItems = auditResults.filter(r => r.status !== "VALID");
      const auditTime = new Date().toISOString();

      let csvContent = "file_path,status,expected_hash,actual_hash,audit_time\n";
      auditResults.forEach(r => {
        csvContent += `"${r.path}",${r.status},${r.expectedHash},${r.actualHash},${auditTime}\n`;
      });

      const csvContainerPath = path.join(manifestDir, "missing_evidence_audit_report.csv");
      await fs.writeFile(csvContainerPath, csvContent, "utf-8");

      let report = `✅ Манифест валиден и аутентифицирован!\n`;
      report += `👤 Подписант: ${author.identity} (${author.role})\n`;
      report += `🔑 Key ID: ${author.public_key.substring(0, 16)}...\n\n`;
      report += `📊 Результаты аудита манифеста "${path.basename(rawPath)}":\n`;
      report += `✅ Успешно проверено (VALID): ${auditResults.length - invalidItems.length}\n`;
      report += `⚠️ Отсутствуют (MISSING): ${auditResults.filter(r => r.status === "MISSING").length}\n`;
      report += `❌ Повреждены/Изменены (HASH_MISMATCH): ${auditResults.filter(r => r.status === "HASH_MISMATCH").length}\n\n`;
      report += `📁 Подробный CSV-отчет записан в: ${csvContainerPath.replace(/^\/mnt\/h\//, 'H:\\').replace(/\//g, '\\')}`;

      return {
        content: [{ type: "text", text: report }]
      };

    } catch (error) {
      return {
        content: [{ type: "text", text: `Ошибка доступа или парсинга: ${error.message}` }],
        isError: true
      };
    }
  }

  if (request.params.name === "sign_crypto_manifest") {
    const rawManifestPath = String(request.params.arguments.manifest_path);
    const privateKeyInput = String(request.params.arguments.private_key || process.env.SIGNING_PRIVATE_KEY || "").trim();

    if (!privateKeyInput) {
      return {
        content: [{ type: "text", text: "❌ Ошибка: Приватный ключ не передан в аргументах и не найден в переменной окружения SIGNING_PRIVATE_KEY (.env)." }],
        isError: true
      };
    }

    const containerPath = rawManifestPath.replace(/^H:\\/i, '/mnt/h/').replace(/\\/g, '/');

    try {
      const fileContent = await fs.readFile(containerPath, "utf-8");
      const jsonData = JSON.parse(fileContent);

      const { signedManifest, publicKeyHex } = signEd25519Manifest(jsonData, privateKeyInput);

      const updatedJsonString = JSON.stringify(signedManifest, null, 2);
      await fs.writeFile(containerPath, updatedJsonString, "utf-8");

      const windowsPath = containerPath.replace(/^\/mnt\/h\//, 'H:\\').replace(/\//g, '\\');

      return {
        content: [{
          type: "text",
          text: `✅ Манифест успешно подписан!\n\n🔑 Public Key: ${publicKeyHex}\n📁 Файл обновлен in-place: ${windowsPath}`
        }]
      };

    } catch (error) {
      return {
        content: [{ type: "text", text: `❌ Ошибка подписания: ${error.message}` }],
        isError: true
      };
    }
  }

  if (request.params.name === "re_sign_manifest") {
    const rawManifestPath = String(request.params.arguments.manifest_path);
    const newPrivateKey = String(request.params.arguments.new_private_key || process.env.SIGNING_PRIVATE_KEY || "").trim();

    if (!newPrivateKey) {
      return {
        content: [{ type: "text", text: "❌ Ошибка: Новый приватный ключ не передан и не найден в переменной окружения SIGNING_PRIVATE_KEY (.env)." }],
        isError: true
      };
    }

    const containerPath = rawManifestPath.replace(/^H:\\/i, '/mnt/h/').replace(/\\/g, '/');

    try {
      const fileContent = await fs.readFile(containerPath, "utf-8");
      const jsonData = JSON.parse(fileContent);

      const { signedManifest, publicKeyHex } = signEd25519Manifest(jsonData, newPrivateKey);

      const updatedJsonString = JSON.stringify(signedManifest, null, 2);
      await fs.writeFile(containerPath, updatedJsonString, "utf-8");

      const windowsPath = containerPath.replace(/^\/mnt\/h\//, 'H:\\').replace(/\//g, '\\');

      return {
        content: [{
          type: "text",
          text: `✅ Манифест успешно переподписан при ротации!\n\n🔑 Новый Public Key: ${publicKeyHex}\n📁 Файл обновлен in-place: ${windowsPath}`
        }]
      };

    } catch (error) {
      return {
        content: [{ type: "text", text: `❌ Ошибка переподписания: ${error.message}` }],
        isError: true
      };
    }
  }

  if (request.params.name === "re_sign_all_manifests") {
    const rawRootDir = String(request.params.arguments.root_dir);
    const newPrivateKey = String(request.params.arguments.new_private_key || process.env.SIGNING_PRIVATE_KEY || "").trim();

    if (!newPrivateKey) {
      return {
        content: [{ type: "text", text: "❌ Ошибка: Новый приватный ключ не передан и не найден в переменной окружения SIGNING_PRIVATE_KEY (.env)." }],
        isError: true
      };
    }

    const containerRootDir = rawRootDir.replace(/^H:\\/i, '/mnt/h/').replace(/\\/g, '/');

    try {
      const allFiles = await getFilesRecursive(containerRootDir);
      const jsonFiles = allFiles.filter(file => 
        file.endsWith('.json') && 
        !file.includes('trusted_keys.json') &&
        !file.includes('audit_report')
      );

      let processedCount = 0;
      let updatedManifests = [];
      let errors = [];

      for (const filePath of jsonFiles) {
        try {
          const content = await fs.readFile(filePath, "utf-8");
          const jsonData = JSON.parse(content);
          if (jsonData && Array.isArray(jsonData.files)) {
            const { signedManifest } = signEd25519Manifest(jsonData, newPrivateKey);
            await fs.writeFile(filePath, JSON.stringify(signedManifest, null, 2), "utf-8");
            const windowsPath = filePath.replace(/^\/mnt\/h\//, 'H:\\').replace(/\//g, '\\');
            updatedManifests.push(windowsPath);
            processedCount++;
          }
        } catch (fileErr) {
          errors.push({ file: filePath, error: fileErr.message });
        }
      }

      let report = `🔄 Массовая ротация и переподпись завершена!\n`;
      report += `📊 Всего обработано манифестов: ${processedCount}\n\n`;
      if (updatedManifests.length > 0) {
        report += `📁 Обновленные файлы:\n`;
        updatedManifests.forEach(p => report += `- ${p}\n`);
      }
      if (errors.length > 0) {
        report += `\n⚠️ Ошибки при обработке ${errors.length} файлов:\n`;
        errors.forEach(e => report += `- ${e.file}: ${e.error}\n`);
      }

      return {
        content: [{ type: "text", text: report }]
      };
    } catch (error) {
      return {
        content: [{ type: "text", text: `❌ Ошибка массового переподписания: ${error.message}` }],
        isError: true
      };
    }
  }

  if (request.params.name === "add_trusted_key") {
    const identity = String(request.params.arguments.identity).trim();
    const rawPubKey = String(request.params.arguments.public_key).trim().toLowerCase();
    const role = String(request.params.arguments.role).trim();

    if (!/^[a-f0-9]{64}$/i.test(rawPubKey)) {
      return {
        content: [{ type: "text", text: "❌ Ошибка: Публичный ключ должен состоять ровно из 64 HEX-символов (32 байта Ed25519)." }],
        isError: true
      };
    }

    const keyringPath = "/app/trusted_keys.json";

    try {
      let keyringData = { trusted_keys: [] };
      try {
        const fileContent = await fs.readFile(keyringPath, "utf-8");
        keyringData = JSON.parse(fileContent);
      } catch {}

      const exists = keyringData.trusted_keys.some(
        k => k.public_key.toLowerCase() === rawPubKey
      );

      if (exists) {
        return {
          content: [{ type: "text", text: `⚠️ Ключ ${rawPubKey.substring(0, 16)}... уже зарегистрирован в реестре.` }]
        };
      }

      const newEntry = {
        identity,
        public_key: rawPubKey,
        role,
        added_at: new Date().toISOString()
      };

      keyringData.trusted_keys.push(newEntry);
      await fs.writeFile(keyringPath, JSON.stringify(keyringData, null, 2), "utf-8");
      trustedKeys = keyringData.trusted_keys;

      return {
        content: [{
          type: "text",
          text: `✅ Новый доверенный ключ успешно добавлен в реестр!\n\n` +
                `👤 Автор: ${identity}\n` +
                `🔑 Public Key: ${rawPubKey}\n` +
                `🛡 Роль: ${role}\n` +
                `📅 Дата добавления: ${newEntry.added_at}`
        }]
      };

    } catch (error) {
      return {
        content: [{ type: "text", text: `❌ Ошибка записи в trusted_keys.json: ${error.message}` }],
        isError: true
      };
    }
  }

  if (request.params.name === "list_trusted_keys") {
    const filter = String(request.params.arguments?.status_filter || "active").toLowerCase();
    const keyringPath = "/app/trusted_keys.json";

    try {
      const fileContent = await fs.readFile(keyringPath, "utf-8");
      const keyringData = JSON.parse(fileContent);
      const keys = keyringData.trusted_keys || [];

      const filteredKeys = keys.filter(k => {
        const isRevoked = k.status === "REVOKED";
        if (filter === "active") return !isRevoked;
        if (filter === "revoked") return isRevoked;
        return true;
      });

      if (filteredKeys.length === 0) {
        return {
          content: [{ type: "text", text: `📭 В реестре не найдено ключей с фильтром: "${filter}".` }]
        };
      }

      let report = `📋 Реестр доверенных ключей Ed25519 (фильтр: ${filter.toUpperCase()}):\n\n`;
      
      filteredKeys.forEach((k, index) => {
        const statusIcon = k.status === "REVOKED" ? "⛔ [ОТОЗВАН]" : "✅ [АКТИВЕН]";
        report += `--- Ключ #${index + 1} ${statusIcon} ---\n`;
        report += `👤 Автор: ${k.identity}\n`;
        report += `🛡 Роль: ${k.role}\n`;
        report += `🔑 Public Key (HEX): ${k.public_key}\n`;
        report += `📅 Добавлен: ${k.added_at || 'Н/Д'}\n`;
        if (k.status === "REVOKED") {
          report += `⚠️ Причина отзыва: ${k.revocation_reason || 'Не указана'}\n`;
          if (k.rotated_to) report += `🔄 Заменен на ключ: ${k.rotated_to}\n`;
        }
        report += `\n`;
      });

      return {
        content: [{ type: "text", text: report }]
      };

    } catch (error) {
      return {
        content: [{ type: "text", text: `❌ Ошибка чтения trusted_keys.json: ${error.message}` }],
        isError: true
      };
    }
  }

  if (request.params.name === "export_trusted_keys_for_pages") {
    const rawOutputDir = String(request.params.arguments.output_dir);
    const fileName = String(request.params.arguments.file_name || "keys.json").trim();
    
    const containerOutputDir = rawOutputDir.replace(/^H:\\/i, '/mnt/h/').replace(/\\/g, '/');
    const internalKeyringPath = "/app/trusted_keys.json";

    try {
      const fileContent = await fs.readFile(internalKeyringPath, "utf-8");
      const keyringData = JSON.parse(fileContent);

      const publicKeysExport = {
        version: "1.0",
        exported_at: new Date().toISOString(),
        description: "Public cryptographic keyring for Actor Dev Environment verification",
        trusted_keys: (keyringData.trusted_keys || []).map(k => ({
          identity: k.identity,
          public_key: k.public_key,
          role: k.role,
          status: k.status || "ACTIVE",
          added_at: k.added_at,
          revoked_at: k.revoked_at || null,
          revocation_reason: k.revocation_reason || null,
          rotated_to: k.rotated_to || null
        }))
      };

      await fs.mkdir(containerOutputDir, { recursive: true });
      const targetFilePath = path.join(containerOutputDir, fileName);
      await fs.writeFile(targetFilePath, JSON.stringify(publicKeysExport, null, 2), "utf-8");

      const windowsPath = targetFilePath.replace(/^\/mnt\/h\//, 'H:\\').replace(/\//g, '\\');

      return {
        content: [{
          type: "text",
          text: `✅ Публичный реестр ключей успешно экспортирован для GitHub Pages!\n\n` +
                `📁 Путь к файлу: ${windowsPath}\n` +
                `📊 Экспортировано ключей: ${publicKeysExport.trusted_keys.length}\n` +
                `🌐 Файл готов к публикации в составе вашего статического сайта.`
        }]
      };

    } catch (error) {
      return {
        content: [{ type: "text", text: `❌ Ошибка экспорта реестра: ${error.message}` }],
        isError: true
      };
    }
  }

  if (request.params.name === "export_trusted_keys_html") {
    const rawOutputDir = String(request.params.arguments.output_dir);
    const fileName = String(request.params.arguments.file_name || "keys.html").trim();
    
    const containerOutputDir = rawOutputDir.replace(/^H:\\/i, '/mnt/h/').replace(/\\/g, '/');
    const internalKeyringPath = "/app/trusted_keys.json";

    try {
      const fileContent = await fs.readFile(internalKeyringPath, "utf-8");
      const keyringData = JSON.parse(fileContent);
      const keys = keyringData.trusted_keys || [];

      let htmlContent = `<!DOCTYPE html>
      <html lang="ru">
      <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Actor Dev Environment — Trusted Keys Registry</title>
          <style>
              body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; background: #0d1117; color: #c9d1d9; }
              h1 { border-bottom: 1px solid #30363d; padding-bottom: 15px; color: #f0f6fc; }
              .key-card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px; margin-bottom: 20px; }
              .key-card.revoked { border-color: #f85149; opacity: 0.75; }
              .badge { display: inline-block; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600; }
              .badge.active { background: #238636; color: #fff; }
              .badge.revoked { background: #da3633; color: #fff; }
              code { background: #030407; padding: 4px 8px; border-radius: 4px; font-family: monospace; color: #58a6ff; word-break: break-all; }
              .meta { font-size: 13px; color: #8b949e; margin-top: 10px; }
              footer { margin-top: 40px; text-align: center; font-size: 12px; color: #8b949e; border-top: 1px solid #30363d; padding-top: 20px; }
          </style>
      </head>
      <body>
          <h1>🛡 Реестр доверенных ключей Ed25519</h1>
          <p>Официальный публичный реестр криптографических подписей среды <strong>A©tor Dev Environment</strong>.</p>
          <hr style="border:0; border-top:1px solid #30363d; margin: 20px 0;">`;

      if (keys.length === 0) {
          htmlContent += `<p>В реестре пока нет зарегистрированных ключей.</p>`;
      } else {
          keys.forEach((k, idx) => {
              const isRevoked = k.status === "REVOKED";
              const badgeClass = isRevoked ? "revoked" : "active";
              const badgeText = isRevoked ? "⛔ ОТОЗВАН" : "✅ АКТИВЕН";
              
              htmlContent += `
              <div class="key-card ${isRevoked ? 'revoked' : ''}">
                  <h3>Ключ #${idx + 1}: ${k.identity} <span class="badge ${badgeClass}">${badgeText}</span></h3>
                  <p><strong>Роль:</strong> ${k.role}</p>
                  <p><strong>Public Key (HEX):</strong><br><code>${k.public_key}</code></p>
                  <div class="meta">
                      📅 Добавлен: ${k.added_at || 'Н/Д'}
                      ${isRevoked ? `<br>⚠️ Отозван: ${k.revoked_at || 'Н/Д'} (Причина: ${k.revocation_reason || 'Не указана'})` : ''}
                      ${k.rotated_to ? `<br>🔄 Заменен на ключ: <code>${k.rotated_to}</code>` : ''}
                  </div>
              </div>`;
          });
      }

      htmlContent += `
          <footer>
              Автоматически сгенерировано MCP-сервером аудита • ${new Date().toISOString()}
          </footer>
      </body>
      </html>`;

      await fs.mkdir(containerOutputDir, { recursive: true });
      const targetFilePath = path.join(containerOutputDir, fileName);
      await fs.writeFile(targetFilePath, htmlContent, "utf-8");

      const windowsPath = targetFilePath.replace(/^\/mnt\/h\//, 'H:\\').replace(/\//g, '\\');

      return {
        content: [{
          type: "text",
          text: `✅ HTML-страница реестра ключей успешно сгенерирована!\n\n` +
                `📁 Путь к файлу: ${windowsPath}\n` +
                `🌐 Страница полностью готова для развертывания на GitHub Pages.`
        }]
      };

    } catch (error) {
      return {
        content: [{ type: "text", text: `❌ Ошибка генерации HTML-страницы: ${error.message}` }],
        isError: true
      };
    }
  }

  if (request.params.name === "revoke_trusted_key") {
    const targetPubKey = String(request.params.arguments.public_key).trim().toLowerCase();
    const reason = String(request.params.arguments.reason).trim();
    const replacementPubKey = request.params.arguments.replacement_public_key 
      ? String(request.params.arguments.replacement_public_key).trim().toLowerCase() 
      : null;

    const keyringPath = "/app/trusted_keys.json";

    try {
      const fileContent = await fs.readFile(keyringPath, "utf-8");
      const keyringData = JSON.parse(fileContent);

      const keyIndex = keyringData.trusted_keys.findIndex(
        k => k.public_key.toLowerCase() === targetPubKey
      );

      if (keyIndex === -1) {
        return {
          content: [{ type: "text", text: `❌ Ключ ${targetPubKey.substring(0, 16)}... не найден в реестре.` }],
          isError: true
        };
      }

      keyringData.trusted_keys[keyIndex].status = "REVOKED";
      keyringData.trusted_keys[keyIndex].revoked_at = new Date().toISOString();
      keyringData.trusted_keys[keyIndex].revocation_reason = reason;
      if (replacementPubKey) {
        keyringData.trusted_keys[keyIndex].rotated_to = replacementPubKey;
      }

      await fs.writeFile(keyringPath, JSON.stringify(keyringData, null, 2), "utf-8");
      trustedKeys = keyringData.trusted_keys;

      let msg = `⛔ Ключ ${targetPubKey.substring(0, 16)}... успешно отозван.\n`;
      msg += `📝 Причина: ${reason}\n`;
      if (replacementPubKey) {
        msg += `🔄 Назначен ключ замены: ${replacementPubKey.substring(0, 16)}...\n`;
      }

      return {
        content: [{ type: "text", text: msg }]
      };

    } catch (error) {
      return {
        content: [{ type: "text", text: `❌ Ошибка записи в trusted_keys.json: ${error.message}` }],
        isError: true
      };
    }
  }

  if (request.params.name === "generate_ed25519_keypair") {
    const rawOutputDir = String(request.params.arguments.output_dir);
    const keyName = String(request.params.arguments.key_name).trim();
    const format = String(request.params.arguments.format || "hex").toLowerCase();
    const autoRegister = request.params.arguments.auto_register !== false;
    const identity = String(request.params.arguments.identity || `${keyName}_author`).trim();
    const role = String(request.params.arguments.role || "Signer").trim();

    const containerDir = rawOutputDir.replace(/^H:\\/i, '/mnt/h/').replace(/\\/g, '/');

    try {
      await fs.mkdir(containerDir, { recursive: true });

      const { publicKey, privateKey } = crypto.generateKeyPairSync("ed25519");

      let pubKeyStr, privKeyStr;
      const pubPath = path.join(containerDir, `${keyName}_public.${format === 'hex' ? 'key' : 'pem'}`);
      const privPath = path.join(containerDir, `${keyName}_private.${format === 'hex' ? 'key' : 'pem'}`);

      const pubDer = publicKey.export({ format: "der", type: "spki" });
      const rawPubKeyHex = pubDer.subarray(-32).toString("hex");

      if (format === "hex") {
        const privDer = privateKey.export({ format: "der", type: "pkcs8" });
        pubKeyStr = rawPubKeyHex;
        privKeyStr = privDer.subarray(-32).toString("hex");
      } else {
        pubKeyStr = publicKey.export({ format: "pem", type: "spki" });
        privKeyStr = privateKey.export({ format: "pem", type: "pkcs8" });
      }

      await fs.writeFile(pubPath, pubKeyStr, "utf-8");
      await fs.writeFile(privPath, privKeyStr, { encoding: "utf-8", mode: 0o600 });

      let registrationStatus = "";

      if (autoRegister) {
        const keyringPath = "/app/trusted_keys.json";
        let keyringData = { trusted_keys: [] };

        try {
          const fileContent = await fs.readFile(keyringPath, "utf-8");
          keyringData = JSON.parse(fileContent);
        } catch {}

        const exists = keyringData.trusted_keys.some(
          k => k.public_key.toLowerCase() === rawPubKeyHex
        );

        if (!exists) {
          const newEntry = {
            identity,
            public_key: rawPubKeyHex,
            role,
            added_at: new Date().toISOString()
          };

          keyringData.trusted_keys.push(newEntry);
          await fs.writeFile(keyringPath, JSON.stringify(keyringData, null, 2), "utf-8");
          
          trustedKeys = keyringData.trusted_keys;
          registrationStatus = `\n🛡 Публичный ключ зарегистрирован в trusted_keys.json (Автор: ${identity}, Роль: ${role}).`;
        } else {
          registrationStatus = `\nℹ️ Публичный ключ уже был в реестре доверенных ключей.`;
        }
      }

      const windowsPub = pubPath.replace(/^\/mnt\/h\//, 'H:\\').replace(/\//g, '\\');
      const windowsPriv = privPath.replace(/^\/mnt\/h\//, 'H:\\').replace(/\//g, '\\');

      return {
        content: [{
          type: "text",
          text: `✅ Успешно сгенерирована новая пара ключей Ed25519!\n\n` +
                `🔑 Публичный ключ: ${windowsPub}\n` +
                `🔒 Приватный ключ: ${windowsPriv}\n` +
                `🔑 Public Key Value (HEX): ${rawPubKeyHex}` +
                `${registrationStatus}`
        }]
      };

    } catch (error) {
      return {
        content: [{ type: "text", text: `❌ Ошибка генерации или авторегистрации: ${error.message}` }],
        isError: true
      };
    }
  }

  if (request.params.name === "generate_rclone_recovery_script") {
    const rawCsvPath = String(request.params.arguments.csv_path);
    const remoteName = String(request.params.arguments.remote_name); 
    
    const containerCsvPath = rawCsvPath.replace(/^H:\\/i, '/mnt/h/').replace(/\\/g, '/');
    const baseDir = path.dirname(containerCsvPath);

    try {
      const csvContent = await fs.readFile(containerCsvPath, "utf-8");
      const lines = csvContent.split('\n').filter(line => line.trim() !== '');
      
      let filesFromContent = "";
      let missingCount = 0;
      
      for (let i = 1; i < lines.length; i++) {
        const columns = lines[i].split(',');
        if (columns.length >= 2 && (columns[1] === 'MISSING' || columns[1] === 'HASH_MISMATCH')) {
          const filePath = columns[0].replace(/^"|"$/g, '');
          const relativePath = filePath.replace(/^H:\\/i, '').replace(/\\/g, '/');
          filesFromContent += `${relativePath}\n`;
          missingCount++;
        }
      }

      if (missingCount === 0) {
        return {
          content: [{ type: "text", text: "Файлы со статусами MISSING или HASH_MISMATCH не найдены." }]
        };
      }

      const listFileName = "rclone_missing_files.txt";
      await fs.writeFile(path.join(baseDir, listFileName), filesFromContent, "utf-8");

      let ps1Content = `# Оптимизированный PowerShell скрипт восстановления\n`;
      ps1Content += `Write-Host "📥 Восстановление ${missingCount} файлов (MISSING/HASH_MISMATCH) через Rclone..." -ForegroundColor Cyan\n`;
      ps1Content += `rclone copy "${remoteName}" "H:\\" --files-from "${listFileName}" -P\n`;
      ps1Content += `Write-Host "✅ Готово!" -ForegroundColor Green\n`;
      
      const ps1FileName = "rclone_recovery.ps1";
      await fs.writeFile(path.join(baseDir, ps1FileName), ps1Content, "utf-8");

      let bashContent = `#!/bin/bash\n`;
      bashContent += `echo "📥 Восстановление ${missingCount} файлов (MISSING/HASH_MISMATCH) через Rclone..."\n`;
      bashContent += `rclone copy "${remoteName}" "/mnt/h/" --files-from "${listFileName}" -P\n`;
      bashContent += `echo "✅ Готово!"\n`;
      
      const bashFileName = "rclone_recovery.sh";
      const bashPath = path.join(baseDir, bashFileName);
      await fs.writeFile(bashPath, bashContent, "utf-8");
      await fs.chmod(bashPath, 0o755);

      return {
        content: [{ 
          type: "text", 
          text: `✅ Сгенерировано 3 файла для восстановления (${missingCount} артефактов):\n1. Список: ${listFileName}\n2. Windows скрипт: ${ps1FileName}\n3. WSL скрипт: ${bashFileName}\n\nДля запуска в Windows используйте PowerShell: & .\\${ps1FileName}` 
        }]
      };

    } catch (error) {
      return {
        content: [{ type: "text", text: `❌ Ошибка: ${error.message}` }],
        isError: true
      };
    }
  }

  if (request.params.name === "generate_rclone_backup_script") {
    const rawManifest = String(request.params.arguments.manifest_path);
    const rawScanDir = String(request.params.arguments.scan_dir);
    const remoteName = String(request.params.arguments.remote_name);

    const containerManifest = rawManifest.replace(/^H:\\/i, '/mnt/h/').replace(/\\/g, '/');
    const containerScanDir = rawScanDir.replace(/^H:\\/i, '/mnt/h/').replace(/\\/g, '/');
    const baseOutput = path.dirname(containerManifest);

    try {
      const manifestContent = await fs.readFile(containerManifest, "utf-8");
      const manifestData = JSON.parse(manifestContent);
      
      const knownFiles = new Set(manifestData.files.map(f => {
        const normalized = f.path.replace(/^H:\\/i, '').replace(/\\/g, '/');
        return normalized;
      }));

      const allPhysicalFiles = await getFilesRecursive(containerScanDir);
      
      let filesFromContent = "";
      let newFilesCount = 0;

      for (const physicalPath of allPhysicalFiles) {
        if (physicalPath.includes("missing_evidence_audit_report") || 
            physicalPath.includes("rclone_recovery") || 
            physicalPath.includes("rclone_backup")) {
          continue;
        }

        const relativeToRoot = physicalPath.replace(/^\/mnt\/h\//, '');
        
        if (!knownFiles.has(relativeToRoot)) {
          filesFromContent += `${relativeToRoot}\n`;
          newFilesCount++;
        }
      }

      if (newFilesCount === 0) {
        return {
          content: [{ type: "text", text: "✅ Новых файлов не найдено. Бэкап не требуется." }]
        };
      }

      const listFileName = "rclone_backup_files.txt";
      await fs.writeFile(path.join(baseOutput, listFileName), filesFromContent, "utf-8");

      let ps1Content = `# Скрипт инкрементального бэкапа новых доказательств\n`;
      ps1Content += `Write-Host "🚀 Запуск бэкапа ${newFilesCount} новых файлов..." -ForegroundColor Cyan\n`;
      ps1Content += `rclone copy "H:\\" "${remoteName}" --files-from "${listFileName}" -P\n`;
      ps1Content += `Write-Host "✅ Бэкап завершен!" -ForegroundColor Green\n`;
      
      const ps1FileName = "rclone_backup.ps1";
      await fs.writeFile(path.join(baseOutput, ps1FileName), ps1Content, "utf-8");

      return {
        content: [{ 
          type: "text", 
          text: `✅ Найдено ${newFilesCount} новых файлов.\n📄 Сгенерирован список: ${listFileName}\n🛠 Скрипт PowerShell: ${ps1FileName}\nЗапустите & .\\${ps1FileName} для отправки данных в облако.` 
        }]
      };

    } catch (error) {
      return {
        content: [{ type: "text", text: `❌ Ошибка генерации бэкапа: ${error.message}` }],
        isError: true
      };
    }
  }

  if (request.params.name === "execute_rclone_recovery") {
    const remoteName = String(request.params.arguments.remote_name);
    const rawListPath = String(request.params.arguments.list_file_path);
    
    const containerListPath = rawListPath.replace(/^H:\\/i, '/mnt/h/').replace(/\\/g, '/');
    const rcloneCmd = `rclone copy "${remoteName}" "/mnt/h/" --files-from "${containerListPath}" --stats 1s -v`;

    try {
      console.error(`Executing: ${rcloneCmd}`);
      const { stdout, stderr } = await execAsync(rcloneCmd, { maxBuffer: 1024 * 1024 * 10 });

      return {
        content: [{ 
          type: "text", 
          text: `✅ Rclone операция успешно выполнена!\n\nВывод STDOUT:\n${stdout}\n\nЛоги STDERR:\n${stderr}` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `❌ Ошибка выполнения Rclone (Код ${error.code}):\n${error.message}\n\nSTDERR:\n${error.stderr || 'отсутствует'}` 
        }],
        isError: true
      };
    }
  }

  if (request.params.name === "git_commit_and_push_manifests") {
    const rawRepoDir = String(request.params.arguments.repo_dir);
    const commitMsg = String(request.params.arguments.commit_message);
    const branch = String(request.params.arguments.branch || "main");

    const containerRepoDir = rawRepoDir.replace(/^H:\\/i, '/mnt/h/').replace(/\\/g, '/');

    try {
      const gitCommands = [
        `git -C "${containerRepoDir}" config --global --add safe.directory "${containerRepoDir}"`,
        `git -C "${containerRepoDir}" add .`,
        `git -C "${containerRepoDir}" diff-index --quiet HEAD || git -C "${containerRepoDir}" commit -m "${commitMsg.replace(/"/g, '\\"')}"`,
        `git -C "${containerRepoDir}" push origin ${branch}`
      ].join(" && ");

      const { stdout, stderr } = await execAsync(gitCommands, { maxBuffer: 1024 * 1024 * 5 });

      return {
        content: [{
          type: "text",
          text: `✅ Изменения успешно закоммичены и отправлены в репозиторий!\n\n` +
                `🌿 Ветка: ${branch}\n` +
                `💬 Сообщение: "${commitMsg}"\n\n` +
                `📤 STDOUT:\n${stdout || 'Нет вывода'}`
        }]
      };

    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `❌ Ошибка выполнения Git операций:\n${error.message}\n\nSTDERR:\n${error.stderr || 'отсутствует'}` 
        }],
        isError: true
      };
    }
  }

  if (request.params.name === "full_sync_and_publish") {
    const rawRootDir = String(request.params.arguments.root_dir);
    const newPrivateKey = String(request.params.arguments.new_private_key || process.env.SIGNING_PRIVATE_KEY || "").trim();

    if (!newPrivateKey) {
      return {
        content: [{ type: "text", text: "❌ Ошибка: Новый приватный ключ не передан и не найден в переменной окружения SIGNING_PRIVATE_KEY (.env)." }],
        isError: true
      };
    }

    const commitMsg = String(request.params.arguments.commit_message || "chore: auto-sign and sync manifests");
    const branch = String(request.params.arguments.branch || "main");

    const containerRootDir = rawRootDir.replace(/^H:\\/i, '/mnt/h/').replace(/\\/g, '/');

    let log = "🚀 Запуск комплексного пайплайна полного цикла (Full Sync & Publish)...\n\n";

    try {
      log += "📂 [Этап 1/3] Сканирование и переподписание манифестов...\n";
      const allFiles = await getFilesRecursive(containerRootDir);
      const jsonFiles = allFiles.filter(file => 
        file.endsWith('.json') && 
        !file.includes('trusted_keys.json') &&
        !file.includes('audit_report')
      );

      let processedCount = 0;
      for (const filePath of jsonFiles) {
        try {
          const content = await fs.readFile(filePath, "utf-8");
          const jsonData = JSON.parse(content);

          if (jsonData && Array.isArray(jsonData.files)) {
            const { signedManifest } = signEd25519Manifest(jsonData, newPrivateKey);
            await fs.writeFile(filePath, JSON.stringify(signedManifest, null, 2), "utf-8");
            processedCount++;
          }
        } catch (fileErr) {
          log += `  ⚠️ Пропущен файл ${path.basename(filePath)}: ${fileErr.message}\n`;
        }
      }
      log += `  ✅ Успешно переподписано манифестов: ${processedCount}\n\n`;

      log += "🔍 [Этап 2/3] Запуск аудита доступности данных (Data Availability)...\n";
      let totalMissing = 0;
      for (const filePath of jsonFiles) {
        try {
          const content = await fs.readFile(filePath, "utf-8");
          const jsonData = JSON.parse(content);
          if (jsonData && Array.isArray(jsonData.files)) {
            const manifestDir = path.dirname(filePath);
            for (const fileObj of jsonData.files) {
              let targetPath = fileObj.path;
              if (/^[a-zA-Z]:\\/.test(targetPath)) {
                targetPath = targetPath.replace(/^H:\\/i, '/mnt/h/').replace(/\\/g, '/');
              } else {
                targetPath = path.resolve(manifestDir, targetPath);
              }
              try {
                await fs.access(targetPath, constants.F_OK);
              } catch {
                totalMissing++;
              }
            }
          }
        } catch {}
      }
      log += `  📊 Аудит завершен. Выявлено отсутствующих файлов: ${totalMissing}\n\n`;

      log += "📤 [Этап 3/3] Синхронизация с удаленным репозиторием Git...\n";
      const gitCommands = [
        `git -C "${containerRootDir}" config --global --add safe.directory "${containerRootDir}"`,
        `git -C "${containerRootDir}" add .`,
        `git -C "${containerRootDir}" diff-index --quiet HEAD || git -C "${containerRootDir}" commit -m "${commitMsg.replace(/"/g, '\\"')}"`,
        `git -C "${containerRootDir}" push origin ${branch}`
      ].join(" && ");

      const { stdout } = await execAsync(gitCommands, { maxBuffer: 1024 * 1024 * 5 });
      log += `  ✅ Git push выполнен успешно в ветку '${branch}'!\n`;

      return {
        content: [{
          type: "text",
          text: `✨ ПАЙПЛАЙН УСПЕШНО ЗАВЕРШЕН!\n\n${log}\n📋 Вывод Git:\n${stdout || 'Изменений для коммита не было (всё актуально)'}`
        }]
      };

    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `❌ Ошибка выполнения пайплайна full_sync_and_publish:\n${error.message}\n\nЛог выполнения до ошибки:\n${log}` 
        }],
        isError: true
      };
    }
  }

  throw new Error(`Tool not found: ${request.params.name}`);
});

const transport = new StdioServerTransport();
await server.connect(transport);
console.error("Custom Node.js MCP Server running on stdio");
