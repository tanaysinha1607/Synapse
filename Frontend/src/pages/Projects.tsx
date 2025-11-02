import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/convex/_generated/api";
import { motion } from "framer-motion";
import { BookOpen, Clock, ExternalLink, MessageSquare, Play, Send } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import { useQuery, useMutation } from "convex/react";
import { toast } from "sonner";

export default function Projects() {
  const { isLoading, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const projects = useQuery(api.projects.getUserProjects);
  const updateProjectContent = useMutation(api.projects.updateProjectContent);
  const submitProject = useMutation(api.projects.submitProject);
  
  const [selectedProject, setSelectedProject] = useState<any>(null);
  const [workContent, setWorkContent] = useState("");

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/auth");
    }
  }, [isLoading, isAuthenticated, navigate]);

  useEffect(() => {
    if (projects && projects.length > 0 && !selectedProject) {
      setSelectedProject(projects[0]);
      setWorkContent(projects[0].workContent || "");
    }
  }, [projects, selectedProject]);

  if (isLoading || !isAuthenticated) {
    return <div>Loading...</div>;
  }

  if (!projects || projects.length === 0) {
    return (
      <div className="min-h-screen pt-20 pb-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl font-bold tracking-tight mb-4">Projects</h1>
          <p className="text-xl text-muted-foreground mb-8">
            Start a career simulation to see your projects here
          </p>
          <Button asChild>
            <Link to="/trajectories">Explore Career Paths</Link>
          </Button>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "text-emerald-300 bg-emerald-500/15";
      case "submitted": return "text-blue-300 bg-blue-500/15";
      case "in_progress": return "text-amber-300 bg-amber-500/15";
      default: return "text-foreground/80 bg-foreground/10";
    }
  };

  const handleSaveWork = async () => {
    if (!selectedProject) return;
    
    try {
      await updateProjectContent({
        projectId: selectedProject._id,
        content: workContent,
      });
      toast.success("Work saved successfully!");
    } catch (error) {
      toast.error("Failed to save work");
    }
  };

  const handleSubmitProject = async () => {
    if (!selectedProject) return;
    
    try {
      await submitProject({ projectId: selectedProject._id });
      toast.success("Project submitted for review!");
      // Refresh the selected project
      const updatedProjects = await projects;
      const updated = updatedProjects?.find(p => p._id === selectedProject._id);
      if (updated) setSelectedProject(updated);
    } catch (error) {
      toast.error("Failed to submit project");
    }
  };

  return (
    <div className="min-h-screen pt-20 pb-12 mt-[100px]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            Your Projects
          </h1>
          <p className="text-xl text-muted-foreground">
            Work on realistic career simulations with AI mentorship
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Project List */}
          <div className="lg:col-span-1">
            <Card className="rounded-2xl backdrop-blur-md bg-black/40 dark:bg-black/40 border border-white/15 ring-1 ring-white/20 dark:ring-white/10 shadow-[0_8px_30px_rgba(0,0,0,0.12)]">
              <CardHeader>
                <CardTitle className="text-lg">Active Projects</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {projects.map((project) => (
                  <div
                    key={project._id}
                    onClick={() => {
                      setSelectedProject(project);
                      setWorkContent(project.workContent || "");
                    }}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedProject?._id === project._id
                        ? "border-primary bg-primary/5"
                        : "border-border hover:bg-muted/50"
                    }`}
                  >
                    <h3 className="font-medium text-sm mb-1">{project.title}</h3>
                    <p className="text-xs text-muted-foreground mb-2">{project.role}</p>
                    <Badge className={`text-xs ${getStatusColor(project.status)}`}>
                      {project.status.replace("_", " ")}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Project Workspace */}
          <div className="lg:col-span-3">
            {selectedProject && (
              <div className="space-y-6">
                {/* Project Header */}
                <Card className="rounded-2xl backdrop-blur-md bg-black/40 dark:bg-black/40 border border-white/15 ring-1 ring-white/20 dark:ring-white/10 shadow-[0_8px_30px_rgba(0,0,0,0.12)]">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-2xl">{selectedProject.title}</CardTitle>
                        <CardDescription className="text-base mt-2">
                          {selectedProject.brief}
                        </CardDescription>
                      </div>
                      <Badge className={`${getStatusColor(selectedProject.status)}`}>
                        {selectedProject.status.replace("_", " ")}
                      </Badge>
                    </div>
                  </CardHeader>
                </Card>

                {/* Resources */}
                <Card className="rounded-2xl backdrop-blur-md bg-black/40 dark:bg-black/40 border border-white/15 ring-1 ring-white/20 dark:ring-white/10 shadow-[0_8px_30px_rgba(0,0,0,0.12)]">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <BookOpen className="h-5 w-5" />
                      <span>Learning Resources</span>
                    </CardTitle>
                    <CardDescription>
                      Curated materials to help you complete this project
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {selectedProject.resources.map((resource: any, index: number) => (
                        <div key={index} className="flex items-center space-x-3 p-3 border rounded-lg">
                          <div className="flex-shrink-0">
                            {resource.type === "video" && <Play className="h-5 w-5 text-red-600" />}
                            {resource.type === "article" && <BookOpen className="h-5 w-5 text-blue-600" />}
                            {resource.type === "course" && <Clock className="h-5 w-5 text-green-600" />}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-sm">{resource.title}</p>
                            <p className="text-xs text-muted-foreground capitalize">{resource.type}</p>
                          </div>
                          <Button size="sm" variant="ghost" asChild>
                            <a href={resource.url} target="_blank" rel="noopener noreferrer">
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          </Button>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Work Area */}
                <Card className="rounded-2xl backdrop-blur-md bg-black/40 dark:bg-black/40 border border-white/15 ring-1 ring-white/20 dark:ring-white/10 shadow-[0_8px_30px_rgba(0,0,0,0.12)]">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <MessageSquare className="h-5 w-5" />
                      <span>Your Work</span>
                    </CardTitle>
                    <CardDescription>
                      Complete your project work here. Save regularly and submit when ready.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Textarea
                      placeholder="Start working on your project here..."
                      value={workContent}
                      onChange={(e) => setWorkContent(e.target.value)}
                      className="min-h-[300px] resize-none"
                      disabled={selectedProject.status === "completed"}
                    />
                    
                    {selectedProject.status !== "completed" && (
                      <div className="flex justify-between">
                        <Button variant="outline" onClick={handleSaveWork}>
                          Save Work
                        </Button>
                        <Button 
                          onClick={handleSubmitProject}
                          disabled={!workContent.trim() || selectedProject.status === "submitted"}
                        >
                          <Send className="h-4 w-4 mr-2" />
                          Submit for Review
                        </Button>
                      </div>
                    )}

                    {selectedProject.status === "completed" && (
                      <div className="text-center p-6 rounded-2xl backdrop-blur-md bg-black/35 dark:bg-black/35 ring-1 ring-white/20 dark:ring-white/10">
                        <h3 className="font-semibold text-emerald-300 mb-2">Project Completed!</h3>
                        <p className="text-sm text-emerald-200 mb-4">
                          Great work! This project has been added to your portfolio.
                        </p>
                        <Button asChild variant="secondary">
                          <Link to="/portfolio">View Portfolio</Link>
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}