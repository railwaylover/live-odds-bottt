/**
 * Minimal Telegram Bot API client over fetch.
 * Replaces python-telegram-bot (no sockets on Workers): only the methods
 * this bot needs — sendMessage with exponential backoff.
 */
export class TelegramClient {
  private base: string;
  private token: string;

  constructor(token: string) {
    this.token = token;
    this.base = `https://api.telegram.org/bot${token}`;
  }

  async sendMessage(chatId: string | number, text: string): Promise<boolean> {
    try {
      const resp = await fetch(`${this.base}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: chatId, text }),
      });
      if (!resp.ok) return false;
      const data = (await resp.json()) as { ok?: boolean };
      return data.ok === true;
    } catch {
      return false;
    }
  }

  /** Mirrors notify.send_with_backoff: 3 attempts, 2s/4s delays. */
  async sendWithBackoff(chatId: string | number, text: string, retries = 3): Promise<boolean> {
    let delay = 2000;
    for (let attempt = 0; attempt < retries; attempt++) {
      if (await this.sendMessage(chatId, text)) return true;
      if (attempt < retries - 1) await new Promise((r) => setTimeout(r, delay));
      delay *= 2;
    }
    return false;
  }
}

/** Minimal subset of the Telegram Update schema this bot consumes. */
export interface TelegramUpdate {
  update_id: number;
  message?: {
    message_id: number;
    chat: { id: number; type?: string };
    text?: string;
    entities?: Array<{ type: string; offset: number; length: number }>;
  };
}

export function extractCommand(text: string | undefined): { command: string; args: string[] } | null {
  if (!text || !text.startsWith("/")) return null;
  const first = text.split(/\s+/)[0]!;
  const command = first.split("@")[0]!.slice(1).toLowerCase();
  const args = text.split(/\s+/).slice(1);
  return { command, args };
}
