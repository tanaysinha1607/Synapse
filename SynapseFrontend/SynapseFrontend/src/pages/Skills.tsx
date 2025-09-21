import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/convex/_generated/api";
import { motion } from "framer-motion";
import { ArrowRight, Brain, FileText, Linkedin, Video } from "lucide-react";
import { useEffect } from "react";
import { Link, useNavigate } from "react-router";
import { useQuery } from "convex/react";

export default function Skills() {
  const { isLoading, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const skills = useQuery(api.skills.getUserSkills);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/auth");
    }
  }, [isLoading, isAuthenticated, navigate]);

  if (isLoading || !isAuthenticated) {
    return <div>Loading...</div>;
  }

  if (!skills || skills.length === 0) {
    return (
      <div className="min-h-screen pt-20 pb-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl font-bold tracking-tight mb-4">Skills Analysis</h1>
          <p className="text-xl text-muted-foreground mb-8">
            Complete your profile setup to see your skills analysis
          </p>
          <Button asChild>
            <Link to="/dashboard">Go to Dashboard</Link>
          </Button>
        </div>
      </div>
    );
  }

  const softSkills = skills.filter(skill => skill.category === "soft");
  const hardSkills = skills.filter(skill => skill.category === "hard");

  const getSourceIcon = (source: string) => {
    switch (source) {
      case "linkedin": return <Linkedin className="h-4 w-4 text-blue-600" />;
      case "resume": return <FileText className="h-4 w-4 text-orange-600" />;
      case "video": return <Video className="h-4 w-4 text-purple-600" />;
      default: return <Brain className="h-4 w-4" />;
    }
  };

  const getStrengthColor = (strength: number) => {
    if (strength >= 80) return "text-green-600";
    if (strength >= 60) return "text-yellow-600";
    return "text-red-600";
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
            Your Skills Profile
          </h1>
          <p className="text-xl text-muted-foreground">
            AI-powered analysis of your capabilities and strengths
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Soft Skills */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5 text-purple-600" />
                  <span>Soft Skills</span>
                </CardTitle>
                <CardDescription>
                  Interpersonal and cognitive abilities
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {softSkills.map((skill, index) => (
                  <motion.div
                    key={skill._id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">{skill.name}</span>
                        {getSourceIcon(skill.source)}
                      </div>
                      <span className={`font-semibold ${getStrengthColor(skill.strength)}`}>
                        {skill.strength}%
                      </span>
                    </div>
                    <Progress value={skill.strength} className="h-2" />
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </motion.div>

          {/* Hard Skills */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5 text-blue-600" />
                  <span>Hard Skills</span>
                </CardTitle>
                <CardDescription>
                  Technical and specialized knowledge
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {hardSkills.map((skill, index) => (
                  <motion.div
                    key={skill._id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">{skill.name}</span>
                        {getSourceIcon(skill.source)}
                      </div>
                      <span className={`font-semibold ${getStrengthColor(skill.strength)}`}>
                        {skill.strength}%
                      </span>
                    </div>
                    <Progress value={skill.strength} className="h-2" />
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Skills Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Skills Overview</CardTitle>
              <CardDescription>
                How your skills were identified and analyzed
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="text-center">
                  <div className="flex justify-center mb-2">
                    <Linkedin className="h-8 w-8 text-blue-600" />
                  </div>
                  <h3 className="font-semibold mb-1">LinkedIn Analysis</h3>
                  <p className="text-sm text-muted-foreground">
                    {skills.filter(s => s.source === "linkedin").length} skills identified
                  </p>
                </div>
                <div className="text-center">
                  <div className="flex justify-center mb-2">
                    <FileText className="h-8 w-8 text-orange-600" />
                  </div>
                  <h3 className="font-semibold mb-1">Resume Analysis</h3>
                  <p className="text-sm text-muted-foreground">
                    {skills.filter(s => s.source === "resume").length} skills identified
                  </p>
                </div>
                <div className="text-center">
                  <div className="flex justify-center mb-2">
                    <Video className="h-8 w-8 text-purple-600" />
                  </div>
                  <h3 className="font-semibold mb-1">Video Analysis</h3>
                  <p className="text-sm text-muted-foreground">
                    {skills.filter(s => s.source === "video").length} skills identified
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap gap-2 mb-6">
                {skills.map((skill) => (
                  <Badge key={skill._id} variant="secondary" className="text-sm">
                    {skill.name}
                  </Badge>
                ))}
              </div>

              <div className="flex justify-center">
                <Button asChild>
                  <Link to="/trajectories">
                    Explore Career Paths
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
