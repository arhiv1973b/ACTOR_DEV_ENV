import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import fs from "fs/promises";
import crypto from "crypto";

const server = new McpServer({
   name: "actor-context-server",
   version: "1.0.0"
});

// Инструмент 1: Чтение и парсинг JSON-артефактов
server.tool(
   "read_json_artifact",
   "Чтение JSON артефакта (evidence_db) из директории проекта",
   {
     filepath: z.string().describe("Абсолютный путь к JSON файлу (например, H:\\ACTOR_DEV_ENV\\master_evidence_db.json)")
   },
   async ({ filepath }) => {
     try {
       const content = await fs.readFile(filepath, "utf-8");
       const parsed = JSON.parse(content);
       return {
         content: [{ type: "text", text: JSON.stringify(parsed, null, 2) }]
       };
     } catch (error) {
       return {
         content: [{ type: "text", text: `Ошибка чтения или парсинга JSON: ${error.message}` }],
         isError: true
       };
     }
   }
);

// Инструмент 2: Вычисление SHA-256
server.tool(
   "calculate_sha256",
   "Вычисление SHA-256 хеша для криптографических артефактов и документов",
   {
     filepath: z.string().describe("Абсолютный путь к файлу для хеширования")
   },
   async ({ filepath }) => {
     try {
       const fileBuffer = await fs.readFile(filepath);
       const hashSum = crypto.createHash("sha256");
       hashSum.update(fileBuffer);
       const hex = hashSum.digest("hex");

       return {
         content: [{ type: "text", text: `SHA-256: ${hex}` }]
       };
     } catch (error) {
       return {
         content: [{ type: "text", text: `Ошибка вычисления хеша: ${error.message}` }],
         isError: true
       };
     }
   }
);

async function main() {
   const transport = new StdioServerTransport();
   await server.connect(transport);
   console.error("A©tor MCP Server запущен. Инструменты read_json_artifact и calculate_sha256 загружены.");
}

main().catch(console.error);
