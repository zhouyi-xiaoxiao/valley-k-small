#!/usr/bin/env node

import fs from "fs";
import os from "os";
import path from "path";
import { pathToFileURL } from "url";

function usage() {
  console.error(
    "Usage: graph_reply_with_attachments.mjs --message-id ID --body-html PATH --attachment PATH [--attachment PATH ...]",
  );
}

function parseArgs(argv) {
  const args = { attachments: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--attachment") {
      args.attachments.push(argv[++i]);
    } else if (token === "--message-id") {
      args.messageId = argv[++i];
    } else if (token === "--body-html") {
      args.bodyHtml = argv[++i];
    } else if (token === "--help" || token === "-h") {
      usage();
      process.exit(0);
    }
  }
  return args;
}

function contentTypeFor(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".pdf") return "application/pdf";
  if (ext === ".zip") return "application/zip";
  if (ext === ".tex") return "application/x-tex";
  if (ext === ".txt") return "text/plain";
  return "application/octet-stream";
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.messageId || !args.bodyHtml || args.attachments.length === 0) {
    usage();
    process.exit(2);
  }

  const servicePath = path.join(os.homedir(), ".codex", "mcp", "m365-graph", "lib", "service.mjs");
  const { M365GraphService } = await import(pathToFileURL(servicePath).href);
  const service = new M365GraphService();

  const bodyHtml = fs.readFileSync(path.resolve(args.bodyHtml), "utf8");
  const draft = await service.graphRequest(`/me/messages/${encodeURIComponent(args.messageId)}/createReply`, {
    method: "POST",
    body: JSON.stringify({}),
  });
  const draftId = draft?.id;
  if (!draftId) {
    throw new Error("createReply did not return a draft id");
  }

  const quotedBody = draft.body?.content || "";
  const separator = bodyHtml && quotedBody ? "<div><br></div>" : "";
  await service.graphRequest(`/me/messages/${encodeURIComponent(draftId)}`, {
    method: "PATCH",
    body: JSON.stringify({
      body: {
        contentType: "HTML",
        content: `${bodyHtml}${separator}${quotedBody}`,
      },
    }),
  });

  const attached = [];
  for (const attachmentPath of args.attachments) {
    const absolute = path.resolve(attachmentPath);
    const stat = fs.statSync(absolute);
    const name = path.basename(absolute);
    const contentBytes = fs.readFileSync(absolute).toString("base64");
    await service.graphRequest(`/me/messages/${encodeURIComponent(draftId)}/attachments`, {
      method: "POST",
      body: JSON.stringify({
        "@odata.type": "#microsoft.graph.fileAttachment",
        name,
        contentType: contentTypeFor(absolute),
        contentBytes,
      }),
    });
    attached.push({ name, size: stat.size });
  }

  await service.graphRequest(`/me/messages/${encodeURIComponent(draftId)}/send`, {
    method: "POST",
    body: JSON.stringify({}),
  });

  console.log(JSON.stringify({ ok: true, draftId, attached }, null, 2));
}

main().catch((error) => {
  console.error(JSON.stringify({ ok: false, error: error?.message || String(error) }, null, 2));
  process.exit(1);
});
