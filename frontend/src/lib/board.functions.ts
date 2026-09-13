import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";
import { requireSupabaseAuth } from "@/integrations/supabase/auth-middleware";
import type { BoardEl } from "./board-types";

const colorEnum = z.enum([
  "node-service",
  "node-data",
  "node-flow",
  "node-edge-net",
  "node-ai",
  "node-external",
  "node-note",
]);

const elSchema = z.discriminatedUnion("kind", [
  z.object({
    id: z.string().max(64),
    kind: z.literal("node"),
    shape: z.string().max(32),
    x: z.number(),
    y: z.number(),
    w: z.number(),
    h: z.number(),
    label: z.string().max(200),
    sub: z.string().max(200),
    color: colorEnum,
  }),
  z.object({
    id: z.string().max(64),
    kind: z.literal("edge"),
    from: z.string().max(64),
    to: z.string().max(64),
    style: z.enum(["solid", "dashed"]),
    arrow: z.enum(["end", "both", "none"]),
    label: z.string().max(200),
    color: colorEnum,
  }),
  z.object({
    id: z.string().max(64),
    kind: z.literal("draw"),
    points: z.array(z.number()).max(6000),
    color: colorEnum,
    width: z.number().min(1).max(24),
  }),
  z.object({
    id: z.string().max(64),
    kind: z.literal("text"),
    x: z.number(),
    y: z.number(),
    text: z.string().max(2000),
    color: colorEnum,
    size: z.number().min(8).max(96),
  }),
]);

const opSchema = z.union([
  z.object({ type: z.literal("upsert"), el: elSchema }),
  z.object({ type: z.literal("delete"), id: z.string().max(64) }),
]);

export interface BoardSession {
  id: string;
  title: string;
  role_title: string;
  candidate_name: string;
  status: string;
  link_revoked: boolean;
}

export const joinBoard = createServerFn({ method: "GET" })
  .inputValidator((d) => z.object({ token: z.string().min(4).max(64) }).parse(d))
  .handler(async ({ data }) => {
    const { supabaseAdmin } = await import("@/integrations/supabase/client.server");
    const { data: session } = await supabaseAdmin
      .from("interview_sessions")
      .select("id,title,role_title,candidate_name,status,link_revoked")
      .eq("join_token", data.token)
      .maybeSingle();

    if (!session) return { found: false as const };
    if (session.link_revoked) return { found: true as const, revoked: true as const };

    const { data: rows, error } = await supabaseAdmin
      .from("board_elements")
      .select("data")
      .eq("session_id", session.id);
    if (error) throw new Error(error.message);

    return {
      found: true as const,
      revoked: false as const,
      session: session as BoardSession,
      elements: (rows ?? []).map((r) => r.data as BoardEl),
    };
  });

export const pushOps = createServerFn({ method: "POST" })
  .inputValidator((d) =>
    z
      .object({
        token: z.string().min(4).max(64),
        ops: z.array(opSchema).max(400),
      })
      .parse(d),
  )
  .handler(async ({ data }) => {
    const { supabaseAdmin } = await import("@/integrations/supabase/client.server");
    const { data: session } = await supabaseAdmin
      .from("interview_sessions")
      .select("id,status,link_revoked")
      .eq("join_token", data.token)
      .maybeSingle();

    if (!session || session.link_revoked || session.status === "completed") {
      return { ok: false as const };
    }

    const upserts = data.ops.filter((o) => o.type === "upsert");
    const deletes = data.ops.filter((o) => o.type === "delete");

    if (upserts.length) {
      const { error } = await supabaseAdmin.from("board_elements").upsert(
        upserts.map((o) => ({
          id: o.el.id,
          session_id: session.id,
          data: o.el,
          updated_at: new Date().toISOString(),
        })),
      );
      if (error) throw new Error(error.message);
    }
    if (deletes.length) {
      const { error } = await supabaseAdmin
        .from("board_elements")
        .delete()
        .eq("session_id", session.id)
        .in(
          "id",
          deletes.map((o) => o.id),
        );
      if (error) throw new Error(error.message);
    }
    return { ok: true as const };
  });

/** Owner-only view of the session behind a token (private notes, controls). */
export const getOwnedSession = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .inputValidator((d) => z.object({ token: z.string().min(4).max(64) }).parse(d))
  .handler(async ({ data, context }) => {
    const { data: row } = await context.supabase
      .from("interview_sessions")
      .select("id,title,notes,status,link_revoked,candidate_name,role_title")
      .eq("join_token", data.token)
      .eq("owner_id", context.userId)
      .maybeSingle();
    return { owned: !!row, session: row ?? null };
  });
