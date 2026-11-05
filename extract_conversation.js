const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const { URL } = require("url");

const TARGET_INPUT =
  "https://share.gemini.google/LR2ljxn55vBY";

function normalizeUrl(input) {
  if (!input || typeof input !== "string") {
    throw new Error("Empty URL");
  }

  let candidate = input.trim();

  const hrefMatch = candidate.match(
    /href=["']([^"']+)["']/i
  );

  if (hrefMatch) {
    candidate = hrefMatch[1];
  }

  let parsed;

  try {
    parsed = new URL(candidate);
  } catch {
    throw new Error(
      `Invalid URL: ${candidate}`
    );
  }

  if (
    parsed.protocol !== "https:" &&
    parsed.protocol !== "http:"
  ) {
    throw new Error(
      `Unsupported protocol: ${parsed.protocol}`
    );
  }

  return parsed.toString();
}

const TARGET_URL =
  normalizeUrl(TARGET_INPUT);

const OUTPUT_DIR = "./output";
const NETWORK_DIR =
  path.join(OUTPUT_DIR, "network");
const SCRIPTS_DIR =
  path.join(OUTPUT_DIR, "scripts");

fs.mkdirSync(
  OUTPUT_DIR,
  { recursive: true }
);

fs.mkdirSync(
  NETWORK_DIR,
  { recursive: true }
);

fs.mkdirSync(
  SCRIPTS_DIR,
  { recursive: true }
);

