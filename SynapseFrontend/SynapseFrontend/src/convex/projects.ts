import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { getCurrentUser } from "./users";

export const getUserProjects = query({
  args: {},
  handler: async (ctx) => {
    const user = await getCurrentUser(ctx);
    if (!user) return [];

    return await ctx.db
      .query("projects")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .collect();
  },
});

export const getProject = query({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    if (!user) return null;

    const project = await ctx.db.get(args.projectId);
    if (!project || project.userId !== user._id) return null;

    return project;
  },
});

export const createProject = mutation({
  args: {
    trajectoryId: v.id("trajectories"),
    title: v.string(),
    brief: v.string(),
    role: v.string(),
  },
  handler: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    if (!user) throw new Error("Not authenticated");

    // Mock resources - in real app these would be AI-generated
    const mockResources = [
      {
        title: "Game Writing Fundamentals",
        url: "https://www.youtube.com/watch?v=example1",
        type: "video" as const,
      },
      {
        title: "Character Development Guide",
        url: "https://example.com/character-guide",
        type: "article" as const,
      },
      {
        title: "Narrative Design Course",
        url: "https://coursera.org/narrative-design",
        type: "course" as const,
      },
    ];

    return await ctx.db.insert("projects", {
      userId: user._id,
      trajectoryId: args.trajectoryId,
      title: args.title,
      brief: args.brief,
      role: args.role,
      status: "not_started",
      resources: mockResources,
    });
  },
});

export const updateProjectContent = mutation({
  args: {
    projectId: v.id("projects"),
    content: v.string(),
  },
  handler: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    if (!user) throw new Error("Not authenticated");

    const project = await ctx.db.get(args.projectId);
    if (!project || project.userId !== user._id) {
      throw new Error("Project not found");
    }

    await ctx.db.patch(args.projectId, {
      workContent: args.content,
      status: "in_progress",
    });
  },
});

export const submitProject = mutation({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    if (!user) throw new Error("Not authenticated");

    const project = await ctx.db.get(args.projectId);
    if (!project || project.userId !== user._id) {
      throw new Error("Project not found");
    }

    await ctx.db.patch(args.projectId, {
      status: "submitted",
      submittedAt: Date.now(),
    });

    // Generate mock feedback
    await ctx.db.insert("feedback", {
      projectId: args.projectId,
      userId: user._id,
      overallScore: 87,
      rubric: {
        clarity: 85,
        creativity: 92,
        accuracy: 84,
      },
      comments: [
        {
          section: "Character Voice",
          comment: "Excellent character development with distinct personality traits",
          type: "positive",
        },
        {
          section: "Dialogue Flow",
          comment: "Consider adding more natural pauses and interruptions",
          type: "improvement",
        },
      ],
      generalFeedback: "Strong work overall! Your character voice is compelling and the environmental storytelling is effective. Focus on making dialogue feel more conversational.",
      nextSteps: [
        "Practice writing dialogue with subtext",
        "Study environmental storytelling techniques",
        "Experiment with different character archetypes",
      ],
      mentorPersona: "Senior Game Producer with 10+ years at major studios",
    });

    await ctx.db.patch(args.projectId, { status: "completed" });
  },
});
