const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const { URL } = require("url");

const TARGET_INPUT =
  "https://grok.com/share/c2hhcmQtNA_fa129e1f-c6bf-42cc-9756-8fa4c4bae1ec";

function normalizeUrl(input) {
  if (!input || typeof input !== "string") {
    throw new Error("Empty URL");
  }

  let candidate = input.trim();

  const hrefMatch = candidate.match(
    /href=["']([^"']+)["']/i
  );

  if (hrefMatch && hrefMatch[1]) {
    candidate = hrefMatch[1];
  }

  let parsed;

  try {
    parsed = new URL(candidate);
  } catch (err) {
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

const OUTPUT_DIR =
  "./grok_output";

const NETWORK_DIR =
  path.join(
    OUTPUT_DIR,
    "network"
  );

const SCRIPTS_DIR =
  path.join(
    OUTPUT_DIR,
    "scripts"
  );

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
  let browser = null;

  const errors = [];
  const networkResponses = [];

  let requestCount = 0;
  let responseCount = 0;
  let dumpIndex = 0;

  try {
    console.log(
      "[*] URL:",
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
        requestCount++;

        try {
          fs.appendFileSync(
            path.join(
              OUTPUT_DIR,
              "requests.log"
            ),
            `${request.method()} ${request.url()}\n`,
            "utf8"
          );
        } catch {}
      }
    );

    page.on(
      "response",
      async response => {
        responseCount++;

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
            `${response.status()} ${url}\n`,
            "utf8"
          );

          const interesting =
            contentType.includes(
              "json"
            ) ||
            url.includes(
              "graphql"
            ) ||
            url.includes(
              "conversation"
            ) ||
            url.includes(
              "messages"
            ) ||
            url.includes(
              "chat"
            ) ||
            url.includes(
              "api"
            ) ||
            url.includes(
              "share"
            ) ||
            url.includes(
              "grok"
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
            `${String(
              dumpIndex++
            ).padStart(
              5,
              "0"
            )}.txt`;

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
                2000000
              )
            ].join("\n"),
            "utf8"
          );
        } catch (err) {
          errors.push(
            String(err)
          );
        }
      }
    );

    console.log(
      "[*] Opening page..."
    );

    await page.goto(
      TARGET_URL,
      {
        waitUntil:
          "domcontentloaded",
        timeout: 120000
      }
    );

    await page.waitForTimeout(
      10000
    );

    const title =
      await page.title();

    const html =
      await page.content();

    const bodyText =
      await page.evaluate(
        () =>
          document.body
            ?.innerText || ""
      );

    const scripts =
      await page.$$(
        "script"
      );

    const candidateScripts =
      [];

    for (
      let i = 0;
      i < scripts.length;
      i++
    ) {
      try {
        const content =
          (
            await scripts[i]
            .textContent()
          ) || "";

        fs.writeFileSync(
          path.join(
            SCRIPTS_DIR,
            `script_${String(i)
              .padStart(
                4,
                "0"
              )}.js`
          ),
          content,
          "utf8"
        );

        if (
          content.includes(
            "__NEXT_DATA__"
          ) ||
          content.includes(
            "__INITIAL_STATE__"
          ) ||
          content.includes(
            "conversation"
          ) ||
          content.includes(
            "messages"
          ) ||
          content.includes(
            "chat"
          ) ||
          content.includes(
            "grok"
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

    const nextData =
      await page.evaluate(() => {
        const el =
          document.querySelector(
            "#__NEXT_DATA__"
          );

        return el
          ? el.textContent
          : null;
      });

    if (nextData) {
      fs.writeFileSync(
        path.join(
          OUTPUT_DIR,
          "__NEXT_DATA__.json"
        ),
        nextData,
        "utf8"
      );
    }

    const globals =
      await page.evaluate(() => {
        const result = {};

        Object.keys(window)
          .filter(key =>
            /next|chat|conversation|message|grok/i.test(
              key
            )
          )
          .slice(0, 300)
          .forEach(key => {
            try {
              const value =
                window[key];

              if (
                typeof value ===
                "string"
              ) {
                result[key] =
                  value.slice(
                    0,
                    500
                  );
              } else {
                result[key] =
                  "[OBJECT]";
              }
            } catch {}
          });

        return result;
      });

    const report = {
      url: TARGET_URL,
      title,
      request_count:
        requestCount,
      response_count:
        responseCount,
      network_payloads:
        networkResponses.length,
      candidate_script_count:
        candidateScripts.length,
      globals,
      errors
    };

    const conversation = {
      url: TARGET_URL,
      title,
      message_count: null,
      extraction_status:
        "raw_capture",
      messages: []
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
        "conversation_debug.json"
      ),
      JSON.stringify(
        report,
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

    fs.writeFileSync(
      path.join(
        OUTPUT_DIR,
        "conversation.md"
      ),
      [
        "# Grok Export",
        "",
        `URL: ${TARGET_URL}`,
        "",
        `TITLE: ${title}`,
        "",
        "---",
        "",
        bodyText
      ].join("\n"),
      "utf8"
    );

    console.log(
      "[+] Export completed"
    );

    console.log(
      "[+] Requests:",
      requestCount
    );

    console.log(
      "[+] Responses:",
      responseCount
    );

    console.log(
      "[+] Payloads:",
      networkResponses.length
    );

    console.log(
      "[+] Candidate scripts:",
      candidateScripts.length
    );

  } catch (err) {
    console.error(
      "[FATAL]",
      err
    );
  } finally {
    try {
      if (browser) {
        await browser.close();
      }
    } catch (closeErr) {
      console.error(
        "[CLOSE ERROR]",
        closeErr
      );
    }
  }
}

main();
