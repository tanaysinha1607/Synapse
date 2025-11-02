import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { getAuthUserId } from "@convex-dev/auth/server";

export const saveAssessment = mutation({
  args: {
    answers: v.object({
      careerGoal: v.optional(v.string()),
      primaryMotivator: v.optional(v.string()),
      fiveYearVision: v.optional(v.string()),
      weeklyHours: v.optional(v.string()),
      learningStyle: v.optional(v.string()),
      skillConfidence: v.optional(v.string()),
      workEnvironment: v.optional(v.string()),
      unconventionalRoles: v.optional(v.string()),
      workEnergy: v.optional(v.string()),
      minSalary: v.optional(v.string()),
    }),
  },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) {
      throw new Error("Not authenticated");
    }

    // Update user to mark assessment as completed
    await ctx.db.patch(userId, {
      assessmentCompleted: true,
    });

    // Get or create profile
    const existingProfile = await ctx.db
      .query("profiles")
      .withIndex("by_user", (q) => q.eq("userId", userId))
      .first();

    if (existingProfile) {
      await ctx.db.patch(existingProfile._id, {
        assessmentAnswers: args.answers,
      });
    } else {
      await ctx.db.insert("profiles", {
        userId,
        assessmentAnswers: args.answers,
      });
    }

    return { success: true };
  },
});

export const getAssessment = query({
  args: {},
  handler: async (ctx) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) {
      return null;
    }

    const profile = await ctx.db
      .query("profiles")
      .withIndex("by_user", (q) => q.eq("userId", userId))
      .first();

    return profile?.assessmentAnswers || null;
  },
});
