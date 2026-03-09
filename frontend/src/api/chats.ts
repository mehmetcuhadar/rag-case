import { request } from "./http";

export type ChatRow = { chat_id: string; chat_name?: string | null };
export type MessageRow = { role: "user" | "assistant"; content: string };

export async function createChat(chat_name: string): Promise<ChatRow> {
  const r = await request<ChatRow>("POST", "/v1/chats/create", { json: { chat_name } });
  if (!r.ok) throw new Error("Cannot create chat.");
  return r.data!;
}

export async function listChats(): Promise<ChatRow[]> {
  const r = await request<ChatRow[]>("GET", "/v1/chats/list");
  if (!r.ok) throw new Error("Cannot load chats.");
  return r.data ?? [];
}

export async function getMessages(chatId: string, limit = 200): Promise<MessageRow[]> {
  const r = await request<MessageRow[]>("GET", `/v1/chats/${chatId}/messages?limit=${limit}`);
  if (!r.ok) throw new Error("Cannot load messages.");
  return r.data ?? [];
}

export async function renameChat(chatId: string, chat_name: string): Promise<ChatRow> {
  const r = await request<ChatRow>("PATCH", `/v1/chats/update/${chatId}`, { json: { chat_name } });
  if (!r.ok) throw new Error("Cannot rename chat.");
  return r.data!;
}

export async function deleteChat(chatId: string): Promise<void> {
  const r = await request("DELETE", `/v1/chats/delete/${chatId}`);
  if (!r.ok) throw new Error("Cannot delete chat.");
}