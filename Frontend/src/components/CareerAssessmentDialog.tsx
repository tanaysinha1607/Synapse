import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Progress } from "@/components/ui/progress";
import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface AssessmentAnswers {
  careerGoal?: string;
  primaryMotivator?: string;
  fiveYearVision?: string;
  weeklyHours?: string;
  learningStyle?: string;
  skillConfidence?: string;
  workEnvironment?: string;
  unconventionalRoles?: string;
  workEnergy?: string;
  minSalary?: string;
}

interface CareerAssessmentDialogProps {
  open: boolean;
  onComplete: (answers: AssessmentAnswers) => void;
}

export function CareerAssessmentDialog({ open, onComplete }: CareerAssessmentDialogProps) {
  const [currentSection, setCurrentSection] = useState(0);
  const [answers, setAnswers] = useState<AssessmentAnswers>({});

  const sections = [
    {
      title: "Your Career Goals",
      description: "Help us understand what you're looking for",
      questions: [
        {
          id: "careerGoal",
          question: "Which of these best describes your immediate career goal?",
          options: [
            { value: "highest-paying", label: "Find the highest-paying job, regardless of role" },
            { value: "top-tier", label: "Secure a role at a top-tier company (e.g., Google, Microsoft)" },
            { value: "startup", label: "Join a high-growth startup with high impact and ownership" },
            { value: "work-life", label: "Find a role with strong work-life balance and remote options" },
            { value: "exploring", label: "I'm exploring and want the best overall match for my skills" },
          ],
        },
        {
          id: "primaryMotivator",
          question: "What is your primary motivator for your next step?",
          options: [
            { value: "learning", label: "Learning and Skill Growth" },
            { value: "salary", label: "Salary and Compensation" },
            { value: "prestige", label: "Company Prestige and Brand" },
            { value: "impact", label: "Impact and Work Ownership" },
          ],
        },
        {
          id: "fiveYearVision",
          question: "Thinking 5 years ahead, what is more appealing?",
          options: [
            { value: "technical", label: "Deep technical mastery (e.g., Principal/Staff Engineer)" },
            { value: "leadership", label: "People and team leadership (e.g., Engineering Manager)" },
            { value: "entrepreneur", label: "Starting your own company or venture" },
          ],
        },
      ],
    },
    {
      title: "Your Learning Style",
      description: "How do you want to get there?",
      questions: [
        {
          id: "weeklyHours",
          question: "How many hours per week can you realistically commit to upskilling?",
          options: [
            { value: "1-3", label: "1-3 hours (Just the basics)" },
            { value: "4-6", label: "4-6 hours (Consistent effort)" },
            { value: "7-10", label: "7-10 hours (Serious commitment)" },
            { value: "10+", label: "10+ hours (Full-time focus)" },
          ],
        },
        {
          id: "learningStyle",
          question: "What's your preferred way to learn a new, complex skill?",
          options: [
            { value: "hands-on", label: "Hands-on projects (Give me a challenge to build)" },
            { value: "structured", label: "Structured courses (Guide me with videos and modules)" },
            { value: "documentation", label: "Reading documentation (I'll figure it out myself)" },
          ],
        },
        {
          id: "skillConfidence",
          question: "When you look at your primary technical skill, how would you rate your confidence?",
          options: [
            { value: "beginner", label: "Beginner: I understand the concepts but have few projects" },
            { value: "intermediate", label: "Intermediate: I've built projects and can work independently" },
            { value: "advanced", label: "Advanced: I'm very confident and could mentor others" },
          ],
        },
      ],
    },
    {
      title: "Your Work Preferences",
      description: "What is your ideal fit?",
      questions: [
        {
          id: "workEnvironment",
          question: "Which of these work environments sounds most appealing?",
          options: [
            { value: "large-company", label: "A large, structured company with clear career ladders" },
            { value: "startup", label: "A fast-paced, 'build-it-from-scratch' startup" },
            { value: "mission-driven", label: "A mission-driven organization (e.g., non-profit, HealthTech, EdTech)" },
            { value: "remote", label: "A fully remote and flexible arrangement" },
          ],
        },
        {
          id: "unconventionalRoles",
          question: "Are you open to exploring 'unconventional' job titles that match your skills?",
          options: [
            { value: "yes", label: "Yes, show me the best matches, even if I don't recognize the title" },
            { value: "no", label: "No, I prefer to stick to traditional roles (e.g., 'Software Engineer')" },
          ],
        },
        {
          id: "workEnergy",
          question: "What kind of work energizes you the most?",
          options: [
            { value: "building", label: "Building and shipping products directly to users" },
            { value: "analyzing", label: "Analyzing data and discovering hidden insights" },
            { value: "designing", label: "Designing and optimizing complex systems and models" },
            { value: "collaborating", label: "Collaborating with people and solving business problems" },
          ],
        },
        {
          id: "minSalary",
          question: "What is your minimum acceptable annual salary (INR)?",
          type: "input",
          placeholder: "e.g., 4,00,000",
        },
      ],
    },
  ];

  const totalSections = sections.length;
  const progress = ((currentSection + 1) / totalSections) * 100;

  const handleAnswer = (questionId: string, value: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
  };

  const canProceed = () => {
    const currentQuestions = sections[currentSection].questions;
    return currentQuestions.every((q) => answers[q.id as keyof AssessmentAnswers]);
  };

  const handleNext = () => {
    if (currentSection < totalSections - 1) {
      setCurrentSection((prev) => prev + 1);
    } else {
      onComplete(answers);
    }
  };

  const handleBack = () => {
    if (currentSection > 0) {
      setCurrentSection((prev) => prev - 1);
    }
  };

  return (
    <Dialog open={open} onOpenChange={() => {}}>
      <DialogContent className="max-w-4xl max-h-[85vh] overflow-y-auto rounded-3xl backdrop-blur-xl bg-black/60 dark:bg-black/70 border border-white/20 shadow-2xl">
        <DialogHeader className="space-y-3 pb-2">
          <DialogTitle className="text-3xl font-bold tracking-tight bg-gradient-to-r from-violet-400 via-fuchsia-400 to-cyan-400 bg-clip-text text-transparent">
            {sections[currentSection].title}
          </DialogTitle>
          <DialogDescription className="text-base text-muted-foreground">
            {sections[currentSection].description}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-8 py-6">
          <div className="space-y-3">
            <div className="flex justify-between text-sm font-medium text-muted-foreground">
              <span>Section {currentSection + 1} of {totalSections}</span>
              <span>{Math.round(progress)}% Complete</span>
            </div>
            <Progress value={progress} className="h-3 bg-white/10" />
          </div>

          <AnimatePresence mode="wait">
            <motion.div
              key={currentSection}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-10"
            >
              {sections[currentSection].questions.map((question) => (
                <div key={question.id} className="space-y-5 p-6 rounded-2xl bg-white/5 border border-white/10">
                  <Label className="text-lg font-semibold leading-relaxed text-foreground">
                    {question.question}
                  </Label>
                  {question.type === "input" ? (
                    <Input
                      type="text"
                      placeholder={question.placeholder}
                      value={answers[question.id as keyof AssessmentAnswers] || ""}
                      onChange={(e) => handleAnswer(question.id, e.target.value)}
                      className="max-w-md text-base h-12 bg-white/10 border-white/20 focus:border-primary/50"
                    />
                  ) : (
                    <RadioGroup
                      value={answers[question.id as keyof AssessmentAnswers] || ""}
                      onValueChange={(value) => handleAnswer(question.id, value)}
                      className="space-y-4"
                    >
                      {question.options?.map((option) => (
                        <div key={option.value} className="flex items-start space-x-4 space-y-0 p-4 rounded-xl hover:bg-white/5 transition-colors border border-transparent hover:border-white/10">
                          <RadioGroupItem value={option.value} id={`${question.id}-${option.value}`} className="mt-0.5" />
                          <Label
                            htmlFor={`${question.id}-${option.value}`}
                            className="font-normal cursor-pointer leading-relaxed text-base flex-1"
                          >
                            {option.label}
                          </Label>
                        </div>
                      ))}
                    </RadioGroup>
                  )}
                </div>
              ))}
            </motion.div>
          </AnimatePresence>
        </div>

        <div className="flex justify-between pt-6 border-t border-white/10">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={currentSection === 0}
            className="h-12 px-6 text-base bg-white/5 border-white/20 hover:bg-white/10"
          >
            <ChevronLeft className="h-5 w-5 mr-2" />
            Back
          </Button>
          <Button
            onClick={handleNext}
            disabled={!canProceed()}
            className="h-12 px-8 text-base bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700"
          >
            {currentSection === totalSections - 1 ? "Complete Assessment" : "Next"}
            {currentSection < totalSections - 1 && <ChevronRight className="h-5 w-5 ml-2" />}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}