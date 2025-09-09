from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from groq import Groq
import re

# ----------------- Direct API Key Declaration -----------------
api_key = "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"

if not api_key or api_key.strip() == "":
    raise ValueError("❌ No API key found! Please add your Groq API key to the api_key variable.")

# ----------------- Server Check -----------------
def check_groq_server(api_key, model="llama-3.1-8b-instant"):
    client = Groq(api_key=api_key)
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "test"}],
            model=model,
            max_tokens=1,
            temperature=0.1
        )
        if response.choices[0].message.content:
            return True
    except Exception:
        return False
    return False

# ----------------- Initialize LLM -----------------
server_status = check_groq_server(api_key)
llm_engine = None
if server_status:
    try:
        llm_engine = ChatGroq(
            groq_api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.7,
            max_retries=2,
            timeout=30
        )
    except Exception as e:
        print(f"⚠ Failed to init LLM: {e}")
        server_status = False

# ----------------- PROMPTS -----------------
system_prompt = SystemMessagePromptTemplate.from_template(
    "You are a senior healthcare professional generating scientifically-grounded 7-day care plans. "
    "You must perform comprehensive analysis of the patient's medical data and create a practical, "
    "safe, and evidence-based care plan. EVERY recommendation must be medically appropriate for "
    "the patient's specific age, conditions, and physical capabilities."
)

