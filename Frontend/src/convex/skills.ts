import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { getCurrentUser } from "./users";

export const getUserSkills = query({
  args: {},
  handler: async (ctx) => {
    const user = await getCurrentUser(ctx);
    if (!user) return [];

    return await ctx.db
      .query("skills")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .collect();
  },
});

export const generateSkills = mutation({
  args: {},
  handler: async (ctx) => {
    const user = await getCurrentUser(ctx);
    if (!user) throw new Error("Not authenticated");

    // Mock skill generation - in real app this would use AI
    const mockSkills = [
      { name: "Storytelling", strength: 85, category: "soft" as const, source: "resume" as const },
      { name: "JavaScript", strength: 78, category: "hard" as const, source: "linkedin" as const },
      { name: "Communication", strength: 92, category: "soft" as const, source: "video" as const },
      { name: "Project Management", strength: 71, category: "soft" as const, source: "resume" as const },
      { name: "React", strength: 82, category: "hard" as const, source: "linkedin" as const },
      { name: "Creative Writing", strength: 88, category: "soft" as const, source: "video" as const },
    ];

    // Clear existing skills
    const existingSkills = await ctx.db
      .query("skills")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .collect();

    for (const skill of existingSkills) {
      await ctx.db.delete(skill._id);
    }

    // Insert new skills
    for (const skill of mockSkills) {
      await ctx.db.insert("skills", {
        userId: user._id,
        ...skill,
      });
    }

    // Mark skills as analyzed
    const profile = await ctx.db
      .query("profiles")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .unique();

    if (profile) {
      await ctx.db.patch(profile._id, { skillsAnalyzed: true });
    }
  },
});
