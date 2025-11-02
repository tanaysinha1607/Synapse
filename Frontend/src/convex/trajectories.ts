import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { getCurrentUser } from "./users";

export const getUserTrajectories = query({
  args: {},
  handler: async (ctx) => {
    const user = await getCurrentUser(ctx);
    if (!user) return [];

    return await ctx.db
      .query("trajectories")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .collect();
  },
});

export const generateTrajectories = mutation({
  args: {},
  handler: async (ctx) => {
    const user = await getCurrentUser(ctx);
    if (!user) throw new Error("Not authenticated");

    // Mock trajectory generation - in real app this would use AI
    const mockTrajectories = [
      {
        title: "Narrative Designer",
        description: "Create compelling stories and dialogue for interactive media",
        growthTrend: "up" as const,
        matchPercentage: 94,
        requiredSkills: ["Creative Writing", "Game Design", "Character Development"],
        whyMatch: "Your storytelling skills and creative background make you perfect for crafting engaging narratives in games and interactive media.",
        industry: "Gaming",
        salaryRange: { min: 65000, max: 120000 },
      },
      {
        title: "UX Content Strategist",
        description: "Shape user experiences through strategic content and messaging",
        growthTrend: "up" as const,
        matchPercentage: 87,
        requiredSkills: ["UX Writing", "Content Strategy", "User Research"],
        whyMatch: "Your communication skills and attention to detail align well with creating user-centered content experiences.",
        industry: "Technology",
        salaryRange: { min: 70000, max: 130000 },
      },
      {
        title: "Technical Writer",
        description: "Create clear documentation and guides for complex technical products",
        growthTrend: "stable" as const,
        matchPercentage: 82,
        requiredSkills: ["Technical Writing", "Documentation", "API Knowledge"],
        whyMatch: "Your ability to explain complex concepts clearly makes you ideal for technical communication roles.",
        industry: "Software",
        salaryRange: { min: 60000, max: 110000 },
      },
      {
        title: "Content Marketing Manager",
        description: "Drive brand growth through strategic content creation and distribution",
        growthTrend: "up" as const,
        matchPercentage: 79,
        requiredSkills: ["Content Marketing", "SEO", "Analytics"],
        whyMatch: "Your storytelling abilities combined with strategic thinking make you well-suited for content marketing leadership.",
        industry: "Marketing",
        salaryRange: { min: 55000, max: 95000 },
      },
    ];

    // Clear existing trajectories
    const existingTrajectories = await ctx.db
      .query("trajectories")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .collect();

    for (const trajectory of existingTrajectories) {
      await ctx.db.delete(trajectory._id);
    }

    // Insert new trajectories
    for (const trajectory of mockTrajectories) {
      await ctx.db.insert("trajectories", {
        userId: user._id,
        ...trajectory,
      });
    }
  },
});
