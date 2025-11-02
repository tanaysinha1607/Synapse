// Frontend/src/lib/mlApi.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:18081/ml/api/v1";

/**
 * Helper to do a JSON POST with timeout and robust parsing.
 */
async function postJson(path: string, payload: any, timeoutMs = 20_000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    // read as text first (some endpoints may not return valid JSON)
    const text = await res.text();

    if (!res.ok) {
      // try parse JSON error else return text
      try {
        const jsonErr = JSON.parse(text);
        throw new Error(jsonErr?.error || jsonErr?.message || JSON.stringify(jsonErr));
      } catch {
        throw new Error(text || `HTTP ${res.status}`);
      }
    }

    try {
      return JSON.parse(text);
    } catch {
      // Not JSON — return raw text
      return text;
    }
  } catch (err) {
    if ((err as any).name === "AbortError") {
      throw new Error("Request timed out");
    }
    throw err;
  } finally {
    clearTimeout(id);
  }
}

/** Generate career plan */
export async function generateCareerPlan(profileData: any, quizData: any) {
  return postJson("/generate_career_plan", { profile_data: profileData, quiz_data: quizData });
}

/** Perform gap analysis */
export async function gapAnalysis(userSkills: string[], dreamRole: string, dreamCompany?: string) {
  return postJson("/gap_analysis", { user_skills: userSkills, dream_role: dreamRole, dream_company: dreamCompany });
}
