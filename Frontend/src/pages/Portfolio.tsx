import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/convex/_generated/api";
import { motion } from "framer-motion";
import { Calendar, ExternalLink, Eye, Share2, User } from "lucide-react";
import { useEffect } from "react";
import { Link, useNavigate } from "react-router";
import { useQuery } from "convex/react";

export default function Portfolio() {
  const { isLoading, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const portfolio = useQuery(api.portfolio.getUserPortfolio);
  const projects = useQuery(api.projects.getUserProjects);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/auth");
    }
  }, [isLoading, isAuthenticated, navigate]);

  if (isLoading || !isAuthenticated) {
    return <div>Loading...</div>;
  }

  const completedProjects = projects?.filter(p => p.status === "completed") || [];

  return (
    <div className="min-h-screen pt-20 pb-12 mt-[100px]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold tracking-tight mb-4">
                {user?.name ? `${user.name}'s Portfolio` : "Your Portfolio"}
              </h1>
              <p className="text-xl text-muted-foreground">
                Showcase your simulated work experience and capabilities
              </p>
            </div>
            <Button variant="outline">
              <Share2 className="h-4 w-4 mr-2" />
              Share Portfolio
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-primary/10 rounded-lg">
                    <User className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{completedProjects.length}</p>
                    <p className="text-sm text-muted-foreground">Completed Projects</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-green-100 rounded-lg">
                    <Eye className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">
                      {new Set(completedProjects.map(p => p.role)).size}
                    </p>
                    <p className="text-sm text-muted-foreground">Roles Explored</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <Calendar className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">
                      {completedProjects.length > 0 ? "Active" : "Getting Started"}
                    </p>
                    <p className="text-sm text-muted-foreground">Portfolio Status</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </motion.div>

        {/* Portfolio Items */}
        {completedProjects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {completedProjects.map((project, index) => (
              <motion.div
                key={project._id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
              >
                <Card className="h-full hover:shadow-lg transition-shadow duration-300">
                  <div className="aspect-video bg-gradient-to-br from-primary/20 to-primary/5 rounded-t-lg flex items-center justify-center">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-3">
                        <User className="h-8 w-8 text-primary" />
                      </div>
                      <p className="font-medium text-primary">{project.role}</p>
                    </div>
                  </div>
                  
                  <CardHeader>
                    <CardTitle className="text-lg">{project.title}</CardTitle>
                    <CardDescription>
                      {project.brief.substring(0, 100)}...
                    </CardDescription>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between text-sm">
                      <Badge variant="secondary">{project.role}</Badge>
                      <span className="text-muted-foreground">
                        {project.submittedAt && new Date(project.submittedAt).toLocaleDateString()}
                      </span>
                    </div>
                    
                    <div className="flex space-x-2">
                      <Button size="sm" className="flex-1">
                        <Eye className="h-4 w-4 mr-2" />
                        View Work
                      </Button>
                      <Button size="sm" variant="outline">
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-16"
          >
            <div className="max-w-md mx-auto">
              <div className="w-24 h-24 bg-muted rounded-full flex items-center justify-center mx-auto mb-6">
                <User className="h-12 w-12 text-muted-foreground" />
              </div>
              <h3 className="text-2xl font-semibold mb-4">Start Building Your Portfolio</h3>
              <p className="text-muted-foreground mb-8">
                Complete career simulation projects to showcase your capabilities and build a compelling portfolio.
              </p>
              <div className="space-y-3">
                <Button asChild className="w-full">
                  <Link to="/trajectories">Explore Career Paths</Link>
                </Button>
                <Button asChild variant="outline" className="w-full">
                  <Link to="/dashboard">Go to Dashboard</Link>
                </Button>
              </div>
            </div>
          </motion.div>
        )}

        {/* Call to Action */}
        {completedProjects.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mt-16"
          >
            <Card>
              <CardHeader className="text-center">
                <CardTitle>Keep Building Your Experience</CardTitle>
                <CardDescription>
                  Explore more career paths and add diverse projects to your portfolio
                </CardDescription>
              </CardHeader>
              <CardContent className="text-center">
                <Button asChild>
                  <Link to="/trajectories">
                    Discover New Opportunities
                  </Link>
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  );
}