async function main() {
  let browser;

  const networkResponses = [];
  const errors = [];

  let requestCounter = 0;
  let responseCounter = 0;
  let dumpCounter = 0;

  try {
    console.log(
      "[*] URL validated:",
      TARGET_URL
    );

    browser =
      await chromium.launch({
        headless: true
      });

    const context =
      await browser.newContext({
        viewport: {
          width: 1920,
          height: 1080
        }
      });

    const page =
      await context.newPage();

    page.on(
      "pageerror",
      err => {
        errors.push(
          `PAGE_ERROR: ${err.message}`
        );
      }
    );

    page.on(
      "console",
      msg => {
        if (
          msg.type() === "error"
        ) {
          errors.push(
            `CONSOLE_ERROR: ${msg.text()}`
          );
        }
      }
    );

    page.on(
      "request",
      request => {
        requestCounter++;

        try {
          fs.appendFileSync(
            path.join(
              OUTPUT_DIR,
              "requests.log"
            ),
            `${request.method()} ${request.url()}\n`
          );
        } catch {}
      }
    );

    page.on(
      "response",
      async response => {
        responseCounter++;

        try {
          const url =
            response.url();

          const contentType =
            response.headers()[
              "content-type"
            ] || "";

          fs.appendFileSync(
            path.join(
              OUTPUT_DIR,
              "responses.log"
            ),
            `${response.status()} ${url}\n`
          );

          const interesting =
            contentType.includes(
              "json"
            ) ||
            url.includes(
              "graphql"
            ) ||
            url.includes(
              "rpc"
            ) ||
            url.includes(
              "batchexecute"
            ) ||
            url.includes(
              "share"
            ) ||
            url.includes(
              "gemini"
            );

          if (!interesting) {
            return;
          }

          let body = "";

          try {
            body =
              await response.text();
          } catch {}

          networkResponses.push({
            url,
            status:
              response.status(),
            contentType
          });

          const dumpFile =
            String(
              dumpCounter++
            ).padStart(
              4,
              "0"
            ) + ".txt";

          fs.writeFileSync(
            path.join(
              NETWORK_DIR,
              dumpFile
            ),
            [
              `URL: ${url}`,
              `STATUS: ${response.status()}`,
              `CONTENT_TYPE: ${contentType}`,
              "",
              body.slice(
                0,
                1000000
              )
            ].join("\n"),
            "utf8"
          );
        } catch (e) {
          errors.push(
            "RESPONSE_ERROR: " +
            String(e)
          );
        }
      }
    );

    console.log(
      "[*] Opening:",
      TARGET_URL
    );

    await page.goto(
      TARGET_URL,
      {
        waitUntil:
          "domcontentloaded",
        timeout: 120000
      }
    );

    await page.waitForLoadState(
      "networkidle"
    );

    await page.waitForTimeout(
      5000
    );

    const title =
      await page
        .title()
        .catch(() => "");

    const html =
      await page
        .content()
        .catch(() => "");

    const bodyText =
      await page
        .evaluate(
          () =>
            document.body
              ?.innerText || ""
        )
        .catch(() => "");

    const scripts =
      await page
        .$$("script")
        .catch(() => []);

    const candidateScripts =
      [];

    for (
      let i = 0;
      i < scripts.length;
      i++
    ) {
      try {
        const content =
          (await scripts[i]
            .textContent()) || "";

        const scriptPath =
          path.join(
            SCRIPTS_DIR,
            `script_${String(i).padStart(
              4,
              "0"
            )}.js`
          );

        fs.writeFileSync(
          scriptPath,
          content,
          "utf8"
        );

        if (
          content.includes(
            "AF_initData"
          ) ||
          content.includes(
            "WIZ_global_data"
          ) ||
          content.includes(
            "conversation"
          ) ||
          content.includes(
            "message"
          ) ||
          content.includes(
            "chat"
          ) ||
          content.includes(
            "gemini"
          )
        ) {
          candidateScripts.push({
            index: i,
            length:
              content.length
          });
        }
      } catch {}
    }

    const globals =
      await page
        .evaluate(() => {
          const result =
            {};

          Object.keys(window)
            .filter(key =>
              /wiz|data|chat|share|gemini|conv/i
                .test(key)
            )
            .slice(
              0,
              200
            )
            .forEach(key => {
              try {
                const value =
                  window[key];

                if (
                  typeof value ===
                    "string" ||
                  typeof value ===
                    "number" ||
                  typeof value ===
                    "boolean"
                ) {
                  result[key] =
                    value;
                } else {
                  result[key] =
                    "[OBJECT]";
                }
              } catch {}
            });

          return result;
        })
        .catch(() => ({}));

    const conversation = {
      url: TARGET_URL,
      title,
      extracted_at:
        new Date()
          .toISOString(),

      message_count:
        null,

      messages: [],

      extraction_status:
        "raw_capture",

      notes: [
        "Conversation reconstruction not verified",
        "Requires API or DOM parsing"
      ]
    };

    const markdown = [
      "# Gemini Share Export",
      "",
      `URL: ${TARGET_URL}`,
      "",
      `TITLE: ${title}`,
      "",
      "---",
      "",
      bodyText
    ].join("\n");

    const debug = {
      url:
        TARGET_URL,

      title,

      html_length:
        html.length,

      body_length:
        bodyText.length,

      request_count:
        requestCounter,

      response_count:
        responseCounter,

      network_count:
        networkResponses.length,

      candidate_script_count:
        candidateScripts.length,

      candidateScripts,

      globals,

      errors
    };

    fs.writeFileSync(
      path.join(
        OUTPUT_DIR,
        "conversation.json"
      ),
      JSON.stringify(
        conversation,
        null,
        2
      ),
      "utf8"
    );

    fs.writeFileSync(
      path.join(
        OUTPUT_DIR,
        "conversation.md"
      ),
      markdown,
      "utf8"
    );

    fs.writeFileSync(
      path.join(
        OUTPUT_DIR,
        "conversation_debug.json"
      ),
      JSON.stringify(
        debug,
        null,
        2
      ),
      "utf8"
    );

    fs.writeFileSync(
      path.join(
        OUTPUT_DIR,
        "rendered_page.html"
      ),
      html,
      "utf8"
    );

    console.log(
      "[+] Export completed"
    );

    console.log(
      `[+] Requests: ${requestCounter}`
    );

    console.log(
      `[+] Responses: ${responseCounter}`
    );

    console.log(
      `[+] Network dumps: ${networkResponses.length}`
    );

    console.log(
      `[+] Candidate scripts: ${candidateScripts.length}`
    );
  } catch (e) {
    console.error(
      "[FATAL]",
      e
    );
  } finally {
    try {
      if (browser) {
        await browser.close();
      }
    } catch (e) {
      console.error(
        "[CLOSE ERROR]",
        e
      );
    }
  }
}

main();
