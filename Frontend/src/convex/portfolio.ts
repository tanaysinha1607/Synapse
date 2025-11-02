import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { getCurrentUser } from "./users";

export const getUserPortfolio = query({
  args: {},
  handler: async (ctx) => {
    const user = await getCurrentUser(ctx);
    if (!user) return [];

    return await ctx.db
      .query("portfolio")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .collect();
  },
});

export const addToPortfolio = mutation({
  args: {
    projectId: v.id("projects"),
    title: v.string(),
    role: v.string(),
    description: v.string(),
    isPublic: v.boolean(),
  },
  handler: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    if (!user) throw new Error("Not authenticated");

    return await ctx.db.insert("portfolio", {
      userId: user._id,
      projectId: args.projectId,
      title: args.title,
      role: args.role,
      description: args.description,
      isPublic: args.isPublic,
      completedAt: Date.now(),
    });
  },
});
