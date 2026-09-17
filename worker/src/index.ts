/**
 * Worker entry: Telegram webhook (fetch) + monitor cron (scheduled).
 * Replaces bot/main.py long-polling: no background process on Workers.
 */
import { routeCommand } from "./commands.ts";
import { settings, type Env } from "./config.ts";
import { cachedHttp } from "./feeds/http.ts";
import { runCycle } from "./monitor.ts";
import { Store } from "./store.ts";
import { TelegramClient, extractCommand, type TelegramUpdate } from "./telegram.ts";

async function handleUpdate(env: Env, update: TelegramUpdate): Promise<void> {
  const cfg = settings(env);
  const tg = new TelegramClient(cfg.botToken);
  const msg = update.message;
  if (!msg?.text) return;
  const parsed = extractCommand(msg.text);
  if (!parsed) return; // non-command messages are ignored (same as PTB setup)
  const store = new Store(env.DB);
  // Mirror PTB post_init: every authorized chat is a subscriber by default.
  for (const id of cfg.authorizedChatIds) await store.ensureSubscription(id);
  await routeCommand(parsed.command, {
    store,
    tg,
    cfg,
    chatId: String(msg.chat.id),
    args: parsed.args,
  });
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return Response.json({ ok: true, service: "live-odds-bot" });
    }
    if (request.method !== "POST" || url.pathname !== "/") {
      return new Response("Not found", { status: 404 });
    }
    // Webhook authenticity: Telegram echoes the secret_token we registered.
    const secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token") ?? "";
    if (!env.WEBHOOK_SECRET || secret !== env.WEBHOOK_SECRET) {
      return new Response("Forbidden", { status: 403 });
    }
    let update: TelegramUpdate;
    try {
      update = (await request.json()) as TelegramUpdate;
    } catch {
      return new Response("Bad request", { status: 400 });
    }
    try {
      await handleUpdate(env, update);
    } catch (e) {
      console.error("update failed", e);
    }
    // Always 200 so Telegram stops retrying (failures are logged, not retried).
    return Response.json({ ok: true });
  },

  async scheduled(_event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    const cfg = settings(env);
    const store = new Store(env.DB);
    for (const id of cfg.authorizedChatIds) await store.ensureSubscription(id);
    const tg = new TelegramClient(cfg.botToken);
    const http = cachedHttp(cfg.fetchTimeoutMs);
    // waitUntil lets the cron invocation finish bookkeeping while work continues.
    ctx.waitUntil(
      (async () => {
        try {
          const stats = await runCycle(store, tg, cfg, http);
          console.log("cycle done", JSON.stringify(stats));
        } catch (e) {
          console.error("cycle failed", e);
        }
      })(),
    );
  },
};
