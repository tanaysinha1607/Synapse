import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/convex/_generated/api";
import { motion } from "framer-motion";
import { ArrowRight, Briefcase, DollarSign, Play, TrendingDown, TrendingUp, Minus } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import { useQuery, useMutation } from "convex/react";
import { toast } from "sonner";

export default function Trajectories() {
  const { isLoading, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const trajectories = useQuery(api.trajectories.getUserTrajectories);
  const createProject = useMutation(api.projects.createProject);

  // Add animated hue like navbar for multicolor glow
  const [hue, setHue] = useState(265);
  useEffect(() => {
    const id = setInterval(() => setHue((h) => (h + 1) % 360), 40);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/auth");
    }
  }, [isLoading, isAuthenticated, navigate]);

  if (isLoading || !isAuthenticated) {
    return <div>Loading...</div>;
  }

  if (!trajectories || trajectories.length === 0) {
    return (
      <div className="min-h-screen pt-20 pb-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl font-bold tracking-tight mb-4">Career Trajectories</h1>
          <p className="text-xl text-muted-foreground mb-8">
            Complete your skills analysis to see personalized career paths
          </p>
          <Button asChild>
            <Link to="/dashboard">Go to Dashboard</Link>
          </Button>
        </div>
      </div>
    );
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "up": return <TrendingUp className="h-5 w-5 text-green-600" />;
      case "down": return <TrendingDown className="h-5 w-5 text-red-600" />;
      default: return <Minus className="h-5 w-5 text-yellow-600" />;
    }
  };

  const getMatchColor = (percentage: number) => {
    if (percentage >= 90) return "text-emerald-300 bg-emerald-500/15";
    if (percentage >= 80) return "text-blue-300 bg-blue-500/15";
    if (percentage >= 70) return "text-amber-300 bg-amber-500/15";
    return "text-rose-300 bg-rose-500/15";
  };

  // Deterministic hue from a string (minimize collisions, stable across renders)
  const hashStringToHue = (str: string) => {
    let hash = 5381;
    for (let i = 0; i < str.length; i++) {
      // djb2 hashing
      hash = ((hash << 5) + hash) + str.charCodeAt(i);
      hash = hash & hash; // Force 32-bit
    }
    // Map to 0-359, add offset to avoid clustering around 0
    const hue = Math.abs(hash) % 360;
    return hue;
  };

  // Generate subtle, readable pastel style per unique skill
  const getSkillStyle = (skillName: string) => {
    const baseHue = hashStringToHue(skillName);
    return {
      backgroundColor: `hsla(${baseHue}, 92%, 60%, 0.14)`,
      color: `hsl(${baseHue}, 92%, 85%)`,
      borderColor: `hsla(${baseHue}, 92%, 70%, 0.35)`,
    } as React.CSSProperties;
  };

  const handleTestDrive = async (trajectory: any) => {
    try {
      const projectId = await createProject({
        trajectoryId: trajectory._id,
        title: `${trajectory.title} Simulation`,
        brief: `Experience the role of a ${trajectory.title} through this hands-on project simulation. You'll work on real-world challenges and receive mentorship from industry experts.`,
        role: trajectory.title,
      });
      
      toast.success("Project created! Starting your simulation...");
      navigate(`/projects`);
    } catch (error) {
      toast.error("Failed to create project");
    }
  };

  return (
    <div className="min-h-screen pt-20 pb-12 mt-[100px]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            Your Career Trajectories
          </h1>
          <p className="text-xl text-muted-foreground">
            Discover personalized career paths based on your skills and interests
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {trajectories.map((trajectory, index) => (
            <motion.div
              key={trajectory._id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
            >
              <Card className="h-full hover:shadow-lg transition-shadow duration-300 rounded-2xl backdrop-blur-md bg-black/40 dark:bg-black/40 border border-white/15 ring-1 ring-white/20 dark:ring-white/10 shadow-[0_8px_30px_rgba(0,0,0,0.12)]">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-xl mb-2">{trajectory.title}</CardTitle>
                      <CardDescription className="text-base">
                        {trajectory.description}
                      </CardDescription>
                    </div>
                    <div className="flex flex-col items-end space-y-2">
                      <div className={`px-3 py-1 rounded-full text-sm font-semibold ${getMatchColor(trajectory.matchPercentage)}`}>
                        {trajectory.matchPercentage}% match
                      </div>
                      <div className="flex items-center space-x-1">
                        {getTrendIcon(trajectory.growthTrend)}
                        <span className="text-sm text-muted-foreground capitalize">
                          {trajectory.growthTrend} trend
                        </span>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Why it matches */}
                  <div>
                    <h4 className="font-semibold mb-2">Why this matches you:</h4>
                    <p className="text-sm text-muted-foreground">{trajectory.whyMatch}</p>
                  </div>

                  {/* Required skills */}
                  <div>
                    <h4 className="font-semibold mb-2">Skills you'll develop:</h4>
                    <div className="flex flex-wrap gap-2">
                      {trajectory.requiredSkills.map((skill, skillIndex) => (
                        <Badge
                          key={skillIndex}
                          variant="outline"
                          className="text-xs border"
                          style={getSkillStyle(skill)}
                        >
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Industry and salary */}
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-2">
                      <Briefcase className="h-4 w-4 text-muted-foreground" />
                      <span className="text-muted-foreground">{trajectory.industry}</span>
                    </div>
                    {trajectory.salaryRange && (
                      <div className="flex items-center space-x-2">
                        <DollarSign className="h-4 w-4 text-muted-foreground" />
                        <span className="text-muted-foreground">
                          ${trajectory.salaryRange.min.toLocaleString()} - ${trajectory.salaryRange.max.toLocaleString()}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Action button */}
                  <div className="relative group">
                    {/* Multicolor animated outline (border-only) */}
                    <div
                      aria-hidden
                      className="absolute inset-0 rounded-xl opacity-80 transition-opacity duration-300 group-hover:opacity-100 pointer-events-none"
                      style={{
                        background: `
                          conic-gradient(
                            from ${hue}deg,
                            hsla(${hue}, 92%, 68%, 0.45),
                            hsla(${(hue + 45) % 360}, 92%, 66%, 0.35),
                            hsla(${(hue + 90) % 360}, 92%, 64%, 0.30),
                            hsla(${(hue + 135) % 360}, 92%, 66%, 0.35),
                            hsla(${(hue + 180) % 360}, 92%, 68%, 0.40),
                            hsla(${(hue + 225) % 360}, 92%, 66%, 0.32),
                            hsla(${(hue + 270) % 360}, 92%, 64%, 0.34),
                            hsla(${(hue + 315) % 360}, 92%, 66%, 0.38),
                            hsla(${hue}, 92%, 68%, 0.45)
                          )
                        `,
                        padding: "1px",
                        WebkitMask: "linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)",
                        WebkitMaskComposite: "xor",
                        maskComposite: "exclude",
                        borderRadius: "0.75rem",
                      } as React.CSSProperties}
                    />
                    <Button
                      onClick={() => handleTestDrive(trajectory)}
                      variant="secondary"
                      className="relative w-full rounded-xl bg-white/10 dark:bg-white/10 backdrop-blur-md border border-white/20 dark:border-white/15 hover:bg-white/15 dark:hover:bg-white/15 transition"
                    >
                      <Play className="h-4 w-4 mr-2" />
                      Test Drive This Job
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Next steps */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-12"
        >
          <Card className="rounded-2xl backdrop-blur-md bg-black/40 dark:bg-black/40 border border-white/15 ring-1 ring-white/20 dark:ring-white/10 shadow-[0_8px_30px_rgba(0,0,0,0.12)]">
            <CardHeader>
              <CardTitle>Ready to Start Your Simulation?</CardTitle>
              <CardDescription>
                Choose a career path above to begin your micro-internship experience
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <span className="text-primary font-bold">1</span>
                  </div>
                  <h3 className="font-semibold mb-2">Choose a Path</h3>
                  <p className="text-sm text-muted-foreground">
                    Select the career trajectory that interests you most
                  </p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <span className="text-primary font-bold">2</span>
                  </div>
                  <h3 className="font-semibold mb-2">Complete Projects</h3>
                  <p className="text-sm text-muted-foreground">
                    Work on realistic projects with AI mentorship
                  </p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <span className="text-primary font-bold">3</span>
                  </div>
                  <h3 className="font-semibold mb-2">Build Portfolio</h3>
                  <p className="text-sm text-muted-foreground">
                    Showcase your simulated work experience
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}