import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { getCurrentUser } from "./users";

export const getProfile = query({
  args: {},
  handler: async (ctx) => {
    const user = await getCurrentUser(ctx);
    if (!user) return null;

    return await ctx.db
      .query("profiles")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .unique();
  },
});

export const updateOnboardingStep = mutation({
  args: {
    step: v.union(
      v.literal("linkedin"),
      v.literal("resume"),
      v.literal("video"),
      v.literal("completed")
    ),
  },
  handler: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    if (!user) throw new Error("Not authenticated");

    const profile = await ctx.db
      .query("profiles")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .unique();

    if (profile) {
      await ctx.db.patch(profile._id, {
        [`${args.step}Uploaded`]: true,
      });
    } else {
      await ctx.db.insert("profiles", {
        userId: user._id,
        [`${args.step}Uploaded`]: true,
      });
    }

    // Update user onboarding status
    const updates: any = {};
    if (args.step === "linkedin") updates.linkedinConnected = true;
    if (args.step === "resume") updates.resumeUploaded = true;
    if (args.step === "video") updates.videoUploaded = true;
    if (args.step === "completed") updates.onboardingCompleted = true;

    await ctx.db.patch(user._id, updates);
  },
});

export const saveLinkedinData = mutation({
  args: {
    linkedinData: v.object({
      profileUrl: v.string(),
      headline: v.string(),
      summary: v.optional(v.string()),
      experience: v.array(v.object({
        title: v.string(),
        company: v.string(),
        duration: v.string(),
        description: v.optional(v.string()),
      })),
      skills: v.array(v.string()),
    }),
  },
  handler: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    if (!user) throw new Error("Not authenticated");

    const profile = await ctx.db
      .query("profiles")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .unique();

    if (profile) {
      await ctx.db.patch(profile._id, {
        linkedinData: args.linkedinData,
      });
    } else {
      await ctx.db.insert("profiles", {
        userId: user._id,
        linkedinData: args.linkedinData,
      });
    }
  },
});

export const setUserName = mutation({
  args: { name: v.string() },
  handler: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    if (!user) throw new Error("Not authenticated");
    await ctx.db.patch(user._id, { name: args.name });
  },
});