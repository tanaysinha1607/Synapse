import { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [gapAnalysis, setGapAnalysis] = useState<any>(null);

  const userId = "amardeep001"; // hardcoded for hackathon demo

  useEffect(() => {
    async function fetchData() {
      try {
        // 1. Fetch profile
        const profileRes = await apiRequest(`/profile/${userId}`);
        setProfile(profileRes);

        // 2. Fetch recommendations
        const recRes = await apiRequest("/recommend", {
          method: "POST",
          body: JSON.stringify({
            skills: profileRes.manual_skills || [],
            project_description: profileRes.resume_file || "",
          }),
        });
        setRecommendations(recRes);

        // 3. Fetch gap analysis
        const gapRes = await apiRequest("/gap_analysis", {
          method: "POST",
          body: JSON.stringify({
            skills: profileRes.manual_skills || [],
            dream_role:
              (profileRes.career_goals && profileRes.career_goals[0]) ||
              "Data Analyst",
            dream_company: "Google",
          }),
        });
        setGapAnalysis(gapRes);

        setLoading(false);
      } catch (err: any) {
        console.error("Error loading dashboard:", err);
        toast.error("Failed to load dashboard data");
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8 space-y-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      {/* User Profile */}
      <Card>
        <CardHeader>
          <CardTitle>User Profile</CardTitle>
        </CardHeader>
        <CardContent>
          <p>
            <strong>User ID:</strong> {userId}
          </p>
          <p>
            <strong>Career Goals:</strong>{" "}
            {profile?.career_goals?.join(", ") || "Not provided"}
          </p>
          <p>
            <strong>Skills:</strong>{" "}
            {profile?.manual_skills?.join(", ") || "Not provided"}
          </p>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          {recommendations ? (
            <div>
              <p>
                <strong>Top Role:</strong>{" "}
                {recommendations.top_role_title || "N/A"}
              </p>
              <p>
                <strong>Skill Match:</strong>{" "}
                {recommendations.your_skill_match_percent ?? "N/A"}%
              </p>
              <p>
                <strong>Market Demand:</strong>{" "}
                {recommendations.market_demand_score ?? "N/A"}%
              </p>

              {/* Next Probable Steps */}
              {recommendations.next_probable_steps && (
                <div>
                  <strong>Next Steps:</strong>{" "}
                  {Array.isArray(recommendations.next_probable_steps)
                    ? recommendations.next_probable_steps.join(", ")
                    : Object.keys(recommendations.next_probable_steps).join(
                        ", "
                      )}
                </div>
              )}

              {/* Tiered Results */}
              <div className="mt-4">
                <strong>Tiers:</strong>
                <ul className="list-disc ml-6">
                  {recommendations.tiers?.aspirational && (
                    <li>
                      Aspirational:{" "}
                      {recommendations.tiers.aspirational.Standard_Title} @{" "}
                      {recommendations.tiers.aspirational.CompanyName}
                    </li>
                  )}
                  {recommendations.tiers?.target && (
                    <li>
                      Target: {recommendations.tiers.target.Standard_Title} @{" "}
                      {recommendations.tiers.target.CompanyName}
                    </li>
                  )}
                  {recommendations.tiers?.discovery && (
                    <li>
                      Discovery: {recommendations.tiers.discovery.Standard_Title}{" "}
                      @ {recommendations.tiers.discovery.CompanyName}
                    </li>
                  )}
                </ul>
              </div>
            </div>
          ) : (
            <p>No recommendations found.</p>
          )}
        </CardContent>
      </Card>

      {/* Gap Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Gap Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          {gapAnalysis ? (
            <div>
              <p>
                <strong>Dream Role:</strong> {gapAnalysis.dream_role || "N/A"}
              </p>
              <p>
                <strong>Match Score:</strong>{" "}
                {gapAnalysis.match_score_percent ?? "N/A"}%
              </p>
              <p>
                <strong>Skills to Develop:</strong>{" "}
                {gapAnalysis.skills_to_develop?.join(", ") || "None 🎉"}
              </p>
            </div>
          ) : (
            <p>No gap analysis available.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
