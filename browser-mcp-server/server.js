import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { chromium } from "playwright";

const server = new Server({
  name: "VimBrowserMCP",
  version: "1.0.0"
}, { capabilities: { tools: {} } });

let browser;
let page;

async function ensureBrowser() {
  if (!browser) {
    browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    page = await context.newPage();
  }
}

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "navigate",
      description: "Открыть URL в браузере",
      inputSchema: {
        type: "object",
        properties: { url: { type: "string" } },
        required: ["url"]
      }
    },
    {
      name: "scroll",
      description: "VIM-скроллинг страницы (j - вниз, k - вверх, h - влево, l - вправо)",
      inputSchema: {
        type: "object",
        properties: { direction: { type: "string", enum: ["j", "k", "h", "l"] } },
        required: ["direction"]
      }
    },
    {
      name: "map_elements",
      description: "Проиндексировать кликабельные элементы на странице и присвоить им VIM-шорткаты",
      inputSchema: { type: "object", properties: {} }
    },
    {
      name: "click_element",
      description: "Кликнуть по элементу, используя присвоенный шорткат",
      inputSchema: {
        type: "object",
        properties: { shortcut: { type: "string" } },
        required: ["shortcut"]
      }
    }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  await ensureBrowser();
  const { name, arguments: args } = request.params;

  try {
    if (name === "navigate") {
      await page.goto(args.url, { waitUntil: "domcontentloaded" });
      return { content: [{ type: "text", text: `Страница ${args.url} загружена.` }] };
    }

    if (name === "scroll") {
      const scrollAmounts = { j: [0, 500], k: [0, -500], h: [-500, 0], l: [500, 0] };
      const [x, y] = scrollAmounts[args.direction];
      await page.evaluate(([dx, dy]) => window.scrollBy(dx, dy), [x, y]);
      return { content: [{ type: "text", text: `Скроллинг выполнен: ${args.direction}` }] };
    }

    if (name === "map_elements") {
      const elementsMap = await page.evaluate(() => {
        const interactives = Array.from(document.querySelectorAll('a, button, input, textarea, [role="button"]'));
        const map = {};
        interactives.forEach((el, index) => {
          const shortcut = index < 26 ? String.fromCharCode(65 + index) : `${String.fromCharCode(65 + Math.floor(index/26) - 1)}${String.fromCharCode(65 + (index%26))}`;
          map[shortcut] = { tag: el.tagName, text: el.innerText || el.placeholder || el.value || 'N/A' };
          
          el.style.border = "2px solid red";
          const label = document.createElement('div');
          label.innerText = shortcut;
          label.style.cssText = "position:absolute; background:yellow; color:black; font-weight:bold; padding:2px; z-index:9999; font-size:12px;";
          el.parentNode.insertBefore(label, el);
          el.setAttribute('data-vim-shortcut', shortcut);
        });
        return map;
      });
      return { content: [{ type: "text", text: JSON.stringify(elementsMap, null, 2) }] };
    }

    if (name === "click_element") {
      const shortcut = args.shortcut.toUpperCase();
      const success = await page.evaluate((s) => {
        const el = document.querySelector(`[data-vim-shortcut="${s}"]`);
        if (el) { el.click(); return true; }
        return false;
      }, shortcut);
      
      return { content: [{ type: "text", text: success ? `Элемент ${shortcut} успешно нажат.` : `Элемент ${shortcut} не найден.` }] };
    }

    throw new Error(`Неизвестный инструмент: ${name}`);
  } catch (error) {
    return { content: [{ type: "text", text: `Ошибка: ${error.message}` }] };
  }
});

async function run() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.log("VimBrowserMCP Server запущен (stdio)");
}

run().catch(console.error);
