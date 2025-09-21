import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/convex/_generated/api";
import { motion } from "framer-motion";
import { Briefcase, DollarSign, Play, TrendingDown, TrendingUp, Minus } from "lucide-react";
import { useEffect } from "react";
import { Link, useNavigate } from "react-router";
import { useQuery, useMutation } from "convex/react";
import { toast } from "sonner";

export default function Trajectories() {
  const { isLoading, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const trajectories = useQuery(api.trajectories.getUserTrajectories);
  const createProject = useMutation(api.projects.createProject);

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
    if (percentage >= 90) return "text-green-600 bg-green-50";
    if (percentage >= 80) return "text-blue-600 bg-blue-50";
    if (percentage >= 70) return "text-yellow-600 bg-yellow-50";
    return "text-red-600 bg-red-50";
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
    <div className="min-h-screen pt-20 pb-12">
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
              <Card className="h-full hover:shadow-lg transition-shadow duration-300">
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
                        <Badge key={skillIndex} variant="outline" className="text-xs">
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
                  <Button 
                    onClick={() => handleTestDrive(trajectory)}
                    className="w-full"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    Test Drive This Job
                  </Button>
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
          <Card>
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
