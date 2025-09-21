// src/pages/Onboarding.tsx
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { motion } from "framer-motion";
import { ArrowLeft, ArrowRight, CheckCircle, FileText, Linkedin, Upload, Video } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { toast } from "sonner";
import { apiRequest } from "@/lib/api";

export default function Onboarding() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);

  const steps = [
    { id: 1, title: "Connect LinkedIn", icon: Linkedin, color: "text-blue-600" },
    { id: 2, title: "Upload Resume", icon: FileText, color: "text-orange-600" },
    { id: 3, title: "Record Video", icon: Video, color: "text-purple-600" },
  ];

  const progress = (currentStep / steps.length) * 100;

  // Step 1: LinkedIn
  const handleLinkedinConnect = async () => {
    if (!linkedinUrl) {
      toast.error("Please enter your LinkedIn URL");
      return;
    }

    try {
      await apiRequest("/onboard", {
        method: "POST",
        body: JSON.stringify({
          user_id: "amardeep001",
          user_data: { linkedin_url: linkedinUrl },
        }),
      });
      toast.success("LinkedIn connected successfully!");
      setCurrentStep(2);
    } catch (error) {
      toast.error("Failed to connect LinkedIn");
    }
  };

  // Step 2: Resume Upload
  const handleResumeUpload = async () => {
    if (!resumeFile) {
      toast.error("Please select a resume file");
      return;
    }

    try {
      await apiRequest("/onboard", {
        method: "POST",
        body: JSON.stringify({
          user_id: "amardeep001",
          user_data: { resume_file: "Uploaded Resume" }, // TODO: handle file upload later
        }),
      });
      toast.success("Resume uploaded successfully!");
      setCurrentStep(3);
    } catch (error) {
      toast.error("Failed to upload resume");
    }
  };

  // Step 3: Video Upload
  const handleVideoUpload = async () => {
    if (!videoFile) {
      toast.error("Please record or upload a video");
      return;
    }

    try {
      await apiRequest("/onboard", {
        method: "POST",
        body: JSON.stringify({
          user_id: "amardeep001",
          user_data: { video_file: "Uploaded Video" }, // TODO: handle file upload later
        }),
      });
      localStorage.setItem("onboardingComplete", "true");
      toast.success("Video uploaded successfully!");
      navigate("/dashboard");
    } catch (error) {
      toast.error("Failed to upload video");
    }
  };

  return (
    <div className="min-h-screen pt-20 pb-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            Set Up Your Profile
          </h1>
          <p className="text-xl text-muted-foreground">
            Let’s gather the information we need to create your personalized career simulation
          </p>
        </motion.div>

        {/* Progress Bar */}
        <Progress value={progress} className="h-2 mb-12" />

        <Card className="max-w-2xl mx-auto">
          {currentStep === 1 && (
            <>
              <CardHeader className="text-center">
                <Linkedin className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                <CardTitle>Connect Your LinkedIn</CardTitle>
                <CardDescription>Provide your LinkedIn profile URL</CardDescription>
              </CardHeader>
              <CardContent>
                <Input
                  placeholder="https://linkedin.com/in/yourprofile"
                  value={linkedinUrl}
                  onChange={(e) => setLinkedinUrl(e.target.value)}
                />
                <div className="flex justify-end mt-6">
                  <Button onClick={handleLinkedinConnect}>
                    Next <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </>
          )}

          {currentStep === 2 && (
            <>
              <CardHeader className="text-center">
                <FileText className="h-12 w-12 text-orange-600 mx-auto mb-4" />
                <CardTitle>Upload Your Resume</CardTitle>
              </CardHeader>
              <CardContent>
                <Input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                />
                <div className="flex justify-between mt-6">
                  <Button variant="outline" onClick={() => setCurrentStep(1)}>
                    <ArrowLeft className="h-4 w-4 mr-2" /> Back
                  </Button>
                  <Button onClick={handleResumeUpload}>
                    Next <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </>
          )}

          {currentStep === 3 && (
            <>
              <CardHeader className="text-center">
                <Video className="h-12 w-12 text-purple-600 mx-auto mb-4" />
                <CardTitle>Upload Your Video</CardTitle>
              </CardHeader>
              <CardContent>
                <Input
                  type="file"
                  accept="video/*"
                  onChange={(e) => setVideoFile(e.target.files?.[0] || null)}
                />
                <div className="flex justify-between mt-6">
                  <Button variant="outline" onClick={() => setCurrentStep(2)}>
                    <ArrowLeft className="h-4 w-4 mr-2" /> Back
                  </Button>
                  <Button onClick={handleVideoUpload}>
                    Complete <CheckCircle className="h-4 w-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </>
          )}
        </Card>
      </div>
    </div>
  );
}
