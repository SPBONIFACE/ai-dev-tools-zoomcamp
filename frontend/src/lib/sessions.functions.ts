import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";
import { requireSupabaseAuth } from "@/integrations/supabase/auth-middleware";

const makeToken = () =>
  Array.from({ length: 4 }, () => Math.random().toString(36).slice(2, 6)).join("").slice(0, 14);

export interface SessionRow {
  id: string;
  title: string;
  candidate_name: string;
  role_title: string;
  status: string;
  join_token: string;
  notes: string;
  link_revoked: boolean;
  created_at: string;
  ended_at: string | null;
}

export const listSessions = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => {
    const { data, error } = await context.supabase
      .from("interview_sessions")
      .select("*")
      .eq("owner_id", context.userId)
      .order("created_at", { ascending: false });
    if (error) throw new Error(error.message);
    return (data ?? []) as SessionRow[];
  });

export const createSession = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((d) =>
    z
      .object({
        title: z.string().min(1).max(120),
        candidate_name: z.string().max(120).default(""),
        role_title: z.string().max(120).default(""),
      })
      .parse(d),
  )
  .handler(async ({ data, context }) => {
    const { data: row, error } = await context.supabase
      .from("interview_sessions")
      .insert({
        owner_id: context.userId,
        title: data.title,
        candidate_name: data.candidate_name,
        role_title: data.role_title,
        join_token: makeToken(),
        status: "live",
      })
      .select("*")
      .single();
    if (error) throw new Error(error.message);
    return row as SessionRow;
  });

export const updateSession = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((d) =>
    z
      .object({
        id: z.string().uuid(),
        notes: z.string().max(20000).optional(),
        status: z.enum(["draft", "live", "completed"]).optional(),
        link_revoked: z.boolean().optional(),
        title: z.string().min(1).max(120).optional(),
      })
      .parse(d),
  )
  .handler(async ({ data, context }) => {
    const { id, ...patch } = data;
    const update: Record<string, unknown> = { ...patch };
    if (patch.status === "completed") update['ended_at'] = new Date().toISOString();
    const { error } = await context.supabase
      .from("interview_sessions")
      .update(update)
      .eq("id", id)
      .eq("owner_id", context.userId);
    if (error) throw new Error(error.message);
    return { ok: true };
  });

export const deleteSession = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((d) => z.object({ id: z.string().uuid() }).parse(d))
  .handler(async ({ data, context }) => {
    const { error } = await context.supabase
      .from("interview_sessions")
      .delete()
      .eq("id", data.id)
      .eq("owner_id", context.userId);
    if (error) throw new Error(error.message);
    return { ok: true };
  });
