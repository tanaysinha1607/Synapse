import { authTables } from "@convex-dev/auth/server";
import { defineSchema, defineTable } from "convex/server";
import { Infer, v } from "convex/values";

// default user roles. can add / remove based on the project as needed
export const ROLES = {
  ADMIN: "admin",
  USER: "user",
  MEMBER: "member",
} as const;

export const roleValidator = v.union(
  v.literal(ROLES.ADMIN),
  v.literal(ROLES.USER),
  v.literal(ROLES.MEMBER),
);
export type Role = Infer<typeof roleValidator>;

const schema = defineSchema(
  {
    // default auth tables using convex auth.
    ...authTables, // do not remove or modify

    // the users table is the default users table that is brought in by the authTables
    users: defineTable({
      name: v.optional(v.string()), // name of the user. do not remove
      image: v.optional(v.string()), // image of the user. do not remove
      email: v.optional(v.string()), // email of the user. do not remove
      emailVerificationTime: v.optional(v.number()), // email verification time. do not remove
      isAnonymous: v.optional(v.boolean()), // is the user anonymous. do not remove

      role: v.optional(roleValidator), // role of the user. do not remove
      
      // Synapse specific fields
      linkedinConnected: v.optional(v.boolean()),
      resumeUploaded: v.optional(v.boolean()),
      videoUploaded: v.optional(v.boolean()),
      onboardingCompleted: v.optional(v.boolean()),
      assessmentCompleted: v.optional(v.boolean()),
    }).index("email", ["email"]), // index for the email. do not remove or modify

    // User profiles with career data
    profiles: defineTable({
      userId: v.id("users"),
      linkedinData: v.optional(v.object({
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
      })),
      resumeFileId: v.optional(v.id("_storage")),
      videoFileId: v.optional(v.id("_storage")),
      skillsAnalyzed: v.optional(v.boolean()),
      assessmentAnswers: v.optional(v.object({
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
      })),
    }).index("by_user", ["userId"]),

    // Skills extracted from user data
    skills: defineTable({
      userId: v.id("users"),
      name: v.string(),
      strength: v.number(), // 0-100
      category: v.union(v.literal("soft"), v.literal("hard")),
      source: v.union(v.literal("resume"), v.literal("linkedin"), v.literal("video")),
      description: v.optional(v.string()),
    }).index("by_user", ["userId"]),

    // Career trajectories generated for users
    trajectories: defineTable({
      userId: v.id("users"),
      title: v.string(),
      description: v.string(),
      growthTrend: v.union(v.literal("up"), v.literal("down"), v.literal("stable")),
      matchPercentage: v.number(), // 0-100
      requiredSkills: v.array(v.string()),
      whyMatch: v.string(),
      industry: v.string(),
      salaryRange: v.optional(v.object({
        min: v.number(),
        max: v.number(),
      })),
    }).index("by_user", ["userId"]),

    // Micro-internship projects
    projects: defineTable({
      userId: v.id("users"),
      trajectoryId: v.id("trajectories"),
      title: v.string(),
      brief: v.string(),
      role: v.string(),
      status: v.union(
        v.literal("not_started"),
        v.literal("in_progress"),
        v.literal("submitted"),
        v.literal("completed")
      ),
      resources: v.array(v.object({
        title: v.string(),
        url: v.string(),
        type: v.union(v.literal("video"), v.literal("article"), v.literal("course")),
      })),
      workContent: v.optional(v.string()),
      submittedAt: v.optional(v.number()),
    }).index("by_user", ["userId"]),

    // Mentor feedback on projects
    feedback: defineTable({
      projectId: v.id("projects"),
      userId: v.id("users"),
      overallScore: v.number(), // 0-100
      rubric: v.object({
        clarity: v.number(), // 0-100
        creativity: v.number(), // 0-100
        accuracy: v.number(), // 0-100
      }),
      comments: v.array(v.object({
        section: v.string(),
        comment: v.string(),
        type: v.union(v.literal("positive"), v.literal("improvement"), v.literal("suggestion")),
      })),
      generalFeedback: v.string(),
      nextSteps: v.array(v.string()),
      mentorPersona: v.string(),
    }).index("by_project", ["projectId"]),

    // Portfolio entries
    portfolio: defineTable({
      userId: v.id("users"),
      projectId: v.id("projects"),
      title: v.string(),
      role: v.string(),
      description: v.string(),
      deliverableFileId: v.optional(v.id("_storage")),
      coverImageUrl: v.optional(v.string()),
      isPublic: v.boolean(),
      completedAt: v.number(),
    }).index("by_user", ["userId"]),
  },
  {
    schemaValidation: false,
  },
);

export default schema;