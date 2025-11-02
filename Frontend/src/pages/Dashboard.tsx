import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/convex/_generated/api";
import { motion } from "framer-motion";
import { ArrowRight, Brain, FileText, Linkedin, Play, Video } from "lucide-react";
import { useEffect } from "react";
import { Link, useNavigate } from "react-router";
import { useMutation, useQuery } from "convex/react";
import { toast } from "sonner";
import { generateCareerPlan, gapAnalysis } from "@/lib/mlApi";

export default function Dashboard() {
  const { isLoading, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  
  const profile = useQuery(api.profiles.getProfile);
  const skills = useQuery(api.skills.getUserSkills);
  const trajectories = useQuery(api.trajectories.getUserTrajectories);
  const projects = useQuery(api.projects.getUserProjects);
  
  const generateSkills = useMutation(api.skills.generateSkills);
  const generateTrajectories = useMutation(api.trajectories.generateTrajectories);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/auth");
    }
  }, [isLoading, isAuthenticated, navigate]);

  if (isLoading || !isAuthenticated || !user) {
    return <div>Loading...</div>;
  }

  // Check onboarding status
  const onboardingComplete = user.linkedinConnected && user.resumeUploaded && user.videoUploaded;
  const skillsGenerated = skills && skills.length > 0;
  const trajectoriesGenerated = trajectories && trajectories.length > 0;

  // Use first name only for greetings (derived from LinkedIn name if available)
  const firstName = user?.name?.split(" ")[0] ?? "there";

  const handleGenerateSkills = async () => {
    try {
      await generateSkills();
      toast.success("Skills analyzed successfully!");
    } catch (error) {
      toast.error("Failed to analyze skills");
    }
  };

  const handleGenerateTrajectories = async () => {
    try {
      await generateTrajectories();
      toast.success("Career trajectories generated!");
    } catch (error) {
      toast.error("Failed to generate trajectories");
    }
  };
  const handleGenerateCareerPlan = async () => {
    try {
      toast("Generating your career plan...");
      const result = await generateCareerPlan(
        { extracted_skills: ["Python", "SQL", "Machine Learning"] },
        { interests: ["AI", "Data Science"] }
      );
      console.log("Career plan response:", result);
      toast.success("Career plan generated! Check console for details.");
    } catch (error: any) {
      console.error(error);
      toast.error("Failed to generate career plan");
    }
  };

  if (!onboardingComplete) {
    return (
      <div className="min-h-screen pt-20 pb-12 mt-[100px]">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl font-bold tracking-tight mb-4">
              Complete Your Profile
            </h1>
            <p className="text-xl text-muted-foreground">
              Let's get your career simulation ready
            </p>
          </motion.div>

          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle>Setup Progress</CardTitle>
              <CardDescription>
                Complete these steps to unlock your career simulation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Linkedin className="h-5 w-5 text-blue-600" />
                    <div>
                      <p className="font-medium">Connect LinkedIn</p>
                      <p className="text-sm text-muted-foreground">Import your professional profile</p>
                    </div>
                  </div>
                  {user.linkedinConnected ? (
                    <div className="text-green-600 font-medium">✓ Complete</div>
                  ) : (
                    <Button size="sm" variant="secondary">Connect</Button>
                  )}
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-5 w-5 text-orange-600" />
                    <div>
                      <p className="font-medium">Upload Resume</p>
                      <p className="text-sm text-muted-foreground">Share your experience and skills</p>
                    </div>
                  </div>
                  {user.resumeUploaded ? (
                    <div className="text-green-600 font-medium">✓ Complete</div>
                  ) : (
                    <Button size="sm" variant="secondary">Upload</Button>
                  )}
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Video className="h-5 w-5 text-purple-600" />
                    <div>
                      <p className="font-medium">Record Introduction</p>
                      <p className="text-sm text-muted-foreground">60-second video about yourself</p>
                    </div>
                  </div>
                  {user.videoUploaded ? (
                    <div className="text-green-600 font-medium">✓ Complete</div>
                  ) : (
                    <Button size="sm" variant="secondary">Record</Button>
                  )}
                </div>
              </div>

              <div className="pt-4">
                <Button asChild className="w-full" variant="secondary">
                  <Link to="/onboarding">Continue Setup</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-20 pb-12 mt-[100px]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            Hey {firstName}, ready to simulate your future?
          </h1>
          <p className="text-xl text-muted-foreground">
            Your personalized career simulation dashboard
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Skills Analysis */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card
              className="rounded-2xl backdrop-blur-md bg-black/40 dark:bg-black/40 border border-white/15 ring-1 ring-white/20 dark:ring-white/10 shadow-[0_8px_30px_rgba(0,0,0,0.12)]"
            >
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5" />
                  <span>Skills Analysis</span>
                </CardTitle>
                <CardDescription>
                  AI-powered analysis of your capabilities
                </CardDescription>
              </CardHeader>
              <CardContent>
                {skillsGenerated ? (
                  <div className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                      {skills?.length} skills identified
                    </p>
                    <Button asChild className="w-full" variant="secondary">
                      <Link to="/skills">View Skills Graph</Link>
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                      Generate your personalized skills profile
                    </p>
                    <Button onClick={handleGenerateSkills} className="w-full" variant="secondary">
                      Analyze My Skills
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Career Trajectories */}
          <motion.div
            initial={{ opacity: 0, x: 0 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card
              className="rounded-2xl backdrop-blur-md bg-black/40 dark:bg-black/40 border border-white/15 ring-1 ring-white/20 dark:ring-white/10 shadow-[0_8px_30px_rgba(0,0,0,0.12)]"
            >
              <CardHeader>
                <CardTitle>Career Trajectories</CardTitle>
                <CardDescription>
                  Discover your potential career paths
                </CardDescription>
              </CardHeader>
              <CardContent>
                {trajectoriesGenerated ? (
                  <div className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                      {trajectories?.length} paths discovered
                    </p>
                    <Button asChild className="w-full" variant="secondary">
                      <Link to="/trajectories">Explore Paths</Link>
                    </Button>
                  </div>
                ) : skillsGenerated ? (
                  <div className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                      Generate career paths based on your skills
                    </p>
                    <Button onClick={handleGenerateTrajectories} className="w-full" variant="secondary">
                      Generate Trajectories
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                      Complete skills analysis first
                    </p>
                    <Button disabled className="w-full" variant="secondary">
                      Generate Trajectories
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Active Projects */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card
              className="rounded-2xl backdrop-blur-md bg-black/40 dark:bg-black/40 border border-white/15 ring-1 ring-white/20 dark:ring-white/10 shadow-[0_8px_30px_rgba(0,0,0,0.12)]"
            >
              <CardHeader>
                <CardTitle>Active Projects</CardTitle>
                <CardDescription>
                  Your micro-internship simulations
                </CardDescription>
              </CardHeader>
              <CardContent>
                {projects && projects.length > 0 ? (
                  <div className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                      {projects.filter(p => p.status !== "completed").length} active projects
                    </p>
                    <Button asChild className="w-full" variant="secondary">
                      <Link to="/projects">View Projects</Link>
                    </Button>
                  </div>
                ) : trajectoriesGenerated ? (
                  <div className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                      Start your first career simulation
                    </p>
                    <Button asChild className="w-full" variant="secondary">
                      <Link to="/trajectories">
                        <Play className="h-4 w-4 mr-2" />
                        Start Simulation
                      </Link>
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                      Generate trajectories to start projects
                    </p>
                    <Button disabled className="w-full" variant="secondary">
                      Start Simulation
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Quick Actions */}
        {skillsGenerated && trajectoriesGenerated && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mt-12"
          >
            <Card
              className="rounded-2xl backdrop-blur-md bg-black/40 dark:bg-black/40 border border-white/15 ring-1 ring-white/20 dark:ring-white/10 shadow-[0_8px_30px_rgba(0,0,0,0.12)]"
            >
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>
                  Jump into your career simulation
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button asChild variant="outline" className="h-auto p-6 w-full">
                    <Link to="/skills" className="flex flex-col items-center space-y-2">
                      <Brain className="h-8 w-8 text-violet-500" />
                      <span className="font-medium text-violet-500">Skills Graph</span>
                      <span className="text-sm text-muted-foreground text-center">
                        Explore your skill network
                      </span>
                    </Link>
                  </Button>
                  
                  <Button asChild variant="outline" className="h-auto p-6 w-full">
                    <Link to="/trajectories" className="flex flex-col items-center space-y-2">
                      <ArrowRight className="h-8 w-8 text-amber-500" />
                      <span className="font-medium text-amber-500">Career Paths</span>
                      <span className="text-sm text-muted-foreground text-center">
                        Discover opportunities
                      </span>
                    </Link>
                  </Button>
                  
                  <Button asChild variant="outline" className="h-auto p-6 w-full">
                    <Link to="/portfolio" className="flex flex-col items-center space-y-2">
                      <FileText className="h-8 w-8 text-emerald-500" />
                      <span className="font-medium text-emerald-500">Portfolio</span>
                      <span className="text-sm text-muted-foreground text-center">
                        View your work
                      </span>
                    </Link>
                  </Button>
                  <Button onClick={handleGenerateCareerPlan} className="h-auto p-6 w-full" variant="outline">
  <div className="flex flex-col items-center space-y-2">
    <Play className="h-8 w-8 text-indigo-500" />
    <span className="font-medium text-indigo-500">Generate Career Plan (AI)</span>
    <span className="text-sm text-muted-foreground text-center">
      Powered by your skills & interests.
    </span>
  </div>
</Button>

                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  );
}