def _strip_think_tags(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

def _extract_plan_only(text: str) -> str:
    patterns = [
        "Enhanced 7-Day Care Plan",
        "7-Day Care Plan", 
        "Day 1",
        "Personalized Care Plan",
        "Daily Care Plan"
    ]
    
    for pattern in patterns:
        idx = text.find(pattern)
        if idx != -1:
            return text[idx:].strip()
    
    return text.strip()

def _format_output(text: str) -> str:
    text = text.strip()
    # Add proper spacing between sections
    text = re.sub(r'(Day \d+)', r'\n\n\1\n', text)
    text = re.sub(r'(🏃|🧘|🥗|💧|❌|✅|⚠)', r'\n\1', text)
    text = re.sub(r'→', ' → ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def _validate_plan(text: str) -> None:
    required = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
    for d in required:
        if d not in text:
            raise ValueError("Plan missing days")

def _remove_unwanted_sections(text: str) -> str:
    """Remove monitoring instructions, medication interactions, fall risk precautions, and conclusion"""
    sections_to_remove = [
        "Monitoring Instructions:",
        "Medication Interactions:",
        "Fall Risk Precautions:",
        "Conclusion:",
        "Regular monitoring and follow-up",
        "Medication adherence:"
    ]
    
    for section in sections_to_remove:
        idx = text.find(section)
        if idx != -1:
            # Remove from this section to the end of the text or to the next section
            next_section = None
            for next_sec in sections_to_remove:
                if next_sec != section:
                    next_idx = text.find(next_sec, idx + len(section))
                    if next_idx != -1 and (next_section is None or next_idx < next_section):
                        next_section = next_idx
            
            if next_section is not None:
                text = text[:idx] + text[next_section:]
            else:
                text = text[:idx]
    
    return text.strip()

def generate_care_plan_from_report(report_text: str) -> str:
    if llm_engine is None:
        raise Exception("LLM engine not available.")
    
    # Enhanced prompt with strict instructions for personalization
    prompt_template = ChatPromptTemplate.from_messages([
        system_prompt,
        HumanMessagePromptTemplate.from_template(""" 

CRITICAL HEALTHCARE ANALYSIS TASK:

PATIENT REPORT TO ANALYZE:
{report_text}

IMPORTANT: ONLY generate the 7-day care plan. DO NOT include any monitoring instructions, medication interactions, fall risk precautions, or conclusion sections.

REQUIRED ANALYSIS PHASE:
1. Extract ALL medical data: demographics, vitals, test results, diagnosed conditions
2. Identify primary health issues and their severity levels
3. Assess patient capabilities based on age, mobility, and existing conditions
4. Determine contraindications and safety limitations

SCIENTIFIC CARE PLAN CREATION RULES:
- Base EVERY recommendation strictly on the patient's actual test results and medical data
- Prioritize SAFETY and medical appropriateness above all else
- Create VARIED but PRACTICAL activities and meals
- Ensure ALL activities are AGE-APPROPRIATE and CONDITION-SAFE
- Include specific, measurable instructions: portion sizes, durations, frequencies
- Address ALL identified medical conditions in each day's plan
- Consider medication interactions, mobility limitations, and fall risks
- Balance variety with practicality

DAILY STRUCTURE (ONLY include these sections):
Day [X]  
🏃 Physical Activity: [Medically safe activity for patient's age/condition] → [Physiological benefit specific to their health issues]  
🧘 Mental Wellness: [Appropriate technique] → [Mental health benefit addressing their specific needs]  
🥗 Meals: [Practical meals with specific ingredients/portions] → [Nutritional benefits for their conditions]  
💧 Hydration: [Appropriate fluid types/amounts] → [Health benefits based on their kidney function, medications, etc.]  
❌ Avoid: [Specific contraindicated items/behaviors] → [Exact risks based on their test results]  
✅ Today's risk reduction: [How today's plan addresses their specific risk percentages]  
⚠ Consequences if skipped: [Realistic worsening of their actual medical conditions]

MANDATORY REQUIREMENTS:
- Reference SPECIFIC patient data in every recommendation
- Ensure all activities are medically safe for their age and conditions
- Maintain practicality - the plan must be executable in real life
- Balance variety with consistency where medically beneficial
- Prioritize evidence-based recommendations over novelty

ABSOLUTELY PROHIBITED:
- Generic advice not tied to specific patient data
- Medically unsafe recommendations
- Activities beyond patient's physical capabilities
- Nutritionally inappropriate suggestions
- Recommendations that contradict their medical conditions
- Monitoring instructions, medication interactions, fall risk precautions, or conclusion sections

The plan must be clinically sound, practical, and tailored to this individual's capabilities and limitations.
""")
    ])
    
    chain = prompt_template | llm_engine | StrOutputParser()
    response = chain.invoke({"report_text": report_text})
    text = _strip_think_tags(response)
    text = _extract_plan_only(text)
    text = _format_output(text)
    text = _remove_unwanted_sections(text)  # Remove unwanted sections
    _validate_plan(text)
    return text

# ----------------- Variable Input -----------------
# This can be changed to any patient report
report_input = """🚀 Training Hypertension Prediction Pipeline...
✅ Training complete!

🧑 Enter patient details manually:
Age:  90
Sex (0=female, 1=male):  1
BMI:  31.5
Family history (0/1):  1
Creatinine:  1.4
Systolic BP:  145
Diastolic BP:  92

🎯 Results
Hypertension Stage: Stage_2
Subtype: White_Coat

⚠ Risks:
  kidney_risk_1yr: 61.52%
  stroke_risk_1yr: 61.72%
  heart_risk_1yr: 61.71%

💬 Risk Statements:
  • 61.52% risk of kidney function decline in 1 year if BP not controlled
  • 61.72% risk of stroke in 1 year if BP not controlled
  • 61.71% risk of heart attack in 1 year if BP not controlled
"""
# ----------------- Generate Care Plan -----------------
if server_status and llm_engine:
    try:
        print("Analyzing patient report and generating care plan...")
        care_plan_output = generate_care_plan_from_report(report_input)
        print("✅ Care plan generated successfully!")
        
        # Store full plan in variable
        care_plan = care_plan_output  

    except Exception as e:
        print(f"❌ Failed: {str(e)}")
else:
    print("⚠ Please check your Groq API connection.")


# ----------------- SEPARATE 7 DAYS -----------------
def split_days(plan_text: str):
    """Split care plan into dictionary with Day 1..Day 7"""
    days = {}
    matches = re.split(r"\n(?=Day \d+)", plan_text.strip())
    for m in matches:
        if m.strip():
            day_label = m.split("\n")[0].strip()
            days[day_label] = m.strip()
    return days


# Separate into 7 variables
days_dict = split_days(care_plan)
day1 = days_dict.get("Day 1", "")
day2 = days_dict.get("Day 2", "")
day3 = days_dict.get("Day 3", "")
day4 = days_dict.get("Day 4", "")
day5 = days_dict.get("Day 5", "")
day6 = days_dict.get("Day 6", "")
day7 = days_dict.get("Day 7", "")


# ----------------- CONDITIONAL PRINTING -----------------
def print_day(day_text: str, day_number: int):
    """Print day content and ask for user input"""
    print(f"\n{'='*60}")
    print(f"DAY {day_number} PLAN")
    print(f"{'='*60}")
    
    # Print everything up to ❌ Avoid with better formatting
    avoid_idx = day_text.find("❌ Avoid")
    if avoid_idx != -1:
        # Find the end of the ❌ Avoid section
        end_of_avoid = day_text.find("\n", avoid_idx)
        if end_of_avoid == -1:
            end_of_avoid = len(day_text)
        
        # Format the text with proper spacing
        formatted_text = day_text[:end_of_avoid].strip()
        formatted_text = re.sub(r'(🏃|🧘|🥗|💧|❌)', r'\n\n\1', formatted_text)
        formatted_text = re.sub(r'→', ' → ', formatted_text)
        print(formatted_text)
    
    # Ask user for choice
    user_choice = input("\nDid you follow today's care plan? (yes/no): ").strip().lower()
    
    reduction_idx = day_text.find("✅ Today's risk reduction")
    consequences_idx = day_text.find("⚠ Consequences if skipped")
    
    if user_choice == "yes" and reduction_idx != -1:
        # Print risk reduction section
        next_idx = consequences_idx if consequences_idx != -1 else len(day_text)
        reduction_text = day_text[reduction_idx:next_idx].strip()
        reduction_text = re.sub(r'→', ' → ', reduction_text)
        print(f"\n{reduction_text}")
    elif user_choice == "no" and consequences_idx != -1:
        # Print consequences section
        consequences_text = day_text[consequences_idx:].strip()
        consequences_text = re.sub(r'→', ' → ', consequences_text)
        print(f"\n{consequences_text}")


# ----------------- Example Usage -----------------
print("\n" + "="*60)
print("DAY-BY-DAY CARE PLAN PROGRESS")
print("="*60)

# Print each day one by one with yes/no interaction
days = [day1, day2, day3, day4, day5, day6, day7]
for i, day in enumerate(days, 1):
    print_day(day, i)
    
    # Ask if user wants to continue to next day
    if i < 7:
        continue_next = input("\nContinue to next day? (yes/no): ").strip().lower()
        if continue_next != "yes":
            print("\nStopping care plan progression.")
            break