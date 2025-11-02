import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/convex/_generated/api";
import { motion } from "framer-motion";
import { ArrowLeft, ArrowRight, CheckCircle, FileText, Linkedin, Upload, Video, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { useMutation, useAction } from "convex/react";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";

export default function Onboarding() {
  const { isLoading, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogTitle, setDialogTitle] = useState<string>("");
  const [dialogMessage, setDialogMessage] = useState<string>("");
  const [validLinkedinName, setValidLinkedinName] = useState<string | null>(null);

  const updateOnboardingStep = useMutation(api.profiles.updateOnboardingStep);
  const validateLinkedinUrl = useAction(api.profilesActions.validateLinkedinUrl);
  const setUserName = useMutation(api.profiles.setUserName);

  const [isValidating, setIsValidating] = useState(false);
  const [isUploadingResume, setIsUploadingResume] = useState(false);
  const [isUploadingVideo, setIsUploadingVideo] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/auth");
    }
  }, [isLoading, isAuthenticated, navigate]);

  if (isLoading || !isAuthenticated || !user) {
    return <div>Loading...</div>;
  }

  const steps = [
    { id: 1, title: "Connect LinkedIn", icon: Linkedin, color: "text-blue-600" },
    { id: 2, title: "Upload Resume", icon: FileText, color: "text-orange-600" },
    { id: 3, title: "Record Video", icon: Video, color: "text-purple-600" },
  ];

  const progress = (currentStep / steps.length) * 100;

  const handleLinkedinConnect = async () => {
    if (!linkedinUrl) {
      toast.error("Please enter your LinkedIn URL");
      return;
    }

    try {
      setIsValidating(true);
      const result = await validateLinkedinUrl({ url: linkedinUrl });
      if (!result?.valid) {
        setValidLinkedinName(null);
        setDialogTitle("Invalid LinkedIn URL");
        setDialogMessage(
          result?.reason ??
            "That doesn't look like a valid LinkedIn profile link. Please check and try again."
        );
        setDialogOpen(true);
        return;
      }

      // Valid — show the extracted name and ask to continue
      setValidLinkedinName(result.name ?? null);
      setDialogTitle("LinkedIn Profile Detected");
      setDialogMessage(`We found this name on the profile: ${result.name}`);
      setDialogOpen(true);
    } catch (error) {
      setValidLinkedinName(null);
      setDialogTitle("Unable to Verify");
      setDialogMessage(
        "We couldn't verify your LinkedIn URL right now. Please try again in a moment."
      );
      setDialogOpen(true);
    } finally {
      setIsValidating(false);
    }
  };

  const confirmLinkedin = async () => {
    try {
      setIsConfirming(true);
      if (validLinkedinName) {
        await setUserName({ name: validLinkedinName });
      }
      await updateOnboardingStep({ step: "linkedin" });
      toast.success(
        validLinkedinName
          ? `LinkedIn connected! Welcome, ${validLinkedinName}.`
          : "LinkedIn connected successfully!"
      );
      setDialogOpen(false);
      setCurrentStep(2);
    } catch {
      setDialogOpen(false);
      toast.error("Failed to connect LinkedIn");
    } finally {
      setIsConfirming(false);
    }
  };

  const handleResumeUpload = async () => {
    if (!resumeFile) {
      toast.error("Please select a resume file");
      return;
    }
    
    try {
      setIsUploadingResume(true);
      await updateOnboardingStep({ step: "resume" });
      toast.success("Resume uploaded successfully!");
      setCurrentStep(3);
    } catch (error) {
      toast.error("Failed to upload resume");
    } finally {
      setIsUploadingResume(false);
    }
  };

  const handleVideoUpload = async () => {
    if (!videoFile) {
      toast.error("Please record or upload a video");
      return;
    }
    
    try {
      setIsUploadingVideo(true);
      await updateOnboardingStep({ step: "video" });
      await updateOnboardingStep({ step: "completed" });
      toast.success("Video uploaded successfully!");
      navigate("/dashboard");
    } catch (error) {
      toast.error("Failed to upload video");
    } finally {
      setIsUploadingVideo(false);
    }
  };

  return (
    <div className="min-h-screen pt-20 pb-12 mt-[100px]">
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
            Let's gather the information we need to create your personalized career simulation
          </p>
        </motion.div>

        {/* Progress Bar */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mb-12"
        >
          <div className="flex items-center justify-between mb-4">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  currentStep > step.id 
                    ? 'bg-primary border-primary text-primary-foreground' 
                    : currentStep === step.id
                    ? 'border-primary text-primary'
                    : 'border-muted-foreground text-muted-foreground'
                }`}>
                  {currentStep > step.id ? (
                    <CheckCircle className="h-5 w-5" />
                  ) : (
                    <step.icon className="h-5 w-5" />
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-24 h-0.5 mx-4 ${
                    currentStep > step.id ? 'bg-primary' : 'bg-muted'
                  }`} />
                )}
              </div>
            ))}
          </div>
          <Progress value={progress} className="h-2" />
        </motion.div>

        {/* Step Content */}
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          <Card className="max-w-2xl mx-auto">
            {currentStep === 1 && (
              <>
                <CardHeader className="text-center">
                  <div className="flex justify-center mb-4">
                    <Linkedin className="h-12 w-12 text-blue-600" />
                  </div>
                  <CardTitle>Connect Your LinkedIn</CardTitle>
                  <CardDescription>
                    We'll analyze your professional profile to understand your experience and skills
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <label className="text-sm font-medium mb-2 block">
                      LinkedIn Profile URL
                    </label>
                    <Input
                      placeholder="https://linkedin.com/in/yourprofile"
                      value={linkedinUrl}
                      onChange={(e) => setLinkedinUrl(e.target.value)}
                    />
                  </div>
                  <div className="flex justify-between">
                    <Button variant="outline" onClick={() => navigate("/dashboard")} disabled={isValidating}>
                      <ArrowLeft className="h-4 w-4 mr-2" />
                      Back
                    </Button>
                    <Button onClick={handleLinkedinConnect} disabled={isValidating || !linkedinUrl}>
                      {isValidating ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Validating...
                        </>
                      ) : (
                        <>
                          Connect LinkedIn
                          <ArrowRight className="h-4 w-4 ml-2" />
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </>
            )}

            {currentStep === 2 && (
              <>
                <CardHeader className="text-center">
                  <div className="flex justify-center mb-4">
                    <FileText className="h-12 w-12 text-orange-600" />
                  </div>
                  <CardTitle>Upload Your Resume</CardTitle>
                  <CardDescription>
                    Share your resume so we can analyze your skills and experience in detail
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
                    <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <div className="space-y-2">
                      <p className="text-sm font-medium">
                        {resumeFile ? resumeFile.name : "Drop your resume here, or click to browse"}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        PDF, DOC, or DOCX up to 10MB
                      </p>
                    </div>
                    <Input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                      className="mt-4"
                    />
                  </div>
                  <div className="flex justify-between">
                    <Button variant="outline" onClick={() => setCurrentStep(1)} disabled={isUploadingResume}>
                      <ArrowLeft className="h-4 w-4 mr-2" />
                      Back
                    </Button>
                    <Button onClick={handleResumeUpload} disabled={isUploadingResume || !resumeFile}>
                      {isUploadingResume ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Uploading...
                        </>
                      ) : (
                        <>
                          Upload Resume
                          <ArrowRight className="h-4 w-4 ml-2" />
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </>
            )}

            {currentStep === 3 && (
              <>
                <CardHeader className="text-center">
                  <div className="flex justify-center mb-4">
                    <Video className="h-12 w-12 text-purple-600" />
                  </div>
                  <CardTitle>Record Your Introduction</CardTitle>
                  <CardDescription>
                    Record a 60-second video introducing yourself and your career goals
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
                    <Video className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <div className="space-y-2">
                      <p className="text-sm font-medium">
                        {videoFile ? videoFile.name : "Record or upload your introduction video"}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        MP4, MOV, or WebM up to 50MB
                      </p>
                    </div>
                    <Input
                      type="file"
                      accept="video/*"
                      onChange={(e) => setVideoFile(e.target.files?.[0] || null)}
                      className="mt-4"
                    />
                  </div>
                  <div className="bg-muted/50 p-4 rounded-lg">
                    <h4 className="font-medium mb-2">Tips for your video:</h4>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Keep it to 60 seconds or less</li>
                      <li>• Speak clearly and naturally</li>
                      <li>• Mention your background and interests</li>
                      <li>• Share what excites you about your career</li>
                    </ul>
                  </div>
                  <div className="flex justify-between">
                    <Button variant="outline" onClick={() => setCurrentStep(2)} disabled={isUploadingVideo}>
                      <ArrowLeft className="h-4 w-4 mr-2" />
                      Back
                    </Button>
                    <Button onClick={handleVideoUpload} disabled={isUploadingVideo || !videoFile}>
                      {isUploadingVideo ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Completing...
                        </>
                      ) : (
                        <>
                          Complete Setup
                          <CheckCircle className="h-4 w-4 ml-2" />
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </>
            )}
          </Card>
        </motion.div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent
            className="sm:max-w-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=open]:fade-in-0 data-[state=closed]:fade-out-0 data-[state=open]:zoom-in-95 md:data-[state=open]:slide-in-from-top-8 md:data-[state=closed]:slide-out-to-top-8 backdrop-blur-xl ring-1 ring-white/20 dark:ring-white/10 shadow-2xl"
          >
            <DialogHeader>
              <DialogTitle>{dialogTitle}</DialogTitle>
              <DialogDescription>
                {dialogMessage}
              </DialogDescription>
            </DialogHeader>
            <DialogFooter className="flex gap-2">
              <Button variant="outline" onClick={() => setDialogOpen(false)} disabled={isConfirming}>
                {validLinkedinName ? "Edit URL" : "Close"}
              </Button>
              {validLinkedinName && (
                <Button onClick={confirmLinkedin} disabled={isConfirming}>
                  {isConfirming ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Connecting...
                    </>
                  ) : (
                    "Continue"
                  )}
                </Button>
              )}
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}