import asyncio
import os

# Ensure CrewAI path is used by default
os.environ.setdefault("USE_CREWAI", "1")

from crews.profiler.profiler_agent import ProfilerAgent


def main():
	user_id = "demo_user_001"
	inputs = {
		"resume_file": (
			"I am a Computer Science student with experience in Python, Machine Learning,"
			" data analysis, and web development. Built a sentiment analysis tool and"
			" a Flask web application."
		),
		"manual_skills": ["Python", "Pandas", "scikit-learn", "Leadership"],
		"career_goals": ["AI/ML Engineer", "Data Scientist"],
		# Optionally add: "video_file": "path/to/video.mp4",
		# Optionally add: "linkedin_url": "https://www.linkedin.com/in/example"
	}

	async def run():
		agent = ProfilerAgent(project_id=os.getenv("GOOGLE_CLOUD_PROJECT_ID", "your-project-id"))
		profile = await agent.process_user_inputs(user_id, inputs)
		print("User:", profile.user_id)
		print("Experience:", profile.experience_level)
		print("Goals:", ", ".join(profile.career_goals))
		print("Skills (first 10):")
		for skill in profile.skill_graph[:10]:
			print(f" - {skill.name} [{skill.category.value}] ({skill.level.value}) conf={skill.confidence:.2f}")

	asyncio.run(run())


if __name__ == "__main__":
	main()